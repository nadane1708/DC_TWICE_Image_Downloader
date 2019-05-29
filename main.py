import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import dc
import configparser


form_class = uic.loadUiType("./res/main.ui")[0]
        
class MyWindow(QMainWindow, form_class, QObject):
    main_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        # UI Setting
        self.setupUi(self)

        self.setFixedSize(397, 256) # Fix window size
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint) # Remove resizing mouse cursor

        # Quit setting
        self.quit = QAction("Quit", self)
        self.quit.triggered.connect(self.closeEvent)

        # Worker Thread
        self.worker = dc.Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Connecting Signals
        self._connectSignals()

        # Set QCombBox Completer for Disabling Auto-Completion
        self.completer = QCompleter(self)
        self.selectGallery.setCompleter(self.completer)

        # ComboBox
        self.selectGallery.setEditText('twice')
        self.selectGallery.activated.connect(self.selectionChanged)

        # PushButton
        self.openPath.clicked.connect(self.btn_openpath)

        # StatusBar
        self.statusBar = QStatusBar(self)
        self.statusBar.setSizeGripEnabled(False) # Remove resizing grip of status bar
        self.setStatusBar(self.statusBar)

        # Download Status Treeview
        self.is_expand = False
        self.treeChild = []
        self.treeParent = QTreeWidgetItem()

        self.expandTreeview.clicked.connect(self.btn_expandTreeview)
        self.tr_selectDel.clicked.connect(self.btn_trSelectDel)
        self.resetTreeview.clicked.connect(self.btn_resetTreeview)

        self.trWidget = QTreeWidget(self.treeView)
        self.trWidget.setColumnCount(2)
        self.trWidget.setHeaderLabels(['글제목(파일명)', '다운 상태', '주소'])
        self.trWidget.setColumnWidth(0, 340)
        self.trWidget.setColumnWidth(1, 70)
        self.trWidget.resize(411, 511)
        self.trWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Load settings from INI file
        parser = configparser.ConfigParser()
        if parser.read('setting.ini') == []:
            pass
        else:
            self.selectGallery.setEditText(parser.get('Preset', 'gallid'))
            self.editPage.setText(parser.get('Preset', 'page'))
            self.editKeyword.setText(parser.get('Preset', 'keyword'))
            self.onlyBy.setChecked(bool(int(parser.get('Preset', 'by'))))
            self.onlyRcmd.setChecked(bool(int(parser.get('Preset', 'rcmd'))))
            self.editExcept.setText(parser.get('Preset', 'except'))
            self.excptPreview.setChecked(bool(int(parser.get('Preset', 'preview'))))
            self.folderSeparate.setChecked(bool(int(parser.get('Preset', 'sprt'))))
            self.editPath.setText(parser.get('Preset', 'path'))

    def selectionChanged(self):
        _gall_id = ['twice', 'twicetv', 'nayeone', 'jungyeon', 'momo', 'sanarang', 'jihyo', 'twicemina', 'dahyeon', 'sonchaeyoung', 'tzuyu0614', 'streaming']

        self.selectGallery.setEditText(_gall_id[self.selectGallery.currentIndex()])

    def btn_openpath(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.editPath.setText('%s\\' % os.path.normpath(fname)) # os.path.normpath(path) --> Change "/" to "\" on Windows OS

    def _connectSignals(self):
        
        self.downloadCancel.clicked.connect(self.forceWorkerReset)

        # Connect worker's pyqtSignal to pyqtSlot
        self.worker.finished.connect(self.updateStatusBar)
        self.worker.finished_err.connect(self.eventHandling)

        # Solved parameter problem for QT connect: https://stackoverflow.com/questions/23317195/pyqt-movetothread-does-not-work-when-using-partial-for-slot
        self.main_signal.connect(self.worker.main)
        self.downloadImg.clicked.connect(self.transmit_content)

        self.retryDownload.clicked.connect(self.btn_retryDownload)

    def forceWorkerReset(self):
        if self.worker_thread.isRunning():
            self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.worker_thread.start()

    def transmit_content(self):
        content_list = [
            self.selectGallery.currentText(),
            self.editKeyword.text(),
            self.editPage.text(),
            self.onlyBy.isChecked(),
            self.onlyRcmd.isChecked(),
            '%s,%s' % (self.editExcept.text(), '프리뷰') if self.excptPreview.isChecked() else self.editExcept.text(),
            self.folderSeparate.isChecked(),
            self.editPath.text()
        ]
        
        self.main_signal.emit(content_list)

    def btn_expandTreeview(self):
        if self.is_expand: # Contract Main window size for hiding Treeview
            self.is_expand = False
            self.expandTreeview.setText("▶")
            self.setFixedSize(397, 256)
        else: # Expand Main window size for showing Treeview
            self.is_expand = True
            self.expandTreeview.setText("◀")
            self.setFixedSize(822, 577)

    def btn_retryDownload(self):
        # print('trying redownload..')
        self.forceWorkerReset()
        re_subject = []
        tr_root = self.trWidget.invisibleRootItem()
        self.statusBar.showMessage('재다운로드를 시작합니다.')

        for i in range(0, tr_root.childCount()): # Top level item
            if not tr_root.child(i).text(1) == '':
                re_subject.append([tr_root.child(i).text(0), tr_root.child(i).text(2)])
            else:
                for j in range(0, tr_root.child(i).childCount()): # Top level item's child 
                    if not tr_root.child(i).child(j).text(1) == '성공':
                        re_subject.append([tr_root.child(i).text(0), tr_root.child(i).text(2)])
                        break

        re_list = [
            re_subject,
            self.folderSeparate.isChecked(),
            self.editPath.text()
        ]

        self.main_signal.emit(re_list)

    def btn_trSelectDel(self):
        tr_root = self.trWidget.invisibleRootItem()
        for i in self.trWidget.selectedItems():
            tr_root.removeChild(i)

    def btn_resetTreeview(self):
        self.forceWorkerReset()
        self.trWidget.clear()
        self.statusBar.showMessage('다운 목록을 모두 삭제했습니다.')

    @pyqtSlot(str)
    def updateStatusBar(self, signal):
        self.statusBar.showMessage(signal)

    # Handle a bunch of events
    @pyqtSlot(list)
    def eventHandling(self, event_list):
        if event_list[0] == '1':
            self.msgbox = QMessageBox(self)
            self.msgbox.setIcon(QMessageBox.Information)
            self.msgbox.setWindowTitle('Error')

            self.msgbox.setText(event_list[1])
            self.msgbox.setInformativeText(event_list[2])
            self.msgbox.setStandardButtons(QMessageBox.Ok)

            self.msgbox.show()
            self.forceWorkerReset()
        elif event_list[0] == '2':
            self.msgbox = QMessageBox(self)
            self.msgbox.setIcon(QMessageBox.Information)
            self.msgbox.setWindowTitle('Error')

            self.msgbox.setText('예기치 못한 오류가 발생했습니다.')
            self.msgbox.setInformativeText("자세한 정보는 아래 Show Details.. 버튼을 눌러 확인해주십시요.")
            self.msgbox.setDetailedText(str(event_list[1]))
            self.msgbox.setStandardButtons(QMessageBox.Ok)

            self.msgbox.show()
            self.forceWorkerReset()
        elif event_list[0] == '3': # Update Treeview datas
            if event_list[1] == '0':
                self.treeParent = QTreeWidgetItem([event_list[2], event_list[3], event_list[4]])
                if not self.treeChild == []:
                    for i in self.treeChild:
                        self.treeParent.addChild(QTreeWidgetItem(i))
                self.trWidget.addTopLevelItem(self.treeParent)
                self.treeChild = []
            elif event_list[1] == '1':
                self.treeChild.append([event_list[2], event_list[3], event_list[4]])

    def closeEvent(self, event):
        # Save settings to INI file
        config = configparser.ConfigParser()

        config['Preset'] = {
            'gallid': self.selectGallery.currentText(),
            'keyword': self.editKeyword.text(),
            'page': self.editPage.text(),
            'by': int(self.onlyBy.isChecked()),
            'rcmd': int(self.onlyRcmd.isChecked()),
            'except': self.editExcept.text(),
            'preview': int(self.excptPreview.isChecked()),
            'sprt': int(self.folderSeparate.isChecked()),
            'path': self.editPath.text()
        }

        try:
            with open('setting.ini', "w") as f:
                config.write(f)
        except Exception as E:
            self.eventHandling(['2', E])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
    print('terminate normally')
    sys.exit()
