import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import dc
import blog_news
import sns
import configparser


form_class = uic.loadUiType("./res/main.ui")[0]
        
class MyWindow(QMainWindow, form_class, QObject):
    main_signal = pyqtSignal(list)
    re_main_signal = pyqtSignal(list)
    nati_main_signal = pyqtSignal(list)
    sns_main_signal = pyqtSignal(list)
    sns_main_signal_2 = pyqtSignal(list)
    sns_main_signal_3 = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        # UI Setting
        self.setupUi(self)

        self.setFixedSize(822, 602) # Fix window size
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint) # Remove resizing mouse cursor

        # Quit setting
        self.quit = QAction("Quit", self)
        self.quit.triggered.connect(self.closeEvent)

        # Worker Thread
        self.worker = dc.Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.reworker = dc.retryWorker()
        self.reworker_thread = QThread()
        self.reworker.moveToThread(self.reworker_thread)

        self.natiworker = blog_news.Worker()
        self.natiworker_thread = QThread()
        self.natiworker.moveToThread(self.natiworker_thread)

        self.snsworker = sns.Worker()
        self.snsworker_thread = QThread()
        self.snsworker.moveToThread(self.snsworker_thread)

        self.snsworker_2 = sns.Worker_2()
        self.snsworker_thread_2 = QThread()
        self.snsworker_2.moveToThread(self.snsworker_thread_2)

        self.snsworker_3 = sns.Worker_3()
        self.snsworker_thread_3 = QThread()
        self.snsworker_3.moveToThread(self.snsworker_thread_3)

        # Connecting Signals
        self._connectSignals()

        # Set QCombBox Completer for Disabling Auto-Completion
        self.completer = QCompleter(self)
        self.selectGallery.setCompleter(self.completer)

        # ComboBox
        self.selectGallery.setEditText('twice_new')
        self.selectGallery.activated.connect(self.selectionChanged)

        # PushButton
        self.openPath.clicked.connect(self.btn_openpath)
        self.openPath_2.clicked.connect(self.btn_openpath_2)
        self.insta_allOpenPath.clicked.connect(self.btn_openpath_SNS_1)
        self.twitt_allOpenPath.clicked.connect(self.btn_openpath_SNS_2)
        self.insta_segOpenPath.clicked.connect(self.btn_openpath_SNS_3)

        # StatusBar
        self.statusBar = QStatusBar(self)
        self.statusBar.setSizeGripEnabled(False) # Remove resizing grip of status bar
        self.setStatusBar(self.statusBar)

        # Download Status Treeview
        self.is_expand = False
        self.treeChild = []
        self.treeParent = QTreeWidgetItem()

        self.tr_selectDel.clicked.connect(self.btn_trSelectDel)
        self.resetTreeview.clicked.connect(self.btn_resetTreeview)

        self.trWidget = QTreeWidget(self.treeView)
        self.trWidget.setColumnCount(2)
        self.trWidget.setHeaderLabels(['글제목(파일명)', '다운 상태', '주소'])
        self.trWidget.setColumnWidth(0, 340)
        self.trWidget.setColumnWidth(1, 70)
        self.trWidget.resize(411, 511)
        self.trWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.treeChild_2 = []
        self.treeParent_2 = QTreeWidgetItem()

        self.tr_selectDel_2.clicked.connect(self.btn_trSelectDel_2)
        self.resetTreeview_2.clicked.connect(self.btn_resetTreeview_2)

        self.trWidget_2 = QTreeWidget(self.treeView_2)
        self.trWidget_2.setColumnCount(2)
        self.trWidget_2.setHeaderLabels(['글제목(파일명)', '다운 상태', '주소'])
        self.trWidget_2.setColumnWidth(0, 340)
        self.trWidget_2.setColumnWidth(1, 70)
        self.trWidget_2.resize(411, 511)
        self.trWidget_2.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # DC Gallery Download Image Preview
        self.dc_imgPreview.resize(351, 281)
        dc_pixmap = QPixmap('./res/icon.png')
        dc_pixmap = dc_pixmap.scaledToHeight(281)
        self.dc_imgPreview.setPixmap(dc_pixmap)

        # Instagram Download Image Preview
        self.insta_imgPreview.resize(375, 341)

        # Load settings from INI file
        parser = configparser.ConfigParser()
        if parser.read('setting.ini') == []:
            pass
        else:
            try:
                self.selectGallery.setEditText(parser.get('Preset', 'gallid'))
                self.editPage.setText(parser.get('Preset', 'page'))
                self.editKeyword.setText(parser.get('Preset', 'keyword'))
                self.onlyBy.setChecked(bool(int(parser.get('Preset', 'by'))))
                self.onlyRcmd.setChecked(bool(int(parser.get('Preset', 'rcmd'))))
                self.editSubject.setText(parser.get('Preset', 'subject'))
                self.editExcept.setText(parser.get('Preset', 'except'))
                self.excptPreview.setChecked(bool(int(parser.get('Preset', 'preview'))))
                self.folderSeparate.setChecked(bool(int(parser.get('Preset', 'sprt'))))
                self.editPath.setText(parser.get('Preset', 'path'))
                self.folderSeparate_2.setChecked(bool(int(parser.get('Preset', 'sprt_2'))))
                self.editPath_2.setText(parser.get('Preset', 'path_2'))
                self.insta_allFolderSeparate.setChecked(bool(int(parser.get('Preset', 'sprt_3'))))
                self.insta_allEditPath.setText(parser.get('Preset', 'path_3'))
                self.twitt_allFolderSeparate.setChecked(bool(int(parser.get('Preset', 'sprt_4'))))
                self.twitt_allEditPath.setText(parser.get('Preset', 'path_4'))
                self.insta_segFolderSeparate.setChecked(bool(int(parser.get('Preset', 'sprt_5'))))
                self.insta_segEditPath.setText(parser.get('Preset', 'path_5'))
            except Exception as E:
                self.eventHandling(['2', E])

    def selectionChanged(self):
        _gall_id = ['twice_new', 'twice', 'twicetv', 'nayeone', 'jungyeon', 'momo', 'sanarang', 'jihyo', 'twicemina', 'dahyeon', 'sonchaeyoung', 'tzuyu0614', 'streaming']

        self.selectGallery.setEditText(_gall_id[self.selectGallery.currentIndex()])

    def btn_openpath(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.editPath.setText('%s\\' % os.path.normpath(fname)) # os.path.normpath(path) --> Change "/" to "\" on Windows OS

    def btn_openpath_2(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.editPath_2.setText('%s\\' % os.path.normpath(fname)) # os.path.normpath(path) --> Change "/" to "\" on Windows OS

    def btn_openpath_SNS_1(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.insta_allEditPath.setText('%s\\' % os.path.normpath(fname))

    def btn_openpath_SNS_2(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.twitt_allEditPath.setText('%s\\' % os.path.normpath(fname))

    def btn_openpath_SNS_3(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.insta_segEditPath.setText('%s\\' % os.path.normpath(fname))

    def _connectSignals(self):
        
        self.downloadCancel.clicked.connect(self.forceWorkerReset)
        self.downloadCancel_2.clicked.connect(self.forceWorkerReset)
        self.insta_allCancel.clicked.connect(self.forceWorkerReset)
        self.twitt_allCancel.clicked.connect(self.forceWorkerReset)
        self.insta_segCancel.clicked.connect(self.forceWorkerReset)

        # Connect worker's pyqtSignal to pyqtSlot
        self.worker.finished.connect(self.updateStatusBar)
        self.worker.finished_err.connect(self.eventHandling)

        self.reworker.finished.connect(self.updateStatusBar)
        self.reworker.finished_err.connect(self.eventHandling)

        self.natiworker.finished.connect(self.updateStatusBar)
        self.natiworker.finished_err.connect(self.eventHandling)

        self.snsworker.finished.connect(self.updateStatusBar)
        self.snsworker.finished_err.connect(self.eventHandling)

        self.snsworker_2.finished.connect(self.updateStatusBar)
        self.snsworker_2.finished_err.connect(self.eventHandling)

        self.snsworker_3.finished.connect(self.updateStatusBar)
        self.snsworker_3.finished_err.connect(self.eventHandling)

        # Solved parameter problem for QT connect: https://stackoverflow.com/questions/23317195/pyqt-movetothread-does-not-work-when-using-partial-for-slot
        self.main_signal.connect(self.worker.main)
        self.downloadImg.clicked.connect(self.transmit_content)

        self.re_main_signal.connect(self.reworker.main)
        self.retryDownload.clicked.connect(self.btn_retryDownload)

        self.nati_main_signal.connect(self.natiworker.main)
        self.downloadImg_2.clicked.connect(self.btn_downloadImg_2)

        self.sns_main_signal.connect(self.snsworker.main)
        self.insta_allDownload.clicked.connect(self.btn_downloadSNS_1)

        self.sns_main_signal_2.connect(self.snsworker_2.main)
        self.twitt_allDownload.clicked.connect(self.btn_downloadSNS_2)

        self.sns_main_signal_3.connect(self.snsworker_3.main)
        self.insta_segDownload.clicked.connect(self.btn_downloadSNS_3)

    def forceWorkerReset(self, var=False):
        status = True
        if var:
            status = False

        # Reset treeview child items
        self.treeChild = []
        self.treeChild_2 = []

        if self.worker_thread.isRunning():
            if status:
                self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.worker_thread.terminate()
            self.worker_thread.wait()

        if self.reworker_thread.isRunning():
            if status:
                self.statusBar.showMessage('재다운로드를 취소하였습니다.')
            self.reworker_thread.terminate()
            self.reworker_thread.wait()

        if self.natiworker_thread.isRunning():
            if status:
                self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.natiworker_thread.terminate()
            self.natiworker_thread.wait()

        if self.snsworker_thread.isRunning():
            if status:
                self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.snsworker_thread.terminate()
            self.snsworker_thread.wait()

        if self.snsworker_thread_2.isRunning():
            if status:
                self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.snsworker_thread_2.terminate()
            self.snsworker_thread_2.wait()

        if self.snsworker_thread_3.isRunning():
            if status:
                self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.snsworker_thread_3.terminate()
            self.snsworker_thread_3.wait()

    def transmit_content(self):
        self.forceWorkerReset(True)
        self.worker_thread.start()

        content_list = [
            self.selectGallery.currentText(),
            self.editKeyword.text(),
            self.editPage.text(),
            self.onlyBy.isChecked(),
            self.onlyRcmd.isChecked(),
            self.editSubject.text(),
            '%s,%s' % (self.editExcept.text(), '프리뷰') if self.excptPreview.isChecked() else self.editExcept.text(),
            self.folderSeparate.isChecked(),
            self.editPath.text()
        ]
        
        self.main_signal.emit(content_list)

    def btn_retryDownload(self):
        self.forceWorkerReset(True)
        self.reworker_thread.start()

        re_subject = []
        tr_root = self.trWidget.invisibleRootItem()

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

        self.re_main_signal.emit(re_list)

    def btn_downloadImg_2(self):
        self.forceWorkerReset(True)
        self.natiworker_thread.start()

        nati_list = [
            self.nati_url.toPlainText(),
            self.folderSeparate_2.isChecked(),
            self.editPath_2.text()
        ]

        self.nati_main_signal.emit(nati_list)

    def btn_trSelectDel(self):
        tr_root = self.trWidget.invisibleRootItem()
        for i in self.trWidget.selectedItems():
            tr_root.removeChild(i)

    def btn_resetTreeview(self):
        self.forceWorkerReset(True)
        self.trWidget.clear()
        self.statusBar.showMessage('다운 목록을 모두 삭제했습니다.')

    def btn_trSelectDel_2(self):
        tr_root = self.trWidget_2.invisibleRootItem()
        for i in self.trWidget_2.selectedItems():
            tr_root.removeChild(i)

    def btn_resetTreeview_2(self):
        self.forceWorkerReset(True)
        self.trWidget_2.clear()
        self.statusBar.showMessage('다운 목록을 모두 삭제했습니다.')

    def btn_downloadSNS_1(self):
        self.forceWorkerReset(True)
        self.snsworker_thread.start()

        sns_list = [
            self.insta_userID.text(),
            self.insta_allFolderSeparate.isChecked(),
            self.insta_allEditPath.text()
        ]

        self.sns_main_signal.emit(sns_list)

    def btn_downloadSNS_2(self):
        self.forceWorkerReset(True)
        self.snsworker_thread_2.start()

        sns_list = [
            self.twitt_userID.text(),
            self.twitt_allRetweet.isChecked(),
            self.twitt_allFolderSeparate.isChecked(),
            self.twitt_allEditPath.text()
        ]

        self.sns_main_signal_2.emit(sns_list)

    def btn_downloadSNS_3(self):
        self.forceWorkerReset(True)
        self.snsworker_thread_3.start()

        sns_list = [
            self.insta_url.toPlainText(),
            self.insta_segFolderSeparate.isChecked(),
            self.insta_segEditPath.text()
        ]

        self.sns_main_signal_3.emit(sns_list)

    @pyqtSlot(str)
    def updateStatusBar(self, signal):
        self.statusBar.showMessage(signal)
        if '다운로드 작업을 완료하였습니다.' in signal:
            self.forceWorkerReset(True)

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
                self.treeParent = QTreeWidgetItem([event_list[2], event_list[3], event_list[4], event_list[5]])
                if '실패' in event_list[3]:
                        self.treeParent.setBackground(1, QColor('yellow')) # Set background color to yellow when page loading failed
                if not self.treeChild == []:
                    for i in self.treeChild:
                        self.treeParent.addChild(QTreeWidgetItem(i))
                        if '실패' in i[1]:
                            self.treeParent.setBackground(1, QColor('yellow')) # Set background color to yellow when image loading failed
                if not event_list[5] is None:
                    self.treeParent.setToolTip(0, event_list[5]) # Set tooltips for previewing texts of the posts
                self.trWidget.addTopLevelItem(self.treeParent)
                self.treeChild = []
            elif event_list[1] == '1':
                if not event_list[5] is None:
                    dc_pixmap = QPixmap()
                    dc_pixmap.loadFromData(event_list[5])
                    dc_pixmap = dc_pixmap.scaledToHeight(281)
                    self.dc_imgPreview.setPixmap(dc_pixmap)
                self.treeChild.append([event_list[2], event_list[3], event_list[4]])
        elif event_list[0] == '4': # Update Treeview datas for blog / news download
            if event_list[1] == '0':
                self.treeParent_2 = QTreeWidgetItem([event_list[2], event_list[3], event_list[4]])
                if '실패' in event_list[3]:
                        self.treeParent_2.setBackground(1, QColor('yellow'))
                if not self.treeChild_2 == []:
                    for i in self.treeChild_2:
                        if '실패' in i[1]:
                            self.treeParent_2.setBackground(1, QColor('yellow'))
                        self.treeParent_2.addChild(QTreeWidgetItem(i))
                self.trWidget_2.addTopLevelItem(self.treeParent_2)
                self.treeChild_2 = []
            elif event_list[1] == '1':
                self.treeChild_2.append([event_list[2], event_list[3], event_list[4]])
        elif event_list[0] == '5': # Update Instagram / Twitter download datas
            sns_pixmap = QPixmap()
            sns_pixmap.loadFromData(event_list[1])
            sns_pixmap = sns_pixmap.scaledToHeight(341)
            self.insta_imgPreview.setPixmap(sns_pixmap)

    def closeEvent(self, event):
        # Save settings to INI file
        config = configparser.ConfigParser()

        config['Preset'] = {
            'gallid': self.selectGallery.currentText(),
            'keyword': self.editKeyword.text(),
            'page': self.editPage.text(),
            'by': int(self.onlyBy.isChecked()),
            'rcmd': int(self.onlyRcmd.isChecked()),
            'subject': self.editSubject.text(),
            'except': self.editExcept.text(),
            'preview': int(self.excptPreview.isChecked()),
            'sprt': int(self.folderSeparate.isChecked()),
            'path': self.editPath.text(),
            'sprt_2': int(self.folderSeparate_2.isChecked()),
            'path_2': self.editPath_2.text(),
            'sprt_3': int(self.insta_allFolderSeparate.isChecked()),
            'path_3': self.insta_allEditPath.text(),
            'retwt': int(self.twitt_allRetweet.isChecked()),
            'sprt_4': int(self.twitt_allFolderSeparate.isChecked()),
            'path_4': self.twitt_allEditPath.text(),
            'sprt_5': int(self.insta_segFolderSeparate.isChecked()),
            'path_5': self.insta_segEditPath.text()
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
    
