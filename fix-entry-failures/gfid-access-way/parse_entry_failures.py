import sys
import os
import json

GFID_ACCESS = 'python $1'
SYNC_ENTRY = 'sync_entry.py'
SYNC_DATA  = 'gfid_file.txt'

SE_HEADER = "import os\nfrom resource import *\n\n\
#Generated by parse-entry-failures.py\n\
#Usage: python sync_entry.py <master-aux-mnt> <slave-aux-mnt>\n\n"

SE_WRAP_FUNC = "def entry_sync(mst_mnt, slv_mnt, entry):\n\
    entry = eval(entry)\n\
    if (os.path.lexists(mst_mnt + '/.gfid/' + entry['gfid'])):\n\
        entry_ops(slv_mnt, entry)\n\n\
def sync_all_entries(mst_mnt, slv_mnt):\n"

FOOTER = "\nif __name__ == '__main__':\n\
    if len(sys.argv) < 3:\n\
        print('USAGE: %s <mst-aux-mnt> <slv-aux-mnt>' % (sys.argv[0]))\n\
        sys.exit(-1)\n\n\
    mst_mnt = sys.argv[1]\n\
    slv_mnt = sys.argv[2]\n\
    sync_all_entries(mst_mnt, slv_mnt)\n"


def parse_json (line):
    data = line.split(" FAILED: (")[-1]
    data = data.rsplit("},", 1)[0]
    data = data + '}'
    return data.replace("'", '"')

def print_usage ():
    print "Usage: python parse_entry_failures <georep_log_file>"

def args_check_0():
    if len(sys.argv) < 2:
        print "ERROR: Insufficient arguments."
        exit(1)

    if not os.path.exists(sys.argv[1]):
        print("ERROR: log file %s doesn't exist" % sys.argv[1])
        print_usage()
        exit(1)

def main():

    args_check_0()

    log_file = sys.argv[1]

    enot_sup = False
    if os.path.exists(SYNC_ENTRY):
        os.unlink(SYNC_ENTRY)
    if os.path.exists(SYNC_DATA):
        os.unlink(SYNC_DATA)

    entryRepeated = False
    metaRepeated = False
    prev_entry = ""
    prev_meta = ""

    entry_fp = open (SYNC_ENTRY, 'a')
    entry_fp.write(SE_HEADER)
    entry_fp.write(SE_WRAP_FUNC)
    data_fp = open (SYNC_DATA, 'a')
    with open (log_file) as f:
        for line in f:
            if "ENTRY FAILED" in line:
                json_data = eval(parse_json(line))
                if prev_entry == json_data['entry']:
                    entryRepeated = True
                if not entryRepeated:
                    entry_fp.write("    entry_sync(mst_mnt, slv_mnt, \"%s\")\n" % (json_data))
                    data_fp.write(".gfid/%s\n" % json_data['gfid'])
                prev_entry = json_data['entry']
                entryRepeated = False
            elif "META FAILED" in line:
                json_data = eval(parse_json(line))
                if prev_meta == json_data['go']:
                    metaRepeated = True
                if not metaRepeated:
                    data_fp.write("%s\n" % json_data['go'])
                prev_meta = json_data['go']
                metaRepeated = False

    entry_fp.write(FOOTER)
    entry_fp.close()
    data_fp.close()

if __name__ == '__main__':
    main()
