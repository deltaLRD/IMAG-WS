import ast
import datetime
import functools
import math
import os
from functools import wraps
from werkzeug.utils import secure_filename
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy.cyextension.processors import str_to_date
import uuid
from admins.models import Admin
from conference.views import search_res
from libs.db import DBSession, Tch, Stu, Account, Prog, Comp

program_bp = Blueprint('program', import_name='program')
program_bp.template_folder = './templates'
program_bp.static_folder = './static'


def cmp(x, y):
    if x['start_time'] is None or x['start_time'] == '':
        return 1
    elif y['start_time'] is None or y['start_time'] == '':
        return -1
    elif x['start_time'] > y['start_time']:
        return -1
    return 1


# 项目界面
@program_bp.route('/', methods=('GET', 'POST'))
def program():
    sessions = DBSession()
    admins = sessions.query(Tch).filter(Tch.account == 'admin').first()
    prog_list = eval(admins.program)
    display = eval(admins.display)
    prog_display=display['prog']
    prog = []
    for id in prog_list:
        if id not in prog_display:
            continue
        prog_one = Admin(Prog, 'program').getOne(int(id))
        if prog_one is not None:
            prog.append(prog_one)
    return render_template('program.html', prog=prog)


# 期刊论文界面
@program_bp.route('/table', methods=('GET', 'POST'))
def prog_add_tch_back():
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    programs=Admin(Prog,'program').getAll()['data']
    for item in programs:
        item['display_name']=item['name']+', '+str(item['start_time'])+'-'+str(item['deadline'])+', '
        if item['cost'] is not None and item['cost']!='':
            item['display_name']+=item['cost']+'万, '
        else:
            item['display_name'] += item['fund'] + ' 万( 直接经费 ), '
        item['display_name']+='主持('+item['principal']+')'
    lenth = len(programs)
    response = dict()
    response['code'] = 0
    response['data'] = programs[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = lenth
    return json.dumps(response, ensure_ascii=False)

# @program_bp.route('/prog_add_tch_back', methods=('GET', 'POST'))
# def prog_add_tch_back():
#     sessions = DBSession()
#     curpage = int(request.args.get('page'))
#     pagesize = int(request.args.get('limit'))
#     item = request.args.get('item')
#     content = request.args.get('content')
#     conf_temp = sessions.query(Prog).order_by(Prog.id).all()
#     if content is None:
#         conf = conf_temp
#     elif item == 'title_search':
#         conf = sessions.query(Prog).filter(Prog.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
#     else:
#         conf = sessions.query(Prog).filter(Prog.principal.ilike('%{word}%'.format(word=content.strip(" ")))).all()
#     index = 0
#     all_conf = []
#     for item in conf:
#         new = dict()
#         start_dat = datetime.datetime.strftime(item.start_time, "%Y-%m-%d")
#         end_dat = datetime.datetime.strftime(item.deadline, "%Y-%m-%d")
#         new['id'] = item.id
#         new[
#             'name'] = item.name + ', ' + start_dat + ' - ' + end_dat + ', ' + item.cost + '万' + ' 主持(' + item.principal + ')'
#         index += 1
#         new['index'] = index
#         new['pro_name'] = item.name
#         all_conf.append(new)
#     lenth = len(all_conf)
#     response = dict()
#     response['code'] = 0
#     response['data'] = all_conf[
#                        min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
#     response['msg'] = ""
#     response['count'] = len(all_conf)
#     return json.dumps(response, ensure_ascii=False)


# 项目教师添加界面
@program_bp.route('/prog_add_tch/<account>/', methods=('GET', 'POST'))
def prog_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('prog_add_tch.html', user_account=tch_info, account_url=tch_info,
                           name="projects")


# 项目学生添加界面
@program_bp.route('/prog_add_stu/<account>/', methods=('GET', 'POST'))
def prog_add_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('prog_add_stu.html', user_account=stu_info, account_url=stu_info,
                           name="projects")


@program_bp.route('/api/<account>', methods=('GET', 'POST'))
def prog_add_page(account):
    sessions = DBSession()
    classify = sessions.query(Account).filter(Account.account == account).first().classify
    if classify == '学生':
        tch_info = eval(sessions.query(Stu).filter(Stu.account == account).first().program)
    else:
        tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().program)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Prog).filter(Prog.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.name
            dic_t['author'] = jn.principal
            start_dat = datetime.datetime.strftime(jn.start_time, "%Y-%m-%d")
            end_dat = datetime.datetime.strftime(jn.deadline, "%Y-%m-%d")
            count += 1
            dic_t['index'] = count
            dic_t[
                'new_item'] = jn.name + ', ' + start_dat + ' - ' + end_dat + ', ' + jn.cost + '万' + ' 主持(' + jn.principal + ')'
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)



# 项目教师上传
@program_bp.route('/prog_upload_back', methods=('GET', 'POST'))
def prog_upload_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    account = form_dic['account']
    response = dict()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    # contract = request.files.getlist('contract')
    # application_files=request.files.getlist('application')
    # Conclusion_book=request.files.getlist('Conclusion_book')
    subdirectory = form_dic['subcon']
    if sessions.query(Prog).filter(Prog.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！专利已存在'
        return json.dumps(response, ensure_ascii=False)
    if form_dic['start_time'] == '':
        form_dic['start_time'] = str_to_date('1990-1-1')
    if form_dic['deadline'] == '':
        form_dic['deadline'] = str_to_date('1990-1-1')
    summary = {'name': form_dic['name'], 'principal': form_dic['principal'], 'level': form_dic['level'],
               'start_time': form_dic['start_time']}
    application = '../program/static/application/%s' % subdirectory,
    new_prog = Prog(
        name=form_dic['name'],
        principal=form_dic['principal'],
        level=form_dic['level'],
        start_time=form_dic['start_time'],
        deadline=form_dic['deadline'],
        cost=form_dic['cost'],
        summary=str(summary),
        prog_num=form_dic['prog_num'],
        pro_source=form_dic['pro_source'],
        application=application
    )
    sessions.add(new_prog)

    new_prog = sessions.query(Prog).filter(Prog.name == form_dic['name']).first()
    if form_dic['adds'] == '1':
        prog = eval(tch_info.program)
        prog.append(str(new_prog.id))
        tch_info.program = str(prog)

    # abspth = os.path.abspath(__file__)
    # applicationpth = os.path.join(os.path.dirname(abspth), 'static', 'application', str(new_prog.id))
    # if not os.path.exists(applicationpth):
    #     os.mkdir(applicationpth)
    # for item in contract:
    #     if item.filename != '':
    #         item.save(os.path.join(applicationpth, item.filename))
    # for item in application_files:
    #     if item.filename != '':
    #         item.save(os.path.join(applicationpth, item.filename))
    # for item in Conclusion_book:
    #     if item.filename != '':
    #         item.save(os.path.join(applicationpth, item.filename))
    sessions.commit()
    sessions.close()
    response = dict()
    response['error'] = 0
    response['msg'] = '上传成功'
    response['url'] = 'program/details_tch/' + str(new_prog.id) + '/' + tch_info.account
    return json.dumps(response, ensure_ascii=False)


# 项目教师上传
@program_bp.route('/prog_upload_file/<account>', methods=('GET', 'POST'))
def prog_upload_file(account):
    f = request.files.getlist('file')
    # 先将文件存储在temp文件夹，待项目上传完毕，再将文件转到该项目id文件下
    abspth = os.path.abspath(__file__)
    # 子目录，表示一个项目
    subdirectory = uuid.uuid4().hex
    applicationpth = os.path.join(os.path.dirname(abspth), 'static', 'application', str(account))
    if not os.path.exists(applicationpth):
        os.mkdir(applicationpth)
    for item in f:
        fname = uuid.uuid4().hex + '.' + (item.filename.split('.')[1])
        # item.save(os.path.join(applicationpth,secure_filename(item.filename)))
        item.save(os.path.join(applicationpth, fname))
    response = {}
    response["code"] = 0
    response["msg"] = "上传成功"
    response["data"] = subdirectory
    return json.dumps(response, ensure_ascii=False)


# 项目教师上传
@program_bp.route('/prog_upload_tch/<account>/', methods=('GET', 'POST'))
def prog_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('prog_upload_tch.html', tch_info=tch_info, account_url=tch_info)


# 项目教师修改
@program_bp.route('/prog_modify_tch/<prog_name>/<account>/', methods=('GET', 'POST'))
def prog_modify_tch(prog_name, account):
    sessions = DBSession()
    modify_prog = sessions.query(Prog).filter(Prog.name == prog_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('prog_modify_tch.html', prog_home=modify_prog, account=account, account_url=tch_info)


@program_bp.route('/prog_modify_back', methods=('GET', 'POST'))
def prog_modify():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Prog).filter(
            Prog.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，项目已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_prog = sessions.query(Prog).filter(Prog.name == form_dic['pre']).first()
    if form_dic['start_time'] == '':
        form_dic['start_time'] = str_to_date('1990-1-1')
    if form_dic['deadline'] == '':
        form_dic['deadline'] = str_to_date('1990-1-1')
    contract = request.files.getlist('contract')
    abspth = os.path.abspath(__file__)
    applicationpth = os.path.join(os.path.dirname(abspth), 'static', 'application', form_dic['name'])
    for item in contract:
        if item.filename != '':
            item.save(os.path.join(applicationpth, item.filename))
    summary = {}
    summary['name'] = form_dic['name']
    summary['principal'] = form_dic['principal']
    summary['level'] = form_dic['level']
    summary['start_time'] = form_dic['start_time']
    application = '../program/static/application/%s' % form_dic['name'],
    modify_prog.name = form_dic['name']
    modify_prog.principal = form_dic['principal']
    modify_prog.level = form_dic['level']
    modify_prog.start_time = form_dic['start_time']
    modify_prog.deadline = form_dic['deadline']
    modify_prog.cost = form_dic['cost']
    modify_prog.summary = str(summary)
    modify_prog.prog_num = form_dic['prog_num']
    modify_prog.pro_source = form_dic['pro_source']
    modify_prog.application = application
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


@program_bp.route('/prog_delete', methods=('GET', 'POST'))
def prog_delete_tch():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Prog).filter(Prog.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)


# 用户添加论文主页后端
@program_bp.route('/details_tch/<id>/<account>', methods=('GET', 'POST'))
def details(id, account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    session = DBSession()
    program = session.query(Prog).filter(Prog.id == id).first()
    return render_template('prog_details.html', program=program, user_account=tch_info, account_url=tch_info)


# 保存项目
def save_pro(name, file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'program', 'static', 'application', name)
    file.save(file_path)
