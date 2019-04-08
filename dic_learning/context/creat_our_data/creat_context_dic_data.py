'''
Context 辞書学習データ(train_conllform.txt)の作成
入れ替え方式
Filtered dataのNEと辞書NEを入れ替える
'''

import random


class Sentences():

    def __init__(self):
        self.sentences_list = [] # sentence class のlist
        self.bie_sentences_list = [] # sentence class のlist
        self.s_sentences_list = [] # sentence class のlist

    def append(self, sent):
        # NEがセンテンス中に1つの場合のみappend
        if sent.num_ne == 1:
            self.sentences_list.append(sent)
            if sent.ne_tag_type == 'B':
                self.bie_sentences_list.append(sent)
            elif sent.ne_tag_type == 'S':
                self.s_sentences_list.append(sent)

    def get_sentences_list(self, label_type):
        if label_type == 'bie':
            return self.bie_sentences_list
        elif label_type == 's':
            return self.s_sentences_list

    def get_one_sentence_context(self, label_type):
        if label_type == 'bie':
            sent_list = self.bie_sentences_list
        elif label_type == 's':
            sent_list = self.s_sentences_list
        one_sent = random.choice(sent_list) 
        return one_sent.front_context, one_sent.back_context


class Sentence():

    def __init__(self, sent):
        self.token_list = sent
        self.num_ne = self.count_ne()
        if self.num_ne == 1:
            self.ne_tag_type = self.get_ne_tag_type()
            self.front_context, self.back_context, = self.get_context()

    def get_context(self):
        # 前提: NEはセンテンス中に１つだけ
        # NEのspanを抽出
        for index, token in enumerate(self.token_list):
            name, label = self.get_name_label(token)
            if self.ne_tag_type == 'B':
                if label[0] == 'B':
                    s_span = index
                elif label[0] == 'E':
                    e_span = index + 1
            elif self.ne_tag_type == 'S':
                if label[0] == 'S':
                    s_span = index
                    e_span = index + 1
        # contextを抽出
        front_context = self.token_list[:s_span]
        back_context = self.token_list[e_span:]
        return front_context, back_context

    def get_ne_tag_type(self):
        # 前提: NEはセンテンス中に１つだけ
        for token in self.token_list:
            name, label = self.get_name_label(token)
            if label[0] == 'S':
                return 'S'
            elif label[0] == 'B':
                return 'B'

    def count_ne(self):
        cnt_ne = 0
        for token in self.token_list:
            name, label = self.get_name_label(token)
            if label[0] == 'S' or label[0] == 'B':
                cnt_ne += 1
        return cnt_ne

    def get_name_label(self, token):
        split_list = token.split()
        name = split_list[0]
        label = split_list[1]
        return name, label


class Splitter():

    def __init__(self):
        pass

    def split(self, read_file):
        token_list = self.read(read_file)
        sent_list = self.split_sent(token_list)
        return sent_list

    def read(self, read_file):
        with open(read_file, 'r') as r:
            token_list = [token for token in r]
        return token_list

    def split_sent(self, token_list):
        sent_list = []
        word_list = []
        for token in token_list:
            if token == '\n':
                # sentences bounder
                sent_list.append(word_list)
                word_list = []
            else:
                # inside sentence
                word_list.append(token.strip())
        return sent_list


def get_instance(sent_list):
    sentences = Sentences()
    for sent in sent_list:
        sentence = Sentence(sent)
        sentences.append(sentence)
    return sentences


def merge_ne_context(filtered_sentences, dic_sentences, label_type):
    all_sent_merged_list = []
    for sentence in dic_sentences.get_sentences_list(label_type):
        one_ne_list = sentence.token_list
        front_context_list, back_context_list = filtered_sentences.get_one_sentence_context(label_type)
        one_sent_merged_list = front_context_list + one_ne_list + back_context_list
        all_sent_merged_list.append(one_sent_merged_list)
    return all_sent_merged_list


def creating(orig_train_file, filtered_file, dic_file, write_file):
    # 辞書とFilteredNEの入れ替え
    splitter = Splitter()
    filtered_sent_list = splitter.split(filtered_file)
    dic_sent_list = splitter.split(dic_file)

    filtered_sentences = get_instance(filtered_sent_list)
    dic_sentences = get_instance(dic_sent_list)

    bie_merged  = merge_ne_context(filtered_sentences, dic_sentences, 'bie')
    s_merged  = merge_ne_context(filtered_sentences, dic_sentences, 's')

    # orig_trainとランダムソートしてからマージ
    orig_train_sent_list = splitter.split(orig_train_file)

    all_merged_list = bie_merged + s_merged + orig_train_sent_list
    random.shuffle(all_merged_list)

    # ファイルへ書き込み
    with open(write_file, 'w') as w:
        for sent in all_merged_list:
            for word in sent:
                w.write(word)
                w.write('\n')
            w.write('\n')


def main():
    # data
    root_dir = '/cl/work/shusuke-t/ds_ner/dic_learning/context'
    orig_train_file = root_dir + '/conllform/non_dic_learning_train_conllform.txt'
    #orig_train_file = root_dir + '/conllform/toy_non_dic_learning_train_conllform.txt'
    filtered_file = root_dir + '/filtered_conllform/filtered_all_conllform.txt'
    #filtered_file = root_dir + '/filtered_conllform/toy_filtered_all_conllform.txt'
    dic_file = '/cl/work/shusuke-t/ds_ner/dic_learning/context/dic_conllform/conllform/train_conllform.txt'
    #dic_file = '/cl/work/shusuke-t/ds_ner/dic_learning/context/dic_conllform/conllform/toy_train_conllform.txt'
    write_file = root_dir + '/conllform/train_conllform.txt'

    # creating
    creating(orig_train_file, filtered_file, dic_file, write_file)


if __name__ == '__main__':
    main()

