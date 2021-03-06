#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
from PyQt5.QtCore import (QUrl, pyqtSignal, Qt, QMimeData, QSize, QPoint, QProcess, 
                            QStandardPaths, QFile, QDir, QSettings, QEvent)
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QSlider, QToolButton, 
                            QMainWindow, QFileDialog, QMenu, qApp, QAction, 
                             QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSpacerItem, QSizePolicy, 
                            QMessageBox, QPlainTextEdit, QSystemTrayIcon)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon, QStandardItem
import RadioFinder

changed = pyqtSignal(QMimeData)
btnwidth = 80

class Editor(QWidget):
    def __init__(self):
        super(Editor, self).__init__()
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.radiofile = ""
        self.radio_editor = QPlainTextEdit()
        self.radio_editor.textChanged.connect(self.setModified)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.radio_editor)
        self.setLayout(self.layout)
        self.setGeometry(0, 0, 800, 600)

    def closeEvent(self, event):
        if self.isModified == True:
            quit_msg = "<b>The document was changed.<br>Do you want to save the changes?</ b>\
                        <br><br><span style='color: #a40000;'>new channels will be available at next start of myRadio</span>"
            reply = QMessageBox.question(None, 'Save Confirmation', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.saveFile():
                    print("file saved\nclosing editor")
                    event.accept()
                else:
                    print("closing editor")
            
    def saveFile(self):
        with open(self.radiofile, 'w') as f:
            f.write(str(self.radio_editor.toPlainText()))
            f.close()
            return True
            
    def setModified(self):
        self.isModified = True
        

class MainWin(QMainWindow):
    def __init__(self):
        super(MainWin, self).__init__()
        self.settings = QSettings("myRadio", "settings")
        self.setStyleSheet(mystylesheet(self))
        self.radioNames = []
        self.radiolist = []
        self.channels = []
        self.radiofile = ""
        self.radioStations = ""
        self.rec_name = ""
        self.rec_url = ""
        self.notificationsEnabled = True
        self.wg = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10 ,2, 10, 2)
        self.layout1 = QHBoxLayout()

        self.outfile = QStandardPaths.standardLocations(QStandardPaths.TempLocation)[0] + "/radio.mp3"
        self.recording_enabled = False
        self.is_recording = False
        ### combo box
        self.urlCombo = QComboBox(self)

        self.play_btn = QPushButton("Play", self)
        self.play_btn.setFixedWidth(btnwidth)
        self.play_btn.setFlat(True)
        self.play_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.layout1.addWidget(self.play_btn)

        self.pause_btn = QPushButton("Pause", self)
        self.pause_btn.setFixedWidth(btnwidth)
        self.pause_btn.setFlat(True)
        self.pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.layout1.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop", self)
        self.stop_btn.setFixedWidth(btnwidth)
        self.stop_btn.setFlat(True)
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.layout1.addWidget(self.stop_btn)
        ### record
        self.rec_btn = QPushButton("Record", self)
        self.rec_btn.setFixedWidth(btnwidth)
        self.rec_btn.setFlat(True)
        self.rec_btn.setIcon(QIcon.fromTheme("media-record"))
        self.rec_btn.clicked.connect(self.recordRadio1)
        self.rec_btn.setToolTip("Record Station")
        self.layout1.addWidget(self.rec_btn)
        ### stop record
        self.stoprec_btn = QPushButton("Stop Rec", self)
        self.stoprec_btn.setFixedWidth(btnwidth)
        self.stoprec_btn.setFlat(True)
        self.stoprec_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stoprec_btn.clicked.connect(self.stop_recording)
        self.stoprec_btn.setToolTip("Stop Recording")
        self.layout1.addWidget(self.stoprec_btn)
        ### edit Radiio List
        self.edit_btn = QPushButton("", self)
        self.edit_btn.setFixedWidth(26)
        self.edit_btn.setFlat(True)
        self.edit_btn.setToolTip("Channel Editor")
        self.edit_btn.setIcon(QIcon.fromTheme("preferences-system"))
        self.edit_btn.clicked.connect(self.edit_Channels)
        self.layout1.addWidget(self.edit_btn)
        ### hide Main Window
        self.hide_btn = QPushButton("", self)
        self.hide_btn.setFixedWidth(26)
        self.hide_btn.setFlat(True)
        self.hide_btn.setToolTip("hide Window")
        self.hide_btn.setIcon(QIcon.fromTheme("window-hide"))
        self.hide_btn.clicked.connect(self.showMain)
        self.layout1.addWidget(self.hide_btn)        
        


        spc1 = QSpacerItem(6, 10, QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.level_sld = QSlider(self)
        self.level_sld.setTickPosition(1)
        self.level_sld.setOrientation(Qt.Horizontal)
        self.level_sld.setValue(65)
        self.level_lbl = QLabel(self)
        self.level_lbl.setAlignment(Qt.AlignHCenter)
        self.level_lbl.setText("Volume 65")
        #self.layout.addWidget(self.urlCombo)
        self.layout.addLayout(self.layout1)
        self.layout.addItem(spc1)
        self.layout.addWidget(self.level_sld)
        self.layout.addWidget(self.level_lbl)
        self.player = RadioPlayer(self)
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.player.error.connect(self.handleError)
        self.play_btn.clicked.connect(self.playRadioStation)
        self.pause_btn.clicked.connect(self.pause_preview)
        self.stop_btn.clicked.connect(self.stop_preview)
        self.level_sld.valueChanged.connect(self.set_sound_level)
        self.urlCombo.currentIndexChanged.connect(self.url_changed)
        self.current_station = ""

        self.process = QProcess()
        self.process.started.connect(self.getPID)

        self.wg.setLayout(self.layout)
        self.setCentralWidget(self.wg)

        self.stoprec_btn.setVisible(False)
        self.readStations()

        self.createStatusBar()
        self.setAcceptDrops(True)
        self.setWindowTitle("Radio")
        self.tIcon = QIcon(os.path.join(os.path.dirname(sys.argv[0]), "radio_bg.png"))
        self.setWindowIcon(self.tIcon)
        self.stationActs = []


        self.setMinimumHeight(180)
        self.setFixedWidth(460)
        self.move(0, 30)

        # Init tray icon
        trayIcon = QIcon(self.tIcon)

        self.trayIcon = QSystemTrayIcon()
        self.trayIcon.setIcon(trayIcon)
        self.trayIcon.installEventFilter(self)
        self.trayIcon.activated.connect(self.setTrayTrigger)
        self.trayIcon.show()
                
        self.metaLabel = QLabel()

        self.geo = self.geometry()
        self.findRadioAction = QAction(QIcon.fromTheme("edit-find"), "find Radio Channels", 
                                    triggered = self.findRadio)
        self.editAction = QAction(QIcon.fromTheme("preferences-system"), "edit Channels", 
                                    triggered = self.edit_Channels)
        self.showWinAction = QAction(QIcon.fromTheme("view-restore"), "show Main Window", triggered = self.showMain)
        self.notifAction = QAction(QIcon.fromTheme("dialog-information"), "disable Notifications", triggered = self.toggleNotif)
        self.togglePlayerAction = QAction("stop playing", triggered = self.togglePlay)
        self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.recordAction = QAction(QIcon.fromTheme("media-record"), "record channel", triggered = self.recordRadio1)
        self.stopRecordAction = QAction(QIcon.fromTheme("media-playback-stop"), "stop recording", 
                                triggered = self.stop_recording)
        self.findExecutable()
        self.readSettings()
        self.makeTrayMenu()
        self.createWindowMenu()
        if QSystemTrayIcon.isSystemTrayAvailable():
            print("QSystemTrayIcon is available")
        else:
            print("QSystemTrayIcon is not available")
        if self.player.state() == QMediaPlayer.StoppedState:
            self.togglePlayerAction.setText("start playing")
            self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-start"))            
        elif self.player.state() == QMediaPlayer.PlayingState:
            self.togglePlayerAction.setText("stop playing")
            self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-stop"))
            
    def createWindowMenu(self):
        self.tb = self.addToolBar("Menu")
        self.tb_menu = QMenu()
        self.tb.setIconSize(QSize(20, 20))
        
        ##### submenus from categories ##########
        b = self.radioStations.splitlines()
        for x in reversed(range(len(b))):
            line = b[x]
            if line == "":
                print(f"empty line {x} removed")
                del(b[x])
               
        i = 0
        for x in range(0, len(b)):
            line = b[x]
            while True:
                if line.startswith("--"):
                    chm = self.tb_menu.addMenu(line.replace("-- ", "").replace(" --", ""))
                    chm.setIcon(self.tIcon)
                    break
                    continue

                elif not line.startswith("--"):
                    chm.addAction(self.stationActs[i])
                    i += 1
                    break
        ####################################
        toolButton = QToolButton()
        toolButton.setIcon(self.tIcon)
        toolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolButton.setText("   Stations")
        toolButton.setMenu(self.tb_menu)
        toolButton.setPopupMode(QToolButton.InstantPopup)
        self.tb.addWidget(toolButton)

        self.tb.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tb.setMovable(False)
        self.tb.setAllowedAreas(Qt.TopToolBarArea)
            
    def eventFilter(self, source, event):
        if source is self.trayIcon:
            if event.type() == QEvent.Wheel:
                vol = self.level_sld.value()
                if event.angleDelta().y() > 1:
                    self.level_sld.setValue(int(vol) + 5)
                else:
                    self.level_sld.setValue(int(vol) - 5)
        return super(MainWin, self).eventFilter(source, event)
        
    def setTrayTrigger(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showMainfromTray()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.muteFromTray()

        
    def muteFromTray(self):
        if self.player.isMuted():
            self.player.setMuted(False)
        else:
            self.player.setMuted(True)
            
            
    def findRadio(self):
        if self.player.state() == 1:
            self.player.stop()
        self.fr = RadioFinder.MainWindow()
        self.fr.setAttribute(Qt.WA_QuitOnClose, False)
        self.fr.show()
        self.fr.findfield.setFocus()
        
        
    def handleError(self):
        print("Error Player: " + self.player.errorString())
        self.trayIcon.showMessage("Error", self.player.errorString(), self.tIcon, 3000)
        self.msglbl.setText(f"Error:\n{self.player.errorString()}")
           
    def togglePlay(self):          
        if self.togglePlayerAction.text() == "stop playing":
            self.stop_preview()
            self.togglePlayerAction.setText("start playing")
            self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-start"))
        else:
            self.playRadioStation()
            self.togglePlayerAction.setText("stop playing")
            self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-stop"))

    def getURLfromPLS(self, inURL):
        print("detecting", inURL)
        t = ""
        if "&" in inURL:
            inURL = inURL.partition("&")[0]
        response = requests.get(inURL)
        print(response.text)
        if "http" in response.text:
            html = response.text.splitlines()
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
        else:
           self.lbl.setText("bad playlist format") 

    def getURLfromM3U(self, inURL):
        print("detecting", inURL)
        response = requests.get(inURL)
        html = response.text.splitlines()
        if "#EXTINF" in str(html):
            url = str(html[1]).partition("http://")[2].partition('"')[0]
            url = f"http://{url}"
        else:
            if len(html) > 1:
                url = str(html[1])
            else:
                url = str(html[0])
        print(url)
        return(url)
        
    def makeTrayMenu(self):
        self.tray_menu = QMenu()
        self.tray_menu.addAction(self.togglePlayerAction)
        self.tray_menu.setStyleSheet("font-size: 7pt;")
        ##### submenus from categories ##########
        b = self.radioStations.splitlines()
        for x in reversed(range(len(b))):
            line = b[x]
            if line == "":
                print("removing empty line:", x)
                del(b[x])
                
        i = 0
        for x in range(0, len(b)):
            line = b[x]
            while True:
                if line.startswith("--"):
                    chm = self.tray_menu.addMenu(line.replace("-- ", "").replace(" --", ""))
                    chm.setIcon(self.tIcon)
                    break
                    continue

                elif  not line.startswith("--"):
                    ch = line.partition(",")[0]                    
                    self.stationActs.append(QAction(QIcon.fromTheme("browser"), ch, triggered = self.openTrayStation))
                    self.stationActs[i].setData(str(i))
                    chm.addAction(self.stationActs[i])
                    i += 1
                    break
        ####################################
        self.tray_menu.addSeparator()
        if self.is_recording == False:
            if not self.urlCombo.currentText().startswith("--"):
                self.tray_menu.addAction(self.recordAction)
                self.recordAction.setText("%s %s: %s" % ("record", "channel", self.urlCombo.currentText()))
        if self.is_recording == True:
            self.tray_menu.addAction(self.stopRecordAction)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.editAction)
        self.tray_menu.addAction(self.showWinAction)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.notifAction)
        self.tray_menu.addAction(self.findRadioAction)
        self.tray_menu.addSeparator()
        exitAction = self.tray_menu.addAction(QIcon.fromTheme("application-exit"), "exit")
        exitAction.triggered.connect(self.exitApp)
        self.trayIcon.setContextMenu(self.tray_menu)

    def showMain(self):
        if self.isVisible() ==False:
            self.showWinAction.setText("hide Main Window")
            self.setVisible(True)
        elif self.isVisible() ==True:
            self.showWinAction.setText("show Main Window")
            self.setVisible(False)
            
    def showMainfromTray(self):
        buttons = qApp.mouseButtons()
        if buttons == Qt.LeftButton:
            if self.isVisible() == False:
                self.showWinAction.setText("hide Main Window")
                self.setVisible(True)
            elif self.isVisible() == True:
                self.showWinAction.setText("show Main Window")
                self.setVisible(False)
        if self.isVisible():
            self.showWinAction.setText("hide Main Window")
        else:
           self.showWinAction.setText("show Main Window") 
            
    def toggleNotif(self):
        if self.notifAction.text() == "disable Notifications":
            self.notifAction.setText("enable Notifications")
            self.notificationsEnabled = False
        elif self.notifAction.text() == "enable Notifications":
            self.notifAction.setText("disable Notifications")
            self.notificationsEnabled = True
        print("Notifications", self.notificationsEnabled )
        self.metaDataChanged()

    def openTrayStation(self):
        action = self.sender()
        if action:
            ind = action.data()
            name = action.text()     
            self.urlCombo.setCurrentIndex(self.urlCombo.findText(name))
            print("%s %s %s" % ("switch to station:", ind, self.urlCombo.currentText()))

    def exitApp(self):
        self.close()
        QApplication.quit()

    def message(self):
        QMessageBox.information(
                None, 'Systray Message', 'Click Message')

    def closeEvent(self, e):
        self.writeSettings()
        print("writing settings ...\nGoodbye ...")
        QApplication.quit()
        

    def readSettings(self):
        print("reading settings ...")
        if self.settings.contains("pos"):
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        else:
            self.move(0, 26)
        if self.settings.contains("lastChannel"):
            lch = self.settings.value("lastChannel")
            self.urlCombo.setCurrentIndex(self.urlCombo.findText(lch))
        if self.settings.contains("notifications"):
            self.notificationsEnabled = self.settings.value("notifications")
            if self.settings.value("notifications") == "false":
                self.notificationsEnabled = False
                self.notifAction.setText("enable Notifications")
            else:
                self.notificationsEnabled = True
                self.notifAction.setText("disable Notifications")
        

    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("index", self.urlCombo.currentIndex())
        self.settings.setValue("lastChannel", self.urlCombo.currentText())
        self.settings.setValue("notifications", self.notificationsEnabled)
        self.settings.sync()

    def readStations(self):
        menuSectionIcon = QIcon(os.path.join(os.path.dirname(sys.argv[0]), "radio_bg.png"))
        self.urlCombo.clear()
        self.radiolist = []
        self.channels = []
        dir = os.path.dirname(sys.argv[0])
        self.radiofile = os.path.join(dir, "myradio.txt")
        with open(self.radiofile, 'r') as f:
            self.radioStations = f.read()
            f.close()
            for t in self.radioStations:
                self.channels.append(t)
            for lines in self.radioStations.split("\n"):
                if not lines.startswith("--"):
                    self.urlCombo.addItem(QIcon.fromTheme("browser"), lines.partition(",")[0],Qt.UserRole - 1)
                elif lines.startswith("--"):
                    m = QStandardItem(menuSectionIcon,lines.partition(",")[0])
                    m.setEnabled(False)
                    self.urlCombo.model().appendRow(m)            
                self.radiolist.append(lines.partition(",")[2])

    def edit_Channels(self):
        dir = os.path.dirname(sys.argv[0])
        self.radiofile = os.path.join(dir, "myradio.txt")
        self.trayIcon.showMessage("Note", "changes are available after restarting myRadio", self.tIcon, 2000)
        self.edWin = Editor()
        self.edWin.radiofile = self.radiofile
        t = open(self.radiofile, 'r').read()
        self.edWin.radio_editor.setPlainText(t)
        self.edWin.isModified = False
        self.edWin.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F5:
            self.playURL()
        elif e.key() == Qt.Key_F1:
            QMessageBox.information(self, "Information", "F5 -> play URL from Clipboard").exec_()
        else:
            e.accept()

    def findExecutable(self):
        wget = QStandardPaths.findExecutable("wget")
        print("wget:", wget)
        if wget != "":
            print("%s %s %s" % ("wget found at ", wget, " *** recording enabled"))
            self.msglbl.setText("recording enabled")
            self.trayIcon.showMessage("Note", "wget found\nrecording enabled", self.tIcon, 1500)
            self.recording_enabled = True
        else:
            self.trayIcon.showMessage("Note", "wget not found\nrecording disabled", self.tIcon, 2000)
            print("wget not found\nrecording disabled")
            self.recording_enabled = False

    def remove_last_line_from_string(self, s):
        return s[:s.rfind('\n')]

    def createStatusBar(self):
        self.msglbl = QLabel()
        self.msglbl.setWordWrap(True)
        self.msglbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.msglbl)
        self.msglbl.setText("Ready")

    def metaDataChanged(self):
        if self.player.isMetaDataAvailable():
            trackInfo = (self.player.metaData("Title"))
            description = (self.player.metaData("Description"))
            comment = (self.player.metaData("Comment"))
            if trackInfo == None:
                self.msglbl.setText("%s %s" % ("playing", self.urlCombo.currentText()))
            new_trackInfo = ""
            new_trackInfo = str(trackInfo)
            if len(new_trackInfo) > 200:
                new_trackInfo = str(new_trackInfo).partition('{"title":"')[2].partition('","')[0].replace('\n', " ")[:200]
            if not new_trackInfo == "None":
                self.msglbl.setText(new_trackInfo)
                self.msglbl.adjustSize()
                self.adjustSize()
            else:
                self.msglbl.setText("%s %s" % ("playing", self.urlCombo.currentText()))
            mt = (f"Title:{new_trackInfo}\nDescription:{description}\nComment: {comment}")
            if description == None:
                mt = (f"Title:{new_trackInfo}\nComment: {comment}")
            if comment == None:
                mt = (f"Title:{new_trackInfo}\nComment: {description}")
            if description == None and comment == None:
                mt = (f"{new_trackInfo}")
            if not mt == "None":
                print(mt)
                if self.notificationsEnabled == True:
                    self.trayIcon.showMessage("myRadio", mt, self.tIcon, 2000)
                    self.trayIcon.setToolTip(mt)
                else:
                    self.trayIcon.setToolTip(mt)
        else:
            self.msglbl.setText("%s %s" % ("playing", self.urlCombo))

    def url_changed(self):
        if self.urlCombo.currentIndex() < self.urlCombo.count() - 1:
            if not self.urlCombo.currentText().startswith("--"):
                ind = self.urlCombo.currentIndex()
                url = self.radiolist[ind]
                
                if url.endswith(".m3u"):
                    url = self.getURLfromM3U(url)
                if url.endswith(".pls"):
                    url = self.getURLfromPLS(url)
                
                self.current_station = url
                self.player.stop()
                self.rec_btn.setVisible(True)
                self.stop_btn.setVisible(True)
                self.play_btn.setVisible(True)
                self.pause_btn.setVisible(True)
                print("%s %s" %("playing", url))
                self.playRadioStation()
                if self.togglePlayerAction.text() == "stop playing":
                    self.togglePlayerAction.setText("start playing")
                    self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-start"))
                else:
                    self.togglePlayerAction.setText("stop playing")
                    self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-stop"))
            else:
                self.rec_btn.setVisible(False)
                self.stop_btn.setVisible(False)
                self.play_btn.setVisible(False)
                self.pause_btn.setVisible(False)
 
    def playRadioStation(self):
        if self.player.is_on_pause:
            self.set_running_player()
            self.player.start()
            self.pause_btn.setFocus()
            self.togglePlayerAction.setText("stop playing")
            self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-stop"))
 
        if not self.current_station:
            return
 
        self.player.set_media(self.current_station)
        self.set_running_player()
        self.player.start()
        if self.is_recording == True:
            self.recordAction.setText(f"stop recording {self.rec_name}")
            self.recordAction.setIcon(QIcon.fromTheme("media-playback-stop"))
        else:
            self.recordAction.setText("%s %s: %s" % ("record", "channel", self.urlCombo.currentText()))
            self.recordAction.setIcon(QIcon.fromTheme("media-record"))
        self.msglbl.setText("%s %s" % ("playing", self.urlCombo.currentText()))
        self.setWindowTitle(self.urlCombo.currentText())        

    def playURL(self):
        clip = QApplication.clipboard()
        if not clip.text().endswith(".pls") and not clip.text().endswith(".m3u"):
            self.current_station = clip.text()
        elif clip.text().endswith(".pls") :
            print("is a pls")
            url = self.getURLfromPLS(clip.text())
            self.current_station = url
        elif clip.text().endswith(".m3u") :
            print("is a m3u")
            url = self.getURLfromM3U(clip.text())
            self.current_station = url
        print(self.current_station)

        if self.player.is_on_pause:
            self.set_running_player()
            self.player.start()
            self.pause_btn.setFocus()
            return
 
        if not self.current_station:
            return
 
        self.player.set_media(self.current_station)
        self.set_running_player()
        self.player.start()
        self.msglbl.setText("%s %s" % ("playing", self.urlCombo.currentText()))
        self.metaDataChanged()
        
    def setVolumeWheel(self):
        print("wheel")
        self.level_sld.setValue(self.level_sld.value() + 5)

 
    def set_running_player(self):
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.rec_btn.setEnabled(True)
 
    def pause_preview(self):
        self.player.set_on_pause()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.rec_btn.setEnabled(False)
        self.play_btn.setFocus(True)
        self.msglbl.setText("Pause")
 
    def stop_preview(self):
        self.player.finish()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.rec_btn.setEnabled(False)
        self.msglbl.setText("Stopped")
        self.togglePlayerAction.setText("start playing")
        self.togglePlayerAction.setIcon(QIcon.fromTheme("media-playback-start"))

 
    def set_sound_level(self, level):
        self.player.set_sound_level(level)
        self.level_lbl.setText("Volume " + str(level))
 
    def update_volume_slider(self, level):
        self.level_lbl.setText("Volume " + str(level))
        self.level_sld.blockSignals(True)
        self.level_sld.setValue(level)
        self.level_lbl.setText("Volume " + str(level))
        self.level_sld.blockSignals(False)

    def recordRadio1(self):
        if self.is_recording == False:
            self.deleteOutFile()
            self.rec_url = self.current_station
            self.rec_name = self.urlCombo.currentText()
            cmd = ("wget -q "  + self.rec_url + " -O " + self.outfile)
            print(cmd)         
            self.is_recording = True   
            self.process.startDetached(cmd)
            self.recordAction.setText(f"stop recording {self.rec_name}")
            self.recordAction.setIcon(QIcon.fromTheme("media-playback-stop"))
            self.rec_btn.setVisible(False)
            self.stoprec_btn.setVisible(True)
        else:
            self.stop_recording()

    def stop_recording(self):
        if self.is_recording == True:
            self.process.close()
            print("stopping recording")
            self.is_recording = False
            QProcess.execute("killall wget")
            if self.isVisible() ==False:
                self.showWinAction.setText("hide Main Window")
                self.setVisible(True)
            self.saveMovie()
            self.stoprec_btn.setVisible(False)
            self.rec_btn.setVisible(True)
            self.recordAction.setText("%s %s: %s" % ("record", "channel", self.urlCombo.currentText()))
            self.recordAction.setIcon(QIcon.fromTheme("media-record"))
            self.showMain()
        else:
            self.trayIcon.showMessage("Note", "Recording is not in progress", self.tIcon, 2000)

    def saveMovie(self):
        if self.is_recording == False:
            print("saving audio")
            infile = QFile(self.outfile)
            path, _ = QFileDialog.getSaveFileName(None, "Save as...", 
                            QDir.homePath() + "/Musik/" + self.rec_name
                            .replace("-", " ").replace(" - ", " ") + ".mp3", "Audio (*.mp3)")
            if (path != ""):
                savefile = path
                if QFile(savefile).exists:
                    QFile(savefile).remove()
                print("%s %s" % ("saving", savefile))
                if not infile.copy(savefile):
                    QMessageBox.warning(self, "Error",
                        "Cannot write file %s:\n%s." % (path, infile.errorString())) 
                print("%s %s" % ("process state: ", str(self.process.state())))
                if QFile(self.outfile).exists:
                    print("exists")
                    QFile(self.outfile).remove()


    def deleteOutFile(self):
        if QFile(self.outfile).exists:
            print("%s %s" % ("deleting file", self.outfile)) 
            if QFile(self.outfile).remove:
                print("%s %s" % (self.outfile, "deleted"))  
            else:  
                print("%s %s" % (self.outfile, "not deleted"))

    def getPID(self):
        print("%s %s" % (self.process.pid(), self.process.processId()))

 
class RadioPlayer(QMediaPlayer):
    def __init__(self, driver):
        super(RadioPlayer, self).__init__()
        self.driver = driver
        self.url = None
        self.auto_sound_level = True
        self.is_running = False
        self.is_on_pause = False
        self.volumeChanged.connect(self.on_volume_changed)
        self.stateChanged.connect(self.on_state_changed)
 
    def set_media(self, media):
        if isinstance(media, QUrl):
            self.url = media
 
        elif isinstance(media, str):
            self.url = QUrl(media)
 
        self.setMedia(QMediaContent(self.url))
 
    def start(self):
        self.is_running = True
        self.is_on_pause = False
        self.play()
 
    def set_on_pause(self):
        self.is_running = False
        self.is_on_pause = True
        self.pause()

 
    def finish(self):
        self.is_running = False
        self.is_on_pause = False
        self.stop()
            
    def set_sound_level(self, level):
        self.auto_sound_level = False
        self.setVolume(level)
 
    def on_volume_changed(self, value):
        if self.auto_sound_level:
            self.update_volume_slider(value)
        self.auto_sound_level = True
 
    def on_state_changed(self, state):
        if not state:
            self.driver.stop_preview()

def mystylesheet(self):
    return """
QPushButton
{
color: #1f3c5d;
}
QComboBox
{
height: 18px;
background: #d3d7cf;
color: #2e3436;
font-size: 8pt;
}
QComboBox::item
{
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #729fcf, stop: 1.0 #204a87);
selection-color: #eeeeec;
}
QStatusBar
{
height: 32px;
color: #888a85;
font-size: 8pt;
background: transparent;
}
QLabel
{
border: 0px;
color: #1f3c5d;
font-size: 9pt;
}
QMainWindow
{
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QSlider::handle:horizontal 
{
background: transparent;
width: 8px;
}

QSlider::groove:horizontal {
border: 1px solid #444;
height: 8px;
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #babdb6, stop: 1.0 #D3D3D3);
border-radius: 4px;
}
QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
    stop: 0 #66e, stop: 1 #bbf);
background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
    stop: 0 #bbf, stop: 1 #55f);
border: 1px solid #777;
height: 8px;
border-radius: 4px;
}
QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #fff, stop:1 #ddd);
border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border-radius: 4px;
}
QSystemTrayIcon::message { 
font-size: 7pt;
color: #2e3436; 
background: #c4a000; 
border: 1px solid #1f3c5d; }
    """    


if __name__ == "__main__":
    app = QApplication([])
    win = MainWin()
    app.setQuitOnLastWindowClosed(False)
    #win.show()
    sys.exit(app.exec_())
    
