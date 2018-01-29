import os
import sys
import uuid
import threading
import time

FILE_DATA = '{"widget": {\n\
    "debug": "on",\n\
    "window": {\n\
        "title": "Sample Konfabulator Widget",\n\
        "name": "main_window",\n\
        "width": 500,\n\
        "height": 500\n\
    },\
    "image": {\n\
        "src": "Images/Sun.png",\n\
        "name": "sun1",\n\
        "hOffset": 250,\n\
        "vOffset": 250,\n\
        "alignment": "center"\n\
    },\n\
    "text": {\n\
        "data": "Click Here",\n\
        "size": 36,\n\
        "style": "bold",\n\
        "name": "text1",\n\
        "hOffset": 250,\n\
        "vOffset": 100,\n\
        "alignment": "center",\n\
        "onMouseUp": "sun1.opacity = (sun1.opacity / 100) * 90;"\n\
    }\n\
}}'

file_list = []

def unlink_thread():
    global file_list
    print("Sleep for 0.1 sec")
    time.sleep(0.1)
    while (True):
        count = 0
        for file in file_list:
            print("Removing %s" % file)
            try:
                os.remove(file)
            except OSError:
                print("Deletion failed. file: %s" % file)
                pass
            file_list.remove(file)
            count = count + 1
            if count == 10:
                break
        print("Sleep for 0.1 sec")
        time.sleep(0.1)
        if not file_list:
            break
    
def main():
    global file_list
    if len(sys.argv) < 2:
        print "Usage: python create-del-workload.py <num of entries>"
        exit(1)

    t = threading.Thread(target=unlink_thread)
    t.start()
    for i in range(0, int(sys.argv[1])):
        fname = str(uuid.uuid4())
        dir1 = fname[0:2]
        dir2 = fname[2:4]
        parentpath = os.path.join(dir1,dir2)
        fpath = os.path.join(dir1, dir2, fname)

        print("Creating file. Count:%s fname:%s" % (i, fpath))
        #Create parent directories and file
        try:
            os.mkdir(dir1)
        except:
            pass
        
        try:
            os.mkdir(parentpath)
        except:
            pass
       
        try:
            with open(fpath, 'w') as f:
                f.write(FILE_DATA)
            file_list.append(fpath)
        except OSError as e:
            print("Creation failed. Count:%s fname:%s error:%s" % (i, fpath, e.strerror))

    t.join()

if __name__ == '__main__':
    main()
