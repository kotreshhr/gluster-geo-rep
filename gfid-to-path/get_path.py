import os
import sys
import xattr
import subprocess
from os.path import basename, abspath, dirname

PROG_DESCRIPTION="GET PATH GIVEN GFID"


def execute(cmd, failure_msg="", success_msg="", exit_code=-1):
    """
        Wrapper to execute CLI commands
    """
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        if success_msg:
            print success_msg
        return out
    else:
        if failure_msg:
            print failure_msg
        else:
            print "Cmd: %s failed with error %s" % (" ".join(cmd), out)
        sys.exit(exit_code)

if len(sys.argv) != 4:
    print ("Usage: python get_path.py <mnt> <brick_path> <gfid>")
    sys.exit(1) 

mnt_path = os.path.abspath(sys.argv[1])
brick_path = os.path.abspath(sys.argv[2])
arg_gfid = sys.argv[3]
dentry = ""

full_path = brick_path + "/" + ".glusterfs/" + arg_gfid[0] + arg_gfid[1] + "/" + arg_gfid[2] + arg_gfid[3] + "/" + arg_gfid
#print ("full_path: %s" % full_path)

try:
    os.lstat(full_path)
except:
    printf ("stat failed on %s" % full_path)
    sys.exit(1)

if os.path.isfile(full_path):
    cmd = ["find", brick_path, "-samefile", full_path]
    print "\nPaths:"
    bnames = execute(cmd).split("\n") 
    for bname in bnames:
        if bname and ".glusterfs" not in bname:
            dentry = bname.replace(brick_path, mnt_path)
            print dentry
            while dentry != mnt_path:
                cmd = ["getfattr", "-n", "glusterfs.gfid.string", dentry]
                print ("\t%s: %s" % (dentry.split("/")[-1], execute(cmd).split("=")[-1].rstrip()))
                dentry = os.path.abspath(os.path.dirname(dentry))
    sys.exit(0)   
 
parent = ""
result = []
fresult = ""
while parent != "00000000-0000-0000-0000-000000000001":
     dir1 = os.path.abspath(os.readlink(full_path))
     result.insert(0, os.path.basename(dir1))
     parent = os.path.basename(os.path.dirname(dir1))
     full_path = brick_path + "/" + ".glusterfs/" + parent[0] + parent[1] + "/" + parent[2] + parent[3] + "/" + parent 

path="/".join(result)
print "path: /%s" % path
entry = ""
for dir1 in result:
    entry = entry + "/" + dir1
    path = mnt_path + entry
    gfid = xattr.getxattr(path, "glusterfs.gfid.string")
    print ("%s : %s" % (dir1, gfid))
