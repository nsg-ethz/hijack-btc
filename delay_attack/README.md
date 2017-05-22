#  Man in The Middle Software


## Experimental Set-up

                                    ___MiTM___
                                   |         |
                                   |   nfq   |
                                   |         |
    Btc Network |<-------------- |   GATEWAY   |<---------------   Victim
                -------------->  |             |--------------->  (20.0.0.X)
                        (82.2.X.Y)             (20.0.0.1)
				  
				  
				  
				  
				  
To run this you will need two Ubuntu machines connected via an Ethernet cable. One machine will act as a Victim and the other as the Man In the Middle.



###  Attacker 
The attacker node also runs on a regular ubuntu machine and acts as gateway to the victim.
It has a public IP in eth0 and private IP, namely 20.0.0.1, in eth1. 

In the attacker's machine add IP address to the interface in which the cable is connected.
 
    $ sudo ip addr add 20.0.0.1/24 dev eth1



###  Victim 
The victim node runs the Bitcoin software v0.12.1. on a regular Ubuntu machine. 
The victim has only one private IP in the range 20.0.0.0/24 
and uses the gateway to connect to the Internet.

In the victim's machine, add an IP address and a gateway.

    $ sudo ip addr add 20.0.0.9/24 dev eth0
    $ sudo route add default gw 20.0.0.1 eth0
    
Start the bitcoin client if it is not already running.


Start the attacker's software (in the attacker's machine)
 
    $ sudo  python mitm.py


Enable forwarding of Bitcoin traffic to the NFQ
 
    $ sudo  ./enable_nfq0.sh

Disable forwarding of Bitcoin traffic to the NFQ

    $ sudo  ./disable_nfd.sh
    
    
    
    





