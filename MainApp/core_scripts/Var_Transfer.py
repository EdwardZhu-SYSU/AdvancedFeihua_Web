def init():
    """
    跨文件流转的变量信息
    var poem_object_comp (list): 存储所有的poem对象
    var rule (object): 存储单条飞花规则
    var usr_input_sentence (string): 存储用户输入的句子

    var return_computer_str (string): 存储回合中程序接句子的信息
    var return_computer_poem (object)
    var return_usr_str (string): 存储回合中程序返回的用户接句子的信息
    var return_usr_poem (object)

    var exception_info (string): 存储判断中的错误提示信息
    var round_number (int): 第几回合

    """
    global global_dict
    global_dict = {}


def set_value(name, value):
    global_dict[name] = value


def get_value(name, def_value=None):
    try:
        return global_dict[name]
    except KeyError:
        return def_value
