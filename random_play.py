import random
import subprocess
import os

# random.randint(1,100)

def getmusic():
    musics = [[[]]]
    musicline = []
    for i in range(0,11):
        musics.append([[]])
    for i in range(0,12):
        for j in range(0,11):
            musics[i].append([])
    for i in range(0,12):
        for j in range(0,12):
            path = 'PartMusic/' + str(i) + '/' + str(j) + '/'
            files = os.listdir(path)
            for file in files:
                ftitle, fext = os.path.splitext(path+file)
                if fext == ".wav":
                    musics[i][j].append(path + file)
                    musicline.append(path + file)
    return musics, musicline

if __name__ == "__main__": 
    musics, musicline = getmusic()
    print(musicline)
    size = len(musicline)
    rand = random.randrange(0, size)
    now = int(musicline[rand].split("/")[1])
    subprocess.call("sox " + musicline[rand] + ' output.wav norm'  ,shell=True)
    
    for t in range(0,100):
        for u in range(0,10):
            rand = random.randrange(0,12)
            if len(musics[now][rand]) > 0:
                break
        if len(musics[now][rand]) == 0:
            rand = random.randint(0, size)
            now = int(musicline[rand].split("/")[1]);
            add = musicline[rand]
        else:
            rand2 = random.randrange(0,len(musics[now][rand]))
            add = musics[now][rand][rand2]
            now = rand
        print(add)
        subprocess.call("sox \'" + add + '\' add.wav norm'  ,shell=True)
        subprocess.call("sox output.wav add.wav output2.wav splice -q $(soxi -D output.wav),0.2"  ,shell=True)
        subprocess.call("mv output2.wav output.wav"  ,shell=True)
        subprocess.call("rm add.wav"  ,shell=True)
