'''
Fuzzy CRFのデータ作成
'''


class FuzzyLabeler():

    def __init__(self):
        pass

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
                word_list.append(token)
        return sent_list

    def fuzzy_labeling(self, sent_list):
        fuzzy_sent_list = []
        for sent in sent_list:
            fuzzy_sent = self.relabeling(sent)
            fuzzy_sent_list.append(fuzzy_sent)
        return fuzzy_sent_list

    def relabeling(self, sent):
        fuzzy_sent = []
        # sent is word_list
        for word in sent:
            name, gold, pred = self.extract(word)
            if gold != pred:
                # FP or FN
                label = '<UNK>'
            elif gold == pred:
                label = gold
            fuzzy_word = name + ' ' + label + '\n'
            fuzzy_sent.append(fuzzy_word)
        return fuzzy_sent

    def extract(self, word):
        info_list = word.split()
        name = info_list[0]
        gold = info_list[1]
        pred = info_list[2]
        return name, gold, pred

    def write(self, write_file, fuzzy_sent_list):
        with open(write_file, 'w') as w:
            for sent in fuzzy_sent_list:
                for fuzzy_word in sent:
                    w.write(fuzzy_word)
                w.write('\n')


def creating(read_file, write_file):
    labeler = FuzzyLabeler()
    token_list = labeler.read(read_file)
    sent_list = labeler.split_sent(token_list)
    fuzzy_sent_list = labeler.fuzzy_labeling(sent_list)
    labeler.write(write_file, fuzzy_sent_list)


def main():
    # data
    read_file = '/cl/work/shusuke-t/flair/resources/taggers/fuzzy_crf_data/test.tsv'
    write_file = '/cl/work/shusuke-t/ds_ner/fuzzy_crf/fuzzy_conllform/train_conllform.txt'

    # creating fuzzy data
    creating(read_file, write_file)


if __name__ == '__main__':
    main()
