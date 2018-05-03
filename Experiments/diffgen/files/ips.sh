#!/bin/bash

ips=($(ip addr show | grep "inet " | grep -v " lo" | grep -v meta | awk '{ print $2 }' | cut -d '/' -f1))
echo "IPs extracted: \n" >> /monroe/results/res.txt 

operators=($(ip addr show | grep mtu | grep -v lo | grep -v meta | awk "{print $2}" | cut -d '@' -f1 | cut -d ' ' -f2))

for i in "${ips[@]}"
do
        echo "Client started for ${operators[$a]} ip ${i} \n" >> /monroe/results/res.txt
        python replay_client.py --ConfigFile=configs_local.cfg --serverInstance=server --jitter=true --doTCPDUMP=true --tcpdump_int=${operators[$a]} --resultsFolder=./res/ --multipleInterface=True --publicIP=${i}
        echo "Client finished for ${operators[$a]} ip ${i} \n" >> /monroe/results/res.txt
        a=$a+1
done

mv ./dump_client_* ./res/tcpdumpsResults/
