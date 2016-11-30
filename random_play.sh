#!/bin/sh
i=0
musics=(`ls PartMusic`)
size=${#musics[*]}
while [ $i -le 10 ];
do
    toplay=${musics[$RANDOM%$size]}
    afplay "PartMusic/$toplay" &
    sleep 2.75
done
