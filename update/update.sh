#!/usr/bin/env sh

# 确保脚本抛出遇到的错误
set -e

# git
git init
git clone https://github.com/yuanyan3060/Arknights-Bot-Resource

# cd Arknights-Bot-Resource/
cp ./Arknights-Bot-Resource/gamedata/excel/character_table.json ./character_table.json
cp ./Arknights-Bot-Resource/gamedata/excel/handbook_info_table.json ./handbook_info_table.json 
cp ./Arknights-Bot-Resource/gamedata/excel/skin_table.json ./skin_table.json 

# 立绘
rm -f ../modules/Gacha/data/dynamic/portrait && mkdir -p ../modules/Gacha/data/dynamic/portrait
cp -r ./Arknights-Bot-Resource/portrait/* ../modules/Gacha/data/dynamic/portrait

# 文件拷贝
cp ./character_table.json ../modules/Gacha/data/dynamic/gamedata/character_table.json
cp ./character_table.json ../modules/AkGuess/resources/character_table.json
cp ./handbook_info_table.json ../modules/AkGuess/resources/handbook_info_table.json
cp ./skin_table.json ../modules/AkGuess/resources/skin_table.json

python ./character_table.py

cp ./character_list.json ../modules/AkGuess/resources/character_list.json


