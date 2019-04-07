'''
文境界を識別し、文を分割。
'''
import os


class Splitter():

    def __init__(self, read_file, write_file):
        self.read_file = read_file
        self.write_file = write_file

    def split(self):
        token_list = self.load()
        splitted_list = self.find_boundary(token_list)
        self.write(splitted_list)
        os.remove(self.read_file)

    def find_boundary(self, token_list):
        splitted_list = []
        for i, token_label in enumerate(token_list):
            splitted_list.append(token_label)
            if token_label != '\n':
                token, label = token_label.split(' ')
                if token == '.':
                    next_token = self.get_next(i, token_list)
                    judge = self.judge_eos(next_token)
                    if judge == 'n':
                        pass
                    elif judge == 'u':
                        splitted_list.append('\n')
                    else:
                        pass
        return splitted_list

    def judge_eos(self, next_token):
        #次の単語が大文字始まりor改行なら文末、それ以外(小文字始まり)なら文中
        if next_token == '\n':
            return 'n'
        elif next_token[0].isupper():
            return 'u'
        else:
            return False

    def get_next(self, i, token_list):
        next_index = i + 1
        next_token_label = token_list[next_index]
        next_token = next_token_label.split(' ')[0]
        return next_token

    def load(self):
        with open(self.read_file, 'r') as r:
            token_list = [token for token in r]
        return token_list

    def write(self, splitted_list):
        with open(self.write_file, 'w') as w:
            for token_label in splitted_list:
                w.write(token_label)

