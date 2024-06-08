import json 
import os
import numpy as np
from scipy import stats


with open("filtered_fqa_questions_answers.json", "r") as f:
    data_original=json.load(f)
data={}
for key in data_original.keys():
    if len(data_original[key]['questions'])!=0:
        # remove this movie from the data
        data[key]=data_original[key]

faq_statistics = {}
l=[]
for key in data.keys():
    faq_statistics[key] = len(data[key]['questions'])
    l.append(len(data[key]['questions']))
    
print(f"Total number of FAQs: {len(faq_statistics)}")
print(f"Total number of questions: {sum(l)}")
print(f"Average number of questions per FAQ: {sum(l)/len(faq_statistics)}")
print(f"Maximum number of questions in a FAQ: {max(l)}")
print(f"Minimum number of questions in a FAQ: {min(l)}")
print(f"Standard deviation of number of questions in FAQs: {np.std(l)}")
print(f"Mean of number of questions in FAQs: {np.mean(l)}")
print(f"Median of number of questions in FAQs: {np.median(l)}")
print(f"Mode of number of questions in FAQs: {stats.mode(l)}")
print(f"Variance of number of questions in FAQs: {np.var(l)}")
    