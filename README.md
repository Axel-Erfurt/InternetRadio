# InternetRadio
play and record internet radio stations

- right click on systray icon -> select channel

## Requirements:
- PyQt5
- wget

### Channel Editor

Format:
```
-- Category --
Name,URL
```

Example:
```
-- Information --
MDR Aktuell,http://mdr-284340-0.cast.mdr.de/mdr/284340/0/mp3/low/stream.mp3
-- Lokal --
Antenne Thüringen,http://stream.antennethueringen.de/live/mp3-128/
```
Each category is shown in the menu as a submenu with the associated channels.

### Installation Mint / Ubuntu

> wget 'https://raw.githubusercontent.com/Axel-Erfurt/InternetRadio/master/InternetRadioInstall.sh' -O ~/Downloads/InternetRadioInstall.sh && chmod +x ~/Downloads/InternetRadioInstall.sh && ~/Downloads/InternetRadioInstall.sh

September 6, 2019 added Channel Editor

![alt text](https://github.com/Axel-Erfurt/InternetRadio/blob/master/radio2.png)

[Linux App 64bit Download](https://www.dropbox.com/s/zcw2lmrkqmpcto0/myRadio64.tar.gz?dl=1)

letztes Update 31.Januar 2020 22:24 Uhr

__RadioSearch.py__

needs constants

`pip3 install --user constants`

find Radio Stations
