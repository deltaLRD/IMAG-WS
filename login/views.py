import os
from functools import wraps

from flask import *
from flask import Blueprint, request, render_template

from libs.db import Account, DBSession, Tch, Stu, People

login_bp = Blueprint('login', import_name='login')
login_bp.template_folder = './templates'
login_bp.static_folder = './static'


# 登陆验证装饰器
def login_required(view_func):
    @wraps(view_func)
    def check(*args, **kwargs):
        if 'uid' in session:
            return view_func(*args, **kwargs)
        else:
            return render_template('login.html', error='请先进行登录')

    return check


@login_bp.route('/login_back', methods=('GET', 'POST'))
def login_back():
    sessions = DBSession()
    response = dict()
    data = request.get_json()
    account = data['account']
    password = data['password']
    user_login = sessions.query(Account).filter(Account.account == account).first()
    if user_login is None:
        response['error'] = 1
        response['message'] = '账号不存在'
        sessions.close()
        return json.dumps(response, ensure_ascii=False)
    if user_login.password != password:
        response['error'] = 1
        response['message'] = '密码错误'
        sessions.close()
        return json.dumps(response, ensure_ascii=False)
    response['error'] = 0
    response['message'] = '登录成功'
    response['classify'] = user_login.classify
    return json.dumps(response, ensure_ascii=False)


# 登录前端
@login_bp.route('/login', methods=('GET', 'POST'))
def login():
    return render_template('login.html')


# 退出登录
@login_bp.route('/logout')
def logout():
    return redirect('/login/login')


# 注册界面
@login_bp.route('/register', methods=('GET', 'POST'))
def register():
    return render_template('register.html')


# 注册界面
@login_bp.route('/register_back', methods=('GET', 'POST'))
def register_back():
    sessions = DBSession()
    # avatar =  request.files['avatar']
    form_dic = request.values.to_dict()
    
    account = form_dic['account']
    response = dict()
    if sessions.query(Account).filter(Account.account == account).first() is not None:
        response['error'] = 1
        response['msg'] = '注册失败！账号已存在'
        return json.dumps(response, ensure_ascii=False)
    teachers = ['博士生导师', '硕士生导师', '其他老师']
    display = {'jn': [], 'patent': [], 'prog': [], 'mono': [], 'soft': [], 'comp': [], 'honor': [], 'course': [],'social':[]}
    classify=form_dic['classify']
    if classify in teachers:
        new_account = Account(
            account=account,
            password=form_dic['password'],
            classify='教师',
            examine='1'
        )
        new_teacher = Tch(
            account=account,
            tch_classify=classify,
            name=form_dic['name'],
            Eng_name=form_dic['Eng_name'],
            profile=form_dic['profile_eng'],
            avatar='../users/static/avatar/%s' % account,
            phone=form_dic['phone'],
            email=form_dic['email'],
            address=form_dic['address'],
            direction=form_dic['direction'],
            profile_c=form_dic['profile_c'],
            display=str(display)

        )
        sessions.add(new_account)
        sessions.add(new_teacher)
        if 'avatar' in request.files.to_dict():
            save_avatar(account,  request.files['avatar'])
    else:
        new_account = Account(
            account=account,
            password=form_dic['password'],
            classify='学生',
            examine='1'
        )
        new_student = Stu(
            account=account,
            stu_classify=classify,
            name=form_dic['name'],
            Eng_name=form_dic['Eng_name'],
            profile=form_dic['profile_c'],
            avatar='../users/static/avatar/%s' % account,
            phone=form_dic['phone'],
            email=form_dic['email'],
            address=form_dic['address'],
            direction=form_dic['direction'],
            tutor=form_dic['tutor'],
            instructor=form_dic['instructor'],
            admission=form_dic['dat']
        )
        sessions.add(new_account)
        sessions.add(new_student)
        if 'avatar' in request.files.to_dict():
            save_avatar(account, request.files['avatar'])
    sessions.commit()
    if classify in teachers:
        peo = sessions.query(People).first()
        peosort = eval(peo.faculty)
        newtea = sessions.query(Tch).filter(Tch.account == account).first()
        peosort.append(newtea.id)
        peo.faculty = str(peosort)
        print(peo.faculty)
    sessions.commit()

    response['error'] = 0
    response['msg'] = '注册成功！'
    return json.dumps(response, ensure_ascii=False)

# 保存头像
def save_avatar(account, avatar_file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'users', 'static', 'avatar', account + ".jpg")
    avatar_file.save(file_path)


def save_resume(account, avatar_file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'users', 'static', 'resume', account + ".doc")
    avatar_file.save(file_path)
