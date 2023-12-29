import ast
import datetime
import math
import os
from functools import wraps
from pickle import dump
import io
from werkzeug.datastructures import FileStorage
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy.cyextension.processors import str_to_date
from file_save.file_Save import save_File
from conference.views import search_res
from libs.db import DBSession, Tch, Stu, Account, Patent, Mono
from admins.models import Admin
monograph_bp = Blueprint('monograph', import_name='monograph')
monograph_bp.template_folder = './templates'
monograph_bp.static_folder = './static'


# 学术专著界面
@monograph_bp.route('/', methods=('GET', 'POST'))
def monograph():
    sessions = DBSession()
    all_mono = sessions.query(Mono).all()
    return render_template('monograph.html', mono_home=all_mono)


# 用户添加论文主页后端
@monograph_bp.route('/mono_add', methods=('GET', 'POST'))
def mono_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    if user is None:
        user = session.query(Stu).join(Account, Account.account == Stu.account).filter(Stu.account == account).first()
    mono_list = user.monograph
    if mono_list is None:
        mono_list = []
    else:
        mono_list = eval(mono_list)
    if str(id) in mono_list:
        response['message'] = "专著已存在!"
        response['error'] = 1
        return json.dumps(response, ensure_ascii=False)
    mono_list.append(str(id))
    user.monograph = str(mono_list)
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 学生学术专著添加界面
@monograph_bp.route('/mono_add_stu/<account>/', methods=('GET', 'POST'))
def mono_add_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('mono_add_stu.html', user_account=stu_info, account_url=stu_info,
                           name="monographs")


# 教师学术专著添加界面
@monograph_bp.route('/mono_add_tch/<account>/', methods=('GET', 'POST'))
def mono_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('mono_add_tch.html', user_account=tch_info, account_url=tch_info,
                           name="monographs")

# 教师学术专著添加界面
@monograph_bp.route('/details_tch/<id>/<account>/', methods=('GET', 'POST'))
def mono_details(id,account):
    sessions = DBSession()
    account_url=sessions.query(Tch).filter(Tch.account==account).first()
    mono=sessions.query(Mono).filter(Mono.id==id).first()
    return render_template('mono_details.html', mono=mono,account_url=account_url)



@monograph_bp.route('/api/<account>', methods=('GET', 'POST'))
def monograph_add_page(account):
    sessions = DBSession()
    classify = sessions.query(Account).filter(Account.account == account).first().classify
    if classify == '学生':
        tch_info = eval(sessions.query(Stu).filter(Stu.account == account).first().monograph)
    else:
        tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().monograph)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Mono).filter(Mono.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.name
            dic_t['author'] = jn.editor
            count += 1
            dic_t['index'] = count
            dic_t['new_item'] = jn.name + ', ' + jn.editor
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)


@monograph_bp.route('/mono_add_tch_back', methods=('GET', 'POST'))
def mono_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Mono).order_by(Mono.id).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
        conf = sessions.query(Mono).filter(Mono.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    else:
        conf = sessions.query(Mono).filter(Mono.editor.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        dat = datetime.datetime.strftime(item.dat, "%Y")
        new['name'] = item.editor + ', ' + item.name + ', ' + dat
        if item.page != '':
            new['name'] += ':' + item.page
        index += 1
        new['index'] = index
        new['mono_name'] = item.name
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)


# 学术专著教师上传
@monograph_bp.route('/mono_upload_back', methods=('GET', 'POST'))
def mono_upload_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    if not 'adds' in form_dic:
        form_dic['adds'] = '0'
    if form_dic['dat'] == '':
        form_dic['dat'] = ('1990-1-1')
    response = dict()
    account = form_dic['account']
    if sessions.query(Mono).filter(Mono.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！学术专利已存在!'
        return json.dumps(response, ensure_ascii=False)
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    summary = {'name': form_dic['name'], 'editor': form_dic['editor']}
    # print(form_dic)
    new_mono = Mono(
        name=form_dic['name'],
        editor=form_dic['editor'],
        language=form_dic['language'],
        employ=form_dic['employ'],
        ISBN=form_dic['ISBN'],
        country=form_dic['country'],
        city=form_dic['city'],
        page=form_dic['page'],
        word=form_dic['word'],
        press=form_dic['press'],
        dat=form_dic['dat'],
        DOI=form_dic['DOI'],
        link=form_dic['link'],
        summary=str(summary),
        encd='../monograph/static/monograph_encd/%s' % form_dic['name'],
    )
    sessions.add(new_mono)
    encd = request.files['encd']
    new_mono = sessions.query(Mono).filter(Mono.name == form_dic['name']).first()
    save_File('monograph', encd, str(new_mono.id))
    if form_dic['adds'] == str(1):
        tch_mono = ast.literal_eval(user_info.monograph)
        tch_mono.append(str(new_mono.id))
        user_info.monograph = str(tch_mono)
    response['error'] = 0
    response['url'] = '/monograph/details_tch/' + str(new_mono.id)+'/'+str(user_info.account)
    response['msg'] = '上传成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)



# 学术专著教师上传
@monograph_bp.route('/mono_upload_tch/<account>/', methods=('GET', 'POST'))
def mono_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('mono_upload_tch.html', tch_info=tch_info, account_url=tch_info)


# 学术专著学生上传
@monograph_bp.route('/mono_upload_stu/<account>/', methods=('GET', 'POST'))
def mono_upload_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('mono_upload_stu.html', stu_info=stu_info, account_url=stu_info)


# 学术专著教师修改
@monograph_bp.route('/mono_modify_tch/<mono_name>/<account>/', methods=('GET', 'POST'))
def mono_modify_tch(mono_name, account):
    sessions = DBSession()
    modify_mono = sessions.query(Mono).filter(Mono.name == mono_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('mono_modify_tch.html', mono_home=modify_mono, account_url=tch_info)


# 学术专著教师修改
@monograph_bp.route('/mono_modify_back', methods=('GET', 'POST'))
def mono_modify_back():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Mono).filter(
            Mono.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，专著已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_mono = sessions.query(Mono).filter(Mono.name == form_dic['pre']).first()
    if form_dic['dat'] == "":
        form_dic['dat'] = '1990-1-1'
    encd = request.files.get('encd')
    if encd:
        save_File('monograph', encd, str(modify_mono.id))
    modify_mono.name = form_dic['name']
    modify_mono.language = form_dic['language']
    modify_mono.employ = form_dic['employ']
    modify_mono.editor = form_dic['editor']
    modify_mono.ISBN = form_dic['ISBN']
    modify_mono.country = form_dic['country']
    modify_mono.city = form_dic['city']
    modify_mono.page = form_dic['page']
    modify_mono.word = form_dic['word']
    modify_mono.press = form_dic['press']
    modify_mono.DOI = form_dic['DOI']
    modify_mono.link = form_dic['link']
    modify_mono.dat=str_to_date(form_dic['dat'])
    summary = {'name': form_dic['name'], 'editor': form_dic['editor']}
    modify_mono.summary=str(summary)
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)




# 学术专著教师修改
@monograph_bp.route('/mono_delete', methods=('GET', 'POST'))
def mono_delete():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Mono).filter(Mono.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)



# 专著收录界面
@monograph_bp.route('/table', methods=('GET', 'POST'))
def table():
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))
    monographs=Admin(Mono,'monograph').getAll()['data']
    response_items = []
    for monograph in monographs:
        response_items.append(monograph)
        
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