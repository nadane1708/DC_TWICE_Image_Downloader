import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5.QtCore import *
import dc
# from functools import partial


form_class = uic.loadUiType("./res/main.ui")[0]


class MyWindow(QMainWindow, form_class, QObject):
    main_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        # UI Setting
        self.setupUi(self)

        self.setFixedSize(361, 256) # Fix window size
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint) # Remove resizing mouse cursor

        # Worker Thread
        self.worker = dc.Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Connecting Signals
        self._connectSignals()

        '''
        # Download Button
        self.downloadImg.clicked.connect(partial(self.worker.main,
                                                    self.gallery_idx,
                                                    self.editKeyword.text(),
                                                    self.editPage.text(),
                                                    self.onlyBy.isChecked(),
                                                    self.onlyRcmd.isChecked(),
                                                    '%s,%s' % (self.editExcept.text(), '프리뷰') if self.excptPreview.isChecked() else self.editExcept.text(),
                                                    self.folderSeparate.isChecked(),
                                                    self.editPath.text()
                                                    ))
        '''

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
        self.worker.finished_err.connect(self.show_msgbox)

        # Solved parameter problem for QT connect: https://stackoverflow.com/questions/23317195/pyqt-movetothread-does-not-work-when-using-partial-for-slot
        self.main_signal.connect(self.worker.main)
        self.downloadImg.clicked.connect(self.transmit_content)

    def forceWorkerReset(self):
        if self.worker_thread.isRunning():
            self.statusBar.showMessage('다운로드를 취소하였습니다.')
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.worker_thread.start()

    def transmit_content(self):
        content_list = [self.selectGallery.currentText(),
                        self.editKeyword.text(),
                        self.editPage.text(),
                        self.onlyBy.isChecked(),
                        self.onlyRcmd.isChecked(),
                        '%s,%s' % (self.editExcept.text(), '프리뷰') if self.excptPreview.isChecked() else self.editExcept.text(),
                        self.folderSeparate.isChecked(),
                        self.editPath.text()]

        self.main_signal.emit(content_list)

    @pyqtSlot(str)
    def updateStatusBar(self, signal):
        self.statusBar.showMessage(signal)

    # Show error messagebox
    @pyqtSlot(list)
    def show_msgbox(self, err_list):

        et = err_list[0]
        er = err_list[1]
        ex = err_list[2]

        self.msgbox = QMessageBox(self)
        self.msgbox.setIcon(QMessageBox.Information)
        self.msgbox.setWindowTitle('Error')

        if et:
            self.msgbox.setText(et)
            self.msgbox.setInformativeText(er)
            self.msgbox.setStandardButtons(QMessageBox.Ok)
        else:
            self.msgbox.setText('예기치 못한 오류가 발생했습니다.')
            self.msgbox.setInformativeText("자세한 정보는 아래 Show Details.. 버튼을 눌러 확인해주십시요.")
            self.msgbox.setDetailedText(str(ex))
            self.msgbox.setStandardButtons(QMessageBox.Ok)
            
        self.msgbox.show()
        self.forceWorkerReset()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())
    
