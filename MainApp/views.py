from django.shortcuts import render, HttpResponse, redirect
from MainApp.models import Poetry, Rule
from MainApp.core_scripts import Basic_feihua
from MainApp.core_scripts import Var_Transfer
import re
import time
import datetime
import random


# Create your views here.
def home(request):
    poem_count = Poetry.objects.count()  # This action will not query the database.
    return render(request, "home.html", {"poem_count": poem_count})


def poem_search(request):
    global error_message, result_list
    result_list = []
    error_message = ""

    def search_db(phr, auth):
        global _tmp_list
        _result_list = []
        _tmp_list = []
        if auth:
            if phr:
                _tmp_list = Poetry.objects.filter(author=auth, paragraphs__contains=phr)
            else:
                _tmp_list = Poetry.objects.filter(author=auth)
        else:
            if phr:
                _tmp_list = Poetry.objects.filter(paragraphs__contains=phr)

        for _obj in _tmp_list:
            _result_list.append([_obj.title, _obj.rhythmic, _obj.author, _obj.paragraphs.split(";")])
        return _result_list

    if request.method == "GET":
        return render(request, "poem_search.html")

    if request.method == "POST":
        key_phrase = request.POST.get("key_phrase")
        author = request.POST.get("author")

        result_list = search_db(key_phrase, author)
        result_length = "%s result(s) found." % len(result_list)

        return render(request, "poem_search.html",
                      {"result_length": result_length, "result_list": result_list, "error_message": error_message})


def advanced_feihua(request):
    global rand_rule, round_number, output_poem_obj_computer, output_poem_sentence_computer, output_poem_obj_user, output_poem_sentence_user

    if request.method == "GET":
        rand_rule = Rule.objects.filter(id=random.randint(1, Rule.objects.count())).first()
        print(rand_rule)
        rand_rule.keyword1 = rand_rule.keyword1.split(";")
        rand_rule.keyword2 = rand_rule.keyword2.split(";")

        print("Round initialized. " + str(time.time()))

        Basic_feihua.basic_feihua_init()
        [output_poem_sentence, output_poem_obj, round_number] = \
            Basic_feihua.basic_feihua_computer_round(rand_rule.keyword1, rand_rule.keyword2, rand_rule.mode)

        output_poem_obj.paragraphs = output_poem_obj.paragraphs.split(";")
        # print(output_poem_sentence, output_poem_obj, rand_rule.keyword1, rand_rule.keyword2, round_number)

        try:
            with open('MainApp/core_scripts/Savedata/save.txt','r') as savedata:
                for lines in savedata:
                    highscore = lines
        except FileNotFoundError:
            highscore = 0

        return render(request, "advanced_feihua.html",
                      {"poem_item": output_poem_obj,
                       "round_number": round_number,
                       "key_description": rand_rule.key_description,
                       "output_poem_sentence_computer": output_poem_sentence,
                       "highscore": highscore})

    if request.method == "POST":

        if request.POST.get('submit_highscore'):
            try:
                print("Leaderboard submitting..")
                Var_Transfer.init()
                Var_Transfer.set_value('round_number', round_number)
                return redirect('../advancedfeihua/leaderboard_submission/')
            except NameError:
                return redirect('../home/')

        try:
            rand_rule = rand_rule # Test if rule is defined
        except NameError:
            return redirect('../home/')

        user_input = request.POST.get("sentence")
        try:
            with open('MainApp/core_scripts/Savedata/save.txt','r') as savedata:
                for lines in savedata:
                    highscore = lines
        except FileNotFoundError:
            highscore = 0

        try:
            output_poem_sentence_user = output_poem_sentence_user
        except NameError:
            output_poem_sentence_user = " "
        try:
            output_poem_obj_user = output_poem_obj_user
        except NameError:
            output_poem_obj_user = " "

        result = Basic_feihua.basic_feihua_user_round(rand_rule.keyword1, rand_rule.keyword2, rand_rule.mode,
                                                      user_input)

        if len(result) == 1:  # Error occurred.
            # print(result[0])
            return render(request, "advanced_feihua.html", {"error_message": result[0],
                                                            "round_number": round_number,
                                                            "key_description": rand_rule.key_description,
                                                            "poem_item": output_poem_obj_user,
                                                            "output_poem_sentence_computer": output_poem_sentence_user,
                                                            "highscore": highscore})
        else:

            [output_poem_sentence_computer, output_poem_obj_computer, round_number] = result
            output_poem_obj_computer.paragraphs = output_poem_obj_computer.paragraphs.split(";")

            [output_poem_sentence_user, output_poem_obj_user, round_number] = \
                Basic_feihua.basic_feihua_computer_round(rand_rule.keyword1, rand_rule.keyword2, rand_rule.mode)
            output_poem_obj_user.paragraphs = output_poem_obj_user.paragraphs.split(";")

            return render(request, "advanced_feihua.html",
                          {"poem_item": output_poem_obj_user,
                           "poem_item_last": output_poem_obj_computer,
                           "round_number": round_number,
                           "key_description": rand_rule.key_description,
                           "output_poem_sentence_user": output_poem_sentence_computer,
                           "output_poem_sentence_computer": output_poem_sentence_user,
                           "highscore": highscore})


def advanced_feihua_leaderboard_submission(request):
    try:
        round_number = Var_Transfer.get_value('round_number')
        with open("MainApp/core_scripts/Savedata/save.txt",'w') as savedata:
            savedata.write(str(round_number))
            return redirect('../')

    except NameError:
        Var_Transfer.init()
        return redirect('../../home')