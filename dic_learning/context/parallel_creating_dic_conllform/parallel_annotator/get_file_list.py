import os

path = '/cl/work/shusuke-t/ds_ner/dic_learning/context/parallel_creating_dic_conllform/dic_conllform/parallel_anno_data/'
files = []

for x in os.listdir(path):
    if os.path.isfile(path + x):  #isdirの代わりにisfileを使う
        files.append(x) 

for file_name in files:
    command = 'nohup python labeling_multi_label.py ' + file_name + ' &'
    print(command)
