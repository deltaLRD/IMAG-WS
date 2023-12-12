import ast
import math
import os
from functools import wraps

from flask import *
from flask import Blueprint, request, render_template

from conference.views import search_res
from libs.db import DBSession, Tch, Stu, Account, Course

course_bp = Blueprint('course', import_name='course')
course_bp.template_folder = './templates'
course_bp.static_folder = './static'


# 用户添加论文主页后端
@course_bp.route('/details_tch/<id>/<account>', methods=('GET', 'POST'))
def details(id, account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    session = DBSession()
    course = session.query(Course).filter(Course.id == id).first()
    return render_template('course_detail.html', course=course, user_account=tch_info, account_url=tch_info)


# 课程
@course_bp.route('/', methods=('GET', 'POST'))
def course():
    sessions = DBSession()
    all_course = sessions.query(Course).all()
    return render_template('course.html', course_home=all_course)


@course_bp.route('/api/<account>', methods=('GET', 'POST'))
def honor_add_page(account):
    sessions = DBSession()
    tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().course)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Course).filter(Course.id == key).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.name
            dic_t['author'] = jn.teacher
            count += 1
            dic_t['index'] = count
            dic_t['new_item'] = jn.name
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)


@course_bp.route('/course_add_tch_back', methods=('GET', 'POST'))
def course_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Course).order_by(Course.id).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
        conf = sessions.query(Course).filter(Course.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    else:
        conf = sessions.query(Course).filter(Course.teacher.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        new['name'] = item.name + ', ' + item.teacher
        index += 1
        new['index'] = index
        new['course_name'] = item.name
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)


# 教师课程添加界面
@course_bp.route('/course_add_tch/<account>/', methods=('GET', 'POST'))
def course_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('course_add_tch.html', user_account=tch_info, account_url=tch_info, name="courses")


# 课程教师上传
@course_bp.route('/course_upload_back', methods=('GET', 'POST'))
def course_upload_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    account = form_dic['account']
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    response = dict()
    summary = {}
    summary['name'] = form_dic['name']
    summary['teacher'] = form_dic['teacher']
    if sessions.query(Course).filter(Course.summary == str(summary)).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！课程已存在'
        return json.dumps(response, ensure_ascii=False)
    new_course = Course(
        name=form_dic['name'],
        teacher=form_dic['teacher'],
        summary=str(summary),
        content=form_dic['content'],
        page=form_dic['page'],
    )
    sessions.add(new_course)
    new_course = sessions.query(Course).filter(Course.name == form_dic['name']).first()
    if form_dic['adds'] == '1':
        dic = eval(tch_info.course)
        dic.append(str(new_course.id))
        tch_info.course = str(dic)
    sessions.commit()
    sessions.close()
    response['error'] = 0
    response['msg'] = '上传成功'
    return json.dumps(response, ensure_ascii=False)


# 课程教师上传
@course_bp.route('/course_upload_tch/<account>/', methods=('GET', 'POST'))
def course_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        teacher = request.form.get('teacher', '')
        content = request.form.get('content', '')
        page = request.form.get('ranking', '')
        adds = request.form.get('adds', '').strip()
        summary = {}
        summary['name'] = name
        summary['teacher'] = teacher
        new_course = Course(
            name=name,
            teacher=teacher,
            content=content,
            page=page,
            summary=str(summary)
        )
        sessions.add(new_course)
        new_course = sessions.query(Course).filter(Course.name == name).first()
        if adds != str(1):
            sessions.commit()
            return redirect(url_for('users.tch_page', account=tch_info.account, account_url=tch_info))
        else:
            if tch_info.course is None:
                tch_course = []
                tch_course.append(str(new_course.id))
                tch_info.course = str(tch_course)
                sessions.commit()
                return redirect(url_for('users.tch_page', account=tch_info.account, account_url=tch_info))
            else:
                tch_course = ast.literal_eval(tch_info.course)
                tch_course.append(str(new_course.id))
                tch_info.course = str(tch_course)
                sessions.commit()
                return redirect(url_for('users.tch_page', account=tch_info.account, account_url=tch_info))
    sessions.commit()
    return render_template('course_upload_tch.html', tch_info=tch_info, account_url=tch_info)


# 用户添加论文主页后端
@course_bp.route('/course_add', methods=('GET', 'POST'))
def course_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    if user is None:
        user = session.query(Stu).join(Account, Account.account == Stu.account).filter(Stu.account == account).first()
    course_list = user.course
    if course_list is None:
        course_list = []
    else:
        course_list = eval(course_list)
    if str(id) in course_list:
        response['message'] = "课程已存在!"
        response['error'] = 1
        return json.dumps(response, ensure_ascii=False)
    course_list.append(str(id))
    user.course = str(course_list)
    session.commit()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


@course_bp.route('/course_modify_tch/<course_name>/<account>/', methods=('GET', 'POST'))
def course_modify_tch(course_name, account):
    sessions = DBSession()
    modify_course = sessions.query(Course).filter(Course.name == course_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('course_modify_tch.html', course_home=modify_course, account_url=tch_info)


@course_bp.route('/course_modify_back', methods=('GET', 'POST'))
def course_modify_back():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Course).filter(
            Course.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，课程已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_course = sessions.query(Course).filter(Course.name == form_dic['pre']).first()
    modify_course.name = form_dic['name']
    modify_course.teacher = form_dic['teacher']
    modify_course.content = form_dic['content']
    modify_course.page = form_dic['page']
    summary = {'name': form_dic['name'], 'teacher': form_dic['teacher']}
    modify_course.summary = str(summary)
    response['error'] = 0
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


@course_bp.route('/course_delete', methods=('GET', 'POST'))
def course_delete():
    data = request.get_json()
    id = data['id']
    sessions = DBSession()
    sessions.query(Course).filter(Course.id == id).delete()
    sessions.commit()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)
