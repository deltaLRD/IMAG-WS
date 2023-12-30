import ast
import datetime
import logging
import math
import os
import re

from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy import func, or_
from sqlalchemy.cyextension.processors import str_to_date

from admins.models import Admin
from conference.views import author_name, author_list, search_res, conference_add, is_Chinese, topingyin, \
    author_transfrom
from libs.db import DBSession, Tch, Stu, Account, Jn, Conf
from login.views import login_required
from file_save.file_Save import save_File

journal_bp = Blueprint('journal', import_name='journal')
journal_bp.template_folder = './templates'
journal_bp.static_folder = './static'


# 期刊论文界面
@journal_bp.route('/', methods=('GET', 'POST'))
def journal():
    sessions = DBSession()
    all_jn = sessions.query(Jn).all()
    return render_template('journal.html', jn_home=all_jn)


# 会议论文推荐目录页面
@journal_bp.route('/jn_rec', methods=('GET', 'POST'))
def jn_rec():
    sessions = DBSession()
    uid = session.get('uid')
    jn_rec = sessions.query(Jn).all()
    if request.method == 'POST':
        return render_template('jn_rec.html', jn=jn_rec)
    else:
        return render_template('jn_rec.html', jn=jn_rec)


# 会议论文学生推荐
@journal_bp.route('/jn_rec_stu/<account>/', methods=('GET', 'POST'))
def jn_rec_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    jn_rec = sessions.query(Jn).all()
    # sessions['account'] = account
    if request.method == 'POST':
        return render_template('jn_rec_stu.html', jn=jn_rec, stu_info=stu_info, account_url=stu_info)
    else:
        return render_template('jn_rec_stu.html', jn=jn_rec, stu_info=stu_info, account_url=stu_info)


# 会议论文教师推荐
@journal_bp.route('/jn_rec_tch/<account>/', methods=('GET', 'POST'))
def jn_rec_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    jn_rec = sessions.query(Jn).all()
    # sessions['account'] = account
    if request.method == 'POST':
        return render_template('jn_rec_tch.html', jn=jn_rec, tch_info=tch_info, account_url=tch_info)
    else:
        return render_template('jn_rec_tch.html', jn=jn_rec, tch_info=tch_info, account_url=tch_info)


def judge(word, data):
    pattern = '.*%s.*' % (word.strip(" "))
    regex = re.compile(pattern, re.IGNORECASE)
    return regex.search(data)


# 会议论文学生上传
@journal_bp.route('/jn_upload_stu/<account>/', methods=('GET', 'POST'))
def jn_upload_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('jn_upload_stu.html', stu_info=stu_info, account_url=stu_info)


# 会议论文学生上传
@journal_bp.route('/jn_upload_tch/<account>/', methods=('GET', 'POST'))
def jn_upload_tch(account):
    sessions = DBSession()
    stu_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('jn_upload_tch.html', stu_info=stu_info, account_url=stu_info)


@journal_bp.route('/api/<account>', methods=('GET', 'POST'))
def journal_add_page(account):
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    name = request.args.get('name')
    tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().journal)
    count = 0
    data = []
    for key, value in tch_info.items():
        jn = sessions.query(Jn).filter(Jn.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = 'j' + str(jn.id)
            dic_t['name'] = jn.name
            dic_t['author'] = jn.author
            count += 1
            dic_t['index'] = count
            dat = datetime.datetime.strftime(jn.dat, "%Y-%m-%d")
            author = ""
            for item in value:
                author += item
                author += ' '
            new_item = jn.name + ', ' + jn.author + ', ' + dat + ', (' + jn.jn_name + ') ' + author.rstrip(' ')
            dic_t['new_item'] = new_item
            if name is None:
                data.append(dic_t)
            elif name is not None and judge(name, jn.name) is not None:
                data.append(dic_t)
            else:
                count -= 1
    data += conference_add(account, count, name)
    lenth = len(data)
    response = dict()
    response['code'] = 0
    response['data'] = data[(curpage - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = lenth
    return json.dumps(response, ensure_ascii=False)


# 论文详情(学生界面)
@journal_bp.route('/jn_home_stu/<account>/<id>', methods=('GET', 'POST'))
@login_required
def jn_home_stu(account, id):
    sessions = DBSession()
    jn_home = sessions.query(Jn).filter(Jn.id == id).first()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('jn_home_stu.html', jn=jn_home, stu_info=stu_info, id=id, account_url=stu_info)


# 论文详情(教师界面)
@journal_bp.route('/jn_home_tch/<account>/<id>', methods=('GET', 'POST'))
# @login_required
def jn_home_tch(account, id):
    sessions = DBSession()
    jn_home = sessions.query(Jn).filter(Jn.id == id).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('jn_home_tch.html', jn=jn_home, tch_info=tch_info, id=id, account_url=tch_info)


@journal_bp.route('/table', methods=('GET', 'POST'))
def table():
    req=request.json
    account=req['account']
    page=int(req['page'])
    limit=int(req['limit'])
    item_type=req['type']
    session=DBSession()
    confs = Admin(Conf, 'conference').getAll()['data']
    tch_info=session.query(Tch).filter(Tch.account==account).first()
    items=eval(getattr(tch_info,item_type))
    journals = Admin(Jn, 'journal').getAll()['data']
    response_items = []
    for conf in confs:
        if 'c'+str(conf['id']) in items:
            conf['is_added']=True
        else:
            conf['is_added']=False
        
        conf['display_name']=str(conf['name'])+' ,('+str(conf['conf_name'])+')'
        conf['id']='c'+str(conf['id'])
        response_items.append(conf)
        
    for journal in journals:
        if 'j'+str(journal['id']) in items:
            journal['is_added']=True
        else:
            journal['is_added']=False
            
        journal['display_name']=str(journal['name'])+' ,('+str(journal['jn_name'])+')'
        journal['id']='j'+str(journal['id'])
        response_items.append(journal)
    

    start_index=(page-1)*limit
    end_index=start_index+limit
    total_items=len(response_items)
    start_index=min(start_index,total_items)
    end_index=min(end_index,total_items)
    res_page=response_items[start_index:end_index]
    res={
        "code":0,
        "msg":"",
        "count":total_items,
        "data":res_page
    }
    return res


# 论文详情
@journal_bp.route('/jn_home/<id>', methods=('GET', 'POST'))
def jn_home(id):
    sessions = DBSession()
    jn_home = sessions.query(Jn).filter(Jn.id == id).first()
    return render_template('jn_home.html', jn=jn_home)


# 教师期刊添加界面
@journal_bp.route('/jn_add_tch/<account>/', methods=('GET', 'POST'))
def jn_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('jn_add_tch.html', user_account=tch_info, account_url=tch_info, name="journals")


@journal_bp.route('/table', methods=('GET', 'POST'))
def jn_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Jn).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
        if is_Chinese(content):
            conf = sessions.query(Jn).filter(Jn.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
        else:
            contentlower = content.lower().strip(" ")
            conf = sessions.query(Jn).filter(func.lower(Jn.name).ilike('%{word}%'.format(word=contentlower))).all()
    else:
        if is_Chinese(content.replace(" ", "")):
            word = topingyin(content.replace(" ", ""))
            conf = sessions.query(Jn).filter(or_(func.lower(Jn.author).ilike('%{word}%'.format(word=word)),
                                                 func.lower(Jn.author).ilike(
                                                     '%{word}%'.format(word=content.strip())))).all()
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
            conf = sessions.query(Jn).filter(or_(func.lower(Jn.author).ilike('%{word}%'.format(word=word1)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word2)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word3)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word4)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word5)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word6)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word7)),
                                                 func.lower(Jn.author).ilike('%{word}%'.format(word=word8)),
                                                 func.lower(Jn.author).ilike(
                                                     '%{word}%'.format(word=content.lower())))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        dat = str(item.dat)
        new['name'] = author_transfrom(
            item.author) + ', ' + '"' + item.name + '," in ' + item.jn_name + ', ' + dat
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
                       min(curpage - 1, math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)


# 学生期刊添加界面
@journal_bp.route('/jn_add_stu/<account>/', methods=('GET', 'POST'))
def jn_add_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('jn_add_stu.html', user_account=stu_info, account_url=stu_info, name="journals")


# 用户添加论文主页后端
@journal_bp.route('/jn_add/', methods=('GET', 'POST'))
def jn_add():
    data = request.get_json()
    account = data['account']
    id = data['id']
    list = data['select']
    arr = ['第一作者', '共同一作', '通讯作者', '其他作者']
    jn_list = []
    for i in range(4):
        if list[i] == 1:
            jn_list.append(arr[i])
    sessions = DBSession()
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    if user_info.journal is None:
        tch_info = dict()
    else:
        tch_info = eval(user_info.journal)
    tch_info[str(id)] = jn_list
    user_info.journal = str(tch_info)
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 期刊论文教师上传
@journal_bp.route('/jn_upload_back', methods=('GET', 'POST'))
def jn_upload_back():
    sessions = DBSession()
    encd = request.files['encd']
    code_encd = request.files['code_encd']
    form_dic = request.values.to_dict()
    account = form_dic['account']
    response = dict()
    if sessions.query(Jn).filter(Jn.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！论文已存在'
        return json.dumps(response, ensure_ascii=False)
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    if form_dic['dat'] == '':
        form_dic['dat'] = '1990'
    summary = {'name': form_dic['name'], 'author': form_dic['author'], 'DOI': form_dic['DOI']}
    new_jn = Jn(
        name=form_dic['name'],
        author=form_dic['author'],
        summary=str(summary),
        jn_name=form_dic['jn_name'],
        dat=datetime.datetime.strptime(form_dic['dat'], '%Y'),
        page=form_dic['page'],
        num=form_dic['num'],
        DOI=form_dic['DOI'],
        employ=form_dic['employ'],
        employ_num=form_dic['employ_num'],
        ccf=form_dic['ccf'],
        cas=form_dic['cas'],
        jcr=form_dic['jcr'],
        times=form_dic['times'],
        vol=form_dic['vol'],
        no=form_dic['no'],
        link=form_dic['link'],
        code_link=form_dic['code_link'],
        encd='../journal/static/journal_encd/%s' % form_dic['name'] + '.pdf',
        code_encd='../journal/static/journal_code/%s' % form_dic['name'],
    )
    sessions.add(new_jn)
    new_jn = sessions.query(Jn).filter(Jn.name == form_dic['name']).first()
    new_jn.encd = '../journal/static/journal_encd/%s' % new_jn.id + '.pdf'
    new_jn.code_encd = '../journal/static/journal_code/%s' % new_jn.id
    if encd:
        save_File('journal', encd, str(new_jn.id) + '.pdf')
    if code_encd:
        save_File('journal', code_encd, str(new_jn.id))
    author_classify = form_dic['author_classify']
    if author_classify[0] != '非作者':
        conf = eval(user_info.journal)
        conf[str(new_jn.id)] = author_classify
        user_info.journal = str(conf)
    response['url'] = '/journal/jn_home_tch/' + user_info.account + '/' + str(new_jn.id)
    sessions.commit()
    sessions.close()
    response['error'] = 0
    response['msg'] = '上传成功'
    return json.dumps(response, ensure_ascii=False)


# 期刊教师修改
@journal_bp.route('/jn_modify_tch/<jn_name>/<account>/', methods=('GET', 'POST'))
def jn_modify_tch(jn_name, account):
    sessions = DBSession()
    modify_jn = sessions.query(Jn).filter(Jn.name == jn_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    modify_jn.dat = modify_jn.dat.year
    return render_template('jn_modify_tch.html', jn_home=modify_jn, account=account, account_url=tch_info)


@journal_bp.route('/jn_modify_back', methods=('GET', 'POST'))
def jn_modify_back():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Jn).filter(
            Jn.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，论文已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_jn = sessions.query(Jn).filter(Jn.name == form_dic['pre']).first()
    if form_dic['dat'] == '':
        form_dic['dat'] = ('1990')
    encd = request.files.get('encd')
    code_encd = request.files.get('code_encd')
    if encd:
        save_File('journal', encd, str(modify_jn.id) + '.pdf')
    if code_encd:
        save_File('journal', code_encd, str(modify_jn.id))
    summary = {'name': form_dic['name'], 'author': form_dic['author'].strip().split(','),
               'DOI': form_dic['DOI']}
    modify_jn.name = form_dic['name']
    modify_jn.jn_name = form_dic['jn_name']
    modify_jn.author = form_dic['author']
    modify_jn.dat = datetime.datetime.strptime(form_dic['dat'], '%Y'),
    modify_jn.num = form_dic['num']
    modify_jn.employ = form_dic['employ']
    modify_jn.employ_num = form_dic['employ_num']
    modify_jn.ccf = form_dic['ccf']
    modify_jn.cas = form_dic['cas']
    modify_jn.jcr = form_dic['jcr']
    modify_jn.times = form_dic['times']
    modify_jn.vol = form_dic['vol']
    modify_jn.no = form_dic['no']
    modify_jn.page = form_dic['page']
    modify_jn.DOI = form_dic['DOI']
    modify_jn.link = form_dic['link']
    modify_jn.code_link = form_dic['code_link']
    modify_jn.summary = str(summary)
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# # 期刊学生修改
# @journal_bp.route('/jn_modify_stu/<jn_name>/<account>/', methods=('GET', 'POST'))
# def jn_modify_stu(jn_name, account):
#     sessions = DBSession()
#     modify_jn = sessions.query(Jn).filter(Jn.name == jn_name).first()
#     stu_info = sessions.query(Stu).filter(Stu.account == account).first()
#     if request.method == "POST":
#         modify_jn.name = request.form.get('name', '').strip()
#         modify_jn.jn_name = request.form.get('jn_name', '').strip()
#         modify_jn.author = request.form.get('author', '').strip()
#         modify_jn.dat = request.form.get('dat', '')
#         modify_jn.num = request.form.get('num', '').strip()
#         modify_jn.employ = request.form.get('employ', '').strip()
#         modify_jn.employ_num = request.form.get('employ_num', '').strip()
#         modify_jn.ccf = request.form.get('ccf', '').strip()
#         modify_jn.cas = request.form.get('cas', '').strip()
#         modify_jn.jcr = request.form.get('jcr', '').strip()
#         modify_jn.times = request.form.get('times', '').strip()
#         modify_jn.vol = request.form.get('vol', '').strip()
#         modify_jn.no = request.form.get('no', '').strip()
#         modify_jn.page = request.form.get('page', '').strip()
#         modify_jn.DOI = request.form.get('DOI', '').strip()
#         modify_jn.link = request.form.get('link', '').strip()
#         modify_jn.code_link = request.form.get('code_link', '').strip()
#         author = request.form.get('author', '').strip().split(',')
#         summary = {}
#         summary['name'] = request.form.get('name', '').strip()
#         summary['author'] = author
#         summary['DOI'] = request.form.get('DOI', '').strip()
#         modify_jn.summary = str(summary)
#         modify_jn.encd = '../journal/static/journal_encd/%s' % modify_jn.name,
#         modify_jn.code_encd = '../journal/static/journal_code/%s' % modify_jn.name,
#         encd = request.files.get('encd')
#         code_encd = request.files.get('code_encd')
#         save_jn(modify_jn.name, encd)
#         save_code(modify_jn.name, code_encd)
#         sessions.commit()
#         return redirect(url_for('users.stu_page', account=account, account_url=stu_info))
#     return render_template('jn_modify_stu.html', jn_home=modify_jn, account=account, account_url=stu_info)


# 期刊教师删除
@journal_bp.route('/jn_delete', methods=('GET', 'POST'))
def jn_delete():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Jn).filter(Jn.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)
