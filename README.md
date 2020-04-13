# infra
☁️ personal infra

## csgo

```
wget -nc -O quake.zip https://forums.alliedmods.net/attachment.php?attachmentid=125461&d=1380903530
unzip quake.zip
aws s3 sync FastDL/sound/quake/standard s3://neel.rdkr.uk/csgo/sound/quake/standard
rm -r GameServer FastDL quake quake.zip
```
