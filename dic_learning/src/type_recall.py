'''
dic learningのtype別Recallを算出
'''


def creat_type_dict(chemd_test):
    systematic_list = []
    family_list = []
    trivial_list = []
    formura_list = []
    abbreviation_list = []
    identifier_list = []
    multiple_list = []
    no_class_list = []

    with open(chemd_test, 'r') as r:
        line_list = [l for l in r]
    for line in line_list:
        splited_list = line.strip().split('\t')
        name = splited_list[4].replace(' ', '')
        ne_type = splited_list[5]
        if ne_type == 'SYSTEMATIC':
            systematic_list.append(name)
        elif ne_type == 'FAMILY':
            family_list.append(name)
        elif ne_type == 'TRIVIAL':
            trivial_list.append(name)
        elif ne_type == 'FORMULA':
            formura_list.append(name)
        elif ne_type == 'ABBREVIATION':
            abbreviation_list.append(name)
        elif ne_type == 'IDENTIFIER':
            identifier_list.append(name)
        elif ne_type == 'MULTIPLE':
            multiple_list.append(name)
        elif ne_type == 'NO CLASS':
            no_class_list.append(name)

    type_list = [set(systematic_list), set(family_list), set(trivial_list), set(formura_list),\
                 set(abbreviation_list), set(identifier_list), set(multiple_list), set(no_class_list)]
    return type_list


def extract_gold_ne(ner_output):
    with open(ner_output, 'r') as r:
        line_list = [l for l in r]

    ne_list = []
    for line in line_list:
        splited_list = line.strip().split(' ')
        if len(splited_list) > 2:
            name = splited_list[0]
            gold = splited_list[1]
            pred = splited_list[2]
            if len(gold) > 1 and gold[0] == 'S':
                temp_list = []
                temp_list.append(line)
                ne_list.append(temp_list)
                temp_list = []
            elif len(gold) > 1 and gold[0] == 'B':
                temp_list = []
                temp_list.append(line)
            elif len(gold) > 1 and gold[0] == 'I':
                temp_list.append(line)
            elif len(gold) > 1 and gold[0] == 'E':
                temp_list.append(line)
                ne_list.append(temp_list)
                temp_list = []

    return ne_list


def get_recall(type_list, gold_ne_list):
    systematic_list, family_list, trivial_list, formura_list,\
    abbreviation_list, identifier_list, multiple_list, no_class_list = type_list

    systematic_correct = 0
    systematic_all = 0
    family_correct = 0
    family_all = 0
    trivial_correct = 0
    trivial_all = 0
    formura_correct = 0
    formura_all = 0
    abbreviation_correct = 0
    abbreviation_all = 0
    identifier_correct = 0
    identifier_all = 0
    multiple_correct = 0
    multiple_all = 0
    no_class_correct = 0
    no_class_all = 0

    cnt_else = 0
    for gold_ne in gold_ne_list: #これで１つのNE
        false_flag = 0
        one_name_list = []
        #print(gold_ne)
        for token_ne in gold_ne: #１NEのスペース区切りごとのトークン
            splited_list = token_ne.split(' ')
            name = splited_list[0]
            gold = splited_list[1]
            pred = splited_list[2]
            if gold != pred:
                false_flag = 1
            one_name_list.append(name)
        join_name = ''.join(one_name_list)
        #print(join_name)

        if join_name in systematic_list:
            if false_flag == 0: #正解
                systematic_correct += 1
            systematic_all += 1
        elif join_name in family_list:
            if false_flag == 0:
                family_correct += 1
            family_all += 1
        elif join_name in trivial_list:
            if false_flag == 0:
                trivial_correct += 1
            trivial_all += 1
        elif join_name in formura_list:
            if false_flag == 0:
                formura_correct += 1
            formura_all += 1
        elif join_name in abbreviation_list:
            if false_flag == 0:
                abbreviation_correct += 1
            abbreviation_all += 1
        elif join_name in identifier_list:
            if false_flag == 0:
                identifier_correct += 1
            identifier_all += 1
        elif join_name in multiple_list:
            if false_flag == 0:
                multiple_correct += 1
            multiple_all += 1
        elif join_name in no_class_list:
            if false_flag == 0:
                no_class_correct += 1
            no_class_all += 1
        else:
            cnt_else += 1
            #print(join_name)
            #print(cnt_else)

    sys_rec = systematic_correct / systematic_all
    print('SYSTEMATIC	:{}/{}	REC:{}'.format(systematic_correct, systematic_all, sys_rec))

    fam_rec = family_correct / family_all
    print('FAMILY	:{}/{}	REC:{}'.format(family_correct, family_all, fam_rec))

    tri_rec = trivial_correct / trivial_all
    print('TRIVIAL	:{}/{}	REC:{}'.format(trivial_correct, trivial_all, tri_rec))

    for_rec = formura_correct / formura_all
    print('FORMURA	:{}/{}	REC:{}'.format(formura_correct, formura_all, for_rec))

    abb_rec = abbreviation_correct / abbreviation_all
    print('ABBREVIATION	:{}/{}	REC:{}'.format(abbreviation_correct, abbreviation_all, abb_rec))

    ide_rec = identifier_correct / identifier_all
    print('IDENTIFIER	:{}/{}	REC:{}'.format(identifier_correct, identifier_all, ide_rec))

    mul_rec = multiple_correct / multiple_all
    print('MULTIPLE	:{}/{}	REC:{}'.format(multiple_correct, multiple_all, mul_rec))

    noc_rec = no_class_correct / no_class_all
    print('NO_CLASS	:{}/{}	REC:{}'.format(no_class_correct, no_class_all, noc_rec))


def main(chemd_test, ner_output):
    type_list = creat_type_dict(chemd_test)
    type_name_list = ['SYSTEMATIC', 'FAMILY', 'TRIVIAL', 'FORMULA', 'ABBREVIATION', 'IDENTIFIER', 'MULTIPLE', 'NO CLASS']
    for i, type_ne in enumerate(type_list):
        print('type:{}	size:{}	sample:{}'.format(type_name_list[i], len(type_ne), list(type_ne)[:10]))
        print('')
    print('')
 
    gold_ne_list = extract_gold_ne(ner_output)
    #print('gold_ne_list sample')
    #print(gold_ne_list[:20])
    #print('')

    get_recall(type_list, gold_ne_list)

if __name__ == '__main__':
    chemd_test = '/cl/work/shusuke-t/ds_ner/orig_data/chemdner/data/full_type_data/orig/evaluation.annotations.txt'
    ner_output = '/cl/work/shusuke-t/flair_lazy/resources/taggers/dic_learning/non_context/mid_medline_0422_2pm/test.tsv'
    main(chemd_test, ner_output)
