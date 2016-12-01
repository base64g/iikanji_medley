import os
import shutil
def copyall(path):
    files = os.listdir(path)
    for file in files:
        if os.path.isdir(path+file):
            copyall(path+file+"/")
        elif os.path.isfile(path+file):
            ftitle, fext = os.path.splitext(path+file)
            if fext == ".wav":
                print(path+file)
                shutil.copyfile(path+file, "./Music/" + file)
            
if __name__ == "__main__":
    copyall('/Users/admin/Music/iTunes/iTunes Media/Music/')
