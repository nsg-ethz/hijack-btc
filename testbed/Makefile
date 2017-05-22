
BITCOIND=bitcoind
BITCOINCLI=bitcoin-cli
B1_FLAGS=
B2_FLAGS=
B1=-datadir=1 $(B1_FLAGS)
B2=-datadir=2 $(B2_FLAGS)
B3=-datadir=3 $(B1_FLAGS)
B4=-datadir=4 $(B2_FLAGS)
B5=-datadir=5 $(B1_FLAGS)



BLOCKS=1
ADDRESS=
AMOUNT=
ACCOUNT=

startall:
	$(BITCOIND) $(B1) -daemon -debug
	$(BITCOIND) $(B2) -daemon -debug
	$(BITCOIND) $(B3) -daemon -debug
	$(BITCOIND) $(B4) -daemon -debug
	$(BITCOIND) $(B5) -daemon -debug
	

start1:
	sudo ip netns exec ns_eth1   $(BITCOIND) $(B1) -daemon -debug

start2:
	sudo ip netns exec ns_eth2  $(BITCOIND) $(B2) -daemon -debug

start3:
	sudo ip netns exec ns_eth3  $(BITCOIND) $(B3) -daemon -debug

start4:
	sudo ip netns exec ns_eth4  $(BITCOIND) $(B4) -daemon -debug

start5:
	sudo ip netns exec ns_eth5 $(BITCOIND) $(B5) -daemon -debug



start-gui:
	$(BITCOINGUI) $(B1) &
	$(BITCOINGUI) $(B2) &

generate1:
	sudo ip netns exec ns_eth1 $(BITCOINCLI) $(B1) setgenerate true $(BLOCKS)


generate2:
	sudo ip netns exec ns_eth2 $(BITCOINCLI) $(B2) setgenerate true $(BLOCKS)


generate3:
	sudo ip netns exec ns_eth3 $(BITCOINCLI) $(B3) setgenerate true $(BLOCKS)


generate4:
	sudo ip netns exec ns_eth4 $(BITCOINCLI) $(B4) setgenerate true $(BLOCKS)


generate5:
	sudo ip netns exec ns_eth5 $(BITCOINCLI) $(B5) setgenerate true $(BLOCKS)




getinfo:
	$(BITCOINCLI) $(B1) getinfo
	$(BITCOINCLI) $(B1) getpeerinfo
getpeernum:
	$(BITCOINCLI) $(B0) getpeerinfo | grep id | wc -l 
	$(BITCOINCLI) $(B1) getpeerinfo | grep id | wc -l 

getpeers:
	$(BITCOINCLI) $(B1) getpeerinfo | grep addr 

send:
	$(BITCOINCLI) $(B1) sendtoaddress $(ADDRESS) $(AMOUNT)

address:
	$(BITCOINCLI) $(B1) getnewaddress $(ACCOUNT)



stop1:
	 sudo ip netns exec ns_eth1   $(BITCOINCLI) $(B1) stop
stop2:
	 sudo ip netns exec ns_eth2   $(BITCOINCLI) $(B2) stop
stop3:
	 sudo ip netns exec ns_eth3   $(BITCOINCLI) $(B3) stop
stop4:
	 sudo ip netns exec ns_eth4   $(BITCOINCLI) $(B4) stop
stop5:
	 sudo ip netns exec ns_eth5   $(BITCOINCLI) $(B5) stop

stopall:
	$(BITCOINCLI) $(B0) stop
	$(BITCOINCLI) $(B1) stop
	$(BITCOINCLI) $(B2) stop
	$(BITCOINCLI) $(B3) stop
	$(BITCOINCLI) $(B4) stop
	$(BITCOINCLI) $(B5) stop
	$(BITCOINCLI) $(B6) stop
	$(BITCOINCLI) $(B7)  stop


clean:
	find 1/regtest/* -not -name 'server.*' -delete
	find 2/regtest/* -not -name 'server.*' -delete