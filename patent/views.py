import ast
import datetime
import math
import os
from functools import wraps
from urllib.parse import unquote
from admins.models import Admin
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy.cyextension.processors import str_to_date
from file_save.file_Save import save_File

from conference.views import search_res, is_Chinese
from libs.db import DBSession, Tch, Stu, Account, Patent

patent_bp = Blueprint('patent', import_name='patent')
patent_bp.template_folder = './templates'
patent_bp.static_folder = './static'


# 首页专利
@patent_bp.route('/', methods=('GET', 'POST'))
def patent():
    sessions = DBSession()
    all_patent = sessions.query(Patent).all()
    return render_template('patent.html', patent_home=all_patent)


# 用户添加论文主页后端
@patent_bp.route('/details_tch/<id>/<account>', methods=('GET', 'POST'))
def details(id, account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    patent=Admin(Patent,'patent').getOne(id)
    sessions.close()
    if patent['encd'] is not None and patent['encd']!='':
        patent['src']="../../static/patent_encd/"+str(id)+'/'+patent['encd']
    return render_template('patent_details.html', patent=patent, user_account=tch_info, account_url=tch_info)


# 用户添加论文主页后端
@patent_bp.route('/patent_add', methods=('GET', 'POST'))
def patent_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    if user is None:
        user = session.query(Stu).join(Account, Account.account == Stu.account).filter(Stu.account == account).first()
    patent_list = user.patent
    if patent_list is None:
        patent_list = []
    else:
        patent_list = eval(patent_list)
    if str(id) in patent_list:
        response['message'] = "专利已存在!"
        response['error'] = 1
        return json.dumps(response, ensure_ascii=False)
    patent_list.append(str(id))
    user.patent = str(patent_list)
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 教师专利添加界面
@patent_bp.route('/patent_add_tch/<account>/', methods=('GET', 'POST'))
def patent_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('patent_add_tch.html', user_account=tch_info, account_url=tch_info,
                           name="patents")


@patent_bp.route('/patent_add_tch_back', methods=('GET', 'POST'))
def patent_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Patent).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
        conf = sessions.query(Patent).filter(Patent.name.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    else:
        conf = sessions.query(Patent).filter(Patent.patentee.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        new['name'] = item.patentee + ': ' + item.name + ', 专利号:' + item.application_num
        index += 1
        new['index'] = index
        new['pat_name'] = item.name
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[
                       min((curpage - 1), math.ceil(lenth / pagesize) - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)




# 专利教师上传
@patent_bp.route('/patent_upload_back', methods=('GET', 'POST'))
def patent_upload_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    isteacher = 0
    response = dict()
    if sessions.query(Patent).filter(Patent.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！专利已存在'
        return json.dumps(response, ensure_ascii=False)
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == form_dic['account']).first()
    if user_info is None:
        isteacher = 0
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == form_dic['account']).first()
    if form_dic['application_dat'] == '':
        form_dic['application_dat'] = str_to_date('1990-1-1')
    if form_dic['effect_dat'] == '':
        form_dic['effect_dat'] = str_to_date('1990-1-1')
    summary = {}
    summary['name'] = form_dic['name']
    summary['patentee'] = form_dic['patentee']
    summary['effect_dat'] = form_dic['effect_dat']
    new_patent = Patent(
        name=form_dic['name'],
        patentee=form_dic['patentee'],
        level=form_dic['level'],
        country=form_dic['country'],
        application_num=form_dic['application_num'],
        patent_num=form_dic['patent_num'],
        IPC_num=form_dic['IPC_num'],
        CPC_num=form_dic['CPC_num'],
        application_dat=form_dic['application_dat'],
        effect_dat=form_dic['effect_dat'],
        DOI=form_dic['DOI'],
        summary=str(summary),
        link=form_dic['link'],
    )
    sessions.add(new_patent)
    new_patent = sessions.query(Patent).filter(Patent.name == form_dic['name']).first()
    new_patent.encd = '../patent/static/patent_encd/%s' % new_patent.id
    encd = request.files['encd']
    if encd:
        save_File('patent', encd, str(new_patent.id))
    if form_dic['adds'] == '1':
        pat = eval(user_info.patent)
        pat.append(str(new_patent.id))
        user_info.patent = str(pat)
    response = dict()
    response['error'] = 0
    response['msg'] = '上传成功'
    if isteacher == 0:
        response['url'] = '/patent/details_tch/' + str(new_patent.id) + '/' + user_info.account
    else:
        response['url'] = '/patent/details_stu/' + str(new_patent.id) + '/' + user_info.account
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 专利教师上传
@patent_bp.route('/patent_upload_tch/<account>/', methods=('GET', 'POST'))
def patent_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('patent_upload_tch.html', tch_info=tch_info, account_url=tch_info)


@patent_bp.route('/api/<account>', methods=('GET', 'POST'))
def patent_add_page(account):
    sessions = DBSession()
    classify = sessions.query(Account).filter(Account.account == account).first().classify
    if classify == '学生':
        tch_info = eval(sessions.query(Stu).filter(Stu.account == account).first().patent)
    else:
        tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().patent)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Patent).filter(Patent.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dat = datetime.datetime.strftime(jn.effect_dat, "%Y-%m-%d")
            dic_t['new_item'] = jn.patentee + ': ' + jn.name + ', 专利号：' + jn.application_num
            dic_t['author'] = jn.patentee
            dic_t['name'] = jn.name
            count += 1
            dic_t['index'] = count
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)


# 专利教师删除
@patent_bp.route('/patent_delete', methods=('GET', 'POST'))
def patent_delete():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Patent).filter(Patent.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)


# 专利教师删除
@patent_bp.route('/patent_delete_page', methods=('GET', 'POST'))
def patent_delete_page():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    account = data['account']
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    data = tch_info.patent
    data.remove(id)
    tch_info.patent = data
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)




# 专利教师修改
@patent_bp.route('/patent_modify_tch/<patent_name>/<account>/', methods=('GET', 'POST'))
def patent_modify_tch(patent_name, account):
    sessions = DBSession()
    modify_patent = sessions.query(Patent).filter(Patent.name == patent_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('patent_modify_tch.html', patent_home=modify_patent, account_url=tch_info, account=account)


# 专利教师修改
@patent_bp.route('/patent_modify_back', methods=('GET', 'POST'))
def patent_modify_back():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    if form_dic['name'] != form_dic['pre'] and sessions.query(Patent).filter(
            Patent.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，专利已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_patent = sessions.query(Patent).filter(Patent.name == form_dic['pre']).first()
    if form_dic['effect_dat'] == '':
        form_dic['effect_dat'] = ('1990-1-1')
    if form_dic['application_dat'] == '':
        form_dic['application_dat'] = ('1990-1-1')
    encd = request.files.get('encd')
    if encd:
        save_File('journal', encd, str(modify_patent.id) + '.pdf')
    modify_patent.name = form_dic['name']
    modify_patent.patentee = form_dic['patentee']
    modify_patent.country = form_dic['country']
    modify_patent.level = form_dic['level']
    modify_patent.application_num = form_dic['application_num']
    modify_patent.patent_num = form_dic['patent_num']
    modify_patent.IPC_num = form_dic['IPC_num']
    modify_patent.CPC_num = form_dic['CPC_num']
    modify_patent.application_dat = form_dic['application_dat']
    modify_patent.effect_dat = form_dic['effect_dat']
    modify_patent.DOI = form_dic['DOI']
    modify_patent.link = form_dic['link']
    summary = {'name': form_dic['name'], 'patentee': form_dic['patentee'],
               'effect_dat': form_dic['effect_dat']}
    modify_patent.summary = str(summary)
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)

# 专利收录界面
@patent_bp.route('/table', methods=('GET', 'POST'))
def table():
    req=request.json
    account=req['account']
    page=int(req['page'])
    limit=int(req['limit'])
    item_type=req['type']
    session=DBSession()
    tch_info=session.query(Tch).filter(Tch.account==account).first()
    items=eval(getattr(tch_info,item_type))
    patents=Admin(Patent,'patent').getAll()['data']
    response_items = []
    for patent in patents:
        if str(patent['id']) in items:
            patent['is_added']=True
        else:
            patent['is_added']=False
        response_items.append(patent)
        
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

