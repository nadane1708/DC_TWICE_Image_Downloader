import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5.QtCore import *
from functools import partial
import dc

form_class = uic.loadUiType("main.ui")[0]


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

        # Variable
        self.gallery_idx = 0

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

        # ComboBox
        self.selectGallery.currentIndexChanged.connect(self.selectionChanged)

        # PushButton
        self.openPath.clicked.connect(self.btn_openpath)

        # StatusBar
        self.statusBar = QStatusBar(self)
        self.statusBar.setSizeGripEnabled(False) # Remove resizing grip of status bar
        self.setStatusBar(self.statusBar)

    def selectionChanged(self):
        self.gallery_idx = self.selectGallery.currentIndex()

    def btn_openpath(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.editPath.setText('%s\\' % os.path.normpath(fname)) # os.path.normpath(path) --> Change "/" to "\" on Windows OS

    def _connectSignals(self):
        self.worker.finished.connect(self.updateStatusBar)
        self.downloadCancel.clicked.connect(self.forceWorkerReset)

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
        content_list = [self.gallery_idx,
                        self.editKeyword.text(),
                        self.editPage.text(),
                        self.onlyBy.isChecked(),
                        self.onlyRcmd.isChecked(),
                        '%s,%s' % (self.editExcept.text(), '프리뷰') if self.excptPreview.isChecked() else self.editExcept.text(),
                        self.folderSeparate.isChecked(),
                        self.editPath.text()
                        ]

        self.main_signal.emit(content_list)

    @pyqtSlot(str)
    def updateStatusBar(self, signal):
        self.statusBar.showMessage(signal)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())
