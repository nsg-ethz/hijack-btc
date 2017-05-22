#!/bin/bash

iptables -F
iptables -X
iptables -F -t nat
iptables -X -t nat

# todo: do the same for mangel and ipv6

echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -A  FORWARD   -p tcp --dport 8333 -j NFQUEUE



iptables -t nat -A POSTROUTING -s 20.0.0.0/24 -o eth0 -j MASQUERADE

iptables -A FORWARD -j LOG --log-level 2 --log-prefix pkt_in_fwd

