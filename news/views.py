import base64
import datetime
import json
import os

import markdown
from sqlalchemy.cyextension.processors import str_to_date
from libs.db import DBSession, Tch, Stu, Account, Patent, Mono, News
from flask import *
from flask import Blueprint, request, render_template

news_bp = Blueprint('news', import_name='news')
news_bp.template_folder = './templates'
news_bp.static_folder = './static'


@news_bp.route('/api', methods=('GET', 'POST'))
def api():
    response = dict()
    response['status'] = 1
    news = []
    sessions = DBSession()
    allnews = sessions.query(News).all()
    # host = request.headers.get
    host="http://127.0.0.1:8080"
    for item in allnews:
        content = item.content
        content=content.replace("news/static", "static")
        content=content.replace("/static/picture",host+'/static/picture')
        dic = dict()
        dic['title'] = item.title
        dic['publisher'] = item.publisher
        # print(json.dump(markdown.markdown(content).text)
        dic['content'] = markdown.markdown(content)
        dic['dat'] = item.dat
        dic['classify'] = item.classify
        news.append(dic)
    response['news'] = news
    return json.dumps(response, ensure_ascii=False)


@news_bp.route('/upload', methods=('GET', 'POST'))
def upload():
    file = request.files.get('editormd-image-file')
    path = ''
    if file:
        abspth = os.path.abspath(__file__)
        path = os.path.join('news', 'static', 'picture')
        file.save(os.path.join(path, file.filename))
    url = (os.path.join('http://127.0.0.1:5000', 'news', 'static', 'picture', file.filename))
    response = dict()
    response['success'] = 1
    response['message'] = '上传成功'
    response['url'] = url
    return json.dumps(response, ensure_ascii=False)


# 新闻界面
@news_bp.route('/', methods=('GET', 'POST'))
def news():
    sessions = DBSession()
    all_news = sessions.query(News).all()
    for item in all_news:
        item.content = markdown.markdown(item.content)
    return render_template('news.html', all_news=all_news)

# 新闻界面
@news_bp.route('/<id>', methods=('GET', 'POST'))
def news_details(id):
    sessions = DBSession()
    news = sessions.query(News).filter(News.id==id).first()
    return render_template('details.html', news=news)



# 新闻教师上传
@news_bp.route('/news_upload_tch/<account>/', methods=('GET', 'POST'))
def news_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    if request.method == "POST":
        title = request.form.get('title', '')
        publisher = request.form.get('publisher', '')
        classify = request.form.get('classify', '')
        content = request.form.get('content', '')
        dat = request.form.get('dat', '')
        if dat == '':
            dat = datetime.date.today()
        summary = {}
        summary['title'] = title
        summary['publisher'] = publisher
        if sessions.query(News).filter(News.summary == str(summary)).first() is not None:
            return render_template('news_upload_tch.html', error='新闻已存在', tch_info=tch_info, account_url=tch_info)
        new_news = News(
            title=title,
            publisher=publisher,
            classify=classify,
            content=content,
            dat=dat,
            summary=str(summary)
        )
        sessions.add(new_news)
        sessions.commit()
        return redirect(url_for('users.tch_page', account=tch_info.account))
    return render_template('news_upload_tch.html', tch_info=tch_info, account_url=tch_info)


# 新闻教师上传
@news_bp.route('/news_upload_back', methods=('GET', 'POST'))
def news_upload_back():
    sessions = DBSession()
    data = request.get_json()
    response = dict()
    summary = {}
    summary['title'] = data['name']
    summary['publisher'] = data['publisher']
    if sessions.query(News).filter(News.summary == str(summary)).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败，新闻已存在！'
        return json.dumps(response, ensure_ascii=False)
    if data['dat'] == '':
        data['dat'] = datetime.date.today()
    new_news = News(
        title=data['name'],
        publisher=data['publisher'],
        classify=data['classify'],
        content=data['markdowndata'],
        dat=data['dat'],
        summary=str(summary)
    )
    sessions.add(new_news)
    sessions.commit()
    sessions.close()
    response['error'] = 0
    response['msg'] = '上传成功'
    return json.dumps(response, ensure_ascii=False)
