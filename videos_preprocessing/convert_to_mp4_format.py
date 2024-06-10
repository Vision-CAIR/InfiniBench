import argparse
import os
import os 
import cv2 
import time 
import json
from tqdm import tqdm

parser = argparse.ArgumentParser('Convert frames to MP4 format')
parser.add_argument('--video_frames_dir', type=str,default="", help="path to the long videos frames")
parser.add_argument('--output_dir', type=str,default="", help="path to save the MP4 videos")
parser.add_argument('--fps', type=int,default=1, help="fps of the video")
parser.add_argument('--source', type=str,default="movienet", help="source of the videos movienet or tvqa")
parser.add_argument('--movies_durations', type=str,default="../movienet_duration.json", help="path to the movies durations json file")
parser.add_argument('--movies_has_subtitles',type=str,default="../movies_has_subtitles.json",help="path to the movies_has_subtitles json file")
parser.add_argument("--original_fps", action="store_true")

parser.add_argument("--start", type=int, default=0,help="start video number to process")
parser.add_argument("--end", type=int, default=110000,help="end video number to process")
args = parser.parse_args()
if args.source=="movienet":
    movies_durations=json.load(open(args.movies_durations))
    
start=args.start
end=args.end

os.makedirs(args.output_dir,exist_ok=True)
movies_has_subtitles=json.load(open(args.movies_has_subtitles))

for i,frames_folder in enumerate(tqdm(os.listdir(args.video_frames_dir))):
    if start<=i<end:
        t1=time.time()
        video_path=os.path.join(args.video_frames_dir,frames_folder)
        # create video from frames 
        video_name=frames_folder+".mp4"
        video_path=os.path.join(args.output_dir,video_name)
        # first frame to get the shape of the frame 
        frame_0_name=os.listdir(video_path)[0]
        frame_0_path=os.path.join(video_path,frame_0_name)
        frame_0=cv2.imread(frame_0_path)
        total_number_of_frames=len(os.listdir(video_path))
        print("Total number of frames ",total_number_of_frames)
        if args.source=="tvqa":
            video_fps=3
        elif args.original_fps and args.source=="movienet":
            movie_duration_in_seconds=movies_durations[frames_folder]*60
            video_fps=total_number_of_frames/movie_duration_in_seconds
            print("Movie FPS ",video_fps)
        elif args.source=="movienet":
                video_fps=args.fps
        video_writer=cv2.VideoWriter(video_path,cv2.VideoWriter_fourcc(*'mp4v'), video_fps, (frame_0.shape[1],frame_0.shape[0]))
        for frame in sorted(os.listdir(video_path)):
            frame_path=os.path.join(video_path,frame)
            frame=cv2.imread(frame_path)
            video_writer.write(frame)
        video_writer.release()
        print("Video created for ",frames_folder)
        print("Time taken ",time.time()-t1)
