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
    query = input()
    if os.path.isfile(query) or os.path.isdir(query):
        copyall(query)
    else:
        print('it is not a file or directory')
