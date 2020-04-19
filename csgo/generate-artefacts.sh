#!/usr/bin/env sh

set -x

mkdir -p /tmp/cs/upload
rm -r /tmp/cs/upload/*

## dm

temp=$(mktemp -d)

wget -nc -P /tmp/cs https://mms.alliedmods.net/mmsdrop/1.10/mmsource-1.10.7-git971-linux.tar.gz
tar xf /tmp/cs/mmsource-1.10.7-git971-linux.tar.gz -C $temp

wget -nc -P /tmp/cs https://sm.alliedmods.net/smdrop/1.10/sourcemod-1.10.0-git6482-linux.tar.gz
tar xf /tmp/cs/sourcemod-1.10.0-git6482-linux.tar.gz -C $temp

mv $temp/addons/sourcemod/plugins/nextmap.smx $temp/addons/sourcemod/plugins/disabled/
mv $temp/addons/sourcemod/plugins/fun* $temp/addons/sourcemod/plugins/disabled

wget -nc -P /tmp/cs https://github.com/Maxximou5/csgo-deathmatch/releases/download/v2.0.9/deathmatch.zip
unzip -q -o /tmp/cs/deathmatch.zip -d $temp/addons/sourcemod

wget -nc -O /tmp/cs/quake.zip https://forums.alliedmods.net/attachment.php?attachmentid=125461&d=1380903530
unzip -q -o /tmp/cs/quake.zip -d /tmp/cs/
cp -r /tmp/cs/GameServer/* $temp
cp -r /tmp/cs/FastDL/* /tmp/cs/upload

wget -nc -O /tmp/cs/quake.smx http://www.sourcemod.net/vbcompiler.php?file_id=155260
cp /tmp/cs/quake.smx $temp/addons/sourcemod/plugins/

tar -C $temp -czf /tmp/cs/upload/dm.tar.gz .

## pug

temp=$(mktemp -d)

wget -nc -P /tmp/cs https://mms.alliedmods.net/mmsdrop/1.10/mmsource-1.10.7-git971-linux.tar.gz
tar xf /tmp/cs/mmsource-1.10.7-git971-linux.tar.gz -C $temp

wget -nc -P /tmp/cs https://sm.alliedmods.net/smdrop/1.10/sourcemod-1.10.0-git6482-linux.tar.gz
tar xf /tmp/cs/sourcemod-1.10.0-git6482-linux.tar.gz -C $temp

mv $temp/addons/sourcemod/plugins/nextmap.smx $temp/addons/sourcemod/plugins/disabled
mv $temp/addons/sourcemod/plugins/fun* $temp/addons/sourcemod/plugins/disabled

wget -nc -P /tmp/cs https://github.com/splewis/csgo-pug-setup/releases/download/2.0.5/pugsetup_2.0.5.zip
unzip -q -o /tmp/cs/pugsetup_2.0.5.zip -d $temp

wget -nc -P /tmp/cs https://github.com/splewis/csgo-practice-mode/releases/download/1.3.3/practicemode_1.3.3.zip
unzip -q -o /tmp/cs/practicemode_1.3.3.zip -d $temp

tar -C $temp -czf /tmp/cs/upload/pug.tar.gz .

## upload

aws s3 sync /tmp/cs/upload s3://neel.rdkr.uk/csgo
