# parse_entry_failures.py
Script to parse entry failure errors from geo-rep log


The script should be run as follows:

    python parse_entry_failures.py <georep_log_file>

The script generates following two files.

1. sync_entry.sh:

    It is a bash script used to sync entries keeping
    the gfid intact between master and slave. This
    should be run as follows.
    ```
    #bash sync_entry.sh <master-aux-mnt> <slave-aux-mnt>
    ```

2. gfid_file.txt:

    It is text file with gfids separated by new line.
    The sample is as below.

    ```
    .gfid/a7106d8e-ef95-4189-a98e-5b75de95dc5d
    .gfid/86c3d058-6cc1-4933-aae5-093482b6bc94
    .gfid/fc71826d-49f7-458f-85a6-01485e8be612
    .gfid/0306651b-f4fa-4b44-92cf-a894894eb82b
     ```
     
     This should used as below by rsync to sync data from master node.
     
     ```
     #cd <master-aux-mnt>
     
     The slave mount can be done on slave host and use ssh as below to sync.
     #rsync -aR --inplace --xattrs --acls --numeric-ids --no-implied-dirs --files-from=<path-to-gfid_file.txt> . -e "ssh" root@<slavehost>:/aux-slave-mnt
     
     OR
     
     The slave mount can be done on master node itself and use below command to sync.
     #rsync -aR --inplace --xattrs --acls --numeric-ids --no-implied-dirs --files-from=<path-to-gfid_file.txt> . /aux-slave-mnt
     ```
