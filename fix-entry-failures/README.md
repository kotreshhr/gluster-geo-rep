# fix-entry-failures.py
Script to parse entry failure errors from geo-rep log
and generates output file with virtual setxattr command
for each entry failures. The output file can be run
as bash script to sync all the failed entries.
  
The script should be run as follows:
    
    python process_entry_failures.py <georep_log_file> <master_aux_mnt>
    python process_entry_failures.py --verify <out_file> <slave_aux_mnt>
    
The name of output file generated is 'process_entry_failures.out'

