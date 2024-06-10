import argparse
import os

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--video_frames_dir', type=str,default="", help="path to the long videos frames")
parser.add_argument('--output_dir', type=str,default="", help="path to save the MP4 videos")

args = parser.parse_args()
