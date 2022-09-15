from email.charset import QP
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys

from crop_video import CropVideo as cv

from IPython import embed

# TO DO:

# implement option to change default frame number value?
    # same for default video file path
# toggle buttons to make different combinations of VideoTools
# add only unique files (when using the add Button)?


class FileSelector(QWidget):

    def __init__(self):
        super().__init__()

        self._open_file
        self._frame_spinbox_value

        hl = QHBoxLayout()
        vl = QVBoxLayout()
        
        self._file_list = QListWidget()
        group = QGroupBox()
        
        addButton = QPushButton('add')
        addButton.clicked.connect(self._open_file)

        removeButton = QPushButton('remove')
        removeButton.clicked.connect(self._remove_file)

        self.frame_spinbox = QSpinBox()
        self.frame_spinbox.setValue(10)
        self.frame_spinbox.valueChanged.connect(self._frame_spinbox_value)
        
        vl.addWidget(addButton)
        vl.addWidget(removeButton)
        group.setLayout(vl)
        
        hl.addWidget(self._file_list)
        hl.addWidget(group)
        hl.addWidget(self.frame_spinbox)
        self.setLayout(hl)
    
    def item_list(self):
        # PROBLEM: QListWidget items not really accessable, how do I get it raw?
        return self._file_list.selectedItems()
    
    def spinbox_value(self):
        return self.frame_spinbox.value()

    def _open_file(self):
        fileName = QFileDialog.getOpenFileNames(self, str("Select Video File"), "/home/efish/etrack", str('Video Files(*.mp4)'))
        print(fileName)
        self._file_list.addItems(fileName[0])
        # add only unique files?
        

    def _remove_file(self):
        print('remove File')

        listItems = self._file_list.selectedItems()
        if not listItems:
            return        
        for item in listItems:
            self._file_list.takeItem(self._file_list.row(item))
    

    def _frame_spinbox_value(self):
        print("current value:"+str(self.frame_spinbox.value()))
        self._spinbox_value = self.frame_spinbox.value()
    

class VideoTools(QWidget):
    
    def __init__(self, file_selector: FileSelector):
        super().__init__()
        
        self.file_selector = file_selector
        
        hl = QHBoxLayout()

        mark_crop_positions_btn = QPushButton('mark crop positions')
        mark_crop_positions_btn.clicked.connect(self.mark_crop_positions)

        plot_btn = QPushButton('plot frame')
        plot_btn.setCheckable(True)
        plot_btn.clicked.connect(self.plot_frame)

        crop_btn = QPushButton('crop video')
        crop_btn.clicked.connect(self.crop_video)
        
        parameter_btn = QPushButton('print parameter')
        parameter_btn.clicked.connect(self.print_parameter)
        
        set_crop_btn = QPushButton('set crop parameter')
        set_crop_btn.clicked.connect(self.set_crop_parameter)

        hl.addWidget(mark_crop_positions_btn)
        hl.addWidget(plot_btn)
        hl.addWidget(crop_btn)
        hl.addWidget(parameter_btn)
        hl.addWidget(set_crop_btn)

        self.setLayout(hl)

    def mark_crop_positions(self):
        frame_number = self.file_selector.spinbox_value()
        file_list = self.file_selector.item_list()
        for file in file_list:
            self.marker_crop_positions = cv.mark_crop_positions(self, file, frame_number)
        embed()
        quit()

        pass

    def plot_frame(self):
        print('plot frame')
        # get marker positions
        

    def crop_video(self):
        print('crop video')
    
    def print_parameter(self):
        print('print parameter')
    
    def set_crop_parameter(self):
        print('set crop parameter')
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        
        self.fs = FileSelector()
        self.vt = VideoTools(self.fs)

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