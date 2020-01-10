#!/bin/sh
cd ~/.local/share/
echo "downloading InternetRadio ..."
wget https://github.com/Axel-Erfurt/InternetRadio/archive/master.zip
echo "unzip InternetRadio"
unzip -o master.zip
echo "remove zip file"
rm master.zip
mv ~/.local/share/InternetRadio-master ~/.local/share/InternetRadio
cp ~/.local/share/InternetRadio/InternetRadio.desktop ~/.local/share/applications
echo "starting InternetRadio ..."
python3 ~/.local/share/InternetRadio/myRadio.py
