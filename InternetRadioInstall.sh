#!/bin/sh
filename=$HOME/.local/share/InternetRadio/myradio.txt
if [ -e "$filename" ]
then
    echo "$filename found, copying to /tmp"
    cp $filename /tmp
else
    echo "$filename not found"
fi
sharedapps=$HOME/.local/share/applications/
if [ -d "$sharedapps" ]
 then
    echo "$sharedapps found"
else
    echo "$sharedapps not found"
    mkdir $sharedapps
fi
desktopfile=$HOME/.local/share/applications/InternetRadio.desktop
if [ -e "$desktopfile" ]
then
    echo "$desktopfile already exists"
else
    echo "$desktopfile not found"
    cp $HOME/.local/share/InternetRadio/InternetRadio.desktop $HOME/.local/share/applications
fi
echo "removing InternetRadio"
rm -rf ~/.local/share/InternetRadio
cd ~/.local/share/
echo "downloading InternetRadio ..."
wget https://github.com/Axel-Erfurt/InternetRadio/archive/master.zip
echo "unzip InternetRadio"
unzip -o master.zip
sleep 1
echo "remove zip file"
rm master.zip
mv ~/.local/share/InternetRadio-master ~/.local/share/InternetRadio
rf=/tmp/myradio.txt
if [ -e "$rf" ]
then
    echo "restore myradio.txt"
    cp $rf $HOME/.local/share/InternetRadio
else
    echo "$filename not found"
fi
#cp ~/.local/share/InternetRadio/InternetRadio.desktop ~/.local/share/applications
rm ~/Downloads/InternetRadioInstall.sh
echo "starting InternetRadio ... please use tray icon context menu with right mouse button"
python3 ~/.local/share/InternetRadio/myRadio.py
