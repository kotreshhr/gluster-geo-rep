# fix-entry-failures.py
Script to parse entry failure errors from geo-rep log
and generates output file with virtual setxattr command
for each entry failures. The output file can be run
as bash script to sync all the failed entries.
  
The script should be run as follows:
    
    python process_entry_failures.py <georep_log_file> <master_aux_mnt>
    python process_entry_failures.py --verify <out_file> <slave_aux_mnt>
    
The name of output file generated is 'process_entry_failures.out'

Sample 'process_entry_failures.out" file looks as below:
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file1
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file2
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file3
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file4
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file5
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file6
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file7
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file8
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file9
setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file10

NOTE: It's little tricky. We need to find out why the first entry is failed. And also need to check whether it's parent
      is synced. If it's parent is not synced, then all it's descedants would still fail even with above script.
      So before running the above script in bash, verify following steps.

      1. In above example first entry is

               setfattr -n glusterfs.geo-rep.trigger-sync -v "1" /aux-mnt//.gfid/ac826afd-3017-405c-a48b-116187b39af0/prob_dir_file1

      2. So check whether '.gfid/ac826afd-3017-405c-a48b-116187b39af0/' exists on slave. If not, sync it first and then run output file.
         To sync, get the bname and parent by traversing backend symlink and run same setfattr command to initiate sync.
