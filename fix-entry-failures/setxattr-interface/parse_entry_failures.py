import sys
import os
import json

SETFATTR ='setfattr -n glusterfs.geo-rep.trigger-sync -v "1" '
OUTFILE = 'process_entry_failures.out'

def verify_entries ():
    out_file = sys.argv[2]
    slav_aux_mnt = sys.argv[3]

    with open(out_file) as f:
        for line in f:
            path = line.split()[-1]
            path = slav_aux_mnt + "/".join(path.split("/")[2:])
            if not os.path.exists(path):
                    print("path %s is not synced to slave" % path)

def parse_json (line):
    data = line.split(" FAILED: (")[-1]
    data = data.rsplit("},", 1)[0]
    data = data + '}'
    return data.replace("'", '"')

def args_check_0():
    if len(sys.argv) < 3:
        print "ERROR: Insufficient arguments."
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

    if not os.path.exists(sys.argv[1]):
        print("ERROR: log file %s doesn't exist" % sys.argv[1])
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

    if not os.path.exists(sys.argv[2]):
        print("ERROR: Master aux mount %s doesn't exist" % sys.argv[2])
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

def args_check_1():
    if len(sys.argv) < 4:
        print "ERROR: Insufficient arguments."
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

    if not os.path.exists(sys.argv[2]):
        print("ERROR: Outfile %s doesn't exist" % sys.argv[2])
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount> <slave_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

    if not os.path.exists(sys.argv[3]):
        print("ERROR: Slave aux mount %s doesn't exist" % sys.argv[2])
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount> <slave_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

def main():

    if len(sys.argv) < 3:
        print "ERROR: Insufficient arguments."
        print "Usage: python process_entry_failures <georep_log_file> <master_aux_mount>"
        print "Usage: python process_entry_failures --verify <outfile> <slave_aux_mount>"
        exit(1)

    if "--verify" == sys.argv[1]:
        args_check_1()
        verify_entries()
        exit(0)

    args_check_0()
    log_file = sys.argv[1]
    mast_aux_mnt = sys.argv[2]

    if os.path.exists(OUTFILE):
        os.unlink(OUTFILE)

    entryRepeated = False
    metaRepeated = False
    prev_entry = ""
    prev_meta = ""
    of = open (OUTFILE, 'a')
    with open (log_file) as f:
        for line in f:
            if "ENTRY FAILED" in line:
                json_data = json.loads(parse_json(line))
                if prev_entry == json_data['entry']:
                    entryRepeated = True
                if os.path.exists(mast_aux_mnt + '/' + json_data['entry']) and not entryRepeated:
                    of.write(SETFATTR + mast_aux_mnt + '/' + json_data['entry'] + '\n')
                prev_entry = json_data['entry']
                entryRepeated = False
            elif "META FAILED" in line:
                json_data = json.loads(parse_json(line))
                if prev_meta == json_data['go']:
                    metaRepeated = True
                if os.path.exists(mast_aux_mnt + '/' + json_data['go']) and not metaRepeated:
                    of.write(SETFATTR + mast_aux_mnt + '/' + json_data['go'] + '\n')
                prev_meta = json_data['go']
                metaRepeated = False

    of.close()

if __name__ == '__main__':
    main()
