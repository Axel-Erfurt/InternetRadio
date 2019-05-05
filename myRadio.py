#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
#os.environ['LD_LIBRARY_PATH'] = "/usr/lib/x86_64-linux-gnu"
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, Qt, QMimeData, QSize, QProcess, QStandardPaths, QFile, QDir
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QSlider, QStatusBar, QMainWindow, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget
from PyQt5.QtGui import QIcon
import urllib

changed = pyqtSignal(QMimeData)
btnwidth = 80

class MainWin(QMainWindow):
    def __init__(self):
        super(MainWin, self).__init__()
        self.setStyleSheet(mystylesheet(self))
        self.wg = QWidget()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10 ,2, 10, 2)
        self.player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.layout1 = QHBoxLayout()

        self.outfile = QStandardPaths.standardLocations(QStandardPaths.TempLocation)[0] + "/radio.mp3"
        self.recording_enabled = False
        self.is_recording = False
        ### combo box
        self.urlCombo = QComboBox(self)

        mydir = os.path.dirname(sys.argv[0])
        print(mydir)
        myradiofile = mydir + "/myradio.txt"
        radio_file = open(myradiofile, "r")
        radioStations = radio_file.read()
        radioStations = self.remove_last_line_from_string(radioStations)
#        print(radioStations)
        radioNames = []
        self.radiolist = []
        self.channels = []
        for t in radioStations:
            self.channels.append(t)
        for lines in radioStations.split("\n"):
            self.urlCombo.addItem(lines.partition(",")[0])
            self.radiolist.append(lines.partition(",")[2])

        self.play_btn = QPushButton("Play", self)
        self.play_btn.setFixedWidth(btnwidth)
        self.play_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.layout1.addWidget(self.play_btn)

        self.pause_btn = QPushButton("Pause", self)
        self.pause_btn.setFixedWidth(btnwidth)
        self.pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.layout1.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop", self)
        self.stop_btn.setFixedWidth(btnwidth)
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.layout1.addWidget(self.stop_btn)
        ### record
        self.rec_btn = QPushButton("Record", self)
        self.rec_btn.setFixedWidth(btnwidth)
        self.rec_btn.setIcon(QIcon.fromTheme("media-record"))
        self.rec_btn.clicked.connect(self.recordRadio)
        self.layout1.addWidget(self.rec_btn)
        ### stop record
        self.stoprec_btn = QPushButton("Stop Rec", self)
        self.stoprec_btn.setFixedWidth(btnwidth)
        self.stoprec_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stoprec_btn.clicked.connect(self.stop_recording)
        self.layout1.addWidget(self.stoprec_btn)

        spc1 = QSpacerItem(6, 10, QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.level_sld = QSlider(self)
        self.level_sld.setTickPosition(1)
        self.level_sld.setSingleStep(5)
        self.level_sld.setOrientation(Qt.Horizontal)
        self.level_sld.setValue(65)
        self.level_lbl = QLabel(self)
        self.level_lbl.setAlignment(Qt.AlignHCenter)
        self.level_lbl.setText("Volume 65")
        self.layout.addWidget(self.urlCombo)
        self.layout.addLayout(self.layout1)
        self.layout.addItem(spc1)
        self.layout.addWidget(self.level_sld)
        self.layout.addWidget(self.level_lbl)
        self.player = RadioPlayer(self)
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.play_btn.clicked.connect(self.playRadioStation)
        self.pause_btn.clicked.connect(self.pause_preview)
        self.stop_btn.clicked.connect(self.stop_preview)
        self.level_sld.valueChanged.connect(self.set_sound_level)
        self.urlCombo.currentIndexChanged.connect(self.url_changed)
        self.current_station = False

        self.process = QProcess()
        self.process.started.connect(self.getPID)
#        self.process.finished.connect(self.saveMovie)

        self.wg.setLayout(self.layout)
        self.setCentralWidget(self.wg)

        self.createStatusBar()
        self.setAcceptDrops(True)
        self.setWindowTitle("Radio")
        self.url_changed()

        self.setMinimumHeight(180)
        self.setFixedWidth(460)
        self.move(0, 30)
        self.findExecutable()
        self.stoprec_btn.setVisible(False)
        print(self.outfile)

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)

    def findExecutable(self):
        wget = QStandardPaths.findExecutable("wget")
        if wget != "":
            print("wget found at " + wget)
            self.recording_enabled = True
        else:
            self.msgbox("wget not found\nrecording disabled")
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
            trackInfo2 = (self.player.metaData("Comment"))
            if not trackInfo == None:
                if not trackInfo2 == None:
                   self.msglbl.setText("%s %s" % (trackInfo, trackInfo2))
                else:
#                    self.bar.showMessage(trackInfo, 0)
                    self.msglbl.setText(trackInfo)
                    self.msglbl.adjustSize()
                    self.adjustSize()
            else:
                self.msglbl.setText("%s %s" % ("playing", self.urlCombo.currentText()))
        else:
            self.msglbl.setText("%s %s" % ("playing", self.urlCombo.currentText()))
 
    def url_changed(self):
        ind = self.urlCombo.currentIndex()
        url = self.radiolist[ind]
        print("playing " + url)
        self.current_station = url
        self.player.stop()
        self.playRadioStation()
 
    def playRadioStation(self):
#        self.player.set_media(None)
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
 
    def set_running_player(self):
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
 
    def pause_preview(self):
        self.player.set_on_pause()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.play_btn.setFocus(True)
        self.msglbl.setText("Pause")
 
    def stop_preview(self):
        self.player.finish()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.msglbl.setText("Stopped")
 
    def set_sound_level(self, level):
        self.player.set_sound_level(level)
        self.level_lbl.setText("Volume " + str(level))
 
    def update_volume_slider(self, level):
        self.level_lbl.setText("Volume " + str(level))
        self.level_sld.blockSignals(True)
        self.level_sld.setValue(value)
        self.level_lbl.setText("Volume " + str(level))
        self.level_sld.blockSignals(False)

    def recordRadio(self):
        if self.is_recording == False:
            self.deleteOutFile()
            cmd = ("wget -q "  + self.current_station + " -O " + self.outfile)
            print(cmd)         
            self.recording = True   
            self.process.startDetached(cmd)
            self.rec_btn.setVisible(False)
            self.stoprec_btn.setVisible(True)
        else:
            self.msgbox("Recording is still in progress")

    def stop_recording(self):
        if self.recording == True:
            self.process.close()
            print("stopping recording")
            self.is_recording = False
            QProcess.execute("killall wget")
            self.saveMovie()
            self.stoprec_btn.setVisible(False)
            self.rec_btn.setVisible(True)
        else:
            self.msgbox("Recording is not in progress")

    def saveMovie(self):
        if self.is_recording == False:
            print("saving audio")
            self.setWindowTitle("myRadio")
            infile = QFile(self.outfile)
            path, _ = QFileDialog.getSaveFileName(self, "Save as...", QDir.homePath() + "/Musik/" + self.urlCombo.currentText().replace("-", " ").replace(" - ", " ") + ".mp3",
                "Audio (*.mp3)")
            if (path != ""):
                savefile = path
                if QFile(savefile).exists:
                    QFile(savefile).remove()
                print("saving " + savefile)
                if not infile.copy(savefile):
                    QMessageBox.warning(self, "Error",
                        "Cannot write file %s:\n%s." % (path, infile.errorString())) 
#                self.deleteOutFile()
#                self.process.setProcessState(0)
                print("process state: " + str(self.process.state()))
                if QFile(self.outfile).exists:
                    print("exists")
                    QFile(self.outfile).remove()


    def deleteOutFile(self):
        if QFile(self.outfile).exists:
            print("deleting file " + self.outfile) 
            if QFile(self.outfile).remove:
                print(self.outfile + " deleted")       
            else:  
                print(self.outfile + " not deleted")   

    def getPID(self):
        print(self.process.pid(), self.process.processId() )

 
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

QComboBox
{
height: 22px;
color: #2e3436;
font-size: 8pt;
}
QStatusBar
{
height: 32px;
color: #888a85;
font-size: 8pt;
background: transparent;
}
QPushButton
{
height: 20px;
color: #2e3436;
font-size: 8pt;
}
QLabel
{
border: 0px;
color: #2e3436;
font-size: 9pt;
}
    """    
 
if __name__ == "__main__":
    app = QApplication([])
    win = MainWin()
    win.setWindowIcon(QIcon.fromTheme("radio"))
    win.show()
    sys.exit(app.exec_())