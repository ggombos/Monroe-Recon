#!/bin/bash

cd /opt/monroe/

scp -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key monroe_node@server:~/diffgen/diffgen.tar.gz /opt/monroe/
tar -xvf diffgen.tar.gz

echo "diffgen.tar.gz downloaded\n" >> /monroe/results/res.txt

cd /opt/monroe/DifferentiationDetector/src/

scp -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key monroe_node@server:~/diffgen/config/configs_local.cfg /opt/monroe/DifferentiationDetector/src/configs_local.cfg

echo "configs_local.cfg downloaded\n" >> /monroe/results/res.txt

pcap_name=""
IFS="="
while read -r name value
do
if [ "$name" = "pcap_name" ]; then
  echo "$name - $value extracted\n" >> /monroe/results/res.txt
  pcap_name=$value
fi
done < /opt/monroe/DifferentiationDetector/src/configs_local.cfg

#apt update
#echo "apt update done\n" >> /monroe/results/res.txt
#apt install -y python-numpy
#echo "apt install done\n" >> /monroe/results/res.txt

scp -r -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key monroe_node@server:~/diffgen/pcaps/$pcap_name /opt/monroe/DifferentiationDetector/data/DifferentiationDetector_parsed_pcaps/

echo "$pcap_name download done\n" >> /monroe/results/res.txt

bash /opt/monroe/ips.sh

cp -r ./res/* /monroe/results/
scp -r -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key ./res/* monroe_node@server:~/diffgen/results/

echo "Results saved \n" >> /monroe/results/res.txt
