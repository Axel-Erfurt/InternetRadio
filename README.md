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

__Installation Mint / Ubuntu__

> wget 'https://raw.githubusercontent.com/Axel-Erfurt/InternetRadio/master/InternetRadioInstall.sh' -O ~/Downloads/InternetRadioInstall.sh && chmod +x ~/Downloads/InternetRadioInstall.sh && ~/Downloads/InternetRadioInstall.sh

__Deinstallation__

`rm /home/brian/.local/share/applications/InternetRadio.desktop`

`rm -rf /home/brian/.local/share/InternetRadio`

![alt text](https://github.com/Axel-Erfurt/InternetRadio/blob/master/radio2.png)

[Linux App 64bit Download](https://www.dropbox.com/s/zcw2lmrkqmpcto0/myRadio64.tar.gz?dl=1)

letztes Update 31.Januar 2020 22:24 Uhr

__RadioSearch.py__

find Radio Stations

(now also included in myRadio)
