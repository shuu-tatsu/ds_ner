'''
limited版に編集してある
'''


class IdCreater():

    def __init__(self, target_file, read_file, file_type):
       self.target_file = target_file
       self.read_file = read_file
       self.file_type = file_type

    def creat_file(self):
        abst_list = self.read()
        self.write(abst_list)

    def read(self):
        with open(self.read_file , 'r') as r:
            abst_list = [abst for abst in r]
        return abst_list

    def write(self, abst_list):
        write_file = self.target_file + 'id_data/id_' + self.file_type + '.txt'
        with open(write_file, 'w') as w:
            for abst in abst_list:
                split_list = abst.split('\t')
                abst_id_str = split_list[0]
                abst_title_str = split_list[1]
                abst_abst_str = split_list[2]
                written_str = abst_id_str + '\t' + abst_abst_str
                w.write(written_str)


class AnnoCreater():

    def __init__(self, target_file, read_file, file_type):
       self.target_file = target_file
       self.read_file = read_file
       self.file_type = file_type

    def creat_file(self):
        ne_list = self.read()
        self.write(ne_list)

    def read(self):
        with open(self.read_file , 'r') as r:
            ne_list = [ne for ne in r]
        return ne_list

    def write(self, ne_list):
        write_file = self.target_file + 'anno_data/anno_' + self.file_type + '.txt'
        with open(write_file, 'w') as w:
            for ne in ne_list:
                #ne: 
                #21826085	A	946	957	haloperidol	TRIVIAL
                split_list = ne.split('\t')
                abst_id_str = split_list[0]
                title_or_abst_tag = split_list[1]
                s_index = split_list[2]
                e_index = split_list[3]
                ne_name = split_list[4]
                ne_type = split_list[5]
                # タイトルは除外
                if title_or_abst_tag == 'A':
                    #written_str = abst_id_str + '\t' + ne_name + '\t' + s_index + '\t' + e_index + '\t' + ne_type
                    if ne_type.strip() in ['SYSTEMATIC', 'FAMILY', 'TRIVIAL']:
                        written_str = abst_id_str + '\t' + ne_name + '\t' + s_index + '\t' + e_index + '\t' + 'CHEMICAL\n'
                        w.write(written_str)



def main():
    TARGET_FILE = '/cl/work/shusuke-t/ds_ner/orig_data/chemdner/data/limited_type_data/'
    make_id_corpus = True
    if make_id_corpus:
        TOY_FILE = TARGET_FILE + 'orig/toy.abstracts.txt' 
        TRAIN_FILE = TARGET_FILE + 'orig/training.abstracts.txt' 
        DEV_FILE = TARGET_FILE + 'orig/development.abstracts.txt'
        EVAL_FILE = TARGET_FILE + 'orig/evaluation.abstracts.txt'

        id_toy_creater = IdCreater(TARGET_FILE, TOY_FILE, 'toy')
        id_toy_creater.creat_file()

        id_toy_creater = IdCreater(TARGET_FILE, TRAIN_FILE, 'train')
        id_toy_creater.creat_file()
        id_valid_creater = IdCreater(TARGET_FILE, DEV_FILE, 'valid')
        id_valid_creater.creat_file()
        id_test_creater = IdCreater(TARGET_FILE, EVAL_FILE, 'test')
        id_test_creater.creat_file()


    make_anno_corpus = True
    if make_anno_corpus:
        TOY_FILE = TARGET_FILE + 'orig/toy.annotations.txt'
        TRAIN_FILE = TARGET_FILE + 'orig/training.annotations.txt'
        DEV_FILE = TARGET_FILE + 'orig/development.annotations.txt'
        EVAL_FILE = TARGET_FILE + 'orig/evaluation.annotations.txt'

        anno_toy_creater = AnnoCreater(TARGET_FILE, TOY_FILE, 'toy')
        anno_toy_creater.creat_file()

        anno_train_creater = AnnoCreater(TARGET_FILE, TRAIN_FILE, 'train')
        anno_train_creater.creat_file()
        anno_valid_creater = AnnoCreater(TARGET_FILE, DEV_FILE, 'valid')
        anno_valid_creater.creat_file()
        anno_test_creater = AnnoCreater(TARGET_FILE, EVAL_FILE, 'test')
        anno_test_creater.creat_file()

if __name__ == '__main__':
    main()
