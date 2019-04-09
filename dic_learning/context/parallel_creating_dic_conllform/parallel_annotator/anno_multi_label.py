#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import tqdm
from flashtext import KeywordProcessor
import random


class DataBase():

    def __init__(self, label, vocab_list):
        self.label = label
        self.vocab_list = vocab_list
        #遺伝子は大文字小文字区別あり。タンパク質、酵素も区別あり。
        if label == 'gene':
            self.case = True
        else:
            self.case = True

    def setting(self, keyword_processor):
        self.keyword_processor = keyword_processor


class Annotation():

    def __init__(self, TRAIN_FILE, DEV_FILE, EVAL_FILE, dict_list):
        self.train_file = TRAIN_FILE
        self.dev_file = DEV_FILE
        self.eval_file = EVAL_FILE
        self.db_list = []
        for dic in dict_list:
            self.db_list.append(self.load(dic))

    def load(self, dict_file_label):
        dict_file = dict_file_label[0]
        dict_label = dict_file_label[1]
        with open(dict_file, 'r') as r:
            vocab_list = [word.strip('\n') for word in r]
        db = DataBase(dict_label, vocab_list)
        return db

    def make_annotation(self):
        make_anno_corpus(self.db_list, self.train_file)
        make_anno_corpus(self.db_list, self.dev_file)
        make_anno_corpus(self.db_list, self.eval_file)


def make_anno_corpus(db_list, target_corpus):
    #NE抽出器生成
    for db in db_list:
        make_ne_founder(db, case=db.case)

    #データからNEを抽出
    extracted_words_list = extract_keywords(target_corpus, db_list) 

    #Write annotation file
    f_index = target_corpus.find('id_data')
    n_index = f_index + len('id_data/id_')
    write_file = target_corpus[:f_index] + 'anno_data/anno_' + target_corpus[n_index:]
    write_annotation(extracted_words_list, write_file)


def write_annotation(extracted_words_list, write_file):
    with open(write_file, 'w') as w:

        #all sentences
        for keywords_found_list in extracted_words_list:

            #one sentence
            for sent_id, keyword_found, tag_type in keywords_found_list:
                w.write(sent_id + '\t')
                w.write(str(keyword_found[0]) + '\t')
                w.write(str(keyword_found[1]) + '\t')
                w.write(str(keyword_found[2]) + '\t')
                w.write(tag_type)
                w.write('\n')


def make_ne_founder(db, case):
    keyword_processor = KeywordProcessor(case_sensitive=case)
    for vocab in tqdm(db.vocab_list):
        keyword_processor.add_keyword(vocab)
    db.setting(keyword_processor)


def extract_keywords(target_corpus, db_list):
    with open(target_corpus, 'r') as r:
        sentences = [sentence.split('\t') for sentence in r]
    extracted_words_list = []
    for sent_id, sentence in tqdm(sentences):
        found_list = []
        for db in db_list:
            found_list.append((db.keyword_processor.extract_keywords(sentence, span_info=True), db.label))
        sorted_list = sort_list(sent_id, found_list)
        extracted_words_list.append(sorted_list)
    return extracted_words_list


def sort_list(sent_id, found_list):
    #同一センテンス内でのソート
    temp_list = []
    for one_type_list in found_list:
        temp_list.extend([(sent_id, ne_found, one_type_list[1]) for ne_found in one_type_list[0]])
    sorted_list = sorted(temp_list, key=lambda x: x[1][1])
    return sorted_list


def labeling_id(target_file, train_file, dev_file, eval_file):
    file_list = [train_file, dev_file, eval_file]
    #file_list = [train_file, dev_file]
    for data_file in file_list:
        write_file = target_file + 'id_data/id_' + data_file[(len(target_file)+5):]
        with open(data_file, 'r') as r, open(write_file, 'w') as w:
            sentence_id = 1
            for sentence in r:
                line = str(sentence_id) + '\t' + sentence
                w.write(line)
                sentence_id += 1


def main(TARGET_FILE, dict_list):
    make_id_corpus = True
    if make_id_corpus:
        TRAIN_FILE = TARGET_FILE + 'orig/train.txt' 
        DEV_FILE = TARGET_FILE + 'orig/valid.txt'
        EVAL_FILE = TARGET_FILE + 'orig/test.txt'
        labeling_id(TARGET_FILE, TRAIN_FILE, DEV_FILE, EVAL_FILE)

    make_anno_corpus = True
    if make_anno_corpus:
        TRAIN_FILE = TARGET_FILE + 'id_data/id_train.txt' 
        DEV_FILE = TARGET_FILE + 'id_data/id_valid.txt'
        EVAL_FILE = TARGET_FILE + 'id_data/id_test.txt'

        anno = Annotation(TRAIN_FILE, DEV_FILE, EVAL_FILE, dict_list)
        anno.make_annotation()


if __name__ == '__main__':
    TARGET_FILE = '/cl/work/shusuke-t/ds_ner/dic_learning/context/parallel_creating_dic_conllform/dic_conllform/'
    CHEMICAL = '/cl/work/shusuke-t/ds_ner/orig_data/dic/data/set_ctd_meshsupp_vocab.txt'
    #dict_list = [(PROTEIN, 'protein'), (GENE, 'gene'), (ENZYME, 'enzyme')]
    dict_list = [(CHEMICAL, 'chemical')]

    main(TARGET_FILE, dict_list)
