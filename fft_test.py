# -*- coding: utf-8 -*-
from scipy import ceil, complex64, float64, hamming, zeros
from scipy.fftpack import fft# , ifft
from scipy import ifft # こっちじゃないとエラー出るときあった気がする
from scipy.io.wavfile import read, write

from matplotlib import pylab as pl
import os
import math
"""
x : 入力信号(モノラル)
win : 窓関数
step : シフト幅
"""
def stft(x, win):
    l = len(x) # 入力信号の長さ
    N = len(win) # 窓幅、つまり切り出す幅
    M = int(ceil(float(l - N + step) / step)) # スペクトログラムの時間フレーム数
    new_x = zeros(N + ((M - 1) * step), dtype = float64)
    new_x[: l] = x # 信号をいい感じの長さにする
    
    X = zeros([M, N/2+1], dtype = complex64) # スペクトログラムの初期化(複素数型)
    for m in range(M):
        start = step * m
        X[m, :] = fft(new_x[start : start + N] * win)[:N/2+1]
    return abs(X)

def fft_distance(x, y):
    l = min(len(x), len(y))
    x = x[:l]
    y = y[:l]
    win = hamming(l)
    spectrum_x = abs(fft(x*win)[:l/2+1])
    spectrum_y = abs(fft(y*win)[:l/2+1])
    point = 0
    for i in range(len(spectrum_x)):
        diff = abs(spectrum_x[i] - spectrum_y[i])
        if diff > threshold:
            point += diff
    print(point)
    return point

def d(spectrogram, t, f):
    if t-2 < 0 or t+1 >= len(spectrogram) or f-1 < 0 or f+1 >= len(spectrogram[0]):
        return 0
    pp = max(spectrogram[t-1][f], spectrogram[t-1][f-1], spectrogram[t-1][f+1],spectrogram[t-2][f])
    np = min(spectrogram[t+1][f], spectrogram[t+1][f-1], spectrogram[t+1][f+1])
    if(spectrogram[t][f] <= pp or np <= pp):
        return 0;
    return spectrogram[t][f] - pp + max(0, spectrogram[t+1][f] - spectrogram[t][f])

def make_graph(plots):
    fig = pl.figure()
    fig.add_subplot(311)
    pl.plot(plots)
    pl.xlim([0, len(plots)])
    pl.title("Data", fontsize = 20)
    pl.show()
    
def cal_beat_power(spectrogram):
    data2 = zeros(len(data), dtype = float64)
    vec_d = zeros(len(spectrogram), dtype = float64)
    for t in range(len(spectrogram)):
        flag = 0
        for f in range(math.floor(len(spectrogram[t])/3)):
            d_temp = d(spectrogram, t, f)
            if d_temp > threshold:
                print(d_temp)
                flag += d_temp
        if flag > 0:
            vec_d[t] = flag
            data2[t*step] += 5
            print(t)
    write('./DebugMusic/' + wavfile.replace(' ', '') + 'outonly.wav', fs, data2)
    return vec_d

def cal_interval(vec_d, bottom_interval, top_interval):
    beat_interval = zeros(top_interval+1, dtype = float64)
    for t in range(len(vec_d)):
        print(t)
        if vec_d[t] > 0:
            for t2 in range(1,top_interval):
                if t+t2 >= len(vec_d):
                    break
                beat_interval[t2] += vec_d[t+t2]
    now_point = 0
    best_interval = 1
    for i in range(math.floor(bottom_interval/2), math.floor(top_interval/2)):
        if now_point < beat_interval[i] + beat_interval[i-1] + beat_interval[i+1]:
            if beat_interval[i*2] > beat_interval[i*2+1]:
                best_interval = i*2
            else:
                best_interval = i*2+1
            now_point = beat_interval[i] + beat_interval[i-1] + beat_interval[i+1]

    for i in range(bottom_interval, top_interval):
        if now_point < beat_interval[i] + beat_interval[i-1] + beat_interval[i+1]:
            best_interval = i
            now_point = beat_interval[i] + beat_interval[i-1] + beat_interval[i+1]

    print(best_interval)
    #make_graph(beat_interval)
    return best_interval

def cal_start(vec_d, best_interval, bottom_interval, top_interval):
    now_point = 0
    vec_t = [0]
    for start in range(best_interval + 50):
        print(start)
        tmp_vec_t = [start]
        point = 0
        i = 0
        before = start
        dts = [4, -4, 3, -3, 2, -2, 1, -1, 0]
        while (before+best_interval+11) < len(vec_d):
            to = 0
            tmppoint = 0
            for dt in dts:
                if vec_d[before+best_interval+dt] > tmppoint + abs(dt) * 5:
                  to = dt
                  tmppoint = vec_d[before+best_interval+dt] - abs(dt) * 5
            point += tmppoint
            before += best_interval+to
            tmp_vec_t.append(before)
            i+=1
        print(point*(1-tmp_vec_t[0]*step/len(data)))
        if now_point*(1-vec_t[0]*step/len(data)) < point*(1-tmp_vec_t[0]*step/len(data)):
            now_point = point
            vec_t = tmp_vec_t
            
    div4vec_t = [vec_t[0]]
    for i in range(len(vec_t)-1):
        for j in range(1,5):
            div4vec_t.append(vec_t[i] + (vec_t[i+1] - vec_t[i])*j/4)
    out = zeros(len(data), dtype = float64)
    for i in range(len(div4vec_t)):
        out[div4vec_t[i]*step] += 5
    write('./DebugMusic/' + wavfile.replace(' ', '') +'beat.wav',fs,out)
    os.system('sox ./Music/' + wavfile.replace(' ', '\ ') + ' -c 1 ./DebugMusic/temp.wav')
    os.system('sox -m ./DebugMusic/' + wavfile.replace(' ', '') +'beat.wav -v 0.4 ./DebugMusic/temp.wav ./DebugMusic/mixbeat' + wavfile.replace(' ', '') + '.wav')
    print(vec_t[0])
    return div4vec_t

def cal_phrase(vec_t):
    yosa = zeros(len(vec_t), dtype = float64)
    for i in range(math.floor(len(vec_t)/3),math.floor(len(vec_t)*2/3)):
        yosa[i] += fft_distance(data[vec_t[i-8]*step:vec_t[i+1]*step], data[vec_t[i]*step:vec_t[i+9]*step])
    tongari = zeros(8, dtype = float64)
    for i in range(3, len(yosa)-3):
        if yosa[i] > yosa[i-1] and yosa[i] > yosa[i+1] and yosa[i] > yosa[i-2] and yosa[i] > yosa[i+2]:
            tongari[i%8] += 1
    #make_graph(yosa)
    #make_graph(tongari)
    cut = 0
    point = 0
    for i in range(len(tongari)):
        if point < tongari[i]:
            cut = i
            point = tongari[i]
    phrase = [vec_t[cut]]
    while cut+8 < len(vec_t):
        cut += 8
        phrase.append(vec_t[cut])

    out = zeros(len(data), dtype = float64)
    for i in range(len(phrase)):
        out[phrase[i]*step] += 5
    write('./DebugMusic/' + wavfile.replace(' ', '') +'phrase.wav',fs,out)
    os.system('sox -m ./DebugMusic/' + wavfile.replace(' ', '') +'phrase.wav -v 0.4 ./DebugMusic/temp.wav ./DebugMusic/mixphrase' + wavfile.replace(' ', '') + '.wav')
        
    return phrase

def split_music(inputfile):
    global fs, data, step, threshold, wavfile
    wavfile = inputfile
    fs, data_tmp = read('./Music/' + wavfile)
    data = data_tmp[:,0]
    
    fftLen = 512 # とりあえず
    win = hamming(fftLen) # ハミング窓
    step = fftLen / 4
    
    ### STFT
    spectrogram = stft(data, win)

    ### 音の立ち上がり認識
    threshold = 500000
    vec_d = cal_beat_power(spectrogram)
    
    ### beatの計算
    bottom_interval = 360
    top_interval = 700
    best_interval = cal_interval(vec_d, bottom_interval, top_interval)

    ### 初期位置の計算
    vec_t = cal_start(vec_d, best_interval, bottom_interval, top_interval)

    ### todo: フレーズの抽出（４小節ごといい感じにに区切る）
    phrase = cal_phrase(vec_t)
    
    ### 出力(最後の８小節は無音であることが多いのでカット)
    for i in range(len(phrase)-1):
        write('./PartMusic/' + wavfile.replace(' ', '') + '_' + str(i) + '.wav', fs, data[phrase[i]*step:phrase[i+1]*step])

if __name__ == "__main__":
    files = os.listdir('Music')
    query = input()
    if query == "all":
        for music in files:
            print(music)
            ftitle, fext = os.path.splitext(music)
            if fext == ".wav":
                split_music(music)
    else:
        split_music(query)
