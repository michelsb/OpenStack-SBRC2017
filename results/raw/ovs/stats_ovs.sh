#!/bin/bash

if [ $# -lt 1 ]; then
   echo "Failed: arguments missing"
   exit 1
fi

scenario=$1

name="ovs"

total_time=10000
interval_time=1000
rounds=100

# bits per second
rate_bits=40000000

#The D-ITG server must be already executing...
server_private="192.168.10.5"

packet_size=(64 128 256 512 1024 1280)

echo "> Generating stats for OVS - Scenario $scenario..."

#ssh -i nfv-key.pem ubuntu@192.168.10.5 "cd /home/ubuntu/results;killall ITGRecv;nohup ITGRecv > /dev/null 2>&1 &"
#sleep 2

x=0
while [ $x != ${#packet_size[@]} ]
do
	ssh -i nfv-key.pem ubuntu@192.168.10.5 "cd /home/ubuntu/results;killall ITGRecv;nohup ITGRecv > /dev/null 2>&1 &"
        sleep 2
	a=1
	while [ $a -le $rounds ]
     	do		
		packet_size_bits=$((${packet_size[$x]}*8))
	        rate_pps=$(($rate_bits/$packet_size_bits))
        	echo ">> Round: $a ---- Packet Size: ${packet_size[$x]} <<"
	        ITGSend -a $server_private -m rttm -t $total_time -c ${packet_size[$x]} -C $rate_pps  -l sender-$name-$scenario-${packet_size[$x]}-$a.log -x receiver-$name-$scenario-${packet_size[$x]}-$a.log
	       	ITGDec sender-$name-$scenario-${packet_size[$x]}-$a.log > summary-$name-$scenario-${packet_size[$x]}-$a.log;
		#ITGDec sender-$name-$scenario-${packet_size[$x]}-$a.log -c 10000 stats-$name-$scenario-${packet_size[$x]}-$a.log;
		a=`expr $a + 1`
		if [ $a  -eq 50 ]; then
			ssh -i nfv-key.pem ubuntu@192.168.10.5 "cd /home/ubuntu/results;killall ITGRecv;nohup ITGRecv > /dev/null 2>&1 &"
			sleep 2
		fi
	done
	let "x = x+1"
done

applications_name=("voip" "dns" "cs")
applications_code=("VoIP -x G.711.1 -h RTP -VAD" "DNS" "CSa")

#ssh -i nfv-key.pem ubuntu@192.168.10.5 "cd /home/ubuntu/results;killall ITGRecv;nohup ITGRecv > /dev/null 2>&1 &"
#sleep 2

x=0
while [ $x != ${#applications_name[@]} ]
do
	ssh -i nfv-key.pem ubuntu@192.168.10.5 "cd /home/ubuntu/results;killall ITGRecv;nohup ITGRecv > /dev/null 2>&1 &"
	sleep 2
	a=1
        while [ $a -le $rounds ]
        do
		echo ">> Round: $a ---- Application: ${applications_name[$x]} <<"
		ITGSend -a $server_private -m rttm -t $total_time -l sender-$name-$scenario-${applications_name[$x]}-$a.log -x receiver-$name-$scenario-${applications_name[$x]}-$a.log ${applications_code[$x]}
		ITGDec sender-$name-$scenario-${applications_name[$x]}-$a.log > summary-$name-$scenario-${applications_name[$x]}-$a.log;
		#ITGDec sender-$name-$scenario-${applications_name[$x]}-$a.log -c 10000 stats-$name-$scenario-${applications_name[$x]}-$a.log
		a=`expr $a + 1`
		if [ $a  -eq 50 ]; then
			ssh -i nfv-key.pem ubuntu@192.168.10.5 "cd /home/ubuntu/results;killall ITGRecv;nohup ITGRecv > /dev/null 2>&1 &"
			sleep 2
                fi
        done
	let "x = x+1"
done


