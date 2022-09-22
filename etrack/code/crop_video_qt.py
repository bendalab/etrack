from email.charset import QP
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys

from crop_video import CropVideo

from IPython import embed
import matplotlib.pyplot as plt
import cv2
import numpy as np

# TO DO:

# implement option to change default frame number value?
    # same for default video file path
# toggle buttons to make different combinations of VideoTools
# add only unique files (when using the add Button)?
# maybe help text when hovering over button? (https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python)


class FileSelector(QWidget):

    def __init__(self):
        super().__init__()

        hl = QHBoxLayout()
        vl = QVBoxLayout()
        
        self._display_file_list = QListWidget()
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
        
        hl.addWidget(self._display_file_list)
        hl.addWidget(group)
        hl.addWidget(self.frame_spinbox)
        self.setLayout(hl)
    

    def _open_file(self):
        fileName = QFileDialog.getOpenFileNames(self, str("Select Video Files"), "/home/student/etrack/videos", str('Video Files(*.mp4)'))
        print(fileName[0], type(fileName[0]))
        self._display_file_list.addItems(fileName[0])
        
        # each file unique?:
        
        # self._fileName_new = []
        # for f in fileName[0]:
        #     if f not in self._fileName_new:
        #         self._fileName_new.append(f)
        
        # def _refresh_file(self): # improvised...
        #     self._display_file_list.addItems(self._fileName_new)
        
             
    def _remove_file(self):
        print('remove File')

        listItems = self._display_file_list.selectedItems()
        if not listItems:
            return        
        for item in listItems:
            self._display_file_list.takeItem(self._display_file_list.row(item))
    
    def _frame_spinbox_value(self):
        print("current value:"+str(self.frame_spinbox.value()))
        self._spinbox_value = self.frame_spinbox.value()
    
    def item_list(self):
        self._file_list = []
        for i in range(self._display_file_list.count()): 
            item = self._display_file_list.item(i).text()
            if item not in self._file_list:
                self._file_list.append(self._display_file_list.item(i).text())
        
        return self._file_list
    
    def spinbox_value(self):
        return self.frame_spinbox.value()


class VideoTools(QWidget):
    
    def __init__(self, file_selector: FileSelector):
        super().__init__()
        
        self.file_selector = file_selector
        
        hl = QHBoxLayout()
        
        mark_crop_positions_btn = QPushButton('mark crop positions')
        mark_crop_positions_btn.clicked.connect(self.mark_crop_positions)

        plot_btn = QPushButton('plot frame')
        # plot_btn.setCheckable(True)
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

    def mark_crop_positions(self):  # theoretically markers only needed for first video
        self.frame_number = self.file_selector.spinbox_value()
        self.file_list = self.file_selector.item_list()
        self.crop_positions = CropVideo.parser_mark_crop_positions(self.file_list[0], self.frame_number)
            
    def plot_frame(self):
        self.cropped_frame_list = []
        for file in self.file_list:
            cropped_frame = CropVideo.parser_plot_frame(file, self.frame_number, self.crop_positions)
            self.cropped_frame_list.append(cropped_frame)

        # source: https://engineeringfordatascience.com/posts/matplotlib_subplots/
        ncols = 3
        # calculate number of rows
        nrows = len(self.cropped_frame_list) // ncols + (len(self.cropped_frame_list) % ncols > 0)

        plt.subplots_adjust(hspace=0.3)
        plt.suptitle("plot frame of videos, frame number = %i" % self.frame_number, fontsize=12)
        
        for n, (frame, filename) in enumerate(zip(self.cropped_frame_list, self.file_list)):
            # add a new subplot iteratively using nrows and cols
            ax = plt.subplot(nrows, ncols, n + 1)
          
            filename = filename.split('/')[-1]
            ax.imshow(frame)
            ax.set_title(filename, fontsize=11)

        plt.show()
        
    def crop_video(self):
        print('crop video')
    
    def print_parameter(self):
        print('print parameter')
    
    def set_crop_parameter(self):
        print('set crop parameter')
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("etrack app")
        
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