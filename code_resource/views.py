import json
import math

from libs.db import DBSession, Tch, Stu, Account, Patent, Mono, Resource, Code
from flask import Blueprint, request, render_template

code_resource_bp = Blueprint('code_resource', import_name='code_resource')
code_resource_bp.template_folder = './templates'
code_resource_bp.static_folder = './static'
from admins.models import Admin


# 数据资源界面
@code_resource_bp.route('/', methods=('GET', 'POST'))
def code_resource():
    sessions = DBSession()
    codes = Admin(Code, 'code').getAll()['data']
    for code in codes:
        user = sessions.query(Tch).filter(Tch.account == code['user']).first()
        if user is None:
            user = sessions.query(Stu).filter(Stu.account == code['user']).first()
        code['user_name'] = user.name
        code['email'] = user.email
    return render_template('code_resource.html', codes=codes)


# # 数据资源界面
# @code_resource_bp.route('/upload_tch/<account>', methods=(['GET']))
# def upload_front_tch(account):
#     sessions = DBSession()
#     account = sessions.query(Tch).filter(Tch.account == account).first()
#     return render_template('code_upload_tch.html', account_url=account)


# 数据资源界面
@code_resource_bp.route('/upload/<account>', methods=(['GET']))
def upload_front(account):
    sessions = DBSession()
    account = sessions.query(Account).filter(Account.account == account).first()
    # print(11)
    return render_template('code_upload_tch.html', account_url=account)


# 数据资源界面
@code_resource_bp.route('/table/<account>', methods=(['GET']))
def table(account):
    sessions = DBSession()
    account = sessions.query(Account).filter(Account.account == account).first()
    return render_template('code_table.html', account_url=account)


# 数据资源界面
@code_resource_bp.route('/table_back/<account>', methods=(['GET']))
def table_back(account):
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    res = sessions.query(Code).filter(Code.user == account).all()
    data = [dict(item) for item in res]
    response = dict()
    lenth = len(data)
    response['code'] = 0
    response['data'] = data[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = lenth
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 数据资源界面
@code_resource_bp.route('/upload', methods=(['POST']))
def upload():
    data = request.form.to_dict()
    Admin(Code, 'code').upLoad(data)
    return {'error': 0, 'msg': '上传成功！'}


# 数据资源界面
@code_resource_bp.route('/modify', methods=(['POST']))
def modify():
    data = request.form.to_dict()
    Admin(Code, 'code').modify(data, data['id'])
    return {'error': 0, 'msg': '修改成功！'}


# 数据资源界面
@code_resource_bp.route('/delete', methods=(['POST']))
def delete():
    data = request.json['id']
    Admin(Code, 'code').deleteOne(data)
    return {'error': 0, 'msg': '删除成功！'}


# 数据资源界面
@code_resource_bp.route('/detail/<id>', methods=(['GET']))
def detail(id):
    data = Admin(Code, 'code').getOne(id)

    return render_template('code_modify.html', data=data)

# # 数据资源界面
# @code_resource_bp.route('/up/<account>', methods=(['GET']))
# def upload_fron(account):
#     sessions = DBSession()
#     account = sessions.query(Account).filter(Account.account == account).first()
#     print(account.classify)
#     return render_template('code_delete.html', account_url=account)
#
# # # 数据资源详情
# @resource_bp.route('/resource_home/<id>', methods=('GET', 'POST'))
# def resource_home(id):
#     sessions = DBSession()
#     resource_home = sessions.query(Resource).filter(Resource.id == id).first()
#     return render_template('resource_home.html', resource_home=resource_home)
#
#
# # 数据资源教师上传
# @resource_bp.route('/resource_upload_tch/<account>/', methods=('GET', 'POST'))
# def resource_upload_tch(account):
#     sessions = DBSession()
#     tch_info = sessions.query(Tch).filter(Tch.account == account).first()
#     if request.method == "POST":
#         name = request.form.get('name', '').strip()
#         link = request.form.get('link', '')
#         classes = request.form.get('classes', '')
#         introduction = request.form.get('introduction')
#         citation = request.form.get('citation')
#         encd = request.files.get('encd')
#         if sessions.query(Resource).filter(Resource.name==name).first() is not None:
#             return render_template('code_upload_tch.html', error='资源已存在',tch_info=tch_info,account_url=tch_info)
#         new_resource = Resource(
#             name=name,
#             link=link,
#             classes=classes,
#             introduction=introduction,
#             citation=citation,
#             encd='../resource/static/resource_encd/%s' % name,
#         )
#         if encd:
#             save_resource(name, encd)
#         sessions.add(new_resource)
#         sessions.commit()
#         # return redirect(url_for('users.tch_page', account=tch_info.account,account_url=tch_info))
#     return render_template('code_upload_tch.html',tch_info=tch_info,account_url=tch_info)
#
#
# # 数据资源学生上传
# @resource_bp.route('/resource_upload_stu/<account>/', methods=('GET', 'POST'))
# def resource_upload_stu(account):
#     sessions = DBSession()
#     stu_info = sessions.query(Stu).filter(Stu.account == account).first()
#     if request.method == "POST":
#         name = request.form.get('name', '').strip()
#         link = request.form.get('link', '')
#         classes = request.form.get('classes', '')
#         introduction = request.form.get('introduction')
#         citation = request.form.get('citation')
#         encd = request.files.get('encd')
#         if sessions.query(Resource).filter(Resource.name==name).first() is not None:
#             return render_template('code_table.html', error='资源已存在', stu_info=stu_info,account_url=stu_info)
#         new_resource = Resource(
#             name=name,
#             link=link,
#             classes=classes,
#             introduction=introduction,
#             citation=citation,
#             encd='../resource/static/resource_encd/%s' % name,
#         )
#         save_resource(name, encd)
#         sessions.add(new_resource)
#         sessions.commit()
#         return redirect(url_for('users.stu_page', account=stu_info.account,account_url=stu_info))
#     return render_template('code_table.html',stu_info=stu_info,account_url=stu_info)
#
#
#
#
#
# # 上传
# def upload():
#     name = request.form.get('name', '').strip()
#     link = request.form.get('link', '')
#     encd = request.files.get('encd')
#     new_resource = Resource(
#         name=name,
#         link=link,
#         encd='../resource/static/resource_encd/%s' % name,
#     )
#     save_resource(name,encd)
#     return new_resource
#
#
#
#
# # 保存数据资源
# def save_resource(name, file):
#     base_dir = os.path.dirname(os.path.abspath(__name__))
#     file_path = os.path.join(base_dir, 'resource', 'static', 'resource_encd', name)
#     file.save(file_path)
