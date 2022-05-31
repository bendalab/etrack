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
        self.cut_out_video
        self.mark_crop_positions


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
  

if __name__ == "__main__":    
    
    parser = argparse.ArgumentParser(description='Crop video to wanted pixel parameters')
    parser.add_argument('-p', action='store_true', help='plot the video to check fit of cropping parameters')
    parser.add_argument('-c', action='store_true', help='set cropping parameters manually for each video')
    parser.add_argument('-d', type=str, help='destination folder for cropped videos')    # const='/home/efish/etrack/cropped_videos/', 
    parser.add_argument('-f', type=int, help='frame number to plot, default=10')    #  const='10',
    args = parser.parse_args()

    print(args.p)
    for enu, file_name in enumerate(glob.glob("/home/efish/etrack/videos/*")): 
        # if file_name == '/home/efish/etrack/videos/2022.03.28_7.mp4':
        print(file_name)
        cv = CropVideo(file_name=file_name)
        
        frame_number = 10
        destination_folder = "/home/efish/etrack/cropped_videos/"
        # if args.d or args.f != None:
        #     frame_number = args.f
        #     destination_folder = args.d

        print(enu)
        if enu == 0 or args.c:
            marker_positions = cv.mark_crop_positions(file_name, frame_number)
        elif args.p:
            file_name = plot_video(file_name, frame_number)
            
        else:
            pass

        print('marker positions done')
        bottom_left_x = int(marker_positions[0]['bottom left corner'][0]) 
        bottom_left_y = int(marker_positions[0]['bottom left corner'][1])
        top_right_x= int(marker_positions[0]['top right corner'][0])
        top_right_y = int(marker_positions[0]['top right corner'][1])

        result = cv.cut_out_video(file_name, destination_folder, (bottom_left_x, bottom_left_y), (top_right_x, top_right_y))
        print(result)