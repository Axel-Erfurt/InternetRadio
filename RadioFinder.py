#!/usr/bin/python3
# -*- coding: utf-8 -*-
##############
"""
made in October 2019 by Axel Schneider
https://github.com/Axel-Erfurt/
Credits: André P. Santos (andreztz) for pyradios
https://github.com/andreztz/pyradios
Copyright (c) 2018 André P. Santos
radio-browser
http://www.radio-browser.info/webservice
"""
##############
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QLineEdit, QComboBox, QInputDialog, 
                             QPushButton, QFileDialog, QAction, QMenu, QMessageBox)
from PyQt5.QtGui import QIcon, QTextCursor, QTextOption
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from urllib import request
import os
import requests
import sys
from xml.etree import ElementTree
from urllib.parse import urljoin


BASE_URL = "http://www.radio-browser.info/webservice/"

endpoints = {
    "countries": {1: "{fmt}/countries", 2: "{fmt}/countries/{filter}"},
    "codecs": {1: "{fmt}/codecs", 2: "{fmt}/codecs/{filter}"},
    "states": {
        1: "{fmt}/states",
        2: "{fmt}/states/{filter}",
        3: "{fmt}/states/{country}/{filter}",
    },
    "languages": {1: "{fmt}/languages", 2: "{fmt}/languages/{filter}"},
    "tags": {1: "{fmt}/tags", 2: "{fmt}/tags/{filter}"},
    "stations": {1: "{fmt}/stations", 3: "{fmt}/stations/{by}/{search_term}"},
    "playable_station": {3: "{ver}/{fmt}/url/{station_id}"},
    "station_search": {1: "{fmt}/stations/search"},
}

def request(endpoint, **kwargs):

    fmt = kwargs.get("format", "json")

    if fmt == "xml":
        content_type = f"application/{fmt}"
    else:
        content_type = f"application/{fmt}"

    headers = {"content-type": content_type, "User-Agent": "getRadiolist/1.0"}

    params = kwargs.get("params", {})

    url = BASE_URL + endpoint

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        if fmt == "xml":
            return resp.text
        return resp.json()

    return resp.raise_for_status()

genres = """Classic Rock
Acoustic
Bluegrass 
Country
Folk
Folk Rock
Grunge
Hard Rock
Blues
Oldies
Pop
Rock
Classic
Beat
Metal
Techno
Schlager"""

class EndPointBuilder:
    def __init__(self, fmt="json"):
        self.fmt = fmt
        self._option = None
        self._endpoint = None

    @property
    def endpoint(self):
        return endpoints[self._endpoint][self._option]

    def produce_endpoint(self, **parts):
        self._option = len(parts)
        self._endpoint = parts["endpoint"]
        parts.update({"fmt": self.fmt})
        return self.endpoint.format(**parts)


class RadioBrowser:
    def __init__(self, fmt="json"):
        self.fmt = fmt
        self.builder = EndPointBuilder(fmt=self.fmt)

    def countries(self, filter=""):
        endpoint = self.builder.produce_endpoint(endpoint="countries")
        return request(endpoint)

    def codecs(self, filter=""):
        endpoint = self.builder.produce_endpoint(endpoint="codecs")
        return request(endpoint)

    def states(self, country="", filter=""):
        endpoint = self.builder.produce_endpoint(
            endpoint="states", country=country, filter=filter
        )
        return request(endpoint)

    def languages(self, filter=""):
        endpoint = self.builder.produce_endpoint(endpoint="languages", filter=filter)
        return request(endpoint)

    def tags(self, filter=""):
        endpoint = self.builder.produce_endpoint(endpoint="tags", filter=filter)
        return request(endpoint)

    def stations(self, **params):
        endpoint = self.builder.produce_endpoint(endpoint="stations")
        kwargs = {}
        if params:
            kwargs.update({"params": params})
        return request(endpoint, **kwargs)

    def stations_byid(self, id):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="byid", search_term=id
        )
        return request(endpoint)

    def stations_byuuid(self, uuid):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="byuuid", search_term=uuid
        )
        return request(endpoint)

    def stations_byname(self, name):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="byname", search_term=name
        )
        return request(endpoint)

    def stations_bynameexact(self, nameexact):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bynameexact", search_term=nameexact
        )
        return request(endpoint)

    def stations_bycodec(self, codec):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bycodec", search_term=codec
        )
        return request(endpoint)

    def stations_bycodecexact(self, codecexact):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bycodecexact", search_term=codecexact
        )
        return request(endpoint)

    def stations_bycountry(self, country):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bycountry", search_term=country
        )
        return request(endpoint)

    def stations_bycountryexact(self, countryexact):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bycountryexact", search_term=countryexact
        )
        return request(endpoint)

    def stations_bystate(self, state):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bystate", search_term=state
        )
        return request(endpoint)

    def stations_bystateexact(self, stateexact):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bystateexact", search_term=stateexact
        )
        return request(endpoint)

    #
    def stations_bylanguage(self, language):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bylanguage", search_term=language
        )
        return request(endpoint)

    def stations_bylanguageexact(self, languageexact):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bylanguageexact", search_term=languageexact
        )
        return request(endpoint)

    def stations_bytag(self, tag):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bytag", search_term=tag
        )
        return request(endpoint)

    def stations_bytagexact(self, tagexact):
        endpoint = self.builder.produce_endpoint(
            endpoint="stations", by="bytagexact", search_term=tagexact
        )
        return request(endpoint)

    def playable_station(self, station_id):
        endpoint = self.builder.produce_endpoint(
            endpoint="playable_station", station_id=station_id, ver="v2"
        )

        return request(endpoint)

    def station_search(self, params, **kwargs):
        # http://www.radio-browser.info/webservice#Advanced_station_search
        assert isinstance(params, dict), "params must be a dictionary."
        kwargs["params"] = params
        endpoint = self.builder.produce_endpoint(endpoint="station_search")
        return request(endpoint, **kwargs)
    

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.tIcon = QIcon(os.path.join(os.path.dirname(sys.argv[0]), "radio_bg.png"))
        self.setWindowIcon(self.tIcon)
        self.setGeometry(0, 0, 700, 400)
        self.setContentsMargins(6, 6, 6, 6)
        self.setStyleSheet(myStyleSheet(self))
        self.setWindowTitle("Radio Suche")
        self.genreList = genres.splitlines()
        self.findfield = QLineEdit()
        self.findfield.setFixedWidth(250)
        self.findfield.addAction(QIcon.fromTheme("edit-find"), 0)
        self.findfield.setPlaceholderText("type search term and press RETURN ")
        self.findfield.returnPressed.connect(self.findStations)
        self.findfield.setClearButtonEnabled(True)
        self.field = QPlainTextEdit()
        self.field.setContextMenuPolicy(Qt.CustomContextMenu)
        self.field.customContextMenuRequested.connect(self.contextMenuRequested)
        self.field.cursorPositionChanged.connect(self.selectLine)
        self.field.setWordWrapMode(QTextOption.NoWrap)
        ### genre box
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.comboSearch)
        self.combo.addItem("choose Genre")
        for m in self.genreList:
            self.combo.addItem(m)
        self.combo.setFixedWidth(150)
        ### toolbar ###
        self.tb = self.addToolBar("tools")
        self.tb.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tb.setMovable(False)
        self.saveButton = QPushButton("Save as txt")
        self.saveButton.setIcon(QIcon.fromTheme("document-save"))
        self.saveButton.clicked.connect(self.saveStations)
        self.savePlaylistButton = QPushButton("Save as m3u")
        self.savePlaylistButton.setIcon(QIcon.fromTheme("document-save"))
        self.savePlaylistButton.clicked.connect(self.savePlaylist)
        self.setCentralWidget(self.field)
        self.tb.addWidget(self.findfield)
        self.tb.addWidget(self.saveButton)
        self.tb.addWidget(self.savePlaylistButton)
        self.tb.addSeparator()
        self.tb.addWidget(self.combo)
        ### player ###
        self.player = QMediaPlayer()
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.startButton = QPushButton("Play")
        self.startButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.startButton.clicked.connect(self.getURLtoPlay)
        self.stopButton = QPushButton("Stop")
        self.stopButton.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stopButton.clicked.connect(self.stopPlayer)
        self.statusBar().addPermanentWidget(self.startButton)
        self.statusBar().addPermanentWidget(self.stopButton)
        ## actions
        self.addToRadiolistAction = QAction(QIcon.fromTheme("add"), "add to myRadio List", self, triggered=self.addToRadiolist)
        self.getNameAction = QAction(QIcon.fromTheme("edit-copy"), "copy Station Name", self, triggered=self.getName)
        self.getUrlAction = QAction(QIcon.fromTheme("edit-copy"), "copy Station URL", self, triggered=self.getURL)
        self.getNameAndUrlAction = QAction(QIcon.fromTheme("edit-copy"), "copy Station Name,URL", self, triggered=self.getNameAndUrl)
        self.getURLtoPlayAction = QAction(QIcon.fromTheme("media-playback-start"), "play Station", self, shortcut="F6", triggered=self.getURLtoPlay)
        self.addAction(self.getURLtoPlayAction)
        self.stopPlayerAction = QAction(QIcon.fromTheme("media-playback-stop"), "stop playing", self, shortcut="F7", triggered=self.stopPlayer)
        self.addAction(self.stopPlayerAction)
        self.helpAction = QAction(QIcon.fromTheme("help-info"), "Help", self, shortcut="F1", triggered=self.showHelp)
        self.addAction(self.helpAction)
        self.statusBar().showMessage("Welcome", 0)
        self.modified = False
        
    def closeEvent(self, event):
        if self.modified == True:
            self.statusBar().showMessage("saved!", 0)
            self.msgbox("new channels available after restarting myRadio")
        
    def addToRadiolist(self):
        text = ""
        filename = os.path.join(os.path.dirname(sys.argv[0]), "myradio.txt")
        print(filename)
        with open(filename, 'r') as f:
            text = f.read()
            text = text[:text.rfind('\n')]
            f.close()
            textlist = text.splitlines()
        mycat = []
        for line in textlist:
            if line.startswith("--"):
                mycat.append(line.replace("-- ", "").replace(" --", ""))
        
        dlg = QInputDialog()
        mc,_ = dlg.getItem(self, "", "select Genre for the station", mycat)
        entry = self.getNameAndUrl()
        print(mc, entry)
        filename = os.path.dirname(sys.argv[0]) + os.sep + "myradio.txt"
        print(filename)
        with open(filename, 'r') as f:
            text = f.read()
            text = text[:text.rfind('\n')]
            f.close()
            textlist = text.splitlines()
            if mc in mycat:
                for x in range(len(textlist)):
                    if textlist[x] == f"-- {mc} --":
                        textlist.insert(x + 1, entry)
            else:
                textlist.append(f"-- {mc} --")
                textlist.append(entry)
        with open(filename, 'w') as f:
            for x in reversed(range(len(textlist))):
                if textlist[x] == "\n":
                    print(x)
                    del textlist[x]
            text = '\n'.join(textlist)
            f.write(text)
            f.write('\n\n')
            f.close()
            self.modified = True
            
            
    def msgbox(self, message):
        msg = QMessageBox(1, "Information", message, QMessageBox.Ok)
        msg.exec()

    def comboSearch(self):
        if self.combo.currentIndex() > 0:
            self.findfield.setText(self.combo.currentText())
            self.findStations()

    def getName(self):
        t = self.field.textCursor().selectedText().partition(",")[0]
        clip = QApplication.clipboard()
        clip.setText(t)

    def getURL(self):
        t = self.field.textCursor().selectedText().partition(",")[2]
        clip = QApplication.clipboard()
        clip.setText(t)

    def getNameAndUrl(self):
        t = self.field.textCursor().selectedText()
        clip = QApplication.clipboard()
        clip.setText(t)
        return(t)
        
    def selectLine(self):
        tc = self.field.textCursor()
        tc.select(QTextCursor.LineUnderCursor)
        tc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor) ##, 
        tc.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.field.setTextCursor(tc)

    def showHelp(self):
        QMessageBox.information(self, "Information", "F6 -> play Station (from line where cursor is)\nF7 -> stop playing")

    def stopPlayer(self):
        self.player.stop()
        self.statusBar().showMessage("Player stopped", 0)

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self, point):
        cmenu = QMenu()
        if not self.field.toPlainText() == "":
            cmenu.addAction(self.getNameAction)
            cmenu.addAction(self.getUrlAction)
            cmenu.addAction(self.getNameAndUrlAction)
            cmenu.addSeparator()
            cmenu.addAction(self.addToRadiolistAction)
            cmenu.addSeparator()
            cmenu.addAction(self.getURLtoPlayAction)
            cmenu.addAction(self.stopPlayerAction)
            cmenu.addSeparator()
            cmenu.addAction(self.helpAction)
        cmenu.exec_(self.field.mapToGlobal(point))  

    def getURLtoPlay(self):
        url = ""
        tc = self.field.textCursor()
        rtext = tc.selectedText().partition(",")[2]
        stext = tc.selectedText().partition(",")[0]
        if rtext.endswith(".pls") :
            url = self.getURLfromPLS(rtext)
        elif rtext.endswith(".m3u") :
            url = self.getURLfromM3U(rtext)
        else:
            url = rtext
        print("stream url=", url)
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()
        self.statusBar().showMessage("%s %s" % ("playing", stext), 0)

    def metaDataChanged(self):
        if self.player.isMetaDataAvailable():
            trackInfo = (self.player.metaData("Title"))
            trackInfo2 = (self.player.metaData("Comment"))
            if not trackInfo == None:
                self.statusBar().showMessage(trackInfo, 0)
                if not trackInfo2 == None:
                   self.statusBar().showMessage("%s %s" % (trackInfo, trackInfo2))

    def getURLfromPLS(self, inURL):
        if "&" in inURL:
            inURL = inURL.partition("&")[0]
        response = request.urlopen(inURL)
        html = response.read().decode("utf-8").splitlines()
        if len(html) > 3:
            if "http" in str(html[1]):
                t = str(html[1])
            elif "http" in str(html[2]):
                t = str(html[2])
            elif "http" in str(html[3]):
                t = str(html[3])
        elif len(html) > 2:
            if "http" in str(html[1]):
                t = str(html[1])
            elif "http" in str(html[2]):
                t = str(html[2])
        else:
            t = str(html[0])
        url = t.partition("=")[2].partition("'")[0]
        return (url)
    
    def getURLfromM3U(self, inURL):
        print("detecting", inURL)
        response = requests.get(inURL)
        html = response.text.splitlines()
        print(html)
        if len(html) > 1:
            url = str(html[1])
        else:
            url = str(html[0])
        print(url)
        return(url)

    def findStations(self):
        self.field.setPlainText("")
        mysearch = self.findfield.text()
        self.statusBar().showMessage("searching ...")
        rb = RadioBrowser()
        myparams = {'name': 'search', 'nameExact': 'false'}
        
        for key in myparams.keys():
                if key == "name":
                    myparams[key] = mysearch
        
        r = rb.station_search(params=myparams)
        
        n = ""
        m = ""
        for i in range(len(r)):
            for key,value in r[i].items():
                if str(key) == "name":
                    n = value.replace(",", " ")
                if str(key) == "url":
                    m = value
                    self.field.appendPlainText("%s,%s" % (n, m))
        if not self.field.toPlainText() == "":
            self.statusBar().showMessage("found "+ str(self.field.toPlainText().count('\n')+1) + " '" + self.findfield.text() + "' Stations")
        else:
            self.statusBar().showMessage("nothing found", 0)

    def saveStations(self):
        if not self.field.toPlainText() == "":
            path, _ = QFileDialog.getSaveFileName(None, "RadioStations", self.findfield.text() + ".txt", "Text Files (*.txt)")
            if path:
                s = self.field.toPlainText()
                with open(path, 'w') as f:
                    f.write(s)
                    f.close()
                    

    def savePlaylist(self):
        if not self.field.toPlainText() == "":
            path, _ = QFileDialog.getSaveFileName(None, "RadioStations", self.findfield.text() + ".m3u", "Playlist Files (*.m3u)")
            if path:
                result = ""
                s = self.field.toPlainText()
                st = []
                for line in s.splitlines():
                    st.append(line)
                result += "#EXTM3U"
                result += '\n'
                for x in range(len(st)):
                    result += "#EXTINF:" + str(x) + "," +  st[x].partition(",")[0]
                    result += '\n'
                    result += st[x].partition(",")[2]
                    result += '\n'
                with open(path, 'w') as f:
                    f.write(result)
                    f.close()
                    self.statusBar().showMessage("saved!", 0)

def myStyleSheet(self):
    return """
QPlainTextEdit
{
background: #eeeeec;
color: #202020;
}
QStatusBar
{
font-size: 8pt;
color: #555753;
}
QMenuBar
{
background: transparent;
border: 0px;
}
QToolBar
{
background: transparent;
border: 0px;
}
QMainWindow
{
     background: qlineargradient(y1: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QLineEdit
{
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #e5e5e5,
                                 stop: 0.5 #e9e9e9, stop: 1.0 #d2d2d2);
}
QPushButton
{
background: #D8D8D8;
}
    """       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    mainWin.findfield.setFocus()
    sys.exit(app.exec_())
    
