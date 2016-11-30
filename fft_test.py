# -*- coding: utf-8 -*-
# ==================================
#
#    Short Time Fourier Trasform
#
# ==================================
from scipy import ceil, complex64, float64, hamming, zeros
from scipy.fftpack import fft# , ifft
from scipy import ifft # こっちじゃないとエラー出るときあった気がする
from scipy.io.wavfile import read, write

from matplotlib import pylab as pl

# ======
#  STFT
# ======
"""
x : 入力信号(モノラル)
win : 窓関数
step : シフト幅
"""
def stft(x, win, step):
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

def d(spectrogram, t, f):
    if t-2 < 0 or t+1 >= len(spectrogram) or f-1 < 0 or f+1 >= len(spectrogram[0]):
        return 0
    pp = max(spectrogram[t-1][f], spectrogram[t-1][f-1], spectrogram[t-1][f+1],spectrogram[t-2][f])
    np = min(spectrogram[t+1][f], spectrogram[t+1][f-1], spectrogram[t+1][f+1])
    if(spectrogram[t][f] <= pp or np <= pp):
        return 0;
    return spectrogram[t][f] - pp + max(0, spectrogram[t+1][f] - spectrogram[t][f])

def add_sound(data, data2, t, loud):
    data2[t] += loud

def make_graph(data):
    fig = pl.figure()
    fig.add_subplot(311)
    pl.plot(data)
    pl.xlim([0, len(data)])
    pl.title("Data", fontsize = 20)
    pl.show()
    
    
if __name__ == "__main__":
    wavfile = "./Music/test.wav"
    fs, data_tmp = read(wavfile)
    data = data_tmp[:,0]
    
    fftLen = 512 # とりあえず
    win = hamming(fftLen) # ハミング窓
    step = fftLen / 4
    
    ### STFT
    spectrogram = stft(data, win, step)

    threshold = 100000
    ### 音の立ち上がり認識
    data2 = zeros(len(data), dtype = float64)
    vec_d = zeros(len(spectrogram), dtype = float64)
    for t in range(len(spectrogram)):
        flag = 0
        for f in range(len(spectrogram[t])):
            d_temp = d(spectrogram, t, f)
            if d_temp > threshold:
                print(d_temp)
                flag += d_temp
        if flag > 0:
            vec_d[t] = flag
            add_sound(data, data2, t*step, flag)
            print(t)
    write('./Music/testout.wav', fs, data)
    write('./Music/outonly.wav', fs, data2)

    ### beatの計算
    bottom_interval = 100
    top_interval = 1000
    beat_interval = zeros(top_interval, dtype = float64)
    for t in range(len(vec_d)):
        print(t)
        if vec_d[t] > 0:
            for t2 in range(bottom_interval,top_interval):
                if t+t2 >= len(vec_d):
                    break
                beat_interval[t2] += vec_d[t+t2]
    now_point = 0
    best_interval = 1
    for i in range(len(beat_interval)):
        if now_point < beat_interval[i]:
            best_interval = i
            now_point = beat_interval[i]
    print(best_interval)
    data3 = zeros(len(data), dtype = float64)
    i = 0
    while i*best_interval*step < len(data3):
        data3[i*best_interval*step] += 1000000
        i+=1
    write('./Music/beat_interval.wav', fs, data3)
    #make_graph(beat_interval)

    ### 初期位置の計算
    data4 = zeros(len(data), dtype = float64)
    now_point = 0
    vec_t = []
    for start in range(top_interval):
        print(start)
        tmp_vec_t = [start]
        editdata = zeros(len(data), dtype = float64)
        point = 0
        i = 0
        before = start
        dts = [10, -10, 9, -9, 8, -8, 7, -7, 6, -6, 5, -5, 4, -4, 3, -3, 2, -2, 1, -1, 0]
        while (before+best_interval+2)*step < len(data4):
            to = 0
            tmppoint = 0
            for dt in dts:
                if vec_d[before+best_interval+dt] > tmppoint:
                  to = dt
                  tmppoint = vec_d[before+best_interval+dt]
            point += tmppoint
            before += best_interval+to
            tmp_vec_t.append(before)
            editdata[before*step] += 1000000
        if now_point < point:
            now_point = point
            data4 = editdata
            vect_t = tmp_vec_t
    write('./Music/beat.wav',fs,data4)
    for i in range(len(vect_t)-4):
        write('./PartMusic/' + str(i) + '.wav', fs, data[vect_t[i]*step:vect_t[i+4]*step])
