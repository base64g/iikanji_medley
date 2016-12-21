# -*- coding: utf-8 -*-
from scipy import ceil, complex64, float64, hamming, zeros
from scipy.fftpack import fft
from scipy import ifft
from scipy.io.wavfile import read, write
import numpy as np

from matplotlib import pylab as pl
import os
import math
import subprocess
"""
x : 入力信号(モノラル)
win : 窓関数
step : シフト幅
"""
def stft(x):
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

def max_power(spectrogram):
    powerful = 0
    for timespec in spectrogram:
        for f in range(math.floor(len(timespec)/5)):
            powerful = max(powerful, timespec[f])
    return powerful

def cal_beat_power(spectrogram):
    data2 = zeros(len(data), dtype = float64)
    vec_d = zeros(len(spectrogram), dtype = float64)
    for t in range(len(spectrogram)):
        flag = 0
        for f in range(math.floor(len(spectrogram[t])/5)):
            d_temp = d(spectrogram, t, f)
            if d_temp > threshold:
                print(d_temp)
                flag += d_temp
        if flag > 0:
            vec_d[t] = flag
            data2[t*step] += 5
            print(t)
    write('./DebugMusic/' + wavfile + 'outonly.wav', fs, data2)
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
    best_interval = 10
    for i in range(math.floor(bottom_interval/2), math.floor(top_interval/2)):
        point = beat_interval[i] + beat_interval[i-1] + beat_interval[i+1] + beat_interval[math.floor(i/2)]
        if now_point < point:
            if beat_interval[i*2] > beat_interval[i*2+1]:
                best_interval = i*2
            else:
                best_interval = i*2+1
            now_point = point

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
    #write('./DebugMusic/' + wavfile +'beat.wav',fs,out)
    #subprocess.call('sox \'./Music/' + wavfile + '\'' + ' -c 1 ./DebugMusic/temp.wav', shell=True)
    #subprocess.call('sox -m \'./DebugMusic/' + wavfile +'beat.wav\' -v 0.3 ./DebugMusic/temp.wav \'./DebugMusic/mixbeat' + wavfile + '.wav\'', shell=True)
    #subprocess.call('rm \'./DebugMusic/' + wavfile +'beat.wav\'', shell=True)
    print(vec_t[0])
    return div4vec_t

def cal_phrase(vec_t, vec_d):
    yosa = zeros(len(vec_t)*2+2, dtype = float64)
    for i in range(5,len(vec_t)-5):
        for k in range(0,2):
            for j in range(-5, 6):
                yosa[i*2+k] += vec_d[vec_t[i]+(vec_t[i+1]-vec_t[i])*k/2+j]
    tongari = zeros(16, dtype = float64)
    for i in range(len(yosa)):
        tongari[i%8] += yosa[i]

    cut = 0
    point = 0
    for i in range(len(tongari)):
        if point < tongari[i]:
            cut = i
            point = tongari[i]
    if cut%2 == 1:
        cut = math.floor(cut/2)
        phrase = [math.floor((vec_t[cut]+vec_t[cut+1])/2)]
        while cut+33 < len(vec_t):
            cut += 32
            phrase.append(math.floor((vec_t[cut]+vec_t[cut+1])/2))
    else:
        cut = math.floor(cut/2 + 0.5)
        phrase = [vec_t[cut]]
        while cut+32 < len(vec_t):
            cut += 32
            phrase.append(vec_t[cut])

    out = zeros(len(data), dtype = float64)
    for i in range(len(phrase)):
        out[phrase[i]*step] += 5
    #write('./DebugMusic/' + wavfile +'phrase.wav',fs,out)
    #subprocess.call('sox -m \'./DebugMusic/' + wavfile +'phrase.wav\' -v 0.3 ./DebugMusic/temp.wav \'./DebugMusic/mixphrase' + wavfile + '.wav\'', shell=True)
    #subprocess.call('rm ./DebugMusic/\'' + wavfile + 'phrase.wav\'' , shell=True)
    return phrase

def scale(spectrum):
    N = len(win)
    freqList = np.fft.fftfreq(N,d=1.0/fs)
    bottom_scale = 220
    top_scale = 1600
    freq = 150
    power = 0
    for i in range(len(spectrum)):
        if(spectrum[i] > power) and bottom_scale < freqList[i] and freqList[i] < top_scale:
            power = spectrum[i]
            freq = freqList[i]
    print(power, freq)
    #make_graph(spectrum)
    if power > threshold*2:
        return math.floor(math.log(440/freq,2) * 12 + 0.5) % 12
    else:
        return 12

def powerful_element(part, tsunagi):
    N = len(win)
    topspectrum = fft(part[tsunagi * fs : tsunagi * fs + N] * win)[:N/2+1]
    bottomspectrum = fft(part[len(part) - tsunagi * fs: len(part) - tsunagi * fs + N] * win)[:N/2+1]
    top = scale(abs(topspectrum))
    bottom = scale(abs(bottomspectrum))
    return top,bottom

def split_music(inputfile):
    global fs, data, step, threshold, wavfile, win
    wavfile = inputfile
    fs, data_tmp = read('./Music/' + wavfile)
    data = data_tmp[:,0]
    
    fftLen = 1024 # とりあえず
    win = hamming(fftLen) # ハミング窓
    step = fftLen / 4
    
    ### STFT
    spectrogram = stft(data)

    ### 音の立ち上がり認識
    threshold = math.floor(max_power(spectrogram) / 40)
    vec_d = cal_beat_power(spectrogram)
    
    ### beatの計算
    bottom_interval = 180
    top_interval = 350
    best_interval = cal_interval(vec_d, bottom_interval, top_interval)

    ### 初期位置の計算
    vec_t = cal_start(vec_d, best_interval, bottom_interval, top_interval)

    ### todo: フレーズの抽出（32小節ごといい感じにに区切る）
    phrase = cal_phrase(vec_t,vec_d)
    
    ### 出力(最後の32小節は無音であることが多いのでカット)
    i=0
    tsunagi=0.2 #spliceする時間[s]
    for i in range(len(phrase)-2):
        if phrase[i]*step - tsunagi*fs >= 0:
            start_scale, end_scale = powerful_element(data[phrase[i]*step - tsunagi*fs : phrase[i+1]*step + tsunagi*fs], tsunagi)
            write('./PartMusic/'+ str(start_scale) + '/' + str(end_scale) + '/'
                  + wavfile + '_' + str(i) + '.wav',
                  fs, data[phrase[i]*step - tsunagi*fs : phrase[i+1]*step + tsunagi*fs])

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
