'''
Context 辞書学習データ(train_conllform.txt)の作成
入れ替え方式
Filtered dataのNEと辞書NEを入れ替える
'''


class Sentences():

    def __init__(self):
        self.sentences_list = [] # sentence class のlist

    def append(self, sent):
        self.sentences_list.append(sent)

    def show(self):
        print(self.sentences_list)


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


def creating(orig_train_file, filtered_file, dic_file, write_file):
    # 辞書とFilteredNEの入れ替え
    splitter = Splitter()
    filtered_sent_list = splitter.split(filtered_file)
    dic_sent_list = splitter.split(dic_file)

    filtered_sentences = get_instance(filtered_sent_list)
    dic_sentences = get_instance(dic_sent_list)


    # orig_trainとランダムソートしてからマージ

    # ファイルへ書き込み


def main():
    # data
    root_dir = '/cl/work/shusuke-t/ds_ner/dic_learning/context'
    orig_train_file = root_dir + '/conllform/non_dic_learning_train_conllform.txt'
    #filtered_file = root_dir + '/filtered_conllform/filtered_all_conllform.txt'
    filtered_file = root_dir + '/filtered_conllform/toy_filtered_all_conllform.txt'
    #dic_file = '/cl/work/shusuke-t/ds_ner/dic_learning/context/dic_conllform/conllform/train_conllform.txt'
    dic_file = '/cl/work/shusuke-t/ds_ner/dic_learning/context/dic_conllform/conllform/toy_train_conllform.txt'
    write_file = root_dir + '/conllform/train_conllform.txt'

    # creating
    creating(orig_train_file, filtered_file, dic_file, write_file)


if __name__ == '__main__':
    main()

