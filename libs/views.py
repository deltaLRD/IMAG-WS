import ast
import os
from functools import wraps

from flask import *
from flask import Blueprint, request,render_template


# 论文添加函数
def add():
    res_dic = {}
    author_num = []
    if request.method == "POST":
        dataJSON = request.form
        data_dic = dataJSON.to_dict()
        addition = request.form.get('addition')
        print('----------------------------------------------------')
        print('addition', addition)
        print('typr',type(addition))
        print('json', data_dic)
        print('----------------------------------------------------')
        for every_paper in data_dic:
            if addition == '1':
                if 'adds' in every_paper:
                    temp = str(data_dic[every_paper]).strip()
                    # res_dic[temp] = data_dic['author_classify'+temp]
                    author_num.append(temp)
                for author in author_num:
                    tem = []
                    for every_paper in data_dic:
                        if 'author_classify' + author in every_paper:  # 对应的复选框的name+{id} 找出文章的作者
                            tem.append(data_dic[every_paper])
                    res_dic[author] = tem  # 将文章 与文章作者对应起来存进字典res_dic
    return res_dic