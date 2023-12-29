import ast
import os
from functools import wraps

from flask import *
from flask import Blueprint, request, render_template

from conference.views import search_res
from libs.db import DBSession, Tch, Stu, Account, Honor
from admins.models import Admin

honor_bp = Blueprint('honor', import_name='honor')
honor_bp.template_folder = './templates'
honor_bp.static_folder = './static'


# 荣誉称号
@honor_bp.route('/', methods=('GET', 'POST'))
def honor():
    sessions = DBSession()
    all_honor = sessions.query(Honor).all()
    return render_template('honor.html', honor_home=all_honor)

@honor_bp.route('/honor_add_tch_back', methods=('GET', 'POST'))
def honor_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Honor).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
            conf = sessions.query(Honor).filter(Honor.title.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    else:
            conf = sessions.query(Honor).filter(Honor.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        new['name'] = item.name+', '+item.title
        index += 1
        new['index'] = index
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[(curpage - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)

@honor_bp.route('/api/<account>', methods=('GET', 'POST'))
def honor_add_page(account):
    sessions = DBSession()
    tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().honor)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Honor).filter(Honor.id == key).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.title
            dic_t['author'] = jn.name
            count += 1
            dic_t['index'] = count
            dic_t['new_item']=jn.title
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)


# 教师荣誉称号添加界面
@honor_bp.route('/honor_add_tch/<account>/', methods=('GET', 'POST'))
def honor_add_tch(account, search=None):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('honor_add_tch.html',  user_account=tch_info, account_url=tch_info,
                           name="awards")


# 荣誉称号教师上传
@honor_bp.route('/honor_upload_tch/<account>/', methods=('GET', 'POST'))
def honor_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        adds = request.form.get('adds', '').strip()
        summary = {}
        summary['name'] = name
        summary['title'] = title
        new_honor = Honor(
            name=name,
            title=title,
            summary=str(summary)
        )
        sessions.add(new_honor)
        new_honor = sessions.query(Honor).filter(Honor.summary == str(summary)).first()
        if adds != str(1):
            sessions.commit()
            return redirect(url_for('users.tch_page', account=tch_info.account, account_url=tch_info))
        else:
            if tch_info.honor is None:
                tch_honor = []
                tch_honor.append(str(new_honor.id))
                tch_info.honor = str(tch_honor)
                sessions.commit()
                return redirect(url_for('users.tch_page', account=tch_info.account, account_url=tch_info))
            else:
                tch_honor = ast.literal_eval(tch_info.honor)
                tch_honor.append(str(new_honor.id))
                tch_info.honor = str(tch_honor)
                sessions.commit()
                return redirect(url_for('users.tch_page', account=tch_info.account, account_url=tch_info))
    return render_template('honor_upload_tch.html', tch_info=tch_info, account_url=tch_info)


# 用户添加论文主页后端
@honor_bp.route('/honor_add', methods=('GET', 'POST'))
def honor_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    if user is None:
        user = session.query(Stu).join(Account, Account.account == Stu.account).filter(Stu.account == account).first()
    honor_list = user.honor
    if honor_list is None:
        honor_list = []
    else:
        honor_list = eval(honor_list)
    if str(id) in honor_list:
        response['message'] = "荣誉称号已存在!"
        response['error'] = 1
        return json.dumps(response, ensure_ascii=False)
    honor_list.append(str(id))
    user.honor = str(honor_list)
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 用户添加论文主页后端
@honor_bp.route('/honor_delete', methods=('GET', 'POST'))
def honor_delete():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Honor).filter(Honor.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)


# 教师荣誉称号添加界面
@honor_bp.route('/honor_modify_tch/<honor_title_name>/<account>/', methods=('GET', 'POST'))
def honor_modify_tch(honor_title_name, account):
    sessions = DBSession()
    honor_title_name_list = honor_title_name.split(',')
    summary = {}
    summary['name'] = honor_title_name_list[1]
    summary['title'] = honor_title_name_list[0]
    print(summary)
    modify_honor = sessions.query(Honor).filter(Honor.summary == str(summary)).first()
    print(modify_honor)
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        modify_honor.name = name
        modify_honor.title = title
        summary_new = {}
        summary_new['name'] = name
        summary_new['title'] = title
        modify_honor.summary = str(summary_new)
        sessions.commit()

    return render_template('honor_modify_tch.html', honor_home=modify_honor, tch_info=tch_info, account_url=tch_info)

@honor_bp.route('/table', methods=('GET', 'POST'))
def table():
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))
    honors=Admin(Honor,'honor').getAll()['data']
    response_items = []
    for honor in honors:
        response_items.append(honor)
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