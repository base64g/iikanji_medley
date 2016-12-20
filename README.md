# iikanji_medley
駆け抜けるアニソンメドレーみたいなやつを自動生成したい

#### copy_music.py
指定したディレクトリ以下のすべてのwavファイルをこのディレクトリのMusicフォルダにコピーするプログラム
`python3 copy_music.py`とした後に`~/Music/`などと標準入力を入れると`~/Music/` 以下のwavファイルが`./Music/`以下にコピーされる
#### iikanji_split.py
実行にはsoxのインストールが必要
wavファイルの音楽をいい感じに切り出して ./PartMusic/ 以下に分類して保存するプログラム
入力されるwavファイルは2チャンネルで，サンプリングレートが44.1kHz，4分の4拍子であることを想定しています．
`python3 iikanji_split.py`とした後に標準入力に`./Music/` 以下のwavファイル名を指定するとその音楽に対して，標準入力に`all`と入力すると`./Music/`以下のすべてのwavファイルに対して解析・処理を行う．
#### random_play.py
実行にはそsoxのインストールが必要
`./PartMusic/`以下に分類された音楽をいい感じにつなげてメドレーを生成するプログラム
`python3 random_play.py`とするとメドレーの`./output.wav`が生成される．
