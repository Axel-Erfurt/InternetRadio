# InternetRadio
play and record internet radio stations

![flag](https://github.com/Axel-Erfurt/InternetRadio/blob/master/de_flag.png)
deutsche Anleitung -> [UbuntuUsers Howto myRadio](https://wiki.ubuntuusers.de/Baustelle/Howto/myRadio/)

![alt text](https://github.com/Axel-Erfurt/InternetRadio/blob/master/radio2.png)

__Requirements:__
- PyQt5
- wget

## Usage ##
It is operated via the context menu of the tray icon or the main window.

- right click on systray icon -> category -> select channel

***find radio channels***

opens a window where you can search for radio stations.

A highlighted entry can be added to the channel list in MyRadio via the context menu add to MyRadio List.

In the dialog box  choose a category or create a new category by typing a new name.

Under this category, the channel is then displayed in MyRadio menu.

***Notifications enable / disable notifications***

on / off for displaying metadata (for example, song title and artist, News)

***show Main Window / hide Main Window***

hide  / show Main Window

***stop playing***

Stops playback

***start playing***

Starts playback

***record Channel: station name***

Recording of the current channel is started

***stop recording***

Recording of the current channel is stopped. A dialog box for saving the recording will be shown.

***exit***

leave application

__Channel Editor__

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

`rm ~/.local/share/applications/InternetRadio.desktop`

`rm -rf ~/.local/share/InternetRadio`

__Bookmarks from Radio Tray__

Python Code to convert a Radio Tray bookmarks.xml 

Insert the text into myradio.txt

change myfile = "/tmp/bookmarks.xml" to the path of your bookmarks.xml

```python
import xml.etree.ElementTree as ET

myfile = "/tmp/bookmarks.xml"
tree = ET.parse(myfile)

root = tree.getroot()

print("-- Radio Tray Import --")
for child in root:
    for x in range(len(child)):
        for value in child[x]:
            name = value.get("name")
            url = value.get("url")
            if not url == None and not "separator" in name:
                print(f'{name},{url}')
```

[Linux App 64bit Download](https://www.dropbox.com/s/zcw2lmrkqmpcto0/myRadio64.tar.gz?dl=1)

letztes Update 31.Januar 2020 22:24 Uhr

__RadioSearch.py__

find Radio Stations

(now also included in myRadio)
