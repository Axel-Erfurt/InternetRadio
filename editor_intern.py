#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import shutil
import csv
from PyQt5.QtCore import Qt, QDir, QModelIndex, QVariant, QSize, QFile
from PyQt5.QtWidgets import (QMainWindow, QTableView, QApplication, QLineEdit, QWidget,  
                             QFileDialog, QAbstractItemView, QMessageBox, QToolButton, QSizePolicy)
from PyQt5.QtGui import QIcon, QKeySequence, QStandardItemModel, QStandardItem


class Viewer(QMainWindow):
    def __init__(self, parent=None):
      super(Viewer, self).__init__(parent)
      self.filename = ""
      self.fname = ""
      self.csv_file = ''
      self.isChanged = False
      self.mychannels_file = 'myradio.txt'
      self.mychannels_file_backup = 'myradio.txt_backup'
      self.setGeometry(0, 0, 1000, 600)
      self.lb = QTableView()
      self.lb.horizontalHeader().hide()
      self.model = QStandardItemModel()
      self.lb.setModel(self.model)
      self.model.itemChanged.connect(self.finishedEdit)
      self.lb.setEditTriggers(QAbstractItemView.DoubleClicked)
      self.lb.setSelectionBehavior(self.lb.SelectRows)
      self.lb.setSelectionMode(self.lb.SingleSelection)
      self.lb.setDragDropMode(self.lb.InternalMove)
      self.setStyleSheet(stylesheet(self))
      self.lb.setAcceptDrops(True)
      self.setCentralWidget(self.lb)
      self.setContentsMargins(10, 10, 10, 10)
      self.statusBar().showMessage("Welcome", 0)
      self.setWindowTitle("myRadio Listeditor")
      self.setWindowIcon(QIcon.fromTheme("multimedia-playlist"))
      self.createToolBar()
      self.create_backup()
      self.show()
      print("Hello")
      self.open_channels(self.mychannels_file)
      self.lb.setFocus()
      
    def finishedEdit(self):
        self.isChanged = True
      
    def setChanged(self):
        self.isChanged = True
      
    def msgbox(self, message):
        msg = QMessageBox(2, "Information", message, QMessageBox.Ok)
        msg.exec()

      
    def create_backup(self):
        if shutil.copyfile(self.mychannels_file, self.mychannels_file_backup):
            self.msgbox('myradio.txt_backup created')

    def closeEvent(self, event):
        print(self.isChanged)
        if  self.isChanged == True:
            quit_msg = "<b>The document has been changed. <br> Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                self.save_file(self.filename)
        else:
            print("no changes.")

    def createToolBar(self):
        tb = self.addToolBar("Werkzeuge")
        tb.setIconSize(QSize(16, 16))
        
        self.findfield = QLineEdit(placeholderText = "find ...")
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(200)
        tb.addWidget(self.findfield)
        
        tb.addSeparator()
        
        self.replacefield = QLineEdit(placeholderText = "replace with ...")
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(200)
        tb.addWidget(self.replacefield)
        
        tb.addSeparator()
        
        btn = QToolButton()
        btn.setText("replace all")
        btn.setToolTip("replace all")
        btn.clicked.connect(self.replace_in_table)
        tb.addWidget(btn)
        
        tb.addSeparator()

        del_btn = QToolButton()
        del_btn.setIcon(QIcon.fromTheme("edit-delete"))
        del_btn.setToolTip("delete row")
        del_btn.clicked.connect(self.del_row)
        tb.addWidget(del_btn)
        
        tb.addSeparator()
        
        add_btn = QToolButton()
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setToolTip("add row")
        add_btn.clicked.connect(self.add_row)
        tb.addWidget(add_btn)

        move_down_btn = QToolButton()
        move_down_btn.setIcon(QIcon.fromTheme("go-down"))
        move_down_btn.setToolTip("move down")
        move_down_btn.clicked.connect(self.move_down)
        tb.addWidget(move_down_btn)
        
        move_up_up = QToolButton()
        move_up_up.setIcon(QIcon.fromTheme("go-up"))
        move_up_up.setToolTip("move up")
        move_up_up.clicked.connect(self.move_up)
        tb.addWidget(move_up_up)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, 0)
        tb.addWidget(spacer)
        
        self.filter_field = QLineEdit(placeholderText = "Filter (press enter)")
        self.filter_field.setClearButtonEnabled(True)
        self.filter_field.setToolTip("insert search term and press Enter")
        self.filter_field.setFixedWidth(200)
        self.filter_field.returnPressed.connect(self.filter_table)
        self.filter_field.textChanged.connect(self.update_filter)
        tb.addWidget(self.filter_field)
        
        
    def move_down(self):
        if self.model.rowCount() < 1:
            return
        row = self.lb.selectionModel().selection().indexes()[0].row()
        if row > self.model.rowCount() - 2:
            return
        nextrow = row + 1
        itemList = self.model.takeRow(row)
        self.model.insertRow(nextrow,itemList)
        self.isChanged = True
        self.lb.selectRow(nextrow)
        
    def move_up(self):
        if self.model.rowCount() < 1:
            return
        row = self.lb.selectionModel().selection().indexes()[0].row()
        if row < 1:
            return
        nextrow = row - 1
        itemList = self.model.takeRow(row)
        self.model.insertRow(nextrow,itemList)
        self.isChanged = True
        self.lb.selectRow(nextrow)
        
    def del_row(self): 
        if self.model.rowCount() < 1:
            return
        row = self.lb.selectionModel().selection().indexes()[0].row()
        self.model.takeRow(row)
        self.isChanged = True
        self.lb.selectRow(row)
            
    def add_row(self): 
        if self.model.rowCount() < 1:
            return
        print("Zeile hinzufügen")
        newrow = ['name', 'group', 'url']       
        items = [QStandardItem(field) for field in newrow]
        self.model.appendRow(items)
        self.isChanged = True
        self.lb.selectRow(self.model.rowCount() - 1)
        
    def open_channels(self, fileName):
        if fileName:
            self.convert_to_csv(fileName)
            print(fileName + " geladen")
            with open(self.csv_file, 'r') as f:
                i = 0
                reader = csv.reader(f, delimiter = '\t')
                self.model.clear()
                for row in reader:  
                    items = [QStandardItem(field) for field in row]
                    self.model.appendRow(items)
                    self.model.setHeaderData(i - 1, Qt.Horizontal, str(i))
                    i = i + 1     
                self.lb.resizeColumnsToContents()           
                self.lb.selectRow(0)
                self.statusBar().showMessage(f"{fileName} loaded", 0)
                self.isChanged = False
                self.lb.verticalHeader().setMinimumWidth(24)
                self.filename = fileName
             
    def convert_to_csv(self, fileName):
        channels_list = open(fileName, 'r').read().splitlines()
        csv_content = ""
        group = ""
        name = ""
        url = ""

        for x in reversed(range(len(channels_list))):
            line = channels_list[x]
            if line == "":
                print(f"empty line {x} removed")
                del(channels_list[x])
               
        i = 0
        for x in range(0, len(channels_list)):
            line = channels_list[x]
            while True:
                if line.startswith("--"):
                    group = line.replace("-- ", "").replace(" --", "")
                    break
                    continue

                elif not line.startswith("--"):
                    ch_line = line.split(",")
                    name = ch_line[0]
                    url = ch_line[1]
                    i += 1
                    break
                    
            if not name == "" and not name == channels_list[x-1].partition(",")[0]:        
                csv_content += (f'{name}\t{group}\t{url}\n')

        self.csv_file = '/tmp/mychannels.csv'
        with open(self.csv_file, 'w') as f:        
            f.write(csv_content)

            
    def save_file(self, fileName):
        f = open(self.csv_file, 'w')

        content = ""
        
        for row in range(self.lb.model().rowCount()):
            itemlist = []
            for column in range(self.lb.model().columnCount()):
                itemlist.append(self.model.item(row, column).text())
            
            content += '\t'.join(itemlist)
            content += '\n'
        with open(self.csv_file, 'w') as f:
            f.write(content)
            
                
            
            # convert to txt
            channels_list = open(self.csv_file, 'r').read().splitlines()

            group = ""
            name = ""
            url = ""
            out_list = []

            for x in range(len(channels_list)):
                line = channels_list[x].split('\t')
                name = line[0]
                group = line[1]
                url = line[2]
                
                out_list.append(f"-- {group} --")
                out_list.append(f'{name},{url}')
                

            tlist = self.ordered_set(out_list)
            m3u_content = '\n'.join(tlist)
            m3u_content += '\n'

            with open(fileName, 'w') as f:        
                f.write(m3u_content)

            print(fileName + " saved")
            self.isChanged = False
            
    def ordered_set(self, in_list):
        out_list = []
        added = set()
        for val in in_list:
            if not val in added:
                out_list.append(val)
                added.add(val)
        return out_list


    def replace_in_table(self):
        if self.model.rowCount() < 1:
            return
        searchterm = self.findfield.text()
        replaceterm = self.replacefield.text()
        if searchterm == "":
            return
        else:
            for i in range(self.lb.model().columnCount() - 1):
                indexes = self.lb.model().match(
                                    self.lb.model().index(0, i),
                                    Qt.DisplayRole,
                                    searchterm,
                                    -1,
                                    Qt.MatchContains
                                )
                for ix in indexes:
                    old_item = self.model.item(ix.row(), i)
                    new_item = old_item.text().replace(searchterm, replaceterm)
                    self.model.setItem(ix.row(), i, QStandardItem(new_item))
                self.lb.resizeColumnsToContents()
                self.isChanged = True
                
    def filter_table(self):
        if self.model.rowCount() < 1:
            return
        searchterm = self.filter_field.text()  
    
        row_list = []
        self.lb.clearSelection()

        for i in range(self.lb.model().columnCount()-1):
            indexes = self.lb.model().match(
                                self.lb.model().index(0, i),
                                Qt.DisplayRole,
                                searchterm,
                                -1,
                                Qt.MatchContains
                            )
            for ix in indexes:
                self.lb.selectRow(ix.row())    
                row_list.append(ix.row()) 
                
        for x in range(self.lb.model().rowCount()):
            if not x in row_list:
                self.lb.hideRow(x)    
       
    def update_filter(self):
        if self.filter_field.text() == "":
            for x in range(self.lb.model().rowCount()):
                self.lb.showRow(x)

def stylesheet(self):
        return """
    QMenuBar
        {
            background: transparent;
            border: 0px;
        }
        
    QMenuBar:hover
        {
            background: #d3d7cf;
        }
        
    QTableView
        {
            border: 1px solid #d3d7cf;
            border-radius: 0px;
            font-size: 8pt;
            background: #eeeeec;
            selection-color: #ffffff
        }
    QTableView::item:hover
        {   
            color: black;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #729fcf, stop:1 #d3d7cf);           
        }
        
    QTableView::item:selected {
            color: #F4F4F4;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6169e1, stop:1 #3465a4);
        } 

    QTableView QTableCornerButton::section {
            background: #D6D1D1;
            border: 0px outset black;
        }
        
    QHeaderView:section {
            background: #d3d7cf;
            color: #555753;
            font-size: 8pt;
        }
        
    QHeaderView:section:checked {
            background: #204a87;
            color: #ffffff;
        }
        
    QStatusBar
        {
        font-size: 7pt;
        color: #555753;
        }
        
    """
 
#if __name__ == "__main__":
# 
#    app = QApplication(sys.argv)
#    main = Viewer()
#    main.show()
#sys.exit(app.exec_())
