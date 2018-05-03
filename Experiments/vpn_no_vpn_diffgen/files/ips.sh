#!/bin/bash

ips=($(ip addr show | grep "inet " | grep -v " lo" | grep -v meta | awk '{ print $2 }' | cut -d '/' -f1))
echo "IPs extracted: \n" >> /monroe/results/res.txt 

operators=($(ip addr show | grep mtu | grep -v lo | grep -v meta | awk "{print $2}" | cut -d '@' -f1 | cut -d ' ' -f2))

for i in "${ips[@]}"
do
        echo "Client started for ${operators[$a]} ip ${i} \n" >> /monroe/results/res.txt
        ssh -i /opt/monroe/server_login.key -L 55555:server:55555 monroe_node@server -b ${i}&
        ssh_tunnel_pid=$!
        python replay_client.py --ConfigFile=configs_local.cfg --serverInstance=localhost --jitter=true --doTCPDUMP=true --tcpdump_int=lo --resultsFolder=./res/ & 
        tunnel_diffgen_pid=$!
        python replay_client.py --ConfigFile=configs_local.cfg --serverInstance=server --jitter=true --doTCPDUMP=true --tcpdump_int=${operators[$a]} --resultsFolder=./res/ --multipleInterface=True --publicIP=${i}&
        diffgen_pid=$!
        wait $tunnel_diffgen_pid $diffgen_pid
        kill $ssh_tunnel_pid
        echo "Client finished for ${operators[$a]} ip ${i} \n" >> /monroe/results/res.txt
        a=$a+1
done

mv ./dump_client_* ./res/tcpdumpsResults/
