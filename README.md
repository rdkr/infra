# infra

## core

* terraform on terraform cloud
    * dns on cloudflare
    * k8s cluster on digitalocean

## csgo

* packer
    * csgo base server on digitalocean
    
```
wget -nc -O quake.zip https://forums.alliedmods.net/attachment.php?attachmentid=125461&d=1380903530
unzip quake.zip
aws s3 sync FastDL/sound/quake/standard s3://neel.rdkr.uk/csgo/sound/quake/standard
rm -r GameServer FastDL quake quake.zip
```


== digital ocean
no where to store secrets

== 