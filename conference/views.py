import ast
import datetime
import math
import time
import logging
import os
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy import func, or_
from sqlalchemy.cyextension.processors import str_to_date
from libs.db import DBSession, Conf, Account, Tch, Stu, People, Jn
from login.views import login_required
import re
from xpinyin import Pinyin
from urllib.parse import quote, unquote
from file_save.file_Save import save_File

conference_bp = Blueprint('conference', import_name='conference')
conference_bp.template_folder = './templates'
conference_bp.static_folder = './static'
from admins.models import Admin


# 会议论文界面
@conference_bp.route('/', methods=('GET', 'POST'))
def conference():
    sessions = DBSession()
    admins=sessions.query(Tch).filter(Tch.account=='admin').first()
    all_conferences=eval(admins.journal)
    display=eval(admins.display)
    display_conferences=display['jn']
    all_conf = []
    for id in all_conferences:
        if id not in display_conferences:
            continue
        if id[0]=='c':
            conference_one=Admin(Conf,'conference').getOne(int(id[1:]))
        else:
            conference_one = Admin(Jn, 'journal').getOne(int(id[1:]))
        if conference_one is not None:
            all_conf.append(conference_one)
    return render_template('conference.html', conf_home=all_conf)


def judge(word, data):
    pattern = '.*%s.*' % (word)
    regex = re.compile(pattern, re.IGNORECASE)
    return regex.search(data)


def conference_add(account, count, name):
    sessions = DBSession()
    tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().conference)
    data = []
    for key, value in tch_info.items():
        con = sessions.query(Conf).filter(Conf.id == eval(key)).first()
        if con is not None:
            dic_t = dict()
            dic_t['id'] = 'c' + str(con.id)
            dic_t['name'] = con.name
            dic_t['author'] = con.author
            count += 1
            dic_t['index'] = count
            dat = datetime.datetime.strftime(con.dat, "%Y-%m-%d")
            author = ""
            for item in value:
                author += item
                author += ' '
            new_item = con.name + ', ' + con.author + ', ' + dat + ', (' + con.conf_name + ') ' + author.rstrip(' ')
            dic_t['new_item'] = new_item
            if name is None:
                data.append(dic_t)
            elif name is not None and judge(name, con.name) is not None:
                data.append(dic_t)
            else:
                count -= 1
    return data


# 会议论文推荐目录页面
@conference_bp.route('/conf_rec', methods=('GET', 'POST'))
def conf_rec():
    sessions = DBSession()
    conf_rec = sessions.query(Conf).all()
    if request.method == 'POST':
        return render_template('conf_rec.html', conf=conf_rec)
    else:
        return render_template('conf_rec.html', conf=conf_rec)


# 会议论文学生推荐
@conference_bp.route('/conf_rec_stu/<account>/', methods=('GET', 'POST'))
def conf_rec_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    conf_rec = sessions.query(Conf).all()
    if request.method == 'POST':
        return render_template('conf_rec_stu.html', conf=conf_rec, stu_info=stu_info, account_url=stu_info)
    else:
        return render_template('conf_rec_stu.html', conf=conf_rec, stu_info=stu_info, account_url=stu_info)


# 会议论文教师推荐
@conference_bp.route('/conf_rec_tch/<account>/', methods=('GET', 'POST'))
def conf_rec_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    conf_rec = sessions.query(Conf).all()
    return render_template('conf_rec_tch.html', conf=conf_rec, tch_info=tch_info, account_url=tch_info)


# 论文详情(学生界面)
@conference_bp.route('/conf_home_stu/<account>/<id>', methods=('GET', 'POST'))
def conf_home_stu(account, id):
    sessions = DBSession()
    uid = session.get('uid')
    conf_home = sessions.query(Conf).filter(Conf.id == id).first()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('conf_home_stu.html', conf=conf_home, stu_info=stu_info, id=id, account_url=stu_info)


# 论文详情(教师界面)
@conference_bp.route('/conf_home_tch/<account>/<id>', methods=('GET', 'POST'))
def conf_home_tch(account, id):
    sessions = DBSession()
    uid = session.get('uid')
    conf_home = sessions.query(Conf).filter(Conf.id == id).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('conf_home_tch.html', conf=conf_home, tch_info=tch_info, id=id, account_url=tch_info)


# 论文详情
@conference_bp.route('/conf_home/<id>', methods=('GET', 'POST'))
def conf_home(id):
    sessions = DBSession()
    conf_home = sessions.query(Conf).filter(Conf.id == id).first()
    return render_template('conf_home.html', conf=conf_home)


# 用户添加论文主页后端
@conference_bp.route('/conf_add_page', methods=('GET', 'POST'))
def conf_add_page():
    data = request.get_json()
    account = data['account']
    id = data['id']
    sessions = DBSession()
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    display = (eval(user_info.display))
    display['conf'] = id
    user_info.display = str(display)
    sessions.commit()
    response = dict()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 用户添加论文主页后端
@conference_bp.route('/conf_add', methods=('GET', 'POST'))
def conf_add():
    data = request.get_json()
    account = data['account']
    id = data['id']
    list = data['select']
    arr = ['第一作者', '共同一作', '通讯作者', '其他作者']
    conf_list = []
    for i in range(4):
        if list[i] == 1:
            conf_list.append(arr[i])
    sessions = DBSession()
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    if user_info.conference is None:
        tch_info = dict()
    else:
        tch_info = eval(user_info.conference)
    tch_info[str(id)] = conf_list
    user_info.conference = str(tch_info)
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def topingyin(search):
    if search is None:
        search = ""
    p = Pinyin()
    if len(search) == 1:
        res = ""
        res += p.get_pinyin(search[0])
        return res
    elif len(search) == 2:
        res = ""
        res += p.get_pinyin(search[1])
        res += p.get_pinyin(search[0])
        return res
    else:
        res = ""
        res += p.get_pinyin(search[1])
        res += p.get_pinyin(search[2])
        res += ' '
        res += p.get_pinyin(search[0])
        return res


def author_transfrom(authorpre):
    author = authorpre.replace(',', '').replace('and', ',')
    return author





@conference_bp.route('/conf_add_tch_back', methods=('GET', 'POST'))
def conf_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Conf).order_by(Conf.id).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
        if is_Chinese(content):
            conf = sessions.query(Conf).filter(Conf.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
        else:
            contentlower = content.lower().strip(" ")
            conf = sessions.query(Conf).filter(func.lower(Conf.name).ilike('%{word}%'.format(word=contentlower))).all()
    else:
        if is_Chinese(content.replace(" ", "")):
            word = topingyin(content.replace(" ", ""))
            conf = sessions.query(Conf).filter(or_(func.lower(Conf.author).ilike('%{word}%'.format(word=word)),
                                                   func.lower(Conf.author).ilike(
                                                       '%{word}%'.format(word=content.rstrip())))).all()
        else:
            newcontent = content.replace(" ", "").lower()
            lenth = len(newcontent)
            word1 = newcontent[2:] + ' ' + newcontent[0:2]
            word2 = newcontent[3:] + ' ' + newcontent[0:3]
            word3 = newcontent[4:] + ' ' + newcontent[0:4]
            word4 = newcontent[5:] + ' ' + newcontent[0:5]
            word5 = newcontent[0:lenth - 2] + ' ' + newcontent[lenth - 2:]
            word6 = newcontent[0:lenth - 3] + ' ' + newcontent[lenth - 3:]
            word7 = newcontent[0:lenth - 4] + ' ' + newcontent[lenth - 4:]
            word8 = newcontent[0:lenth - 5] + ' ' + newcontent[lenth - 5:]
            conf = sessions.query(Conf).filter(or_(func.lower(Conf.author).ilike('%{word}%'.format(word=word1)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word2)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word3)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word4)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word5)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word6)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word7)),
                                                   func.lower(Conf.author).ilike('%{word}%'.format(word=word8)),
                                                   func.lower(Conf.author).ilike(
                                                       '%{word}%'.format(word=content.lower())))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        dat = item.dat
        new['name'] = author_transfrom(
            item.author) + ', ' + '"' + item.name + '," in ' + item.conf_name + ', ' + dat
        if item.page != '':
            new['name'] += ', pp.' + item.page
        index += 1
        new['index'] = index
        new['conf_name'] = item.name
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)


# 教师会议论文添加界面前端
@conference_bp.route('/conf_add_tch/<account>/', methods=('GET', 'POST'))
def conf_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('conf_add_tch.html', user_account=tch_info, account_url=tch_info, name='conferences')





def search_res(db, word, search_item):
    sessions = DBSession()
    data = sessions.query(db).all()
    suggestions = []
    pattern = '.*%s.*' % (word)
    regex = re.compile(pattern, re.IGNORECASE)
    for item in data:
        if search_item == 'title_search':
            match = regex.search(item.name)
        else:
            match = regex.search(item.author)
        if match:
            new = dict()
            new['id'] = item.id
            new['name'] = item.name
            author_all = ""
            for item in eval(item.summary)['author']:
                author_all += item
                author_all += ','
            new['author'] = author_all.strip(',')
            suggestions.append(new)
    return suggestions


# 会议论文教师上传
@conference_bp.route('/conf_upload_back', methods=('GET', 'POST'))
def conf_upload_tch_back():
    sessions = DBSession()
    encd = request.files['encd']
    code_encd = request.files['code_encd']
    form_dic = request.values.to_dict()
    isteacher = 1
    account = form_dic['account']
    response = dict()
    if sessions.query(Conf).filter(Conf.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！论文已存在'
        return json.dumps(response, ensure_ascii=False)
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        isteacher = 0
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    if form_dic['dat'] == '':
        form_dic['dat'] = ('1990')
    if form_dic['conf_dat'] == '':
        form_dic['conf_dat'] = ('1990-1-1')
    # print(form_dic['conf_dat'])
    summary = {}
    summary['name'] = form_dic['name']
    summary['author'] = form_dic['author']
    summary['DOI'] = form_dic['DOI']
    # print(datetime.datetime.strptime(form_dic['dat'], '%Y-%m-%d').strftime('%Y'))
    new_conf = Conf(
        name=form_dic['name'],
        author=form_dic['author'],
        summary=str(summary),
        conf_name=form_dic['conf_name'],
        organizer=form_dic['organizer'],
        conf_dat=datetime.datetime.strptime(form_dic['conf_dat'], '%Y-%m-%d'),
        dat=datetime.datetime.strptime(form_dic['dat'], '%Y'),
        page=form_dic['page'],
        address=form_dic['address'],
        num=form_dic['num'],
        DOI=form_dic['DOI'],
        employ=form_dic['employ'],
        employ_num=form_dic['employ_num'],
        ccf=form_dic['ccf'],
        times=form_dic['times'],
        link=form_dic['link'],
        code_link=form_dic['code_link'])
    sessions.add(new_conf)
    new_conf = sessions.query(Conf).filter(Conf.name == form_dic['name']).first()
    new_conf.encd = '../conference/static/conference_encd/%s' % new_conf.id + '.pdf'
    new_conf.code_encd = '../conference/static/conference_code/%s' % new_conf.id
    if encd:
        save_File('conference', encd, str(new_conf.id) + '.pdf')
    if code_encd:
        save_File('conference', code_encd, str(new_conf.id))
    author_classify = form_dic['author_classify']
    if author_classify[0] != '非作者':
        conf = eval(user_info.conference)
        conf[str(new_conf.id)] = author_classify
        user_info.conference = str(conf)
    response['error'] = 0
    response['msg'] = '上传成功'
    if isteacher == 1:
        response['url'] = '/conference/conf_home_tch/' + user_info.account + '/' + str(new_conf.id)
    else:
        response['url'] = '/conference/conf_home_stu/' + user_info.account + '/' + str(new_conf.id)
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 会议论文学生上传
@conference_bp.route('/conf_upload_stu/<account>/', methods=('GET', 'POST'))
def conf_upload_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('conf_upload_stu.html', stu_info=stu_info, account_url=stu_info)


# 会议论文学生上传
@conference_bp.route('/conf_upload_tch/<account>/', methods=('GET', 'POST'))
def conf_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('conf_upload_tch.html', tch_info=tch_info, account_url=tch_info)


@conference_bp.route('/conf_modify_back', methods=('GET', 'POST'))
def conf_midify():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Conf).filter(
            Conf.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，论文已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_conf = sessions.query(Conf).filter(Conf.name == form_dic['pre']).first()
    if form_dic['dat'] == '':
        form_dic['dat'] = str_to_date('1990-1-1')
    if form_dic['conf_dat'] == '':
        form_dic['conf_dat'] = str_to_date('1990-1-1')
    encd = request.files['encd']
    if encd:
        save_File('conference', encd, str(modify_conf.id) + '.pdf')
    code_encd = request.files['code_encd']
    if code_encd:
        save_File('conference', code_encd, str(modify_conf.id))
    summary = {'name': form_dic['name'], 'author': form_dic['author'], 'DOI': form_dic['DOI']}
    modify_conf.summary = str(summary)
    modify_conf.name = form_dic['name']
    modify_conf.conf_name = form_dic['conf_dat']
    modify_conf.organizer = form_dic['organizer']
    modify_conf.author = form_dic['author']
    modify_conf.conf_dat = datetime.datetime.strptime(form_dic['conf_dat'], '%Y-%m-%d')
    modify_conf.dat = datetime.datetime.strptime(form_dic['dat'], '%Y')
    modify_conf.page = form_dic['page']
    modify_conf.address = form_dic['address']
    modify_conf.num = form_dic['num']
    modify_conf.DOI = form_dic['DOI']
    modify_conf.employ = form_dic['employ']
    modify_conf.employ_num = form_dic['employ_num']
    modify_conf.ccf = form_dic['ccf']
    modify_conf.times = form_dic['times']
    modify_conf.link = form_dic['link']
    modify_conf.code_link = form_dic['code_link']
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 教师会议修改
@conference_bp.route('/conf_modify_tch/<conf_name>/<account>/', methods=('GET', 'POST'))
def conf_modify_tch(conf_name, account):
    sessions = DBSession()
    account = unquote(account, 'utf-8')
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    modify_conf = sessions.query(Conf).filter(Conf.name == conf_name).first()
    modify_conf.dat = modify_conf.dat.year
    return render_template('conf_modify_tch.html', conf_home=modify_conf, account_url=tch_info, account=account)


# 教师会议删除
@conference_bp.route('/conf_delete', methods=('GET', 'POST'))
def conf_delete():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Conf).filter(Conf.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)


def author_name(name):
    name_list = []
    for i in range(5):
        x = request.form.get(name + str(i + 1), '').strip()
        if x != '':
            name_list.append(x)
    return name_list


# 把作者的字符串转为
def author_list(author):
    author_list = []
    author = author.split(' and ')
    for row in author:
        row = row.split(',')
        for i in row:
            author_list.append(i)
    return author_list


# 教师会议删除
@conference_bp.route('/api', methods=('GET', 'POST'))
def api():
    sessions = DBSession()
    sort = eval(sessions.query(People).first().faculty)
    response = []
    for index in sort:
        print(index)
        item = sessions.query(Tch).filter(Tch.id == int(index)).first()
        print(item)
        every_response = dict()
        info = dict()
        every_response['status'] = 1
        every_response['classify'] = 0
        info['name'] = item.name
        info['Eng_name'] = item.Eng_name
        info['phone'] = item.phone
        info['email'] = item.email
        info['profile'] = item.profile
        info['address'] = item.address
        info['profile_c'] = item.profile_c
        info['direction'] = item.direction
        info['avatar'] = item.avatar
        every_response['info'] = info
        confdisplay = eval(item.display)
        # for i in range(0,len(confdisplay['jn'])):
        #     confdisplay['jn'][i]['id']=i+1
        every_response['conference'] = confdisplay['jn']
        # for i in range(0, len(confdisplay['patent'])):
        #     confdisplay['patent'][i]['id'] = i + 1
        every_response['patent'] = confdisplay['patent']
        # for i in range(0, len(confdisplay['soft'])):
        #     confdisplay['soft'][i]['id'] = i + 1
        every_response['softwareCopyright'] = confdisplay['soft']
        # for i in range(0, len(confdisplay['mono'])):
        #     confdisplay['mono'][i]['id'] = i + 1
        every_response['monograph'] = confdisplay['mono']
        # for i in range(0, len(confdisplay['honor'])):
        #     confdisplay['honor'][i]['id'] = i + 1
        every_response['honor'] = confdisplay['honor']
        # for i in range(0, len(confdisplay['prog'])):
        #     confdisplay['prog'][i]['id'] = i + 1
        every_response['project'] = confdisplay['prog']
        # for i in range(0, len(confdisplay['comp'])):
        #     confdisplay['comp'][i]['id'] = i + 1
        every_response['competition'] = confdisplay['comp']
        # for i in range(0, len(confdisplay['course'])):
        #     confdisplay['course'][i]['id'] = i + 1
        every_response['course'] = confdisplay['course']
        response.append(every_response)
    return json.dumps(response, ensure_ascii=False)
