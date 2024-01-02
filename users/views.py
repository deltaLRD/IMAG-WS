import datetime
import os
from functools import wraps
import ast
from admins.models import Admin
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy.sql.elements import or_
from libs.db import DBSession, Conf, Account, Tch, Stu, Jn, Patent, Prog, Comp, Mono, Soft, Gra, Honor, Course, People, \
    Socialwork,LogRecord
from login.views import save_avatar, login_required, save_resume
from log.views import createInnerLog
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
users_bp = Blueprint('users', import_name='users')
users_bp.template_folder = './templates'
users_bp.static_folder = './static'


@users_bp.route('/people', methods=('GET', 'POST'))
def people():
    sessions = DBSession()
    response = dict()
    sort = eval(sessions.query(People).first().faculty)
    faculty = []
    for index in sort:
        item = sessions.query(Tch).filter(Tch.id == int(index)).first()
        info = dict()
        info['id'] = item.id
        info['name'] = item.name
        info['Eng_name'] = item.Eng_name
        info['phone'] = item.phone
        info['email'] = item.email
        info['page'] = item.home_page
        # info['profile'] = item.profile
        # info['address'] = item.address
        # info['profile_c'] = item.profile_c
        # info['direction'] = item.direction
        info['avatar'] = item.avatar
        faculty.append(info)
    response['Faculty'] = faculty
    phd = []
    allphd = sessions.query(Stu).filter(Stu.stu_classify == '博士生').all()
    for item in allphd:
        info = dict()
        info['id'] = item.id
        info['name'] = item.name
        info['Eng_name'] = item.Eng_name
        info['phone'] = item.phone
        info['email'] = item.email
        info['page'] = item.home_page
        info['avatar'] = item.avatar
        phd.append(info)
    response['phD'] = phd
    Master = []
    allma = sessions.query(Stu).filter(Stu.stu_classify == '硕士生').all()
    for item in allma:
        info = dict()
        info['id'] = item.id
        info['name'] = item.name
        info['Eng_name'] = item.Eng_name
        info['phone'] = item.phone
        info['email'] = item.email
        info['page'] = item.home_page
        info['avatar'] = item.avatar
        Master.append(info)
    response['Master'] = Master
    Associated_Faculty = []
    response['Associated_Faculty'] = Associated_Faculty
    return json.dumps(response, ensure_ascii=False)


# 实验室成员展示页面
@users_bp.route('/people_page', methods=('GET', 'POST'))
def people_page():
    sessions = DBSession()
    sort = sessions.query(People).first()
    sort_faculty = eval(sort.faculty)
    # print(sort_faculty)
    # faculty = sessions.query(Tch).join(Account, Tch.account == Account.account).filter(
    #     or_(Tch.tch_classify == '博士生导师', Tch.tch_classify == '硕士生导师', Tch.tch_classify == '其他老师'),
    #     Account.examine == '1').all()
    a = '1'
    b = '0'
    qt = '其他老师'
    s = '硕士生'
    b = '博士生'
    ass_faculty = sessions.query(Tch).join(Account, Tch.account == Account.account).filter(Tch.tch_classify == qt,
                                                                                           Account.examine == a).all()
    PhD = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(
        Stu.stu_classify == b, Account.examine == a, Stu.graduated == '0').order_by(Stu.admission, Stu.id).all()
    ME = sessions.query(Stu).join(Account, Stu.account == Account.account).filter(Stu.stu_classify == s,
                                                                                  Account.examine == a,
                                                                                  Stu.graduated == '0').order_by(
        Stu.admission, Stu.id).all()
    factory_list = list()

    for faculty_id in sort_faculty:
        print(faculty_id)
        tch = sessions.query(Tch).join(Account, Tch.account == Account.account).filter(Tch.id == faculty_id,
                                                                                       Account.examine == a).first()
        if tch is not None:
            factory_dict = dict()
            factory_dict['id'] = faculty_id
            factory_dict['name'] = tch.name
            factory_dict['Eng_name'] = tch.Eng_name
            factory_dict['avatar'] = tch.avatar
            factory_dict['phone'] = tch.phone
            factory_dict['email'] = tch.email
            factory_dict['home_page'] = tch.home_page
            factory_dict['account'] = tch.account
            factory_dict['job_title'] = tch.job_title
            factory_list.append(factory_dict)

    # pri_ass_faculty = dict()
    # for ass_faculty_row in ass_faculty:
    #     pri_ass_faculty[ass_faculty_row.id] = ass_faculty_row
    # for ass_faculty_id in sort_ass_faculty:
    #     ass_factory_dict = dict()
    #     ass_factory_dict['id'] = ass_faculty_id
    #     ass_factory_dict['name'] = pri_ass_faculty[ass_faculty_id].name
    #     ass_factory_dict['Eng_name'] = pri_ass_faculty[ass_faculty_id].Eng_name
    #     ass_factory_dict['avatar'] = pri_ass_faculty[ass_faculty_id].avatar
    #     ass_factory_dict['phone'] = pri_ass_faculty[ass_faculty_id].phone
    #     ass_factory_dict['email'] = pri_ass_faculty[ass_faculty_id].email
    #     ass_factory_dict['home_page'] = pri_ass_faculty[ass_faculty_id].home_page
    #     ass_factory_list.append(ass_factory_dict)
    # response['ass_faculty'] = ass_factory_list

    # pri_PhD = dict()
    # for PhD_row in PhD:
    #     pri_PhD[PhD_row.id] = PhD_row
    # for PhD_id in sort_phD:
    #     PhD_dict = dict()
    #     PhD_dict['id'] = PhD_id
    #     PhD_dict['name'] = pri_PhD[PhD_id].name
    #     PhD_dict['Eng_name'] = pri_PhD[PhD_id].Eng_name
    #     PhD_dict['avatar'] = pri_PhD[PhD_id].avatar
    #     PhD_dict['phone'] = pri_PhD[PhD_id].phone
    #     PhD_dict['email'] = pri_PhD[PhD_id].email
    #     PhD_dict['home_page'] = pri_PhD[PhD_id].home_page
    #     PhD_list.append(PhD_dict)
    # response['PhD'] = PhD_list

    # pri_ME = dict()
    # for ME_row in ME:
    #     pri_ME[ME_row.id] = ME_row
    # for ME_id in sort_ME:
    #     ME_dict = dict()
    #     ME_dict['id'] = ME_id
    #     ME_dict['name'] = pri_ME[ME_id].name
    #     ME_dict['Eng_name'] = pri_ME[ME_id].Eng_name
    #     ME_dict['avatar'] = pri_ME[ME_id].avatar
    #     ME_dict['phone'] = pri_ME[ME_id].phone
    #     ME_dict['email'] = pri_ME[ME_id].email
    #     ME_dict['home_page'] = pri_ME[ME_id].home_page
    #     ME_list.append(ME_dict)
    # response['ME'] = ME_list

    # graduates = sessions.query(Gra).all()
    sessions.close()
    # return json.dumps(response, ensure_ascii=False)

    return render_template('people_page.html', faculty=factory_list, ass_faculty=ass_faculty, PhD=PhD, ME=ME)


# 学生个人资料前端
@users_bp.route('/stu_info/<account>/', methods=('GET', 'POST'))
def stu_info(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    return render_template('stu_info.html', stu_info=stu_info, account_url=stu_info)


# 教师个人资料前端
@users_bp.route('/tch_info/<account>/', methods=('GET', 'POST'))
def tch_info(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first()
    return render_template('tch_info.html', tch_info=tch_info, account_url=tch_info)


# 隐藏
@users_bp.route('/hide', methods=('GET', 'POST'))
def hide():
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                     'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    sessions = DBSession()
    data = request.json
    # print(data)
    account = data['account']
    name = data['name']
    id = data['id']
    ishide = data['ishide']
    last_item = data['last_item']
    tch = sessions.query(Tch).filter(Tch.account == account).first()
    display = eval(tch.display)
    updata = display[display_items[name]]
    if ishide == 1:
        if str(id) in updata:
            updata.remove(str(id))
    else:
        idindex = -1
        if last_item != -1:
            idindex = updata.index(str(last_item))
        updata.insert(idindex + 1, str(id))
    display[display_items[name]] = updata
    tch.display = str(display)
    # print(display)
    sessions.commit()
    sessions.close()
    return {}



# # 隐藏
# @users_bp.route('/swap', methods=('GET', 'POST'))
# def swap():
#     sessions = DBSession()
#     data = request.json
#     account = data['account']
#     pre = data['pre']
#     next = data['next']
#     tch = sessions.query(Tch).filter(Tch.account == account).first()
#     display = eval(tch.display)
#     jn_display = int(display['prog'])
#     prog = eval(tch.program)
#     prog[pre], prog[next] = prog[next], prog[prog]
#     if (jn_display >> pre) & 1 != (jn_display >> next) & 1:
#         jn_display = jn_display ^ ((1 << pre) | (1 << next))
#     display['jn'] = str(jn_display)
#     tch.display = str(display)
#     sessions.commit()
#     sessions.close()
#     return {}


# 教师个人资料修改后端
@users_bp.route('/tch_info_back', methods=('GET', 'POST'))
def tch_info_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    # print(form_dic)
    tch_info = sessions.query(Tch).join(Account, Account.account == Tch.account).filter(
        Tch.account == form_dic['account']).first()
    tch_account = sessions.query(Account).filter(Account.account == form_dic['account']).first()
    tch_info.tch_classify = form_dic['classify']
    tch_info.phone = form_dic['phone']
    tch_info.email = form_dic['email']
    tch_info.profile = form_dic['profile']
    tch_info.profile_c = form_dic['profile_c']
    tch_info.home_page = form_dic['home_page']
    tch_info.name = form_dic['name']
    tch_info.Eng_name = form_dic['Eng_name']
    tch_info.job_title = form_dic['job_title']
    if 'avatar' in request.files.to_dict():
        save_avatar(form_dic['account'], request.files['avatar'])
    if form_dic['password'] != '':
        tch_account.password = form_dic['password']
    response = dict()
    response['error'] = 0
    response['msg'] = '上传成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 学生个人资料修改后端
@users_bp.route('/stu_info_back', methods=('GET', 'POST'))
def stu_info_back():
    sessions = DBSession()
    form_dic = request.values.to_dict()
    stu_account = sessions.query(Account).filter(Account.account == form_dic['account']).first()
    stu_info = sessions.query(Stu).filter(Stu.account == form_dic['account']).first()
    stu_info.stu_classify = form_dic['classify']
    stu_info.phone = form_dic['phone']
    stu_info.email = form_dic['email']
    stu_info.profile = form_dic['profile']
    stu_info.admission = form_dic['dat']
    if 'avatar' in request.files.to_dict():
        save_avatar(form_dic['account'], request.files['avatar'])
    if form_dic['password'] != '':
        stu_account.password = form_dic['password']
    if 'tutor' in form_dic:
        stu_info.tutor = form_dic['tutor']
    if 'instructor' in form_dic:
        stu_info.instructor = form_dic['instructor']
    response = dict()
    response['error'] = 0
    response['msg'] = '更改成功'
    sessions.commit()
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


# 学生个人主页
@users_bp.route('/stu_page/<account>/', methods=('GET', 'POST'))
def stu_page(account):
    sessions = DBSession()
    stu_info = sessions.query(Stu).filter(Stu.account == account).first()
    sessions.close()
    return render_template('stu_page.html', stu_info=stu_info, account_url=stu_info)


# conference和journal等有多个作者添加的个人主页显示函数
def getJournal(display_jn, all_jn):
    db_dic = {'j': Jn, 'c': Conf}
    dis_name = {'j': 'jn_name', 'c': 'conf_name'}
    jn_info_dict = []
    sessions = DBSession()
    for id, author_list in all_jn.items():
        ishide = 0
        if id not in display_jn:
            ishide = 1
        journal = sessions.query(db_dic[id[0]]).filter(db_dic[id[0]].id == int(id[1:])).first()
        if journal is None:
            createInnerLog()
            continue
        journal = dict(journal)
        author = ""
        for it in author_list:
            author += it
            author += ' '
        display_item = journal['name'] + ', ' + journal['author'] + ', ' + '(' + journal[
            dis_name[id[0]]] + ') ' + author.rstrip(' ')
        jn_info_dict.append({'display_name': display_item, 'id': id, 'is_hide': ishide})
    sessions.close()
    return jn_info_dict


# competition和program等个人主页显示函数
def getOthers(display, all, db):
    data = []
    sessions = DBSession()
    for item in all:
        data_item = sessions.query(db).filter(db.id == int(item)).first()
        if data_item is None:
            createInnerLog()
            continue
        ishide = 0
        if str(item) not in display:
            ishide = 1
        display_item=preprocess_data(db,data_item)
        display_item['is_hide']=ishide
        # data.append({'display': dict(data_item), 'id': item, 'ishide': ishide})
        data.append(display_item)
    sessions.close()
    # print(data)
    return data


# 教师个人主页
@users_bp.route('/tch_page/<account>/', methods=('GET', 'POST'))
def tch_page(account):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.account == account).first()
    display = eval(tch_info.display)
    jn_info_dict = getJournal(display['jn'], eval(tch_info.journal))
    patent_info = getOthers(display['patent'], eval(tch_info.patent), Patent)
    prog_info = getOthers(display['prog'], eval(tch_info.program), Prog)
    mono_info = getOthers(display['mono'], eval(tch_info.monograph), Mono)
    soft_info = getOthers(display['soft'], eval(tch_info.software), Soft)
    comp_info = getOthers(display['comp'], eval(tch_info.competition), Comp)
    honor_info = getOthers(display['honor'], eval(tch_info.honor), Honor)
    course_info = getOthers(display['course'], eval(tch_info.course), Course)
    social_info = getOthers(display['social'], eval(tch_info.social), Socialwork)
    return render_template('tch_page.html', tch_info=tch_info, journal=jn_info_dict, social_info=social_info,
                           patent_info=patent_info, program=prog_info, mono_info=mono_info, soft_info=soft_info,
                           competition=comp_info, honor_info=honor_info, course_info=course_info, account_url=tch_info)

# 显示设置的Controller
@users_bp.route('/tch_page/<account>/visible',methods=('GET','POST'))
def tch_page_visisble(account):
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                    'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    model_mp={'patent':Patent,'prog':Prog,'mono':Mono,'soft':Soft,'comp':Comp,'honor':Honor,'course':Course,'social':Socialwork}

    req=request.json
    page=req['page']
    limit=req['limit']
    item_type=req['type']
    session=DBSession()
    tch_info=session.query(Tch).filter(Tch.account==account).first()
    display=eval(tch_info.display)
    if item_type=='journal' or item_type=='conference':
        res=get_journal_by_page(display[display_items[item_type]],eval(getattr(tch_info,item_type)),page,limit)
    else:    
        model=model_mp[display_items[item_type]]
        res=get_others_by_page(display[display_items[item_type]],eval(getattr(tch_info,item_type)),page,limit,model)
    return res
# 显示设置中的分页查询
def get_journal_by_page(display,all,page,limit):
    db_dic = {'j': Jn, 'c': Conf} # model映射
    dis_name = {'j': 'jn_name', 'c': 'conf_name'}
    jn_info_dict = []
    sessions = DBSession()
    for id, author_list in all.items():
        is_hide = 0
        if id not in display:
            is_hide = 1
        journal = sessions.query(db_dic[id[0]]).filter(db_dic[id[0]].id == int(id[1:])).first()
        if journal is None:
            createInnerLog()
            # todo 找不到报错
            continue
        journal = dict(journal)
        author = ""
        for it in author_list:
            author += it
            author += ' '
        display_item = journal['name'] + ', ' + journal['author'] + ', ' + '(' + journal[dis_name[id[0]]] + ') ' + author.rstrip(' ')
        journal['display_name']=display_item
        journal['is_hide']=is_hide
        journal['id']=id
        jn_info_dict.append(journal)
    sessions.close()
    # 分页逻辑
    start_index=(page-1)*limit
    end_index=start_index+limit
    total_items=len(jn_info_dict)
    start_index=min(start_index,total_items)
    end_index=min(end_index,total_items)
    jn_info_dict_page=jn_info_dict[start_index:end_index]
    res={
        "code":0,
        "msg":"",
        "count":total_items,
        "data":jn_info_dict_page
    }
    return res
# 显示设置中的除论文之外的分页查询
def get_others_by_page(display,all,page,limit,model):
    session=DBSession()
    data=[]
    for id in all:
        # print(id)
        data_item=session.query(model).filter(model.id==int(id)).first()
        if data_item is None:
            createInnerLog()
            #Todo 添加报错
            continue
        is_hide=False
        if str(id) not in display:
            is_hide=True
        # data.append({'display': display_content, 'id': id, 'ishide': is_hide})
        display_content=preprocess_data(model,data_item)
        display_content['is_hide']=is_hide
        data.append(display_content)
    session.close()
    start_index=(page-1)*limit
    end_index=start_index+limit
    total_items=len(data)
    start_index=min(start_index,total_items)
    end_index=min(end_index,total_items)
    data_page=data[start_index:end_index]
    res={
        "code":0,
        "msg":"",
        "count":total_items,
        "data":data_page
    }
    return res

# 统一处理前端显示层
def preprocess_data(model,data_item):
    res=dict(data_item)
    if model == Patent:
        res['display_name']=str(res['name'])+','+str(res['patentee'])+','+str(res['patent_num'])+','+str(res['application_dat'])
    
    elif model == Prog:
        res['display_name']= str(res['pro_source'])+', \"'+str(res['name'])+'\",'+ str(res['start_time'])+' - '+str(res['deadline'])
        if data_item.cost is not None:
            res['display_name']=res['display_name']+str(res['cost'])+'万,'
        else:
            res['display_name']=res['display_name']+str(res['fund'])+'万 (直接经费),'
        res['display_name']=res['display_name']+"主持("+str(res['principal'])+')'
        
    elif model == Mono:
        res['display_name']=str(res['name'])+','+str(res['employ'])+','+str(res['editor'])
    
    elif model == Soft:
        res['display_name']=str(res['name'])+','+str(res['author'])
    
    elif model == Comp:
        res['display_name']=str(res['participant'])+','+str(res['name'])+str(res['ranking'])+' , 指导老师：'+str(res['teachers'])
    
    elif model == Honor:
        res['display_name']=str(res['name'])+','+str(res['title'])
    
    elif model == Course:
        res['display_name']=str(res['teacher'])+','+str(res['name'])
    
    elif model == Socialwork:
        res['display_name']=str(res['name'])+','+str(res['title'])
    
    elif model==Jn:
        res['display_name']=str(res['name']) + ', ' + str(res['author']) + ', ' + '(' + str(res['jn_name']) + ')'
    
    elif model==Conf:
        res['display_name']=str(res['name']) + ', ' + str(res['author']) + ', ' + '(' + str(res['conf_name']) + ')'
    return res
    

# 改变某一条目的可见性
@users_bp.route('/display',methods=('GET','POST'))
def display():
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                    'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    session =DBSession()
    req=request.json
    account=req['account']
    name=req['name']
    id=req['id']
    is_hide=req['ishide']
    tch=session.query(Tch).filter(Tch.account==account).first()
    # print("===========wj_debug===========")
    display=eval(tch.display)# 用户的全部display预设
    # print("display:{}".format(display))
    item_display=display[display_items[name]] # 目前种类的display预设
    # print("item_display:{}".format(item_display))
    items=eval(getattr(tch,name)) # 目前修改种类的预设
    # print("items:{}".format(items))
    items_list=None
    if name=='journal' or name=='conference':
        items_list=list(items.keys()) # 目前修改种类的键列表，为了做有序化
    else:
        items_list=items
    # print("items_list:{}".format(items_list))
    last_display_index=len(items_list)-1 # 寻找最后一个显示的元素的index
    for index,value in enumerate(items_list):
        if value not in item_display:
            last_display_index=max(0,index-1)
            break
    # print("last_display_index:{}".format(last_display_index))
    if is_hide==1:
        if str(id) in item_display:
            item_display.remove(str(id))
        items_list.remove(str(id))
        items_list.insert(last_display_index,str(id))
        # print("items_list:{}".format(items_list))
        updated_items=None
        if name=='conference' or name=='journal':
            updated_items={}
            for val in items_list:
                updated_items[val]=items[val]
        else:
            updated_items=list(items_list)
    else:
        item_display.append(str(id))
        items_list.remove(str(id))
        items_list.insert(last_display_index+1,str(id))
        # print("items_list:{}".format(items_list))
        updated_items=None
        if name=='conference' or name=='journal':
            updated_items={}
            for val in items_list:
                updated_items[val]=items[val]
        else:
            updated_items=list(items_list)
    display[display_items[name]]=item_display
    setattr(tch,name,str(updated_items))
    tch.display=str(display)
    session.commit()
    session.close()
    return {}

# 显示设置页面的搜索功能
@users_bp.route('/search',methods=(['POST']))
def search():
    req=request.json
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                    'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    content=req['content']# 搜索内容
    item=req['item'] # 搜索种类
    account=req['account'] # 账户
    page=int(req['page'])
    limit=int(req['limit'])
    session=DBSession()
    tch_info=session.query(Tch).filter(Tch.account==account).first()
    items=eval(getattr(tch_info,item)) # 用户对应项目所收录的
    display=eval(tch_info.display) # 用户全部展示项目
    type_items=display[display_items[item]] # 用户对应项目所展示的
    # print("items:{}".format(items))
    model_mp={'journal':Jn,'conference':Conf,'patent':Patent,'program':Prog,'monograph':Mono,'software':Soft,'competition':Comp,'honor':Honor,'course':Course,'social':Socialwork}
    res=[]
    if(item=='journal'):
        search_journals=session.query(Jn).filter(Jn.name.like('%'+content+'%')).all()
        search_conference=session.query(Conf).filter(Conf.name.like('%'+content+'%')).all()
        for journal in search_journals:
            if 'j'+str(journal.id) in items:
                display_item=preprocess_data(Jn,journal)
                is_hide=True
                if 'j'+str(journal.id) in type_items:
                    is_hide=False
                display_item['is_hide']=is_hide
                display_item['id']='j'+str(journal.id)
                res.append(display_item)
        for conference in search_conference:
            if 'c'+str(conference.id) in items:
                display_item=preprocess_data(Conf,conference)
                is_hide=True
                if 'c'+str(conference.id) in type_items:
                    is_hide=False
                display_item['is_hide']=is_hide
                display_item['id']='c'+str(conference.id)
                res.append(display_item)
    else:
        search_items=session.query(model_mp[item]).filter(model_mp[item].name.like('%'+content+'%')).all()  
        for search_item in search_items:
            if str(search_item.id) in items:
                display_item=preprocess_data(model_mp[item],search_item)
                is_hide=True
                if str(search_item.id) in type_items:
                    is_hide=False
                display_item['is_hide']=is_hide
                res.append(display_item)

    start_index=(page-1)*limit
    end_index=start_index+limit
    total_items=len(res)
    start_index=min(start_index,total_items)
    end_index=min(end_index,total_items)
    final_res=res[start_index:end_index]
    result={
        "code":0,
        "msg":"",
        "count":total_items,
        "data":final_res
    }
    return result

############################

# 用户添加论文主页后端
@users_bp.route('/add', methods=('GET', 'POST'))
def add():
    # dict_=['conference','journal']
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                     'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    data = request.get_json()
    session = DBSession()
    account = data['account']
    id = data['id']
    item = data['item']
    response = dict()
    user = dict(session.query(Tch).join(Account, Account.account == Tch.account).filter(Tch.account == account).first())
    up_data = eval(user[item])
    up_data_copy=None
    display = eval(user['display'])
    if item == 'journal':
        up_data_copy={}
        if (str(id)) in up_data:
            response['error'] = 1
            response['message'] = "已存在!"
            return json.dumps(response, ensure_ascii=False)
        else:
            list = data['select']
            arr = ['第一作者', '共同一作', '通讯作者', '其他作者']
            jn_list = []
            for i in range(4):
                if list[i] == 1:
                    jn_list.append(arr[i])

            up_data_copy[str(id)]=jn_list# 为了保证字典顺序，将新添加的项目放于头部
            for key,values in up_data.items():
                up_data_copy[key]=values
            display[display_items[item]].append(str(id))

    else:
        up_data_copy=[]
        if str(id) in up_data:
            response['error'] = 1
            response['message'] = "已存在"
            return json.dumps(response, ensure_ascii=False)
        else:
            up_data_copy.append(str(id))
            print("id:{}".format(str(id)))
            for id in up_data:
                up_data_copy.append(id)
            print("up_data_copy:{}".format(up_data_copy))
            print("display_items[item]:{}".format(display_items[item]))
            print("dispaly[display_items[item]]:{}".format(display[display_items[item]]))
            display[display_items[item]].append(str(id))
            print("dispaly[display_items[item]]:{}".format(display[display_items[item]]))
    session.query(Tch).filter(Tch.account == account).update(
        {item: str(up_data_copy), 'display': str(display)})
    session.commit()
    session.close()
    response['message'] = "添加成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# # 教师个人主页
# @users_bp.route('/tch_page_database/<account>/', methods=('GET', 'POST'))
# def tch_page_database(account):
#     sessions = DBSession()
#     tch_info = sessions.query(Tch).filter(Tch.account == account).first()
#     conf_info_dict = paper(tch_info.conference, Conf)
#     jn_info_dict = paper(tch_info.journal, Jn)
#     patent_info = gain(tch_info.patent, Patent)
#     prog_info = gain(tch_info.program, Prog)
#     social_info = gain(tch_info.social, Socialwork)
#     mono_info = gain(tch_info.monograph, Mono)
#     soft_info = gain(tch_info.software, Soft)
#     comp_info = gain(tch_info.competition, Comp)
#     honor_info = gain(tch_info.honor, Honor)
#     course_info = gain(tch_info.course, Course)
#     return render_template('tch_page_database.html', tch_info=tch_info,
#                            jn_info_dict=jn_info_dict, conf_info_dict=conf_info_dict, social_info=social_info,
#                            patent_info=patent_info, prog_info=prog_info, mono_info=mono_info, soft_info=soft_info,
#                            comp_info=comp_info, honor_info=honor_info, course_info=course_info, account_url=tch_info)


# 教师个人主页
@users_bp.route('/tch_page_public/<id>/', methods=('GET', 'POST'))
def tch_page_public(id):
    sessions = DBSession()
    tch_info = sessions.query(Tch).filter(Tch.id == id).first()
    display = eval(tch_info.display)
    jn_info_dict = getJournal(display['jn'], eval(tch_info.journal))
    patent_info = getOthers(display['patent'], eval(tch_info.patent), Patent)
    # for item in patent_info_items:
    #     patent = sessions.query(Patent).filter(Patent.id == int(item)).first()
    #     dat = datetime.datetime.strftime(patent.effect_dat, "%Y-%m-%d")
    #     display_item = patent.patentee + ': ' + patent.name + ', 专利号：' + patent.application_num
    #     patent_info.append({'display': display_item, 'id': item})
    prog_info = getOthers(display['prog'], eval(tch_info.program), Prog)
    mono_info = getOthers(display['mono'], eval(tch_info.monograph), Mono)
    # for item in mono_info_items:
    #     mono = sessions.query(Mono).filter(Mono.id == int(item)).first()
    #     display_item = mono.name + ', ' + mono.editor
    #     mono_info.append({'display': display_item, 'id': item})
    soft_info = getOthers(display['soft'], eval(tch_info.software), Soft)
    # for item in soft_info_items:
    #     soft = sessions.query(Soft).filter(Soft.id == int(item)).first()
    #     times = datetime.datetime.strftime(soft.times, "%Y-%m-%d")
    #     display_item = soft.name + ', ' + soft.author + ', ' + times
    #     soft_info.append({'display': display_item, 'id': item})
    comp_info = getOthers(display['comp'], eval(tch_info.competition), Comp)
    # for item in all_comps:
    #     ishide = 0
    #     if item not in comp_info_items:
    #         ishide = 1
    #     comp = sessions.query(Comp).filter(Comp.id == int(item)).first()
    #     if comp is None:
    #         continue
    #     display_item = comp.participant + ' , ' + comp.name + '  ' + comp.ranking + ' , 指导老师:  ' + comp.teachers
    #     comp_info.append({'display': display_item, 'id': item, 'ishide': ishide})
    honor_info = getOthers(display['honor'], eval(tch_info.honor), Honor)
    # for item in honor_info_items:
    #     honor = sessions.query(Honor).filter(Honor.id == int(item)).first()
    #     display_item = honor.title
    #     honor_info.append({'display': display_item, 'id': item})
    course_info = getOthers(display['course'], eval(tch_info.course), Course)
    # for item in course_info_items:
    #     course = sessions.query(Course).filter(Course.id == int(item)).first()
    #     display_item = course.name
    #     course_info.append({'display': display_item, 'id': item})
    social_info = getOthers(display['social'], eval(tch_info.social), Socialwork)
    # for item in social_info_items:
    #     social = sessions.query(Socialwork).filter(Socialwork.id == int(item)).first()
    #     display_item = social.title
    #     social_info.append({'display': display_item, 'id': item})
    return render_template('tch_page_public.html', tch_info=tch_info,
                           journal=jn_info_dict, social_info=social_info,
                           patent_info=patent_info, program=prog_info, mono_info=mono_info, soft_info=soft_info,
                           competition=comp_info, honor_info=honor_info, course_info=course_info, account_url=tch_info)


##学生无 honor 和 course
@users_bp.route('/user_page/<name>', methods=('GET', 'POST'))
def queryByid(name):
    sessions = DBSession()
    response = dict()
    classify = '1'
    tch = sessions.query(Tch).filter(Tch.name == name).first()
    if tch is not None:
        classify = '0'
    if classify == '0':
        user = sessions.query(Tch).filter(Tch.name == name).first()
        response['classify'] = '0'
    else:
        user = sessions.query(Stu).filter(Stu.name == name).first()
        response['classify'] = '1'
    response['status'] = 1
    response['id'] = user.id
    info = dict()
    info['name'] = user.name
    info['Eng_name'] = user.Eng_name
    info['phone'] = user.phone
    info['email'] = user.email
    info['profile'] = user.profile
    info['address'] = user.address
    info['direction'] = user.direction
    info['avatar'] = user.avatar
    response['info'] = info
    display = eval(user.display)
    response['journal'] = display['jn']
    response['softwareCopyright'] = display['soft']
    response['patent'] = display['patent']
    response['monograph'] = display['mono']
    response['competition'] = display['comp']
    response['project'] = display['prog']
    if classify == '教师':
        response['honor'] = display['honor']
        response['course'] = display['course']
        response['info']['profile_c'] = user.profile_c
    return json.dumps(response, ensure_ascii=False)


# 用户主页修改后端
@users_bp.route('/delete', methods=('GET', 'POST'))
def user_database():
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                     'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    dict_data = ['journal', 'conference']
    sessions = DBSession()
    data = request.get_json()
    print(data)
    account = data['account']
    id = str(data['id'])
    item = data['item']
    user_info = dict(sessions.query(Tch).filter(Tch.account == account).first())
    update_data = eval(user_info[item]) # 用户对应项目的已收录列表
    display = eval(user_info['display']) # 用户全部显示项目
    hide = display[display_items[item]] # 用户对应显示项目
    if item in dict_data:
        del update_data[id]
    else:
        update_data.remove(id)
    if str(id) in hide:
        hide.remove(id)
        display[display_items[item]] = hide
    sessions.query(Tch).filter(Tch.account == account).update({item: str(update_data), 'display': str(display)})
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "删除成功!"
    return json.dumps(response, ensure_ascii=False)


# 用户主页修改后端
@users_bp.route('/order', methods=(['POST']))
def order():
    display_items = {'conference': 'jn', 'journal': 'jn', 'competition': 'comp', 'course': 'course', 'patent': 'patent',
                     'program': 'prog', 'social': 'social', 'software': 'soft', 'honor': 'honor', 'monograph': 'mono'}
    sessions = DBSession()
    data = request.get_json()
    account = data['account']
    item = data['item']
    order_items = data['order_items']
    pre = eval(dict(sessions.query(Tch).filter(Tch.account == account).first())[item])
    if item == 'journal':
        order_items_dic = dict()
        for id in order_items:
            order_items_dic[id] = pre[id]
        for id in pre:
            if id not in order_items_dic:
                order_items_dic[id]=pre[id]
        order_items = order_items_dic
        print(order_items)
    else:
        commit_items=[]
        for id in order_items:
            commit_items.append(id)
        for id in pre:
            if id not in commit_items:
                commit_items.append(id)          
        order_items=commit_items  
    sessions.query(Tch).filter(Tch.account == account).update({item: str(order_items)})
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "排序成功!"
    return json.dumps(response, ensure_ascii=False)


# 用户主页修改后端
@users_bp.route('/user_page_back', methods=('GET', 'POST'))
def user_page_back():
    sessions = DBSession()
    data = request.get_json()
    account = data['account']
    display = data['display']
    user_display = {'jn': display['journal'], 'comp': display['competition'], 'course': display['course'],
                    'patent': display['patent'], 'prog': display['program'], 'social': display['social'],
                    'soft': display['software'], 'mono': display['monograph'], 'honor': display['honor']}
    user_info = sessions.query(Tch).filter(Tch.account == account).first()
    if user_info is None:
        user_info = sessions.query(Stu).filter(Stu.account == account).first()
    user_info.display = str(user_display)
    print(user_display)
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "保存成功!"
    return json.dumps(response, ensure_ascii=False)


