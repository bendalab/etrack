# from types import NoneType
import matplotlib.pyplot as plt 
import numpy as np
import glob
import os
import math
import argparse
import pprint
from ffmpy import FFmpeg
from IPython import embed
from calibration_functions import *


class CropVideo():
    
    def __init__(self, file_name) -> None: 
        super().__init__()

        self._file_name = file_name
        self.mark_crop_positions
        self.cut_out_video
        self.plot_frame
        self.crop_frame


    def mark_crop_positions(self, file_name, frame_number):
        
        task = MarkerTask("crop area", ["bottom left corner", "top left corner", "top right corner", "bottom right corner"], "Mark crop area")
        im = ImageMarker([task])
        
        marker_crop_positions = im.mark_movie(file_name, frame_number)
        plt.close()

        # np.save('marker_crop_positions', marker_crop_positions)
        return marker_crop_positions

 
    def cut_out_video(self, video_path: str, output_dir: str, start_pix: tuple, size: tuple):
        ext = os.path.basename(video_path).strip().split('.')[-1]
        print(ext)
        
        output_path = video_path.split('/')[-1].split('.')[:-1]
        output_path = '.'.join(output_path)
        print(output_path)
        
        if ext not in ['mp4', 'avi', 'flv']:
            raise Exception('format error')
        result = os.path.join(output_dir, '{}_out.{}'.format(output_path, ext))
        
        ff = FFmpeg(inputs={video_path: None},
                    outputs={result: f'-y -filter:v crop={size[0]-start_pix[0]}:{start_pix[1] - size[1]}:{start_pix[0]}:{size[1]}'}) 
                        # crop=out_w:out_h:x:y
        ff.run()
        # embed()
        # quit()
        return result
    

    def crop_frame(self, frame, marker_crop_positions):

        # load the four marker positions 
        bottom_left_x, bottom_left_y, bottom_right_x, bottom_right_y, top_left_x, top_left_y, top_right_x, top_right_y = assign_marker_positions(marker_crop_positions)

        # define boundaries of frame, taken by average of points on same line but slightly different pixel values
        left_bound = int(np.mean([bottom_left_x, top_left_x]))
        right_bound = int(np.mean([bottom_right_x, top_right_x]))
        top_bound = int(np.mean([top_left_y, top_right_y]))
        bottom_bound = int(np.mean([bottom_left_y, bottom_right_y]))
        
        # crop the frame by boundary values
        cropped_frame = frame[top_bound:bottom_bound, left_bound:right_bound]
        # cropped_frame = np.mean(cropped_frame, axis=2)    # mean over 3rd dimension (RGB/color values)

        return cropped_frame


    def plot_frame(self, filename, frame_number, marker_crop_positions):
        if not os.path.exists(filename):
            raise IOError("file %s does not exist!" % filename)
        video = cv2.VideoCapture()
        video.open(filename)
        frame_counter = 0
        success = True
        frame = None
        while success and frame_counter <= frame_number:    # iterating until frame_counter == frame_number --> success (True)
            print("Reading frame: %i" % frame_counter, end="\r")
            success, frame = video.read()
            frame_counter += 1
        if success:
            cropped_frame = cv.crop_frame(frame, marker_crop_positions)  
            
            fig, ax = plt.subplots()
            ax.imshow(cropped_frame)    # plot wanted frame of video
        else:
           print("Could not read frame number %i either failed to open movie or beyond maximum frame number!" % frame_number)
           return []
        plt.title(filename)
        plt.show(block=True)
        
        return filename


if __name__ == "__main__":    
    
    parser = argparse.ArgumentParser(description='Crop video to wanted pixel parameters', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-pf', '--plot_frame', action='store_true', help='crop interface for first video, afterwards plot a wanted frame of each video to check cropping parameters; can be combined with crop_videos')
    parser.add_argument('-cv', '--crop_video', action='store_true', help='set cropping parameters manually for each video via interface; can be combined with plot_frame')
    parser.add_argument('-d', '--destination', type=str, metavar='', help='destination folder for cropped videos', default='/home/efish/etrack/cropped_videos/')
    parser.add_argument('-s', '--source', type=str, metavar='', help='source folder for videos', default='/home/efish/etrack/videos/*')
    parser.add_argument('-f', '--frame', type=int, metavar='', help='frame number to plot', default=10)
    parser.add_argument('-pp', '--print_parameter', type=str, metavar='', help='print cropping parameters, path of wanted video as input') #, default='/home/efish/etrack/videos/2022.03.28_5.mp4')
    parser.add_argument('-scp', '--set_crop_parameter', type=int, metavar='', help='type in cropping values manually, needed parameters for manual cropping (use same input shape):\n bottom_left_x bottom_left_y top_right_x top_right_y', nargs=4)
    args = parser.parse_args()
    
    for enu, file_name in enumerate(sorted(glob.glob(args.source))):
        print(file_name)
        cv = CropVideo(file_name)
   
        if args.print_parameter != None:
            marker_crop_positions = cv.mark_crop_positions(args.print_parameter, args.frame)
            print('needed parameters for manual cropping:\n bottom_left_x, bottom_left_y, top_right_x, top_right_y')
            pprint.pprint(marker_crop_positions)
            break

        elif args.set_crop_parameter != None:
            result = cv.cut_out_video(file_name, args.destination, (args.set_crop_parameter[0], args.set_crop_parameter[1]), (args.set_crop_parameter[2], args.set_crop_parameter[3]))    # actual cropping of video
            continue

        elif enu == 0:    # first run always cropping to get first marker positions
            marker_crop_positions = cv.mark_crop_positions(file_name, args.frame)
            print('enu=0')
        
        else:   # for each other file
            if args.crop_video and args.plot_frame == True:   # crop positions and plotting
                marker_crop_positions = cv.mark_crop_positions(file_name, args.frame)
                file_name = cv.plot_frame(file_name, args.frame, marker_crop_positions)
            elif args.crop_video == False and args.plot_frame == True:    # only plotting
                file_name = cv.plot_frame(file_name, args.frame, marker_crop_positions)
            elif args.crop_video == True and args.plot_frame == False:    # only crop positions
                marker_crop_positions = cv.mark_crop_positions(file_name, args.frame)
            else:
                pass
        
        bottom_left_x = int(marker_crop_positions[0]['bottom left corner'][0]) 
        bottom_left_y = int(marker_crop_positions[0]['bottom left corner'][1])
        top_right_x= int(marker_crop_positions[0]['top right corner'][0])
        top_right_y = int(marker_crop_positions[0]['top right corner'][1])
        
        result = cv.cut_out_video(file_name, args.destination, (bottom_left_x, bottom_left_y), (top_right_x, top_right_y))    # actual cropping of video
       

# +++++++++++++++++++++++++++++++++++++++++
        # overall working
        # missing: set_crop_parameter working but not in combination with others like plot_frame
        # documentation!
        
        # next: put this in pyQT6!
# +++++++++++++++++++++++++++++++++++++++++
        