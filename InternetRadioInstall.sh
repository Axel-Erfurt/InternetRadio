#!/bin/sh
filename=$HOME/.local/share/InternetRadio/myradio.txt
if [ -e "$filename" ]
then
    echo "$filename found, copying to /tmp"
    cp $filename /tmp
else
    echo "$filename not found"
fi
echo "removing desktop file"
rm ~/.local/share/applications/InternetRadio.desktop
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
cp ~/.local/share/InternetRadio/InternetRadio.desktop ~/.local/share/applications
echo "starting InternetRadio ..."
python3 ~/.local/share/InternetRadio/myRadio.py
