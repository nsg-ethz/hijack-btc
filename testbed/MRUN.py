#!/usr/bin/env python
import os, sys
import datetime
from time import sleep
from helpers import run
from helpers import runb
from helpers import runo
import random
import argparse
INDIR='/home/virt/code/prj/vms/in/'
OUTDIR='/home/virt/code/prj/vms/out'
SYNCDIR= '/home/virt/code/prj/vms/conf/' # directory with files that should be rsynced to all vms

VMOUTDIR='/home/ubuntu/bitcoin-testnet-box/1/testnet3/'
VMRSYNCDIR='/home/ubuntu/bitcoin-testnet-box'
NODES_NUM=7

# PICK ON OF THE VMS as controller
controller='ubuntu@17.15.137.163'

#EXAMPLES:
#./MRUN.PY giveme  206 2 'addnode 109.39.152.46:19000 'onetry''
#./MRUN.PY giveme  206 2 getpeerinfo
# sudo chown -R ubuntu bitcoin-testnet-box/


 with open(INDIR+"btc_clients", "r") as ins:
    for line2 in ins:
      l=line2.split()
      hj.append((l[0],l[1],l[2]))
    i=0
    conn=set()
    for i in range(len(hj)):
      j=i+1
      conn[hj[i]]=set()
      while len(conn[hj[i])<10:
        while j < len(hj):
          if hj[j] not in conn[hj[i]] and hj[i] not in conn[hj[j]] :
            conn[hj[i]].add(hj[j])
            j=j+1
        j=0



def  map_nodes():
  vm2ip={}
  with open(INDIR+"btc_clients", "r") as ins:
    for line2 in ins:
      l=line2.split()
      c=(l[2],l[1]) #(,vm,node)
      vm2ip[c]=l[0]
  return vm2ip

def map_vms():
  vm2ip={}
  with open(INDIR+"ips_2_ssh", "r") as ins:
    for line2 in ins:
      l=line2.split()
      vm2ip[int(l[1][2:])]=l[0]
  return vm2ip

def giveme (vm, node, cmd):
  node_adrr=map_nodes()
  c='bitcoin-cli -rpcconnect=%s -rpcport=19100 -datadir=/home/ubuntu/bitcoin-testnet-box/%s %s ' % (node_adrr[(str(vm),str(node))],node,cmd)
  print c 
  run(c,controller)  
  return

def test_n_start(ffrom, to):
  started=0
  for vm in range(ffrom, to+1):
    for node in range(1,6):
      print "will check", vm, node
      try:
        giveme("vm"+str(vm) , node , 'getinfo')

      except Exception as e:
        started=started+1
        print "Probably not running"
        run_start ( vm, vm, [node] )
  print "____STARTED___", started, '____out of____ ',(to-ffrom+1)*5

def new_connections(ffrom, to , c):
  node2ip=map_nodes()
  all_nodes=node2ip.values()
  for vm in range(ffrom, to+1): 
    for node in range(1,6):
      for k in range(int(c)):
        nn=random.choice(all_nodes)
        cmd="addnode %s:18333 'onetry'" % nn
        print cmd
        try:
          giveme ("vm"+str(vm), node, cmd)
        except:
          pass
  return


def bind_ips_to_nodes(a,ase):
  with open(INDIR+"btc_clients", "r") as ins:
    for line2 in ins:
      l=line2.split()
      vm=l[2][2:]
      node=l[1]
      ip=l[0]
      port=18333
      rpcport=19100
      VMDIR='/home/virt/code/prj/vms/conf/%s/%s' % (vm,node)
      try:
       re=open(VMDIR+'/bitcoin.conf','wb') 
      except Exception as e:
        print e
        run('mkdir -p '+ VMDIR )
        re=open(VMDIR+'/bitcoin.conf','wb') 
      re.write('testnet=1\ndnsseed=0\nupnp=0\nbind=%s:%s\nport=%s\nexternalip=%s\nrest=1\nrpcport=%s\nserver=1\nrpcallowip=0.0.0.0/0\nrpcuser=admin1\nrpcpassword=123'% (ip , port,port ,ip, rpcport))
      re.close()


def rsync(f, to):
  for vm in range(f, to+1):     
    cmd='rsync -avz %s    vm%s:%s' % (SYNCDIR+str(vm)+'/' , vm, VMRSYNCDIR)
    #rsync -avz /home/virt/code/prj/vms/sync2vms/   node5:/home/ubuntu/bitcoin-testnet-box
    print 'Rsync to VM %s. cmd:     %s' % (vm,cmd)
    run(cmd)
  return

def ns(f, to):
  vm2ip=map_vms()
  for vm in range(f, to+1): 
    cmd='sudo /home/ubuntu/bitcoin-testnet-box/namespace ' 
    run(cmd, "ubuntu@%s" % vm2ip[vm])
    print "Name spaces for vm %s" % vm  
  return

def make(vm,node, cmd):
  ssh_to_node=map_vms()

  cmd='cd /home/ubuntu/bitcoin-testnet-box; make %s%s >> /tmp/make_out.txt' % (cmd, node)
  print "VM %s node %s will execute %s" % (vm, node, cmd)
  try:
    pid=run(cmd, "ubuntu@%s" % ssh_to_node[int(vm)])
  except:
    pass
  return

def make_all(ffrom, to, cmd):
  for vm in range(ffrom, to+1): 
    for node in range(1,6):
      make(vm,node,cmd)
  return

def scp(f, to):
  now=str(datetime.datetime.now())
  now=now[5:-10].replace(' ', '_')
  #scp node5:__PUSH_TO_SERVER.SH ./
  for vm in range(f, to+1):
    try:
      run('scp vm%s:%s/log %s' % (vm,VMRSYNCDIR,OUTDIR))
      cmd=run('mv %s/log %s/%s_%s' % (OUTDIR, OUTDIR, vm,'con') )
    except Exception as e:
      print "__ERROR__",vm,e
    for node in range(0):
      run('scp vm%s:%s/%s/testnet3/debug.log %s' % (vm,VMRSYNCDIR,node,OUTDIR))
      run('mv %s/debug.log %s/%s_%s' % (OUTDIR, OUTDIR, vm,"addr") )
  return

#one entry per vm =(first asigned IP) 'where do i ssh?'

#one entry per node  = (IP:port) 'which node am I looking for , where should a node connect'
#o.write('node%s_%s   %s:%s\n'%(vm, ip_id ,ip , port+ip_id ))



def make_hosts(f,to):
  i=to-f+1
  print './cloneCtrl.py clone %s test' % i
  run('./cloneCtrl.py clone %s test' % i)
  return


def run_start ( f , to, nodes=[1,2,3,4,5] ):
  ssh_to_node=map_vms()
  for vm in range(f, to+1):
    print "VM",vm
    for node in nodes:
      print '______',node
      cmd='cd /home/ubuntu/bitcoin-testnet-box; make start%s >> /tmp/make_out.txt' % node
      print cmd
      pid=run(cmd, "ubuntu@%s" % ssh_to_node[vm])
      #pid.kill()
  return

def clean_server(a,b):
  run("sudo ./kill_all")
  return

def run_cmd ( f , to, cmd ):
  command=cmd+ " >> /tmp/log.txt &"
  ssh_to_node=map_vms()
  for i in range(f, to+1):
    print 'Node %s will execute command %s' % (i,command)
    try:   
      run(command, "ubuntu@%s" % ssh_to_node[i])
    except Exception as e:
      pass
  return
def del_ ( f , to, filee ):
  ssh_to_node=map_vms()
  for i in range(f, to+1):
   
      cmd='sudo rm /home/ubuntu/bitcoin-testnet-box/*/testnet3/%s' %  filee
      try:   
        run(cmd, "ubuntu@%s" % ssh_to_node[i])
      except Exception as e:
        print 'Node %s fail do execute cmd %s with %s' % (i,cmd,e)
  return

def chown ( f , to ):
  ssh_to_node=map_vms()
  cmd='sudo chown -R ubuntu bitcoin-testnet-box/'
  for i in range(f, to+1):
    print 'Node %s will execute cmd %s' % (i,cmd)
    try:   
      run(cmd, "ubuntu@%s" % ssh_to_node[i])
    except Exception as e:
      print 'Node %s fail do execute cmd %s with %s' % (i,cmd,e)
  return
def save_peers(f,to):
# do sudo cp bitcoin-testnet-box/$i/testnet3/peers.dat  bitcoin-testnet-box/$i/testnet3/peers.dat.bak; done
  ssh_to_node=map_vms()
  cmd='for i in {1..5}; do sudo cp bitcoin-testnet-box/$i/testnet3/peers.dat bitcoin-testnet-box/$i/testnet3/peers.dat.bak; done'
  for i in range(f, to+1):
    print 'Node %s will execute cmd %s' % (i,cmd)
    try:   
      run(cmd, "ubuntu@%s" % ssh_to_node[i])
    except Exception as e:
      print 'Node %s fail do execute cmd %s with %s' % (i,cmd,e)
  return

def cp_peers(f,to):
# do sudo cp bitcoin-testnet-box/$i/testnet3/peers.dat  bitcoin-testnet-box/$i/testnet3/peers.dat.bak; done
  ssh_to_node=map_vms()
  cmd='for i in {1..5}; do sudo cp bitcoin-testnet-box/$i/testnet3/peers.dat.bak bitcoin-testnet-box/$i/testnet3/peers.dat; done'
  for i in range(f, to+1):
    print 'Node %s will execute cmd %s' % (i,cmd)
    try:   
      run(cmd, "ubuntu@%s" % ssh_to_node[i])
    except Exception as e:
      print 'Node %s fail do execute cmd %s with %s' % (i,cmd,e)
  return
def delete_hosts(f, to):

  for i in range(f, to+1): 
      try: 
         run('./cloneCtrl.py stopAndDelete ub1404-%s' % i)
      except Exception as e: 
        print e
  return

def delete_nets(f, to):

  for vm in range(f, to+1):
    for node in range(1,6):
      try: 
         run('virsh net-destroy net%s_%s' % (vm,node))
      except Exception as e: 
        print e
  return

def stop_hosts(f, to):
  for i in range(f, to+1):
      try: 
        run('virsh destroy ub1404-%s' % i)
       
      except Exception as e: 
        print e
  return

#echo -e "lal\n kmcoefpw"
def write_nets(ffrom , to ,op):
  if op=='new':
    re=open(INDIR+'ips_2_ssh', 'wb')
    cl=open(INDIR+'btc_clients', 'wb')
    ssh=open("/home/virt/.ssh/config", 'wb' )
    ssh.write("Host * \nStrictHostKeyChecking no\n")
    ssh.write("Host golden \nHostName 192.168.122.185\nUser ubuntu\n")
    ssh.close()
    re.close()
    cl.close()
  re=open(INDIR+'ips_2_ssh', 'r+')  
  re.read()
  ssh=open("/home/virt/.ssh/config", 'r+' )
  ssh.read()
  cl=open(INDIR+'btc_clients', 'r+')
  cl.read()
  os.chdir('/home/virt/_dumps')

  for vm in range(ffrom, to+1):
    for node in range(0,6):
      a1=random.randint(2 ,199 )
      while a1==127:
        a1=random.randint(2 ,199 )
      a2=random.randint(2 ,253 )
      a3=random.randint(2 ,253 )
      a4=random.randint(2 ,253 )
      ll=map(str,[a1,a2,a3,a4])
      ip='.'.join(ll)
      ll=map(str,[a1,a2,a3,'1'])
      net='.'.join(ll)
      if node==0:
        re.write(str( ip)+' vm'+str(vm)+"\n")
        ssh.write("Host vm"+str(vm)+"\nHostName "+str(ip) +"\nUser ubuntu\n" )
      else:
        cl.write(str(ip)+' '+str(node)+' vm'+str(vm)+"\n")
      print 'Write to net%s_%s.xml' % (vm,node)
      open('net%s_%s.xml' % (vm,node), 'w').write(
        '''<network>
          <name>net%s_%s</name>
          <bridge name="virbr%s_%s" />
          <forward mode="route" />
      <ip address='%s' netmask='255.255.255.0'>
        <dhcp>
          <range start='%s' end='%s'/>
        </dhcp>
      </ip>    
      </network>''' % (vm,node,vm,node,net,ip,ip))
      try: run('virsh net-destroy net%s_%s' % (vm,node))
      except: pass
  ssh.close()
  re.close()
  cl.close()
  os.chdir('..')

def create_nets(ffrom , to ):
  os.chdir('/home/virt/_dumps')
  for vm in range(ffrom, to+1):
    for node in range(0,6):
      try: 
        run('virsh net-create net%s_%s.xml' % (vm,node))
        print '  net%s_%s created' % (vm,node)
        sleep(2)
      except: 
        pass
  os.chdir('..')
  return 

def asign_nets_to_vms(ffrom , to ):
  # assign vms to nets
  os.chdir('/home/virt/_dumps')
  for vm in range(ffrom, to+1):
      try: run('virsh destroy ub1404-%s' % vm)
      except: pass
      run('virsh dumpxml ub1404-%s > %s' % (vm,vm))

      run('sed -i "s/default/net%s_0/" %s' % (vm,vm) )
      for ii in range(1,6):
        run('sed -i "s/eth%s/net%s_%s/" %s' % (ii,vm,ii,vm) )
      
      run('virsh define %s' % (vm))

      
  os.chdir('..')

def start_vms(ffrom, to):
  for vm in range(ffrom, to+1):
    run('virsh start ub1404-%s' % vm)
    print 'ub1404-%s started !' % vm

parser = argparse.ArgumentParser("{delete_nets, stop_hosts,set_up,delete_hosts}")
parser.add_argument("option", type=str, help=" ")
parser.add_argument("start", type=int, help="start")
parser.add_argument("end", type=int, help="end")
parser.add_argument("extra", type=str,nargs='*', help="end")

args = parser.parse_args()
opt= args.option
start= args.start
end= args.end
extra= args.extra
if opt=="make_hosts":
  make_hosts(start,end)
#Write will destroy a network if you ask to rewrite it!!!!!
#If you want to rewrite all better reboot the server this will destroy them automatically :D
elif opt=='write_nets'and len(extra):
  write_nets(start,end,extra[0])

elif opt=='create_nets':
  create_nets(start,end)
#define
elif opt=='asign':
  asign_nets_to_vms(start,end)

elif opt=='start_vms':
  start_vms(start,end)

elif opt=='chown':
  chown(start,end)

elif opt=='test_n_start':
  test_n_start(start,end)


elif opt=='bind':
  bind_ips_to_nodes(start,end)

elif opt=="rsync" :
  rsync(start,end)

elif opt=='ns':
  ns(start,end)

elif opt=="run_start" :
  if len(extra):
    run_start(start,end,extra)
  else:
      run_start(start,end) 

if opt=='kill_back':
  clean_server(start,end)

elif opt=='log' :
  run_cmd(start, end, 'nohup python  '+ VMRSYNCDIR+'/simple_log.py ')

elif opt=='save_peers':
  save_peers(start,end)
elif opt=='stop_log' :
  run_cmd(start, end, 'pkill -f simple_log.py')

elif opt=='giveme':
  giveme("vm"+str(start),end,extra[0])
elif opt=='make_all':
  make_all(start, end, extra[0])
elif opt=='make':
  make (start, end, extra[0]) # def make(vm,node, cmd):
elif opt=="scp" :
  scp(start,end)
elif opt=='new_connections':
  new_connections(start,end, extra[0])
elif opt=='stop_hosts':
  stop_hosts(start,end)

elif opt=="delete_nets":
  delete_nets(start,end)
elif opt=="cp_peers":
  cp_peers(start,end)
elif opt=="delete_hosts":
  delete_hosts(start,end)
elif opt=='del_':
  del_(start,end, extra[0])
elif opt=="run" and len(extra):
  [e]=extra
  if 'start' in e:
    print "Start is not an API cmd call  {./MRUN.PY run_start  5 5 }"
    sys.exit(0)
  run_cmd(start,end,extra[0])


#./MRUN.PY run_start  5 5  
# ./MRUN.PY run  5 5  'make -C bitcoin-testnet-box getinfo'




