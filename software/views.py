import ast
import datetime
import math
import os
from functools import wraps

from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy.cyextension.processors import str_to_date

from conference.views import search_res
from libs.db import DBSession, Tch, Stu, Account, Patent, Soft
from file_save.file_Save import save_File
software_bp = Blueprint('software', import_name='software')
software_bp.template_folder = './templates'
software_bp.static_folder = './static'


# 期刊论文界面
@software_bp.route('/', methods=('GET', 'POST'))
def software():
    sessions = DBSession()
    all_soft = sessions.query(Soft).all()
    return render_template('software.html', soft_home=all_soft)


@software_bp.route('/api/<account>', methods=('GET', 'POST'))
def soft_add_page(account):
    sessions = DBSession()
    classify = sessions.query(Account).filter(Account.account == account).first().classify
    if classify == '学生':
        tch_info = eval(sessions.query(Stu).filter(Stu.account == account).first().software)
    else:
        tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().software)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Soft).filter(Soft.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.name
            dic_t['author'] = jn.author
            count += 1
            dic_t['index'] = count
            times= datetime.datetime.strftime(jn.times, "%Y-%m-%d")
            dic_t['new_item']=jn.name+', '+jn.author+', '+times
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)

# 教师软件著作添加前端
@software_bp.route('/soft_add_tch/<account>/', methods=('GET', 'POST'))
def soft_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('soft_add_tch.html', user_account=tch_info, account_url=tch_info,
                           name="copyrights")
# 学生软件著作添加界面
@software_bp.route('/soft_add_stu/<account>/', methods=('GET', 'POST'))
def soft_add_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('soft_add_stu.html', user_account=stu_info, account_url=stu_info,
                           name="copyrights")

# 用户添加论文主页后端
@software_bp.route('/soft_add', methods=('GET', 'POST'))
def soft_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    if user is None:
        user = session.query(Stu).join(Account, Account.account == Stu.account).filter(Stu.account == account).first()
    soft_list = user.software
    if soft_list is None:
        soft_list = []
    else:
        soft_list = eval(soft_list)
    if str(id) in soft_list:
        response['message'] = "软著已存在!"
        response['error'] = 1
        return json.dumps(response, ensure_ascii=False)
    soft_list.append(str(id))
    user.software = str(soft_list)
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 用户添加论文主页后端
@software_bp.route('/details_tch/<id>/<account>', methods=('GET', 'POST'))
def details(id,account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    session = DBSession()
    soft = session.query(Soft).filter(Soft.id == id).first()
    return render_template('soft_detail.html', soft=soft, user_account=tch_info, account_url=tch_info)


# 软件著作教师上传
@software_bp.route('/soft_upload_back', methods=('GET', 'POST'))
def soft_upload_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    if not 'adds' in form_dic:
        form_dic['adds'] = '0'
    if form_dic['times']=='':
        form_dic['times']=('1990-1-1')
    response = dict()
    account = form_dic['account']
    if sessions.query(Soft).filter(Soft.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！软著已存在!'
        return json.dumps(response, ensure_ascii=False)
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    summary = {}
    summary['name'] = form_dic['name']
    summary['author'] = form_dic['author']
    summary['times'] = form_dic['times']
    new_soft = Soft(
        name=form_dic['name'],
        author=form_dic['author'],
        num=form_dic['num'],
        way=form_dic['way'],
        DOI=form_dic['DOI'],
        limits=form_dic['limits'],
        times=form_dic['times'],
        link=form_dic['link'],
        summary=str(summary),
        encd='../software/static/software_encd/%s' % form_dic['name']
    )
    sessions.add(new_soft)
    new_soft = sessions.query(Soft).filter(Soft.name == form_dic['name']).first()
    encd = request.files['encd']
    if encd:
        save_File('software',encd,str(new_soft.id))
    if form_dic['adds'] == str(1):
        tch_soft = ast.literal_eval(user_info.software)
        tch_soft.append(str(new_soft.id))
        user_info.software = str(tch_soft)
        sessions.commit()
    response['error'] = 0
    response['url'] = '/software/details_tch/' + str(new_soft.id)+'/'+form_dic['account']
    response['msg'] = '上传成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)



# 软件著作教师上传
@software_bp.route('/soft_upload_tch/<account>/', methods=('GET', 'POST'))
def soft_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).join(Account,Account.account==Tch.account).filter(Tch.account == account).first()
    return render_template('soft_upload_tch.html', tch_info=tch_info, account_url=tch_info)




@software_bp.route('/soft_add_tch_back', methods=('GET', 'POST'))
def soft_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Soft).order_by(Soft.id).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
            conf = sessions.query(Soft).filter(Soft.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    else:
            conf = sessions.query(Soft).filter(Soft.author.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        new['name'] = item.author+', '+item.name+', DOI:'+item.DOI
        index += 1
        new['index'] = index
        new['soft_name'] = item.name
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)



# 软件著作学生上传
@software_bp.route('/soft_upload_stu/<account>/', methods=('GET', 'POST'))
def soft_upload_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('soft_upload_stu.html', stu_info=stu_info, account_url=stu_info)


# 软件著作教师修改
@software_bp.route('/soft_modify_tch/<soft_name>/<account>/', methods=('GET', 'POST'))
def soft_modify_tch(soft_name, account):
    sessions = DBSession()
    modify_soft = sessions.query(Soft).filter(Soft.name == soft_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('soft_modify_tch.html', soft_home=modify_soft, tch_info=tch_info, account_url=tch_info)


# 软件著作教师修改
@software_bp.route('/soft_modify_back', methods=('GET', 'POST'))
def soft_modify_back():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Soft).filter(
            Soft.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，软著已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_soft = sessions.query(Soft).filter(Soft.name == form_dic['pre']).first()
    if form_dic['times']=="":
        form_dic['times']= '1990-1-1'
    encd = request.files.get('encd')
    if encd:
        save_File('software', encd, str(modify_soft.id))
    modify_soft.name = form_dic['name']
    modify_soft.author = form_dic['author']
    modify_soft.num = form_dic['num']
    modify_soft.way = form_dic['way']
    modify_soft.DOI = form_dic['DOI']
    modify_soft.limits = form_dic['limits']
    modify_soft.times = str_to_date(form_dic['times'])
    modify_soft.link = form_dic['link']
    modify_soft.encd = request.form.get('encd', '')
    summary = form_dic['name'] + ' , ' + form_dic['author'] + ' , ' + form_dic['times']
    modify_soft.summary=str(summary)
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 专利教师删除
@software_bp.route('/soft_delete', methods=('GET', 'POST'))
def soft_delete():
    data = request.get_json()
    id = data['id']
    sessions = DBSession()
    sessions.query(Soft).filter(Soft.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)



