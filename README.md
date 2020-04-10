# infra
☁️ personal infra

## csgo

```

mv serverfiles/csgo/addons/sourcemod/plugins/fun* serverfiles/csgo/addons/sourcemod/plugins/disabled

wget https://github.com/splewis/csgo-pug-setup/releases/download/2.0.5/pugsetup_2.0.5.zip
unzip pugsetup_2.0.5.zip -d serverfiles/csgo/

wget https://github.com/splewis/csgo-practice-mode/releases/download/1.3.3/practicemode_1.3.3.zip
unzip practicemode_1.3.3.zip -d serverfiles/csgo/

wget https://github.com/Maxximou5/csgo-deathmatch/releases/download/v2.0.9/deathmatch.zip
unzip deathmatch.zip -d serverfiles/csgo/addons/sourcemod/

wget https://github.com/bcserv/mapconfigs/archive/1.2.tar.gz
tar --extract --file=1.2.tar.gz --strip-components=1 --directory=serverfiles/csgo

```