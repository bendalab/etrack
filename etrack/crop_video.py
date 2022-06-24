# from types import NoneType
import matplotlib.pyplot as plt 
import numpy as np
import glob
import os
import math
import argparse
from ffmpy import FFmpeg
from IPython import embed
from calibration_functions import *


class CropVideo():
    
    def __init__(self, file_name) -> None: 
        super().__init__()

        self._file_name = file_name
        self.mark_crop_positions
        self.cut_out_video
        self.plot_video
        self.crop_frame


    def mark_crop_positions(self, file_name, frame_number):
        
        task = MarkerTask("crop area", ["bottom left corner", "top left corner", "top right corner", "bottom right corner"], "Mark crop area")
        im = ImageMarker([task])
        
        marker_positions = im.mark_movie(file_name, frame_number)
        print(marker_positions)

        np.save('marker_positions', marker_positions)
        plt.close()
        return marker_positions

 
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
    

    def crop_frame(self, frame, marker_positions):

        # load the four marker positions 
        bottom_left_x, bottom_left_y, bottom_right_x, bottom_right_y, top_left_x, top_left_y, top_right_x, top_right_y = assign_marker_positions(marker_positions)

        # define boundaries of frame, taken by average of points on same line but slightly different pixel values
        left_bound = int(np.mean([bottom_left_x, top_left_x]))
        right_bound = int(np.mean([bottom_right_x, top_right_x]))
        top_bound = int(np.mean([top_left_y, top_right_y]))
        bottom_bound = int(np.mean([bottom_left_y, bottom_right_y]))
        
        # crop the frame by boundary values
        cropped_frame = frame[top_bound:bottom_bound, left_bound:right_bound]
        # cropped_frame = np.mean(cropped_frame, axis=2)    # mean over 3rd dimension (RGB/color values)

        return cropped_frame


    def plot_video(self, filename, frame_number, marker_positions):
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
            cropped_frame = cv.crop_frame(frame, marker_positions)  
            
            fig, ax = plt.subplots()
            ax.imshow(cropped_frame)    # plot wanted frame of video
        else:
           print("Could not read frame number %i either failed to open movie or beyond maximum frame number!" % frame_number)
           return []
        plt.title(filename)
        plt.show(block=True)
        
        return filename


if __name__ == "__main__":    
    
    parser = argparse.ArgumentParser(description='Crop video to wanted pixel parameters')
    parser.add_argument('-p', action='store_true', help='plot the video to check fit of cropping parameters')
    parser.add_argument('-c', action='store_true', help='set cropping parameters manually for each video')
    parser.add_argument('-d', type=str, help='destination folder for cropped videos', default='/home/efish/etrack/cropped_videos/') 
    parser.add_argument('-f', type=int, help='frame number to plot, default=10', default=10)
    args = parser.parse_args()

    for enu, file_name in enumerate(glob.glob("/home/efish/etrack/videos/*")): 
        print(file_name)
        cv = CropVideo(file_name)

        if enu == 0:    # first run always cropping to get first marker positions
            marker_positions = cv.mark_crop_positions(file_name, args.f)
            print('enu=0')
            
        else:   # for each other file
            if args.c and args.p == True:   # crop positions and plotting
                marker_positions = cv.mark_crop_positions(file_name, args.f)
                file_name = cv.plot_video(file_name, args.f, marker_positions)
            elif args.c == False and args.p == True:    # only plotting
                file_name = cv.plot_video(file_name, args.f, marker_positions)
            elif args.c == True and args.p == False:    # only crop positions
                marker_positions = cv.mark_crop_positions(file_name, args.f)
            else:
                pass
        
        bottom_left_x = int(marker_positions[0]['bottom left corner'][0]) 
        bottom_left_y = int(marker_positions[0]['bottom left corner'][1])
        top_right_x= int(marker_positions[0]['top right corner'][0])
        top_right_y = int(marker_positions[0]['top right corner'][1])

        result = cv.cut_out_video(file_name, args.d, (bottom_left_x, bottom_left_y), (top_right_x, top_right_y))    # actual cropping of video
        
        