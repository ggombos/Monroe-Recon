
# Experiment (Youtube)
In this measurement we check the policies of the internet providers. We analyzed the youtube videos traffic on different interfaces. We used the pytomo tools (https://github.com/LouisPlisso/pytomo) for the measurement. This tool simulates the behavior of the users when it watches the youtube. The default work process is download the most popular videos and download the 30 sec from each and store the result in a databases. The tool is written in python, and it is open-source. We extended it with a parameter to change the default interface. The pytomo uses socket for downloading. We changed this socket to can use different IP address:
The default values are (can be overridden by a /monroe/config):
```
{
        true_socket = socket.socket
        socket.socket = bound_socket

        def bound_socket(*a, **k):
                sock = true_socket(*a, **k)
                sock.bind((config_pytomo.bindIp, 0))

}
```

Another problem with the tool is the SSL certificate. We got error messages („hostname doesn't match”) when try to download the videos. We can solve the problem with the code below:
```
{
        import ssl
        ssl.match_hostname = lambda cert, hostname: True

}
```

A Monroe node has more interfaces, so we need to change between them. If we want to change the interface, we have to change the ‘resolv.conf’ and the routing information.  The function below make this changes.

```
{
def monroe_dns_rewriter(ip):
	str = ''
	interface = ''
	with open('/dns') as dnsfile:
		dnsdata = dnsfile.readlines()
		print "dnsdata: ",dnsdata
		dnslist = [ x.strip() for x in dnsdata ]
		for item in dnslist:
			print "item",item
			if ip in item:
				interface = item.split('@')[2]
				print "ip",ip,"item",interface
				break
		for item in dnslist:
			# server=195.67.199.18@172.18.21.2@op1
			print "item2",item
			if interface in item:
				str += item.split('@')[0]
                            .replace("server=", "nameserver ")
				str += "\n"
	with open("/etc/resolv.conf", "w") as f:
		print "str",str
		f.write(str)
	try:
		output2 = subprocess.check_output(['bash','-c',
                     "ip route del default"])
	except:
		print "WARN: route del default return not null"
	output = subprocess.check_output(['bash','-c', "ip route show table all | grep default | grep \"dev "+interface+"\" | cut -d\" \" -f1,2,3,4,5"])
	output = subprocess.check_output(['bash','-c', 
                       "ip route add "+output.strip()])

}
```

## Videos

For measurement we used 4 youtube videos. We download 
a popular short video: ‘First Look at Nontendo Labo’ (https://www.youtube.com/watch?v=P3Bd3HUMkyU) duration: ~2:52, 
a popular long video: ‘Oscar nominations 2018 announced for the 90th Academy Awards | ABC News’ (https://www.youtube.com/watch?v=jdSUea1CEPc) duration: ~54:50, 
a non-popular short video: ‘Az M1 híradóban a migránsos videó’ (http://www.youtube.com/watch?v=rjf94G9HFkU) duration: ~3:01 and 
a non-popular long video: ‘146. Der Trucker .A kamionos. S2 E3’ (http://www.youtube.com/watch?v=w5k7A7vuVic) duration: ~1:00:59. 
We downloaded from each video the first 120 seconds. 


