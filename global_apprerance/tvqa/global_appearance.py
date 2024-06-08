import os
import json 
import cv2
from tqdm import tqdm

with open ("tvqa_plus_annotations/tvqa_plus_train.json") as f :
    training_data=json.load(f)

with open ("tvqa_plus_annotations/tvqa_plus_val.json") as f :
    validation_data=json.load(f)
bbt_main_characters={
    "Leonard":True,
    "Sheldon":True,
    "Penny":True,
    "Howard":True,
    "Raj":True,
    "Bernadette":True,
    "Amy":True,
    "Stuart":True,
    "Emily":True,
    "Leslie":True,
    }
video_bbox={}
max_img_id=0
data_splits=[training_data,validation_data]
# {"video_name":{"frame_num":[{bbox1},{bbox2}]}}
for split in data_splits:
    for data in split:
        if data["vid_name"] not in video_bbox:
            video_bbox[data["vid_name"]]={}
        for frame_number in data["bbox"]:
            max_img_id=max(max_img_id,int(frame_number))
            if frame_number not in video_bbox[data["vid_name"]]:
                video_bbox[data["vid_name"]][frame_number]=[]
            characters_ann=[]
            added_characters=[] # to avoid adding multiple bbox for the same character in the same frame
            for bbox in data["bbox"][frame_number]:
                if bbt_main_characters.get(bbox["label"],False) and bbox["label"] not in added_characters:
                    characters_ann.append(bbox)
                    added_characters.append(bbox["label"])
            video_bbox[data["vid_name"]][frame_number].extend(characters_ann)

# save bbox annotations 
with open("video_bbox.json","w") as f:
    json.dump(video_bbox,f)
print(f"max image id {max_img_id}")

video_bbox = json.load(open("video_bbox.json"))
def draw_bbox (frame ,bbox ,video_name,frame_count,save_path="character_cropped_images_clips",color=(255,0,0)):
    x1=bbox["left"]
    y1=bbox["top"]
    x2=x1+bbox["width"]
    y2=y1+bbox["height"]
    label=bbox["label"]
    try:
        # crop the bbox and sava the image in folder of the label name
        output_path=os.path.join(save_path,video_name,label)
        os.makedirs(output_path,exist_ok=True)
        cropped_img=frame[y1:y2,x1:x2]
        save_name=str(frame_count).zfill(5)
        # resize the image to 224x224
        # cropped_img=cv2.resize(cropped_img,(224,224))
        cv2.imwrite(os.path.join(output_path,f"{save_name}.jpg"),cropped_img)
    except:
        print(f"Error in saving image {video_name} {frame_count} {label}")
    # draw the bbox on the frame
    # cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)
    # cv2.putText(frame,label,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.9,color,2)
    
    return frame



# os.makedirs("videos_out",exist_ok=True)
for key in tqdm(sorted(video_bbox.keys())) :
    # if key =="s05e01_seg01_clip_01":
    video_path=os.path.join("/ibex/project/c2090/datasets/TVR_dataset/videos/video_files/frames_hq/bbt_frames",key)
    for frame_id in sorted(os.listdir(video_path)):
        frame_number=int(frame_id[:-4])
        bbox_dict=video_bbox[key]
        if bbox_dict.get(str(frame_number),False):
            frame_bbox_list=bbox_dict[str(frame_number)]
            for bbox in frame_bbox_list:
                frame=cv2.imread(os.path.join(video_path,frame_id))
                draw_bbox(frame,bbox,key,frame_number)
    # print(f"video {key} done , number of frames {frame_number}")
    
        