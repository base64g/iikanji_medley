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
    
    X = zeros([M, N], dtype = complex64) # スペクトログラムの初期化(複素数型)
    for m in range(M):
        start = step * m
        X[m, :] = fft(new_x[start : start + N] * win)
    return X

def d(spectrogram, t, f):
    if t-2 < 0 or t+1 >= len(spectrogram) or f-1 < 0 or f+1 >= len(spectrogram[0]):
        return 0
    pp = max(spectrogram[t-1][f], spectrogram[t-1][f-1], spectrogram[t-1][f+1],spectrogram[t-2][f])
    np = min(spectrogram[t+1][f], spectrogram[t+1][f-1], spectrogram[t+1][f+1])
    if(spectrogram[t][f] <= pp or np <= pp):
        return 0;
    return spectrogram[t][f] - pp + max(0, spectrogram[t+1][f] - spectrogram[t][f])

def add_sound(data, t, soundst):
    data[t] += 1000000
    #sounds = soundst[:25]
    #for i in range(len(sounds)):
    #    data[min(t+i, len(data-1))] += sounds[i][0]

if __name__ == "__main__":
    wavfile = "./Music/test.wav"
    fs, data_tmp = read(wavfile)
    soundfs, sounddata = read("./Sound/c.wav")
    data = data_tmp[:,0]
    
    fftLen = 512 # とりあえず
    win = hamming(fftLen) # ハミング窓
    step = fftLen / 4
    
    ### STFT
    spectrogram = stft(data, win, step)

    threshold = 20000
    ### 音の立ち上がり認識
    for t in range(len(spectrogram)):
        flag = False
        for f in range(len(spectrogram[t])):
            if abs(d(spectrogram, t, f)) > threshold:
                print(abs(d(spectrogram, t, f)))
                flag = True
        if flag:
            add_sound(data, t*step, sounddata)
            print(t)
    write('./Music/testout.wav', fs, data)
    
