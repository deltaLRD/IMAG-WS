import json
from flask import Blueprint, request, render_template
from libs.db import DBSession, Tch, Honor, Socialwork, Account, Stu
from admins.models import Admin
social_bp = Blueprint('social', import_name='social')
social_bp.template_folder = './templates'
social_bp.static_folder = './static'


# 荣誉称号教师上传
@social_bp.route('/social_upload_tch/<account>/', methods=('GET', 'POST'))
def honor_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('social_upload_tch.html', tch_info=tch_info, account_url=tch_info)

# 教师课程添加界面
@social_bp.route('/social_add_tch/<account>/', methods=('GET', 'POST'))
def social_add_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('social_add_tch.html', user_account=tch_info,account_url=tch_info,name="social-works")


@social_bp.route('/social_add_tch_back', methods=('GET', 'POST'))
def social_add_tch_back():
    sessions = DBSession()
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    item = request.args.get('item')
    content = request.args.get('content')
    conf_temp = sessions.query(Socialwork).all()
    if content is None:
        conf = conf_temp
    elif item == 'title_search':
            conf = sessions.query(Socialwork).filter(Socialwork.title.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    else:
            conf = sessions.query(Socialwork).filter(Socialwork.teacher.ilike('%{word}%'.format(word=content.strip(" ")))).all()
    index = 0
    all_conf = []
    for item in conf:
        new = dict()
        new['id'] = item.id
        new['name'] = item.name+', '+item.title
        index += 1
        new['index'] = index
        new['title']=item.title
        new['author']=item.name
        all_conf.append(new)
    lenth = len(all_conf)
    response = dict()
    response['code'] = 0
    response['data'] = all_conf[(curpage - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = len(all_conf)
    return json.dumps(response, ensure_ascii=False)



@social_bp.route('/social_upload_back',methods=('GET', 'POST'))
def social_upload_tch():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    account = form_dic['account']
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    response=dict()
    summary = {}
    summary['name'] = form_dic['name']
    summary['title'] = form_dic['title']
    if sessions.query(Socialwork).filter(Socialwork.summary==str(summary)).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！社会兼职已存在'
        return json.dumps(response, ensure_ascii=False)
    new_social = Socialwork(
        name=form_dic['name'],
        title=form_dic['title'],
        summary=str(summary)
    )
    sessions.add(new_social)
    new_social = sessions.query(Socialwork).filter(Socialwork.summary == str(summary)).first()
    if form_dic['adds']=='1':
        dic=eval(tch_info.social)
        dic.append(str(new_social.id))
        tch_info.social=str(dic)
    sessions.commit()
    sessions.close()
    response['error'] = 0
    response['msg'] = '上传成功'
    return json.dumps(response, ensure_ascii=False)


@social_bp.route('/social_delete', methods=('GET', 'POST'))
def social_delete_tch():
    sessions = DBSession()
    data = request.get_json()
    id = data['id']
    sessions.query(Socialwork).filter(Socialwork.id == id).delete()
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)

# 用户添加论文主页后端
@social_bp.route('/details_tch/<id>/<account>', methods=('GET', 'POST'))
def details(id, account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    session = DBSession()
    social = session.query(Socialwork).filter(Socialwork.id == id).first()
    return render_template('social_details.html', social=social, user_account=tch_info, account_url=tch_info)


@social_bp.route('/api/<account>', methods=('GET', 'POST'))
def social_add_page(account):
    sessions = DBSession()
    tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().social)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Socialwork).filter(Socialwork.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.title
            dic_t['author'] = jn.name
            count += 1
            dic_t['index'] = count
            dic_t['new_item']=jn.title
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    print(data)
    return json.dumps(response, ensure_ascii=False)

# 用户添加论文主页后端
@social_bp.route('/social_add', methods=('GET', 'POST'))
def social_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    prog_list = user.social
    if prog_list is None:
        prog_list = []
    else:
        prog_list = eval(prog_list)
    if str(id) in prog_list:
        response['error'] = 1
        response['message'] = "社会兼职已存在!"
        return json.dumps(response, ensure_ascii=False)
    prog_list.append(str(id))
    user.social = str(prog_list)
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)

# 教师荣誉称号添加界面
@social_bp.route('/social_modify_tch/<social_title_name>/<account>/', methods=('GET', 'POST'))
def social_modify_tch(social_title_name, account):
    sessions = DBSession()
    honor_title_name_list = social_title_name.split(',')
    modify_social = sessions.query(Socialwork).filter(Socialwork.name==honor_title_name_list[0],Socialwork.title==honor_title_name_list[1]).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('social_modify_tch.html', social_home=modify_social, tch_info=tch_info, account_url=tch_info)


# 教师荣誉称号添加界面
@social_bp.route('/social_modify_back', methods=('GET', 'POST'))
def social_modify_back():
    form_dic = request.values.to_dict()
    sessions = DBSession()
    response = dict()
    summary_new = {}
    summary_new['name'] = form_dic['name']
    summary_new['title'] = form_dic['title']
    if summary_new != form_dic['pre'] and sessions.query(Socialwork).filter(
            Socialwork.name == str(summary_new)).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，社会兼职已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_social = sessions.query(Socialwork).filter(Socialwork.summary == form_dic['pre']).first()
    modify_social.summary=str(summary_new)
    modify_social.name=form_dic['name']
    modify_social.title=form_dic['title']
    response['error'] = 0
    response['msg'] = '修改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)

@social_bp.route('/table', methods=('GET', 'POST'))
def table():
    req=request.json
    account=req['account']
    page=int(req['page'])
    limit=int(req['limit'])
    item_type=req['type']
    session=DBSession()
    tch_info=session.query(Tch).filter(Tch.account==account).first()
    items=eval(getattr(tch_info,item_type))
    socials=Admin(Socialwork,'social').getAll()['data']
    response_items = []
    for social in socials:
        if str(social['id']) in items:
            social['is_added']=True
        else:
            social['is_added']=False
        response_items.append(social)
        
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
