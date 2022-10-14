import random
import re
from MainApp.models import Poetry


def basic_feihua_init():
    """
    if is_init == 1:
        return True
    else:
        is_init = 1
    """
    """
    :param keyword1: 两个由单个或若干单字构成的集合
    :param keyword2: 两个由单个或若干单字构成的集合
    :param mode: 模式
        firstonly: 仅Match keyword1
        secondonly：仅Match keyword2
        both: 需要两个keyword同时Match
    :param topic_description: 对题目相关背景的描述
    :param key_description: 对关键字或识别字的描述
    """
    global round_number, played_poems, tmp_index

    round_number = 0
    played_poems = []
    tmp_index = 0  # 用于顺序识别单字时的临时索引


def basic_feihua_computer_round(keyword1, keyword2, mode):
    global round_number, played_poems, tmp_index
    global output_poem_obj_comp, output_poem_obj, output_poem_sentence  # 最终输出的Object
    output_poem_sentence = ""
    output_poem_obj = None

    def shuffle_keywords():
        random.shuffle(keyword1)
        random.shuffle(keyword2)

    # print(keyword1, keyword2)

    if mode == "firstonly":  # 只需满足字在第一个集合内
        shuffle_keywords()
        output_poem_obj_comp = Poetry.objects.filter(paragraphs__contains=keyword1[0])
        output_poem_obj = output_poem_obj_comp[random.randint(0, output_poem_obj_comp.count())]

        for sentence in output_poem_obj.paragraphs.split(";"):
            if keyword1[0] in sentence:
                output_poem_sentence = sentence

    elif mode == "secondonly":  # 只需满足字在第二个集合内
        shuffle_keywords()
        output_poem_obj_comp = Poetry.objects.filter(paragraphs__contains=keyword2[0])
        output_poem_obj = output_poem_obj_comp[random.randint(0, output_poem_obj_comp.count() + 1)]

        for sentence in output_poem_obj.paragraphs.split(";"):
            if keyword2[0] in sentence:
                output_poem_sentence = sentence

    # elif mode == "both":  # 需同时满足两个集合内的字——调试，暂时不能使用
    # shuffle_keywords()
    # output_poem_obj_comp = Poetry.objects.filter(paragraphs__contains=keyword1[0]).filter(paragraphs__contains=keyword2[0])

    # for single_poem in output_poem_obj_comp:
    # for sentence in single_poem.paragraphs.split(";"):

    # print(sentence)
    # if any(kwd in sentence for kwd in keyword1):
    # if any(kwd in sentence for kwd in keyword2):
    # output_poem_obj = single_poem
    # output_poem_sentence = sentence

    elif mode == "taketurnfirst":  # 第一个集合内轮流满足
        global tmp_index
        output_poem_obj_comp = Poetry.objects.filter(paragraphs__contains=keyword1[tmp_index])
        output_poem_obj = output_poem_obj_comp[random.randint(0, output_poem_obj_comp.count() + 1)]

        for sentence in output_poem_obj.paragraphs.split(";"):
            if keyword1[tmp_index] in sentence:
                output_poem_sentence = sentence

        tmp_index += 1
        if tmp_index > (len(keyword1) - 1):
            tmp_index = 0

    round_number += 1
    # Var_Transfer.set_value("round_number", round_number)
    played_flag = 0  # 判别这首诗是否已经被说过

    if output_poem_obj in played_poems:
        played_flag = 1

    if played_flag == 0:
        # Var_Transfer.set_value("return_computer_str", sentence.rstrip("\n"))
        # Var_Transfer.set_value("return_computer_poem", poem_object)
        played_poems.append(output_poem_obj)

        return [output_poem_sentence, output_poem_obj, round_number]


def basic_feihua_user_round(keyword1, keyword2, mode, sentence_input):

    global match_poem_obj_comp, round_number, played_poems, tmp_index
    output_poem_sentence_user = ""

    def identify_sentence(sentence):
        """
        鉴别单句是否满足要求
        :param sentence: 待鉴别的原始单句
        :return: Return 3 说明被识别
        """
        if mode == "firstonly":  # 只需满足字在第一个集合内
            for char in keyword1:
                if char:
                    if re.match(r'.*%s.*' % char, sentence):
                        return 3
        elif mode == "secondonly":  # 只需满足字在第二个集合内
            for char in keyword2:
                if char:
                    if re.match(r'.*%s.*' % char, sentence):
                        return 3
        elif mode == "both":  # 需同时满足两个集合内的字
            count = 0
            for char in keyword1:
                if char:
                    if re.match(r'.*%s.*' % char, sentence):
                        count += 1
                        break
            for char in keyword2:
                if char:
                    if re.match(r'.*%s.*' % char, sentence):
                        count += 1
                        break
            if count == 2:
                return 3
        elif mode == "taketurnfirst":  # 第一个集合内轮流满足
            global tmp_index
            if re.match(r'.*%s.*' % keyword1[tmp_index], sentence):
                # print("Keyword Match: %s" % keyword1[tmp_index])
                tmp_index += 1
                if tmp_index > (len(keyword1) - 1):
                    tmp_index = 0
                return 3

    try:
        debug_token = 1
        # 用于捕获错误的token
        # 0_找到
        # 1_正常执行循环，但未找到
        # 3_与已有重复
        # 4_根本不含关键词或一开始的正则就不匹配
        sentence_idf_loose = r'^.{3,7}((,|，).{3,7})?(\.|。)?$'
        sentence_idf_strict = r'^.{3,7}(,|，).{3,7}(\.|。)$'

        if sentence_input == "quit":
            raise KeyboardInterrupt  # To quit main Loop

        if re.match(sentence_idf_loose, sentence_input):

            sentence_input = sentence_input.replace(",", "，")
            sentence_input = sentence_input.replace(".", "。")

            if identify_sentence(sentence_input) == 3:  # 检验用户输入的句子内含不含关键词
                match_poem_obj_comp = Poetry.objects.filter(paragraphs__contains=sentence_input)

                if match_poem_obj_comp:
                    matched_poem = match_poem_obj_comp.first()

                    played_flag = 0
                    if matched_poem in played_poems:
                        played_flag = 1
                        debug_token = 3

                    if played_flag == 0:  # 得到一个匹配
                        played_poems.append(matched_poem)
                        debug_token = 0
                        # round_number += 1
                        for sentence in matched_poem.paragraphs.split(";"):
                            if sentence_input in sentence:
                                output_poem_sentence_user = sentence

                        return [output_poem_sentence_user, matched_poem, round_number]
                else:
                    debug_token = 1
            else:
                debug_token = 4
        else:
            debug_token = 4

        if debug_token == 1:
            return ["什么都没找到。"]
        if debug_token == 3:
            return ["这句诗已经说过了。"]
        else:
            return ["检查输入格式。"]
    except KeyboardInterrupt:
        print("Quit")