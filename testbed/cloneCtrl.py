#!/usr/bin/python
#based on code developed by David Gugelmann
import sys
import os
import re
import shutil
import datetime
import time

ROOT_DIR = './ub1404'
GOLDEN_DOMAIN = 'ub1404_golden'
IMAGE_DOMAIN_PREFIX = 'ub1404-'

def run(cmd, remoteHost=None):
    '''Executes command on local host if remoteHost==None or on remoteHost using ssh.
    Output of command is not redirected.
    Raises an exception of type 'CalledProcessError' if the exit status of the command is not 0 (this also works when using ssh)
    '''
    import subprocess
    if remoteHost:
        #cmd = '/usr/bin/ssh %s %s' % (remoteHost, cmd)
        cmd = '/usr/bin/ssh %s \'%s\'' % (remoteHost, cmd)
    subprocess.check_call(cmd, shell=True)




def test():
    print "hello"
    return



def runo(cmd, remoteHost=None):
    '''Executes command on local host if remoteHost==None or on remoteHost using ssh.
        Raises an exception of type 'CalledProcessError' if the exit status of the command is not 0 (this also works when using ssh).
        In the case of an exception, the output is available in 'CalledProcessError.out'.
        @return: (stdout, stderr) of command
        '''
    import subprocess
    if remoteHost:
        cmd = '/usr/bin/ssh %s \'%s\'' % (remoteHost, cmd)
        #cmd = '/usr/bin/ssh %s %s' % (remoteHost, cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    out = p.communicate()
    if p.returncode != 0:
        e = subprocess.CalledProcessError(p.returncode, cmd)
        e.out = out
        raise e
    return out
#stdout=subprocess.PIPE
def runb(cmd, remoteHost=None,shell=True):
    import subprocess, os
    assert (shell or type (cmd) is list), "shell==True with string or shell==False with list "
    global runb_running_processes_x023xmbhhm218b48xng
    if remoteHost:
        cmd = '/usr/bin/ssh %s %s' % (remoteHost, cmd)
        #cmd = '/usr/bin/ssh %s \'%s\'' % (remoteHost, cmd)
    p = subprocess.Popen(cmd, shell=shell, preexec_fn=os.setsid)
    print p.pid
    # ^-- The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    # Otherwise only the shelreloadl but not the cmd is killed on p.kill().
    # [ http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true ]
    try: runb_running_processes_x023xmbhhm218b48xng.append((p, cmd))
    except NameError: runb_running_processes_x023xmbhhm218b48xng = [(p, cmd)]
    return p








def newBase():
    c1 = CloneCtrl(ROOT_DIR, GOLDEN_DOMAIN)
    c1.copyMainToBase()


def clone(nbrClones, suffixes):
    c1 = CloneCtrl(ROOT_DIR, GOLDEN_DOMAIN)
    id = c1.getFreeId()
    for s in suffixes:
        for t in range(nbrClones):
            c1.createNewImageBasedOnNewestBaseAndRegisterIt(id, IMAGE_DOMAIN_PREFIX)
            #start('%s%i' % (IMAGE_DOMAIN_PREFIX, id))
            id = id + 1
            
            
def start(domain):
    run('%s start %s' % (CloneCtrl.VIR, domain))


def stop(domain):
    run('%s destroy %s' % (CloneCtrl.VIR, domain))


def stopAndDelete(domain):
    if len(re.compile("\d+$").findall(domain)) != 1:
        raise Exception('Only domain names ending with a number may be destroyed and deleted!') # make sure that golden domains can not be deleted accidentially
    cc = CloneCtrl('/tmp', domain) # rootDir does not matter
    if domain in cc.getRunningDomains():
        stop(domain)
    run('%s undefine %s' % (CloneCtrl.VIR, domain))
    os.remove(cc.mainImage)
    os.rmdir(os.path.dirname(cc.mainImage))


def mount(domain):
    cc = CloneCtrl('/tmp', domain) # rootDir does not matter
    cc.mountImage(cc.mainImage, 2)
    out("'%s' mounted on '%s'" % (cc.mainImage, cc.IMAGE_MOUNT_PATH))

    
def umount(domain):
    cc = CloneCtrl('/tmp', domain)
    cc.umountImage() 
    

def main():
    try: cmd = sys.argv[1]
    except: usage()
        
    if cmd == 'newBase':
        newBase()
    elif cmd == 'clone':
        try: nbrClones = int(sys.argv[2])
        except: usage()
        suffixes = sys.argv[3:]
        if not len(suffixes): usage()
        clone(nbrClones, suffixes)
    else:
        try: domain = sys.argv[2]
        except: usage()
        
        if cmd == 'start':
            start(domain)
        elif cmd == 'stop':
            stop(domain)
        elif cmd == 'stopAndDelete':
            stopAndDelete(domain)
        elif cmd == 'mount':
            mount(domain)
        elif cmd == 'umount':
            umount(domain)
        else:
            usage()

def usage():
    sys.stderr.write('usage: %s newBase | clone <nbr clones per name suffix> <suffix 1> [... <suffix N>] | start <domain> | stop <domain> | stopAndDelete <domain> | mount <domain> | umount <domain>\n' % sys.argv[0])
    sys.exit(-1)




def out(str):
    print str





## end helpers

class CloneCtrl():
    VIR = '/usr/bin/virsh -c qemu:///system'
    QEMU_IMG = '/usr/bin/qemu-img'
    VIRT_CLONE = '/usr/bin/virt-clone --connect=qemu:///system'
    KVM_NBD = '/usr/bin/qemu-nbd'
    MOUNT = '/bin/mount'
    UMOUNT = '/bin/umount'
    
    IMAGE_STORAGE_HOST = 'pisco'
    BASE_IMAGE_PREFIX = 'BASE'
    IMAGE_FORMAT = 'qcow2'
    IMAGE_MOUNT_PATH = '/tmp/image'
    
    def __init__(self, rootDir, mainDomain):
        self.cmdHost = None
        if runo('hostname')[0].rstrip() != self.IMAGE_STORAGE_HOST:
            self.cmdHost = self.IMAGE_STORAGE_HOST        
        
        if shutil.abspath(rootDir) != rootDir:
            Exception('Absolute base path required!')
        self.rootDir = shutil.abspath(rootDir) # removes trailing slashes
        self.baseDir = '%s/%s' % (self.rootDir, self.BASE_IMAGE_PREFIX)
        self.mainDomain = mainDomain
            
        self.mainImage = self.getImagePathForDomain(self.mainDomain)

    
    def getImagePathForDomain(self, domain):
        out = runo('%s dumpxml %s' % (self.VIR, domain), self.cmdHost)[0]
        imgs = re.compile("<source file='(.*?)'/>").findall(out)
        assert(len(imgs) == 1), imgs
        assert(imgs[0].endswith(self.IMAGE_FORMAT))
        return imgs[0]
            
    def getRunningDomains(self):
        domains = []
        out = runo('%s list' % self.VIR, self.cmdHost)[0]
        for r in out.split('\n'):
            s = r.split()
            if len(s) == 3 and s[1] != 'Name':
                domains.append(s[1])
        return domains

        
    def copyMainToBase(self):
        if self.mainDomain in self.getRunningDomains():
            raise Exception('Golden domain still running! Shut it down first!')
        assert(os.path.isdir(self.baseDir)), "create '%s' if you run this scirpt for the first time, otherwise check why this folder is missing!" % self.baseDir
        dt = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
        dst = '%s/%s-%s.%s' % (self.baseDir, self.mainDomain, dt, self.IMAGE_FORMAT)
        out("copying golden image '%s' to base '%s'" % (self.mainImage, dst))
        shutil.copyfile(self.mainImage, dst)


    def createNewImageBasedOnNewestBaseAndRegisterIt(self, id, prefix):
        '''@see http://www.linux-kvm.com/content/how-you-can-use-qemukvm-base-images-be-more-productive-part-1
        
        1) we clone the image using a template base image
        2) we use virt-clone with the preserve-data option set to create a libvirt config for the new image based on the golden image config
        
        use qemu-img info <path to image> to show info
        '''	
	print self.baseDir
        assert(os.path.isdir(self.baseDir))
        baseImage = self.baseDir + '/' + sorted(os.listdir(self.baseDir))[-1]
        domain = prefix + str(id)
        dstDir = '%s/%s' % (self.rootDir, id)
        if os.path.isdir(dstDir):
            raise Exception("'%s' already exists!" % dstDir)
        os.mkdir(dstDir)
        dst = '%s/img.%s' % (dstDir, self.IMAGE_FORMAT)
        out("creating image '%s' based on '%s'" % (dst, baseImage))
        run('%s create -b %s -f %s %s' % (self.QEMU_IMG, baseImage, self.IMAGE_FORMAT, dst))
        run('%s -o %s -n %s --preserve-data -f %s' % (self.VIRT_CLONE, self.mainDomain, domain, dst))

        
    def mountImage(self, imagePath, partition_nbr=1):
        '''@see http://tjworld.net/wiki/Linux/MountQemuQcowImages
           @see http://blog.loftninjas.org/2008/10/27/mounting-kvm-qcow2-qemu-disk-images/
           
           ONLY ONE IMAGE CAN BE MOUNTED AT A TIME BECAUSE WE ALWAYS USE '/dev/nbd0' AND A FIXED IMAGE_MOUNT_PATH

           In case of errors, try to install sudo apt-get install nbd-client.
           
        '''
        run('sudo modprobe nbd')
        try:
            os.mkdir(self.IMAGE_MOUNT_PATH)
        except:
            pass
        run('sudo %s -c /dev/nbd0 %s' % (self.KVM_NBD, imagePath))
        for i in range(5): # device is sometimes not ready
            time.sleep(2**i)
            try:
                run('sudo %s /dev/nbd0p%i %s' % (self.MOUNT, partition_nbr, self.IMAGE_MOUNT_PATH))
                break
            except:
                pass
                

    def umountImage(self):
        run('sudo %s %s' % (self.UMOUNT, self.IMAGE_MOUNT_PATH))
        runo('sudo %s -d /dev/nbd0' % (self.KVM_NBD)) # prints each time /dev/nbd0 disconnected


    def setName(self, domain, name):
        self.mountImage(self.getImagePathForDomain(domain))
        nameFile = '%s/%s.name' % (self.IMAGE_MOUNT_PATH, name)
        open(nameFile, 'w').close() # touch the python way :-)
        self.umountImage()


    def getFreeId(self):
        id = 215
	print self.rootDir
        for f in sorted(os.listdir(self.rootDir)):
            try: i = int(f)
            except: continue
            if i >= id:
                id = i+1
        
        return id

if __name__ == '__main__':
    main()
