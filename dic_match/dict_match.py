#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flashtext import KeywordProcessor


class Metric():

    def __init__(self, predict, correct):
        self.predict_list = predict
        self.correct_list = correct

    def precision(self):
        cnt_token = []
        cnt_correct = 0
        for abst in self.predict_list:
            no_abst, predict_span_list = abst
            cnt_token.extend(predict_span_list)
            correct_span = [span[2:4] for span in self.correct_list if span[0] == no_abst and span[1] == 'A']
            #predict_span_listの内、何割がcorrect_listに存在するか
            for pred_span in predict_span_list:
                exist = [c_span for c_span in correct_span if pred_span[1] == int(c_span[0]) and pred_span[2] == int(c_span[1])]
                if len(exist) > 0:
                    cnt_correct += 1
        self.precision_score = cnt_correct / len(cnt_token)

    def recall(self):
        correct_abst_list = [line for line in self.correct_list if line[1] == 'A']
        cnt_correct = 0
        for abst in correct_abst_list:
            no_abst = abst[0]
            correct_span = abst[2:4]
            for span in self.predict_list:
                if span[0] == no_abst:
                    predict_span_list = span[1]
                    break
                else:
                    predict_span_list = []
            #correct_listの内、何割がpredict_span_listに存在するか
            exist = [pred_span for pred_span in predict_span_list if int(correct_span[0]) == pred_span[1] and int(correct_span[1]) == pred_span[2]]
            if len(exist) > 0:
                cnt_correct += 1
        self.recall_score = cnt_correct / len(correct_abst_list)

    def type_recall(self):
        self.type_recall_score_list = []
        self.type_list = ['SYSTEMATIC','FAMILY', 'TRIVIAL', 'FORMULA', 'ABBREVIATION', 'IDENTIFIER', 'MULTIPLE', 'NO CLASS']
        for label_type in self.type_list:
            correct_abst_list = [line for line in self.correct_list if line[1] == 'A' and line[5].strip() == label_type]
            type_recall_score = self.culc_recall(correct_abst_list)
            self.type_recall_score_list.append(type_recall_score)

    def culc_recall(self, correct_abst_list):
        cnt_correct = 0
        for abst in correct_abst_list:
            no_abst = abst[0]
            correct_span = abst[2:4]
            for span in self.predict_list:
                if span[0] == no_abst:
                    predict_span_list = span[1]
                    break
                else:
                    predict_span_list = []
            #correct_listの内、何割がpredict_span_listに存在するか
            exist = [pred_span for pred_span in predict_span_list if int(correct_span[0]) == pred_span[1] and int(correct_span[1]) == pred_span[2]]
            if len(exist) > 0:
                cnt_correct += 1
        recall_score = cnt_correct / len(correct_abst_list)
        print(cnt_correct)
        print(len(correct_abst_list))
        print('')
        return recall_score

    def f1(self):
        self.f1_score = 2 * self.precision_score * self.recall_score / (self.precision_score + self.recall_score)


def make_ne_founder(DICT_FILE):
    keyword_processor = KeywordProcessor(case_sensitive=False)
    with open(DICT_FILE, 'r') as r:
        vocab_list = [vocab for vocab in r]
    for vocab in vocab_list:
        keyword_processor.add_keyword(vocab.strip('\n'))
    return keyword_processor


def extract_keywords(TEST_FILE, keyword_processor):
    with open(TEST_FILE, 'r') as r:
        sentences = [sentence.strip().split('\t') for sentence in r]
    extracted_words_list = []
    for sentence in sentences:
        keywords_found = keyword_processor.extract_keywords(sentence[2], span_info=True)
        extracted_words_list.append((sentence[0], keywords_found))
    return extracted_words_list


def evaluate(extracted_words_list, ANNOTATIONS_FILE):
    with open(ANNOTATIONS_FILE, 'r') as r:
        annotations_list = [abst.split('\t') for abst in r]
    metric = Metric(extracted_words_list, annotations_list)
    metric.precision()
    metric.recall()
    metric.f1()
    metric.type_recall()
    return metric.precision_score, metric.recall_score, metric.f1_score, metric.type_recall_score_list, metric.type_list


def main(TEST_FILE, DICT_FILE, ANNOTATIONS_FILE):
    keyword_processor = make_ne_founder(DICT_FILE)
    extracted_words_list = extract_keywords(TEST_FILE, keyword_processor)
    precision, recall, f1, type_recall_list, type_list = evaluate(extracted_words_list, ANNOTATIONS_FILE)
    print('Precision:{} Recall:{} Span-F1:{}'.format(precision, recall, f1))
    for i, type_label in enumerate(type_list):
        print('{}: {}'.format(type_label, type_recall_list[i]))


if __name__ == '__main__':
    TEST_FILE = '/cl/work/shusuke-t/ds_ner/orig_data/chemdner/data/orig/evaluation.abstracts.txt'
    ANNOTATIONS_FILE = '/cl/work/shusuke-t/ds_ner/orig_data/chemdner/data/orig/evaluation.annotations.txt'
    DICT_FILE = '/cl/work/shusuke-t/ds_ner/orig_data/dic/data/set_ctd_meshsupp_vocab.txt'
    main(TEST_FILE, DICT_FILE, ANNOTATIONS_FILE)
