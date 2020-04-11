# infra
☁️ personal infra

## csgo

```

wget -nc https://mms.alliedmods.net/mmsdrop/1.10/mmsource-1.10.7-git971-linux.tar.gz
tar xfv mmsource-1.10.7-git971-linux.tar.gz -C serverfiles/csgo

wget -nc https://sm.alliedmods.net/smdrop/1.10/sourcemod-1.10.0-git6482-linux.tar.gz
tar xfv sourcemod-1.10.0-git6482-linux.tar.gz -C serverfiles/csgo

mv serverfiles/csgo/addons/sourcemod/plugins/nextmap.smx serverfiles/csgo/addons/sourcemod/plugins/disabled/
mv serverfiles/csgo/addons/sourcemod/plugins/fun* serverfiles/csgo/addons/sourcemod/plugins/disabled

wget https://github.com/splewis/csgo-pug-setup/releases/download/2.0.5/pugsetup_2.0.5.zip
unzip pugsetup_2.0.5.zip -d serverfiles/csgo/

wget https://github.com/splewis/csgo-practice-mode/releases/download/1.3.3/practicemode_1.3.3.zip
unzip practicemode_1.3.3.zip -d serverfiles/csgo/

```

wget https://github.com/Maxximou5/csgo-deathmatch/releases/download/v2.0.9/deathmatch.zip
unzip deathmatch.zip -d serverfiles/csgo/addons/sourcemod/

```
