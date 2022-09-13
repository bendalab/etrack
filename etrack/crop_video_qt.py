from email.charset import QP
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys

from crop_video import CropVideo as cv

# TO DO:

# implement option to change default frame number value?
    # same for default video file path
# toggle buttons to make different combinations of VideoTools


class FileSelector(QWidget):

    def __init__(self):
        super(FileSelector, self).__init__()

        hl = QHBoxLayout()
        vl = QVBoxLayout()
        
        self._fileList = QListWidget()
        group = QGroupBox()
        
        addButton = QPushButton('add')
        addButton.clicked.connect(self._openFile)

        removeButton = QPushButton('remove')
        removeButton.clicked.connect(self._removeFile)

        self.frameSpinBox = QSpinBox()
        self.frameSpinBox.setValue(10)
        self.frameSpinBox.valueChanged.connect(self.frameSpinBoxValue)
        
        vl.addWidget(addButton)
        vl.addWidget(removeButton)
        group.setLayout(vl)
        
        hl.addWidget(self._fileList)
        hl.addWidget(group)
        hl.addWidget(self.frameSpinBox)
        self.setLayout(hl)


    def _openFile(self):
        fileName = QFileDialog.getOpenFileName(self, str("Select Video File"), "/home/efish/etrack", str('Video Files(*.mp4)'))
        print(fileName)
        self._fileList.addItem(fileName)
        itemList = self._fileList.selectedItems()
        return itemList

    def _removeFile(self):
        print('remove File')

        listItems = self._fileList.selectedItems()
        if not listItems:
            return        
        for item in listItems:
            self._fileList.takeItem(self._fileList.row(item))
    

    def frameSpinBoxValue(self):
        print("current value:"+str(self.frameSpinBox.value()))
        value = self.frameSpinBox.value()
        return value


class VideoTools(QWidget):
    
    def __init__(self):
        super(VideoTools, self).__init__()


        hl = QHBoxLayout()

        plotButton = QPushButton('plot frame')
        plotButton.clicked.connect(self._plotFrame)
        cropButton = QPushButton('crop video')
        cropButton.clicked.connect(self._cropVideo)
        parameterButton = QPushButton('print parameter')
        parameterButton.clicked.connect(self._printParameter)
        setcropButton = QPushButton('set crop parameter')
        setcropButton.clicked.connect(self._setcropParameter)

        hl.addWidget(plotButton)
        hl.addWidget(cropButton)
        hl.addWidget(parameterButton)
        hl.addWidget(setcropButton)

        self.setLayout(hl)

    def _plotFrame(self, ):
        print('plot frame')
        # get marker positions
        cv.plot_frame(itemList, args.frame, marker_crop_positions)

    def _cropVideo(self):
        print('crop video')
    
    def _printParameter(self):
        print('print parameter')
    
    def _setcropParameter(self):
        print('set crop parameter')
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        
        self.fs = FileSelector()
        self.vt = VideoTools()

        layout = QVBoxLayout()
        layout.addWidget(self.fs)
        layout.addWidget(self.vt)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()