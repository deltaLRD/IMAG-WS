
import os
from functools import wraps
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy.cyextension.processors import str_to_date
from libs.db import Account, DBSession, Tch, Stu, Issues
from datetime import datetime
others_bp = Blueprint('others', import_name='others')
others_bp.template_folder = './templates'
others_bp.static_folder = './static'


# 联系界面
@others_bp.route('/contact', methods=('GET', 'POST'))
def contact():
    a='已解决'
    b='未解决'
    sessions = DBSession()
    all_issue = sessions.query(Issues).all()
    solved_issue = sessions.query(Issues).filter(Issues.solve == a).all()
    unsolved_issue = sessions.query(Issues).filter(Issues.solve == b).all()
    return render_template('contact.html', issues=all_issue,solved_issue=solved_issue,unsolved_issue=unsolved_issue)


# 上传问题
@others_bp.route('/issue_upload', methods=('GET', 'POST'))
def issue_upload():
    sessions = DBSession()
    all_issue = sessions.query(Issues).all()
    if request.method == "POST":
        data = request.get_data()
        data = bytes.decode(data)
        print(data)
        data = json.loads(data)
        issue = data['issue']
        time = datetime.now()
        name = data['name']
        phone = data['phone']
        new_issue = Issues(
            issue=issue,
            time=time,
            name=name,
            phone=phone
        )
        sessions.add(new_issue)
        sessions.commit()
        all_issue = sessions.query(Issues).all()
        return render_template('contact.html', issues=all_issue)
    else:
        return render_template('contact.html', issues=all_issue)

