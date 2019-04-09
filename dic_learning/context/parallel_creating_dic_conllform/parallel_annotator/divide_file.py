def divide(read_file, write_dir):
    with open(read_file, 'r') as r:
        line_list = [line for line in r]

    # 1 file分を格納
    part_list = []
    for line in line_list:
        part_list.append(line)
        ne_no_int = int(line.split()[0])
        if ne_no_int % 1000 == 0:
            # write file
            write_file = write_dir + 'divide_no_' + str(ne_no_int) + '.txt'
            with open(write_file, 'w') as w:
                for part in part_list:
                    w.write(part)
            part_list = []


def main():
    root_dir = '/cl/work/shusuke-t/ds_ner/dic_learning/context/parallel_creating_dic_conllform/dic_conllform/'

    anno_data = root_dir + 'anno_data/anno_train.txt'
    write_anno_dir = root_dir + 'parallel_anno_data/'

    id_data = root_dir + 'id_data/id_train.txt'
    write_id_dir = root_dir + 'parallel_id_data/'

    divide(anno_data, write_anno_dir)
    divide(id_data, write_id_dir)


if __name__ == '__main__':
    main()
