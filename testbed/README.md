# VM testbed
___Requirements___

    $  sudo apt-get install qemu-kvm
    $  sudo apt-get install x11-apps virt-manager


### Build the required repositories

    $  mkdir out;  mkdir in; mkdir conf; mkdir _dumps
    $  mkdir -p  ub1404/BASE
 
 Download the the [image](https://www.dropbox.com/s/yjme2vtyj5043qe/ub1404_golden.qcow2?dl=0
) and the [configurations](https://www.dropbox.com/s/i2800iifq1j2947/ub1404_golden.xml?dl=0). Copy them to testbed/ub1404/ub1404_golden/
 
  
    
    
### Add your key to  the golden image

Type virt-manager to the server and start the ub1404_golden vm.
Connect to it and copy your public key to the .ssh/config/authorizedkeys.
if you don't do that when you will be asked to give a passworrd when you ssh into the vms you will create.

### Add 5 more interfecase to the goldenimage
    
    $  cd golden ub1404/ub1404_golden/
    $  virsh define ub1404_golden.xml
    $  ./cloneCtrl.py newBase


## Set-up VMs
The following instructions willl help you create N vms.<br />
Each of these will by default run 5 clients.<br />

    $ chmod +x MRUN.py
Create N vms with indeces 1 to N. 

    $ sudo ./MRUN.py make_hosts 1 N

Randomely selects IPs for each client. Saves mapping in the 'in' directory.<br />
Create suitable xml to let vitrtmanger create the networks.<br />
Updates the ssh/config of the server to allow easy ssh to the vm.<br /> 

    $ sudo ./MRUN.py write_nets 1 N new

Create all networks, asign them to vms and start them.
    
    $ sudo ./MRUN.py create_nets 1 N
    $ sudo ./MRUN.py asign 1 N
    $ sudo ./MRUN.py start_vms 1 N


You should be able to connect to a vm simply by typing ssh vmX (X == the index of your vm). If you are asked for a password then you have not added your public key in the golden image.


## Run Bitcoin clients  

If you are useing our golden image the
[bitcoin-testnet-box](https://github.com/freewil/bitcoin-testnet-box) will  already be in each vm.<br />
Still we need to change the owner of the Bitcoin directory.<br />

    $ ./MRUN.py chown 1 N
    $ chmod +x namespace
    $ cp namespace  conf/*/
    $ chmod +x Makefile
    $ cp Makefile  conf/*/

Change the configuration of the clients to run using a specific IP.<br />
Copy using rsync the custimozed for each vm configuration.

    $ sudo ./MRUN.py bind 1 N
    $ ./MRUN.py rsync 1 N
  
Create namespaces in each VM to allow multiple *independent* clients per VM<br />

    $ ./MRUN.py ns 1 N



Start the bitcoin clients in each VM<br />
   
    $ ./MRUN.py run_start 1 N

Instruct the nodes to establish k random connections 
Note that their peers.dat is empty in the first run.
   
    $ ./MRUN.py new_connections 1 N k


In the MRUN.py change the controller='TO_BE_CHANGED'. Select one vm to be the controller, the controller is used to request Bitcoin status from each vm

You can use 'giveme' to access the [API of each Bitcoin client](https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list).
For instance the following will return the client's peers, the blockchain length and object containing various state info respectively of the third client running on vm 1
    
    $ ./MRUN.py giveme  1 3 getpeerinfo 
    $ ./MRUN.py giveme 1 3 'getblockcount'
    $ ./MRUN.py  giveme 1 3 getinfo


## Destroy vms
The testbed will consume a lot of resources of the sever make sure you clean it properly.

    $ ./MRUN.py stop_btc 1 N
    $ ./MRUN.py stop_hosts 1 N
    $ ./MRUN.py delete_nets 1 N
    $ sudo ./MRUN.py delete_hosts 1 N
    
## Please contact me if you have questions
  apmaria at ethz dot ch
