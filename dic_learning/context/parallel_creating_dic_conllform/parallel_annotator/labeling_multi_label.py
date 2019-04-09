#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import tqdm
import sys
import re
#import split_sent

def preprocessing(sentence):
    sentence = sentence.replace(')', ' ) ')
    sentence = sentence.replace('(', ' ( ')
    sentence = sentence.replace('-', ' - ')
    sentence = sentence.replace(', ', ' , ')
    sentence = sentence.replace('. ', ' . ')
    sentence = sentence.replace('; ', ' ; ')
    sentence = sentence.replace('.\n', ' . ')
    sentence = re.split('\s+', sentence.strip())
    return sentence


def judge(ne_abs_id_list, abs_id):
    if abs_id in ne_abs_id_list:
        return True
    else:
        return False


def o_token_processing(s_index, e_index, abs_sent):
    #NE以外のセンテンス処理
    if e_index == 'end':
        sentence = abs_sent[s_index:]
    else:
        sentence = abs_sent[s_index:e_index]
    token_list = preprocessing(sentence)
    try:
        if len(token_list[-1]) == 0:
            token_list = token_list[:-1]
        if len(token_list[0]) == 0:
            token_list = token_list[1:]
    except IndexError:
        pass
    return token_list


def update_start_index(ne_end_index, char_or_space):
    #NE後がスペースか文字かで分岐
    if char_or_space != ' ':
        #文字なら次ステップへ伝達
        return ne_end_index
    else:
        #スペースなら切り捨てる
        return ne_end_index+1


def bio_labeling(abs_sent, start_index, ne, labeled_token_list, ne_no, last_ne_no):
    ne_start_index = int(ne[2])
    ne_end_index = int(ne[3])
    ne_tag_type = ne[4]
    #NE以外のセンテンス処理
    #NEの前がスペース否かで場合分け
    if abs_sent[ne_start_index - 1] == ' ':
        #NEの前がスペース(NEは独立した単語)
        o_token_list = o_token_processing(start_index, ne_start_index-1, abs_sent)
    else:
        #NEの前がスペースではない（NEは単語の一部分）
        o_token_list = o_token_processing(start_index, ne_start_index, abs_sent)
    labeled_token_list.extend(o_labeling(o_token_list))
    #NEの処理
    ne_token_list = preprocessing(abs_sent[ne_start_index:ne_end_index])
    labeled_token_list.extend(bi_labeling(ne_token_list, ne_tag_type))
    next_start_index = update_start_index(ne_end_index, abs_sent[ne_end_index])

    if ne_no == last_ne_no:
        #NE以外のセンテンス処理
        o_token_list = o_token_processing(next_start_index, 'end', abs_sent)
        labeled_token_list.extend(o_labeling(o_token_list))
        return labeled_token_list, 'end'
    return labeled_token_list, next_start_index


def o_labeling(token_list):
    labeled_token_list = []
    for token in token_list:
        if len(token) > 0:
            string = token + ' O'
        else:
            string = token
        labeled_token_list.append(string)
    return labeled_token_list


def bi_labeling(token_list, ne_tag_type):
    labeled_ne_list = []
    token_len = len(token_list)
    if token_len == 1:
       # S
       string = token_list[0] + ' S-' + ne_tag_type.upper()
       labeled_ne_list.append(string)
    else:
        for i, token in enumerate(token_list):
            if i == 0:
                string = token + ' B-' + ne_tag_type.upper()
            elif i+1 == token_len:
                string = token + ' E-' + ne_tag_type.upper()
            else:
                string = token + ' I-' + ne_tag_type.upper()
            labeled_ne_list.append(string)
    return labeled_ne_list


def write_file(w, token_list):
    for token in token_list:
        w.write(token)
        w.write('\n')


if __name__ == '__main__':
    args = sys.argv

    file_name = args[1]

    # data
    root_path = '/cl/work/shusuke-t/ds_ner/dic_learning/context/parallel_creating_dic_conllform/dic_conllform/'

    id_file_path = root_path + 'parallel_id_data/'
    id_anno_file_path = root_path + 'parallel_anno_data/'
    conllform_file_path = root_path + 'conllform/'

    ne_sent_only = True #default is True
    id_file = id_file_path + file_name
    id_anno_file = id_anno_file_path + file_name
    conllform_file = conllform_file_path + file_name


    with open(id_file, 'r') as r1, open(id_anno_file, 'r') as r2:
        absts = [line.split('\t') for line in r1]
        annos = [line.strip('\n').split('\t') for line in r2]
        ne_abs_id_list = [int(i[0]) for i in annos]

    w = open(conllform_file, 'w')
    for abs_id, abs_sent in tqdm(absts):
        #print('abs_sent:{}'.format(abs_sent))
        if judge(ne_abs_id_list, int(abs_id)):
            #This abst includes NE.
            ne_index_list = [i for i, ne_abs_id in enumerate(ne_abs_id_list) \
                             if ne_abs_id == int(abs_id)]
            next_start_index = 0
            labeled_token_list = [] #ラベル付けされたセンテンスを格納するリスト
            last_ne_no = len(ne_index_list)
            for i, ne_index in enumerate(ne_index_list):
                ne_no = i + 1
                labeled_token_list, next_start_index = bio_labeling(abs_sent,
                                                                    next_start_index,
                                                                    annos[ne_index],
                                                                    labeled_token_list,
                                                                    ne_no,
                                                                    last_ne_no)
            labeled_token_list.append('')
            write_file(w, labeled_token_list)
        else:
            #This abst does not include NE.
            if ne_sent_only:
                pass
            else:
                labeled_token_list = o_labeling(preprocessing(abs_sent))
                labeled_token_list.append('')
                write_file(w, labeled_token_list)
    w.close()

