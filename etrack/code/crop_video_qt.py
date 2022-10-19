from email.charset import QP
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sys

from crop_video import CropVideo

from IPython import embed
import matplotlib.pyplot as plt
import cv2
import numpy as np
from calibration_functions import *

# TO DO:

# layout management...

# implement option to change default frame number value?
    # same for default video file path
# toggle buttons to make different combinations of VideoTools
# add only unique files (when using the add Button)?
# maybe help text when hovering over button? (https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python)
# clean up functions.. maybe merge calibration functions with crop video or new class
# source and destination folder as QFileDialog?

# ffmpeg has to be installed...!

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()

        gl = QGridLayout()
        gl.addWidget(self.add_remove_group(), 0, 1)
        gl.addWidget(self.browse_group(), 1, 1)
        gl.addWidget(self.item_list(), 0, 0)
        gl.addWidget(self.destination_box(), 1, 0)
        gl.addWidget(self.frame_spinbox(), 0, 2, -1 ,1)
        self.setLayout(gl)        


    def item_list(self):
        
        self.display_item_list = QListWidget()
        self.display_item_list.setMaximumHeight(400)
        
        self.list_items = []
        for i in range(self.display_item_list.count()): 
            item = self.display_item_list.item(i).text()
            if item not in self.list_items:
                self.list_items.append(self.display_item_list.item(i).text())
        
        return self.display_item_list


    def add_remove_group(self):
        groupBox = QGroupBox()

        addButton = QPushButton('add')
        addButton.clicked.connect(self.open_file)

        removeButton = QPushButton('remove')
        removeButton.clicked.connect(self.remove_file)
        
        vbox = QVBoxLayout()
        vbox.addWidget(addButton)
        vbox.addWidget(removeButton)

        groupBox.setLayout(vbox)

        return groupBox


    def open_file(self):
        fileName = QFileDialog.getOpenFileNames(self, str("Select Video Files"), "/home/student/etrack/videos", str('Video Files(*.mp4)'))
        self.display_item_list.addItems(fileName[0])
        # each file unique?
        
             
    def remove_file(self):
        listItems = self.display_item_list.selectedItems()
        if not listItems:
            return        
        for item in listItems:
            self.display_item_list.takeItem(self.display_item_list.row(item))


    def destination_box(self):
        self.destination = QListWidget()
        self.destination.setFixedHeight(30)
        return self.destination


    def browse_group(self):
        groupBox = QGroupBox()
        browseButton = QPushButton('browse')
        browseButton.setFixedHeight(30)
        
        self.destination_list = []
        
        browseButton.clicked.connect(self.browse_file)
        
        vbox = QVBoxLayout()
        vbox.addWidget(browseButton)
        groupBox.setLayout(vbox)
     
        return groupBox


    def browse_file(self):
        self.path = str(QFileDialog.getExistingDirectory(self, "Select Directory", '/home/student/etrack/cropped_videos'))
        self.destination.addItem(self.path)
        if len(self.destination) > 1:
            self.destination.clear()
            self.destination.addItem(self.path)
        return self.path        


    def frame_spinbox(self):
        groupBox = QGroupBox()

        frame_spinbox = QSpinBox()
        frame_spinbox.setValue(10)
        
        print("current value:"+str(frame_spinbox.value()))
        self.spinbox_value = frame_spinbox.value()

        vbox = QVBoxLayout()
        vbox.addWidget(frame_spinbox)
        groupBox.setLayout(vbox)

        return groupBox


    def spinbox_value(self):
        return self.frame_spinbox.value()


class VideoTools(QWidget):
    
    def __init__(self, file_selector: FileSelector):
        super().__init__()
        
        self.file_selector = file_selector
        
        # how to define them for the whole class?
        self.frame_number = self.file_selector.spinbox_value
        self.file_list = self.file_selector.item_list
        

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


    def mark_crop_positions(self):  # set marker for first (!) video, used for all following videos    
        self.crop_positions = CropVideo.parser_mark_crop_positions(self.file_list[0], self.frame_number)


    def plot_frame(self):   # check how croppping for the different videos would look like
        self.cropped_frame_list = []
        embed()
        quit()
        for file in self.file_list:
            cropped_frame = CropVideo.parser_plot_frame(file, self.frame_number, self.crop_positions)
            self.cropped_frame_list.append(cropped_frame)

        # source: https://engineeringfordatascience.com/posts/matplotlib_subplots/
        ncols = 3
        nrows = len(self.cropped_frame_list) // ncols + (len(self.cropped_frame_list) % ncols > 0)  # self adjusting row number depending on number of videos

        plt.subplots_adjust(hspace=0.3)
        plt.suptitle("plot frame of videos, frame number = %i" % self.frame_number, fontsize=12)
        
        for n, (frame, filename) in enumerate(zip(self.cropped_frame_list, self.file_list)):
            ax = plt.subplot(nrows, ncols, n + 1)   # add subplot for each video/frame
          
            ax.imshow(frame)    # plot frame
          
            filename = filename.split('/')[-1]
            ax.set_title(filename, fontsize=11)
        plt.show()
        

    def crop_video(self):
        print('crop video')

        # file list empty..
        
        for file in self.file_list:
            marker_crop_positions = CropVideo.parser_mark_crop_positions(file, self.frame_number)
            
            bottom_left_x, bottom_left_y, bottom_right_x, bottom_right_y, top_left_x, top_left_y, top_right_x, top_right_y = assign_marker_positions(marker_crop_positions)
            result = CropVideo.parser_cut_out_video_parser(file, str(self.destination.item(0).text()), (bottom_left_x, bottom_left_y), (top_right_x, top_right_y))  
            print(self.file_list)

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
    
        layout = QGridLayout()
        layout.addWidget(self.fs,)
        layout.addWidget(self.vt)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()