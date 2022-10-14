import json
import os
import random

from zhconv import convert

from MainApp.models import Poetry

poem_comp = []
file_list = []


class poem_single(object):
    def __init__(self, title, rhythmic, author, paragraphs):
        self.title = title
        self.rhythmic = rhythmic
        self.author = author
        self.paragraphs = paragraphs

    def translate_to_simplified_chinese(self):
        self.title = convert(self.title, 'zh-cn')
        self.author = convert(self.author, 'zh-cn')
        self.rhythmic = convert(self.rhythmic, 'zh-cn')

        for _ in range(0, len(self.paragraphs) - 1):
            self.paragraphs[_] = convert(self.paragraphs[_], 'zh-cn')


def walk_directory(directory):
    file_list.clear()

    for root, dirs, files in os.walk(directory):
        for indv_dir in dirs:
            file_list.append(str(os.path.join(root, indv_dir)))
        for file in files:
            file_list.append(str(os.path.join(root, file)))


def establish_database(source_json_dir):
    print("Building Database..")

    walk_directory(source_json_dir)

    for filedir in file_list:
        if filedir.endswith(".json"):
            try:
                with open(filedir, "r", encoding="UTF-8") as target_json:

                    for indv_object in json.load(target_json):
                        if "rhythmic" not in indv_object:
                            indv_object["rhythmic"] = ""
                        if "title" not in indv_object:
                            indv_object["title"] = ""
                        if "author" not in indv_object:
                            indv_object["author"] = ""
                        if "paragraphs" not in indv_object:
                            indv_object["paragraphs"] = ""

                        poem_comp.append(
                            poem_single(indv_object["title"], indv_object["rhythmic"], indv_object["author"],
                                        indv_object["paragraphs"]))
            except IOError:
                return "IOError"

    random.shuffle(poem_comp)
    print("Database Curating Completed. %s Poems Catalogued.\n\n" % len(poem_comp))

    print("Deleting original data and writing new data.")
    Poetry.objects.all().delete()
    print("Removed all existing objects.")

    for indv_poem in poem_comp:
        indv_poem.translate_to_simplified_chinese()  # No need to follow an object, already defined.

        # print(indv_poem.title, indv_poem.rhythmic, indv_poem.author, ";".join(indv_poem.paragraphs))
        try:
            Poetry.objects.create(title=indv_poem.title, rhythmic=indv_poem.rhythmic, author=indv_poem.author,
                                  paragraphs=";".join(indv_poem.paragraphs))
        except:
            pass

    print("Database exported.")
