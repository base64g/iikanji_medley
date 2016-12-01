#!/bin/sh
i=0
musics=(`ls PartMusic`)
size=${#musics[*]}
while [ $i -le 100 ];
do
    toplay=${musics[$RANDOM%$size]}
    afplay "PartMusic/$toplay" &
    sleep 11
    i=$((i + 1));
done
