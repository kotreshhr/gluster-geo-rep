# Convert gfid to path in gluster
This script gets the path given the brick path and gfid.
It also prints the gfid for dentry involved in the path.
The prerequisite for this is to know brick to which gfid
belongs. This can done by getting the list of all the bricks
from "gluster vol info" and stat on "<brick-path>/.glusterfs/gfid[0]gfid[1]/gfid[2]gfid[3]/gfid"

### Usage:
python get_path.py <gluster_mount> <brick_path> <gfid>

### Example:
##### 1. Regular file:
```
#python ~/scripts/get_path.py /mastermnt /bricks/brick0/b0 77054d64-d79f-4963-bafe-aa796a54b506

Paths:
/mastermnt/dir1/dir2/dir3/file1
        file1: "77054d64-d79f-4963-bafe-aa796a54b506"
        dir3: "d54ff5b2-0193-4639-bcac-1bf2fd46bf9d"
        dir2: "cb0cdd86-2436-40ad-8c78-af526d5f3313"
        dir1: "5dcaaa33-f25c-4bbd-829b-eddf8236eb95"
/mastermnt/dir1/dir2/dir3/hl_file1
        hl_file1: "77054d64-d79f-4963-bafe-aa796a54b506"
        dir3: "d54ff5b2-0193-4639-bcac-1bf2fd46bf9d"
        dir2: "cb0cdd86-2436-40ad-8c78-af526d5f3313"
        dir1: "5dcaaa33-f25c-4bbd-829b-eddf8236eb95"
/mastermnt/root_hl_file1
        root_hl_file1: "77054d64-d79f-4963-bafe-aa796a54b506"
```

##### 2. Directory:
```
#python ~/scripts/get_path.py /mastermnt /bricks/brick0/b0 d54ff5b2-0193-4639-bcac-1bf2fd46bf9d
path: /dir1/dir2/dir3
dir1 : 5dcaaa33-f25c-4bbd-829b-eddf8236eb95
dir2 : cb0cdd86-2436-40ad-8c78-af526d5f3313
dir3 : d54ff5b2-0193-4639-bcac-1bf2fd46bf9d
```
