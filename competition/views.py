import ast
import functools
import math
from sqlalchemy import desc
from admins.models import Admin
from flask import *
from flask import Blueprint, request, render_template
from libs.db import DBSession, Tch, Stu, Account, Comp
from file_save.file_Save import save_File

competition_bp = Blueprint('competition', import_name='competition')
competition_bp.template_folder = './templates'
competition_bp.static_folder = './static'

#竞赛排序函数
def compare(x, y):
    score_dic = {
        '一等奖': 1.1,
        '第一名': 1,
        '二等奖': 2.1,
        '第二名': 2,
        '三等奖': 3.1,
        '第三名': 3,
        '优胜奖': 4
    }

    # 先对时间进行排序
    if x['year'] > y['year']:
        return -1
    elif x['year'] < y['year']:
        return 1
    # 再对排名进行排序,先进行映射，后排序，规则是 不在score_dic就排最前面，然后是第一名 一等奖 第二名 ....最后是优胜奖
    x_score = score_dic[x['ranking']] if x['ranking'] in score_dic else 0
    y_score = score_dic[y['ranking']] if y['ranking'] in score_dic else 0
    return x_score - y_score


# 首页论文
@competition_bp.route('/', methods=('GET', 'POST'))
def competition():
    sessions = DBSession()
    comp = sessions.query(Comp).all()
    comp = [dict(i) for i in comp]
    comp = sorted(comp, key=functools.cmp_to_key(compare))
    return render_template('competition.html', comp=comp)


# 用户添加论文主页后端
@competition_bp.route('/details_tch/<id>/<account>', methods=('GET', 'POST'))
def details(id, account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    comp = Admin(Comp, 'competition').getOne(id)
    if comp['pic'] is not None and comp['pic'] != '':
        comp['src'] = "../../static/competition_encd/" + str(id) + '/' + comp['pic']
    else:
        comp['src'] = ''
    sessions.close()
    return render_template('comp_details.html', comp=comp, user_account=tch_info, account_url=tch_info)


@competition_bp.route('/api/<account>', methods=('GET', 'POST'))
def competition_add_page(account):
    sessions = DBSession()
    classify = sessions.query(Account).filter(Account.account == account).first().classify
    if classify == '学生':
        tch_info = eval(sessions.query(Stu).filter(Stu.account == account).first().competition)
    else:
        tch_info = eval(sessions.query(Tch).filter(Tch.account == account).first().competition)
    count = 0
    data = []
    for key in tch_info:
        jn = sessions.query(Comp).filter(Comp.id == eval(key)).first()
        if jn is not None:
            dic_t = dict()
            dic_t['id'] = jn.id
            dic_t['name'] = jn.name
            dic_t['author'] = jn.teachers
            count += 1
            dic_t['index'] = count
            dic_t['new_item'] = jn.name + ', ' + jn.ranking
            data.append(dic_t)
    response = dict()
    response['code'] = 0
    response['data'] = data
    response['msg'] = ""
    response['count'] = count
    return json.dumps(response, ensure_ascii=False)

# 比赛收录界面
@competition_bp.route('/table', methods=('GET', 'POST'))
def table():
    req=request.json
    account=req['account']
    page=int(req['page'])
    limit=int(req['limit'])
    item_type=req['type']
    session=DBSession()
    tch_info=session.query(Tch).filter(Tch.account==account).first()
    items=eval(getattr(tch_info,item_type))
    competitions=Admin(Comp,'competition').getAll()['data']
    response_items = []
    print(f'items:{items}')
    for competition in competitions:
        print(competition['id'])
        if str(competition['id']) in items:
            competition['is_added']=True
        else:
            competition['is_added']=False
        response_items.append(competition)
        
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


# # 教师竞赛添加界面
# @competition_bp.route('/comp_add_tch/<account>/', methods=('GET', 'POST'))
# def comp_add_tch(account):
#     sessions = DBSession()
#     tch_info = sessions.query(Tch).filter(Tch.account == account).first()
#     return render_template('comp_add_tch.html', user_account=tch_info, account_url=tch_info, name="competitions")


# 用户添加论文主页后端
@competition_bp.route('/add', methods=('GET', 'POST'))
def comp_add():
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    response = dict()
    user = session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    comp_list = user.competition
    if comp_list is None:
        comp_list = []
    else:
        comp_list = eval(comp_list)
    if str(id) in comp_list:
        response['error'] = 1
        response['message'] = "竞赛已存在!"
        return json.dumps(response, ensure_ascii=False)
    display = eval(user.display)
    comp = int(display['comp'])
    comp = comp ^ (1 << data['mount'])
    display['comp'] = str(comp)
    user.display = str(display)
    comp_list.append(str(id))
    user.competition = str(comp_list)
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 竞赛教师上传后端
@competition_bp.route('/comp_upload_back', methods=('GET', 'POST'))
def comp_upload_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    if not 'adds' in form_dic:
        form_dic['adds'] = '0'
    # print(form_dic)
    response = dict()
    account = form_dic['account']
    if sessions.query(Comp).filter(Comp.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '上传失败！竞赛已存在!'
        return json.dumps(response, ensure_ascii=False)
    user_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == account).first()
    if user_info is None:
        # isteacher = 0
        user_info = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
            Stu.account == account).first()
    summary = {}
    summary['name'] = form_dic['name']
    summary['teachers'] = form_dic['teachers']
    summary['participant'] = form_dic['participant']
    summary['ranking'] = form_dic['ranking']
    new_comp = Comp(
        name=form_dic['name'],
        teachers=form_dic['teachers'],
        participant=form_dic['participant'],
        ranking=form_dic['ranking'],
        summary=str(summary)
    )
    sessions.add(new_comp)
    new_comp = sessions.query(Comp).filter(Comp.name == form_dic['name']).first()
    if form_dic['adds'] == str(1):
        tch_comp = ast.literal_eval(user_info.competition)
        tch_comp.append(str(new_comp.id))
        user_info.competition = str(tch_comp)
    response['error'] = 0
    response['url'] = '/competition/details/' + str(new_comp.id)
    response['msg'] = '上传成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 竞赛教师上传
@competition_bp.route('/comp_upload_tch/<account>/', methods=('GET', 'POST'))
def comp_upload_tch(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('comp_upload_tch.html', tch_info=tch_info, account_url=tch_info)


@competition_bp.route('/comp_modify_tch/<comp_name>/<account>', methods=('GET', 'POST'))
def comp_modify_tch(comp_name, account):
    sessions = DBSession()
    modify_comp = sessions.query(Comp).filter(Comp.name == comp_name).first()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    return render_template('comp_modify_tch.html', comp_home=modify_comp, ch_info=tch_info, account_url=tch_info)


@competition_bp.route('/comp_modify_back', methods=('GET', 'POST'))
def comp_modify_back():
    form_dic = request.values.to_dict()
    print(form_dic)
    sessions = DBSession()
    response = dict()
    if form_dic['pre'] != form_dic['name'] and sessions.query(Comp).filter(
            Comp.name == form_dic['name']).first() is not None:
        response['error'] = 1
        response['msg'] = '修改失败，竞赛已存在！'
        return json.dumps(response, ensure_ascii=False)
    modify_comp = sessions.query(Comp).filter(Comp.name == form_dic['pre']).first()
    summary = {}
    summary['name'] = form_dic['name']
    summary['teachers'] = form_dic['teachers']
    summary['participant'] = form_dic['participant']
    summary['ranking'] = form_dic['ranking']
    modify_comp.ranking = form_dic['ranking']
    modify_comp.name = form_dic['name']
    modify_comp.teachers = form_dic['teachers']
    modify_comp.participant = form_dic['participant']
    modify_comp.summary = str(summary)
    response['error'] = 0
    response['msg'] = '修改成功'
    response['url'] = '/competition/details_tch/' + str(modify_comp.id) + '/' + form_dic['account']
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 竞赛删除
@competition_bp.route('/delete/<id>', methods=(['DELETE']))
def comp_delete(id):
    Admin(Comp, 'competition').deleteOne(id)
    response = dict()
    response['message'] = "删除成功"
    return json.dumps(response, ensure_ascii=False)
