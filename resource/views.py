import os

from libs.db import DBSession, Tch, Stu, Account, Patent, Mono, Resource
from flask import *
from flask import Blueprint, request, render_template


resource_bp = Blueprint('resource', import_name='resource')
resource_bp.template_folder = './templates'
resource_bp.static_folder = './static'


# 数据资源界面
@resource_bp.route('/', methods=('GET', 'POST'))
def resource():
    sessions = DBSession()
    all_resource = sessions.query(Resource).all()
    return render_template('resource.html', all_resource=all_resource)


# 数据资源详情
@resource_bp.route('/resource_home/<id>', methods=('GET', 'POST'))
def resource_home(id):
    sessions = DBSession()
    resource_home = sessions.query(Resource).filter(Resource.id == id).first()
    return render_template('resource_home.html', resource_home=resource_home)


# 数据资源教师上传
@resource_bp.route('/resource_upload_tch/<account>/', methods=('GET', 'POST'))
def resource_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        link = request.form.get('link', '')
        classes = request.form.get('classes', '')
        introduction = request.form.get('introduction')
        citation = request.form.get('citation')
        encd = request.files.get('encd')
        if sessions.query(Resource).filter(Resource.name==name).first() is not None:
            return render_template('resource_upload_tch.html', error='资源已存在',tch_info=tch_info,account_url=tch_info)
        new_resource = Resource(
            name=name,
            link=link,
            classes=classes,
            introduction=introduction,
            citation=citation,
            encd='../resource/static/resource_encd/%s' % name,
        )
        if encd:
            save_resource(name, encd)
        sessions.add(new_resource)
        sessions.commit()
        # return redirect(url_for('users.tch_page', account=tch_info.account,account_url=tch_info))
    return render_template('resource_upload_tch.html',tch_info=tch_info,account_url=tch_info)


# 数据资源学生上传
@resource_bp.route('/resource_upload_stu/<account>/', methods=('GET', 'POST'))
def resource_upload_stu(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        link = request.form.get('link', '')
        classes = request.form.get('classes', '')
        introduction = request.form.get('introduction')
        citation = request.form.get('citation')
        encd = request.files.get('encd')
        if sessions.query(Resource).filter(Resource.name==name).first() is not None:
            return render_template('resource_upload_stu.html', error='资源已存在', stu_info=stu_info,account_url=stu_info)
        new_resource = Resource(
            name=name,
            link=link,
            classes=classes,
            introduction=introduction,
            citation=citation,
            encd='../resource/static/resource_encd/%s' % name,
        )
        save_resource(name, encd)
        sessions.add(new_resource)
        sessions.commit()
        return redirect(url_for('users.stu_page', account=stu_info.account,account_url=stu_info))
    return render_template('resource_upload_stu.html',stu_info=stu_info,account_url=stu_info)





# 上传
def upload():
    name = request.form.get('name', '').strip()
    link = request.form.get('link', '')
    encd = request.files.get('encd')
    new_resource = Resource(
        name=name,
        link=link,
        encd='../resource/static/resource_encd/%s' % name,
    )
    save_resource(name,encd)
    return new_resource




# 保存数据资源
def save_resource(name, file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'resource', 'static', 'resource_encd', name)
    file.save(file_path)