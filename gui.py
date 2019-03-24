import os
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5.QtCore import *
import dc

form_class = uic.loadUiType("gui.ui")[0]


class MyWindow(QMainWindow, form_class, QObject):
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

        self._connectSignals()

        # Variable
        self.gallery_idx = 0

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
        self.downloadImg.clicked.connect(lambda: self.worker.main(self.gallery_idx,
                                                                        self.editKeyword.text(),
                                                                        self.editPage.text(),
                                                                        self.onlyBy.isChecked(),
                                                                        self.onlyRcmd.isChecked(),
                                                                        '%s,%s' % (self.editExcept.text(), '프리뷰') if self.excptPreview.isChecked() else self.editExcept.text(),
                                                                        self.folderSeparate.isChecked(),
                                                                        self.editPath.text()
                                                                        ))
        self.worker.finished.connect(self.updateStatusBar)
        self.downloadCancel.clicked.connect(self.forceWorkerReset)

    def forceWorkerReset(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.worker_thread.start()

    @pyqtSlot(str)
    def updateStatusBar(self, signal):
        self.statusBar.showMessage(signal)
