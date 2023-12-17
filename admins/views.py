import base64
import os
import time
import functools
import bibtexparser
from flask import *
from flask import Blueprint, request, render_template
from sqlalchemy import or_
# from sqlalchemy.cyextension.processors import str_to_date
from sqlalchemy.cyextension.processors import str_to_date
# from sqlalchemy.cyextension.processors import str_to_date
from libs.db import DBSession, Conf, Account, Stu, Tch, Jn, Patent, Soft, Mono, Prog, Comp, Course, Honor, News, \
    Resource, Issues, People
from login.views import save_avatar
from resource.views import save_resource
from flask import make_response
from .models import Admin
host = os.environ.get("HOST", "http://10.10.109.100")
# host='http://10.10.109.100'
admins_bp = Blueprint('admins', import_name='admins')
admins_bp.template_folder = './templates'
admins_bp.static_folder = './static'

pictureKinds = ['xbm', 'tif', 'pjp', 'svgz', 'jpg', 'jpeg', 'ico', 'tiff', 'gif', 'svg', 'jfif', 'webp', 'png',
                'bmp', 'pjpeg', 'avif']

# 审批页面
@admins_bp.route('/people', methods=(['GET']))
def people():
    response = dict()
    response['name'] = "教师展示顺序自定义"
    response['id'] = 'edit'
    response = make_response(jsonify([response]))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-10/1'
    return response


# 审批页面
@admins_bp.route('/people/edit', methods=(['PUT']))
def people_save():
    sessions = DBSession()
    data = request.json['items']
    sort_list=[item['id'] for item in data]
    tch=sessions.query(People).first()
    tch.faculty=str(sort_list)
    sessions.commit()
    sessions.close()
    return {"id":"edit"}


# 审批页面
@admins_bp.route('/people/edit', methods=(['GET']))
def people_edit():
    sessions = DBSession()
    sort = sessions.query(People).first()
    sort_faculty = eval(sort.faculty)
    response = dict()
    items = []
    for id in sort_faculty:
        tch = sessions.query(Tch).filter(Tch.id == id).first()
        items.append({'id': tch.id, 'account': tch.account, 'name': tch.name})
    response['items'] = items
    response['name'] = "教师展示顺序自定义"
    response['id'] = 'edit'
    return response




# 论文作者修正
def author_modify(raw_author):
    # 按and进行切分，形成数组
    author_Lists = raw_author.split('and')
    res = ""
    for item in author_Lists:
        # 对每一个作者人名进行切分形成 first last
        author_split = bibtexparser.customization.splitname(item)
        # 定制化 按first_name last_name, 进行拼接
        if len(author_split['first'])>0:
            res=res+author_split['first'][0] + ' '
        res = res + author_split['last'][0] + ', '
    # 舍弃最后多余的逗号与空格
    return res[:-2]


# 论文bibtex上传
@admins_bp.route('/Upload', methods=(['POST']))
def create_bibtex():
    data = request.json
    conference_key = ["name", "author", "conf_name", "organizer", "conf_dat", "dat", "page", "address", "num", "DOI",
                      "employ", "employ_num", "ccf", "times", "link", "code_link", "author_classify", "bibtex", "encd",
                      "code_encd"]
    journal_key = ["name", "author", "jn_name", "dat", "num", "employ", "employ_num", "ccf", "cas", "jcr", "times",
                   "vol", "no", "page", "DOI", "link", "code_link", "encd", "code_encd"]
    res = dict()
    for item_data in data['sample']:
        type = item_data['entryType']
        item = item_data['entryTags']
        if type == 'inproceedings':
            # print(item['entryTags']['title'])
            Upload_data = dict.fromkeys(conference_key, '')
            Upload_data['name'] = item['title']
            # print(author_modify(item['author']))
            Upload_data['author'] = author_modify(item['author'])
            if 'pages' in item:
                Upload_data['page'] = item['pages']
            if 'year' in item:
                Upload_data['dat'] = item['year']
            if 'booktitle' in item:
                Upload_data['conf_name'] = item['booktitle']
            Upload_data['bibtex'] = False
            print(Upload_data)
            res = Admin(Conf, 'conference').upLoad(Upload_data)
        else:
            Upload_data = dict.fromkeys(journal_key, '')
            Upload_data['name'] = item['title']
            Upload_data['author'] = author_modify(item['author'])
            if 'pages' in item:
                Upload_data['page'] = item['pages']
            if 'year' in item:
                Upload_data['dat'] = item['year']
            if 'journal' in item:
                Upload_data['jn_name'] = item['journal']
            if 'volume' in item:
                Upload_data['vol'] = item['volume']
            if 'number' in item:
                Upload_data['no'] = item['number']
            Upload_data['bibtex'] = False
            print(Upload_data)
            res = Admin(Jn, 'journal').upLoad(Upload_data)
    return res






# 查询列表
@admins_bp.route('/competition', methods=(['GET']))
def posts():
    res = Admin(Comp, 'competition').getAll()
    response = make_response(jsonify(res['data']))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-24/' + str(len(res['data']))
    return response


# 上传
@admins_bp.route('/competition', methods=(['POST']))
def create():
    data = request.json
    files = None
    data['file'] = []
    data['pic'] = ''
    if 'files' in data:
        files = data['files']
        file = []
        st = 0
        if data['pictures'] == 1:
            data['pic'] = files[0]['title']
            st = 1
        for i in range(st, len(files)):
            file.append(files[i]['title'])
        data['file'] = file
    res = Admin(Comp, 'competition').upLoad(data)
    if files is not None:
        for item in files:
            save_Filebase64('competition', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(res['id']), item['title']))
    return res


# 详情
@admins_bp.route('/competition/<int:id>', methods=(['GET']))
def posts_id(id):
    res = Admin(Comp, 'competition').getOne(id)
    pictures = []
    if res['pic'] != '':
        pictures.append(
            {'src': host+'/competition/static/competition_encd/' + str(id) + '/' + res['pic'],
             'title': res['pic']})
        # pictures.append(
        #     {'src': 'http://127.0.0.1:5000/competition/static/competition_encd/' + str(id) + '/' + res['pic']})

        res['pictures'] = pictures
    del res['pic']
    files = []
    for item in eval(res['file']):
        files.append(
            {'title': item, 'src': host+'/competition/static/competition_encd/' + str(id) + '/' + item})
    del res['file']
    res['files'] = files

    return res


# 修改
@admins_bp.route('/competition/<int:id>', methods=["PUT"])
def modify(id):
    data = request.json
    modify_word = ['name', 'participant', 'ranking', 'teachers']
    update_data = dict()
    files = None
    st = 0
    if 'files' in data:
        files = data['files']
        file = []
        if data['ispictures'] == 1:
            update_data['pic'] = files[0]['title']
            st = 1
        update_data['file'] = str(data['files_name'][st:])
    else:
        if data['ispictures'] == 1:
            update_data['pic'] = data['files_name'][0]
            st = 1
        else:
            update_data['pic'] = ''
        update_data['file'] = str(data['files_name'][st:])
    for item in modify_word:
        update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('competition', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Comp, 'competition').modify(update_data, id)


# 删除
@admins_bp.route('/competition/<int:id>', methods=["DELETE"])
def delete_id(id):
    Admin(Comp, 'competition').deleteOne(id)
    return dict()


# 查询列表
@admins_bp.route('/program', methods=(['GET']))
def posts_pro():
    range = eval(request.args.get("range"))
    res = Admin(Prog, 'competition').getAll()
    response = make_response(jsonify(res['data'][range[0]:range[1] + 1]))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-10/' + str(len(res['data']))
    return response


# 上传
@admins_bp.route('/program', methods=(['POST']))
def upload_pro():
    data = request.json
    files = None
    data['file'] = []
    if 'files' in data:
        files = data['files']
        file = []
        for item in files:
            file.append(item['title'])
        data['file'] = file
    res = Admin(Prog, 'program').upLoad(data)
    if files is not None:
        for item in files:
            save_Filebase64('program', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(res['id']), item['title']))
    if files is not None:
        for item in files:
            save_Filebase64('program', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(res['id']), item['title']))
    return res


# 详情
@admins_bp.route('/program/<int:id>', methods=(['GET']))
def posts_id_pro(id):
    res = Admin(Prog, 'competition').getOne(id)
    files = []
    for item in eval(res['file']):
        files.append(
            {'title': item, 'src': host+'/program/static/program_encd/' + str(id) + '/' + item})
    res['files'] = files
    res['level_file'] = host+'/program/static/program_encd/项目分类一览表.pdf'
    return res


# 修改
@admins_bp.route('/program/<int:id>', methods=["PUT"])
def modify_pro(id):
    data = request.json
    modify_word = ["name", "principal", "level", "start_time", "deadline", "cost", "prog_num", "pro_source", "member",
                   "fund","role"]
    update_data = dict()
    st = 0
    files = None
    if 'files' in data:
        files = data['files']
        file = []
        if data['ispictures'] == 1:
            update_data['pic'] = files[0]['title']
            st = 1
        update_data['file'] = str(data['files_name'][st:])
    else:
        if data['ispictures'] == 1:
            update_data['pic'] = data['files_name'][0]
            st = 1
        update_data['file'] = str(data['files_name'][st:])
    for item in modify_word:
        update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('program', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Prog, 'program').modify(update_data, id)


# 删除
@admins_bp.route('/program/<int:id>', methods=["DELETE"])
def delete_id_pro(id):
    Admin(Prog, 'competition').deleteOne(id)
    return dict()


# 删除
@admins_bp.route('/conference/<int:id>', methods=["DELETE"])
def delete_id_conference(id):
    Admin(Conf, 'conference').deleteOne(id)
    return dict()


# 查询列表
@admins_bp.route('/conference', methods=(['GET']))
def posts_conference():
    range = eval(request.args.get("range"))
    res = Admin(Conf, 'conference').getAll()
    res['data'].sort(key=lambda conference: conference['bibtex'])
    response = make_response(jsonify(res['data'][range[0]:range[1] + 1]))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-10/' + str(len(res['data']))
    return response


# 修改
@admins_bp.route('/conference/<int:id>', methods=["PUT"])
def modify_con(id):
    data = request.json
    modify_word = ["name", "author", "conf_name", "organizer", "conf_dat", "dat", "page", "address", "num", "DOI",
                   "employ", "employ_num", "ccf", "times", "link", "code_link", "bibtex"]
    update_data = dict()
    st = 0
    files = None
    if 'files' in data:
        files = data['files']
        if data['ispictures'] == 1:
            update_data['encd'] = files[0]['title']
            st = 1
        update_data['code_encd'] = str(data['files_name'][st:])
    else:
        if data['ispictures'] == 1:
            update_data['encd'] = data['files_name'][0]
            st = 1
        update_data['code_encd'] = str(data['files_name'][st:])
    for item in modify_word:
        update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('conference', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Conf, 'conference').modify(update_data, id)


# 上传
@admins_bp.route('/conference', methods=(['POST']))
def create_c():
    data = request.json
    files = None
    data['code_encd'] = []
    data['encd'] = ''
    if 'files' in data:
        files = data['files']
        file = []
        st = 0
        if data['pictures'] == 1:
            data['encd'] = files[0]['title']
            st = 1
        for i in range(st, len(files)):
            file.append(files[i]['title'])
        data['code_encd'] = file
    res = Admin(Conf, 'conference').upLoad(data)
    if files is not None:
        for item in files:
            save_Filebase64('conference', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(res['id']), item['title']))
    return res


# 详情
@admins_bp.route('/conference/<int:id>', methods=(['GET']))
def posts_id_c(id):
    res = Admin(Conf, 'conference').getOne(id)
    pictures = []
    if res['encd'] is not None and res['encd'] != '':
        pictures.append(
            {'src': host+'/conference/static/conference_encd/' + str(id) + '/' + res['encd'],
             'title': res['encd']})
        res['pictures'] = pictures
    del res['encd']
    files = []
    for item in eval(res['code_encd']):
        files.append(
            {'title': item, 'src': host+'/conference/static/conference_encd/' + str(id) + '/' + item})
    del res['code_encd']
    res['files'] = files
    return res


# 删除
@admins_bp.route('/journal/<int:id>', methods=["DELETE"])
def delete_id_journal(id):
    Admin(Jn, 'journal').deleteOne(id)
    return dict()


# 查询列表
@admins_bp.route('/journal', methods=(['GET']))
def posts_J():
    range = eval(request.args.get("range"))
    res = Admin(Jn, 'journal').getAll()
    res['data'].sort(key=lambda journal: journal['bibtex'])
    response = make_response(jsonify(res['data'][range[0]:range[1] + 1]))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-10/' + str(len(res['data']))
    return response


# 上传
@admins_bp.route('/journal', methods=(['POST']))
def create_J():
    data = request.json
    files = None
    data['code_encd'] = []
    data['encd'] = ''
    if 'files' in data:
        files = data['files']
        file = []
        st = 0
        if data['pictures'] == 1:
            data['encd'] = files[0]['title']
            st = 1
        for i in range(st, len(files)):
            file.append(files[i]['title'])
        data['code_encd'] = file
    res = Admin(Jn, 'journal').upLoad(data)
    if files is not None:
        for item in files:
            save_Filebase64('journal', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(res['id']), item['title']))
    return res


# 详情
@admins_bp.route('/journal/<int:id>', methods=(['GET']))
def posts_id_J(id):
    res = Admin(Jn, 'journal').getOne(id)
    pictures = []
    if res['encd'] is not None and res['encd'] != '':
        pictures.append(
            {'src': host+'/journal/static/journal_encd/' + str(id) + '/' + res['encd'],
             'title': res['encd']})
        res['pictures'] = pictures
    del res['encd']
    files = []
    for item in eval(res['code_encd']):
        files.append(
            {'title': item, 'src': host+'/journal/static/journal_encd/' + str(id) + '/' + item})
    del res['code_encd']
    res['files'] = files
    return res


# 修改
@admins_bp.route('/journal/<int:id>', methods=["PUT"])
def modify_journal(id):
    data = request.json
    modify_word = ["name", "author", "jn_name", "dat", "num", "employ", "employ_num", "ccf", "cas", "jcr", "times",
                   "vol", "no", "page", "DOI", "link", "code_link", "bibtex"]
    update_data = dict()
    st = 0
    files = None
    if 'files' in data:
        files = data['files']
        if data['ispictures'] == 1:
            update_data['encd'] = files[0]['title']
            st = 1
        update_data['code_encd'] = str(data['files_name'][st:])
    else:
        if data['ispictures'] == 1:
            update_data['encd'] = data['files_name'][0]
            st = 1
        update_data['code_encd'] = str(data['files_name'][st:])
    for item in modify_word:
        update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('journal', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Jn, 'journal').modify(update_data, id)


# 查询列表
@admins_bp.route('/honor', methods=(['GET']))
def posts_honor():
    res = Admin(Honor, 'journal').getAll()
    response = make_response(jsonify(res['data']))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-24/' + str(len(res))
    return response


# 上传
@admins_bp.route('/honor', methods=(['POST']))
def create_honor():
    data = request.json
    data['encd'] = ''
    picture = None
    if 'files' in data:
        picture = data['files'][0]
        data['encd'] = picture['title']
    res = Admin(Honor, 'honor').upLoad(data)
    if picture is not None:
        save_Filebase64('honor', base64.b64decode(handlebase64(picture['src'])),
                        os.path.join(str(res['id']), picture['title']))
    return res


# 详情
@admins_bp.route('/honor/<int:id>', methods=(['GET']))
def posts_id_honor(id):
    res = Admin(Honor, 'journal').getOne(id)
    if res['encd'] is not None and res['encd'] != '':
        pictures = []
        pictures.append({"src": host+'/honor/static/honor_encd/' + str(res['id']) + '/' + res['encd'],
                         "title": res['encd']})
        res['pictures'] = pictures
    return res


# 修改
@admins_bp.route('/honor/<int:id>', methods=["PUT"])
def modify_honor(id):
    data = request.json
    modify_word = ["name", "title", "dat"]
    update_data = dict()
    files = None
    if 'files' in data:
        files = data['files']
        picture = data['files'][0]
        update_data['encd'] = picture['title']
    else:
        if len(data['files_name']) > 1:
            update_data['encd'] = str(data['files_name'][0])
        else:
            update_data['encd'] = ''
    for item in modify_word:
        if item in request.json:
            update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('honor', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Honor, 'honor').modify(update_data, id)


# 删除
@admins_bp.route('/honor/<int:id>', methods=["DELETE"])
def delete_honor(id):
    Admin(Honor, 'honor').deleteOne(id)
    return dict()


# 删除
@admins_bp.route('/patent/<int:id>', methods=["DELETE"])
def delete_patent(id):
    Admin(Patent, 'patent').deleteOne(id)
    return dict()


# 查询列表
@admins_bp.route('/patent', methods=(['GET']))
def posts_patent():
    res = Admin(Patent, 'patent').getAll()
    response = make_response(jsonify(res['data']))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-10/' + str(len(res['data']))
    return response


# 详情
@admins_bp.route('/patent/<int:id>', methods=(['GET']))
def patent_id_J(id):
    res = Admin(Patent, 'patent').getOne(id)
    print(res)
    if res['encd'] != '':
        pictures = []
        pictures.append({"src": host+'/patent/static/patent_encd/' + str(res['id']) + '/' + res['encd'],
                         "title": res['encd']})
        res['pictures'] = pictures
    return res


# 专利上传
@admins_bp.route('/patent', methods=(['POST']))
def create_patent():
    data = request.json
    data['encd'] = ''
    picture = None
    if 'files' in data:
        picture = data['files'][0]
        data['encd'] = picture['title']
    res = Admin(Patent, 'patent').upLoad(data)
    if picture is not None:
        save_Filebase64('patent', base64.b64decode(handlebase64(picture['src'])),
                        os.path.join(str(res['id']), picture['title']))
    return res


# 修改
@admins_bp.route('/patent/<int:id>', methods=["PUT"])
def modify_patent(id):
    data = request.json
    modify_word = ["name", "patentee", "country", "level", "application_num", "patent_num", "IPC_num", "CPC_num",
                   "application_dat", "effect_dat", "DOI", "link"]
    update_data = dict()
    files = None
    if 'files' in data:
        files = data['files']
        picture = data['files'][0]
        update_data['encd'] = picture['title']
    else:
        if len(data['files_name']) > 1:
            update_data['encd'] = str(data['files_name'][0])
        else:
            update_data['encd'] = ''
    for item in modify_word:
        if item in request.json:
            update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('patent', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Patent, 'patent').modify(update_data, id)


# 删除
@admins_bp.route('/software/<int:id>', methods=["DELETE"])
def delete_software(id):
    Admin(Soft, 'software').deleteOne(id)
    return dict()


# 查询列表
@admins_bp.route('/software', methods=(['GET']))
def posts_software():
    res = Admin(Soft, 'software').getAll()
    response = make_response(jsonify(res['data']))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-10/' + str(len(res['data']))
    return response


# 详情
@admins_bp.route('/software/<int:id>', methods=(['GET']))
def software_id_J(id):
    res = Admin(Soft, 'software').getOne(id)
    pictures = []
    if res['encd'] != '':
        pictures.append(
            {'src': host+'/software/static/software_encd/' + str(res['id']) + '/' + res['encd'],
             "title": res['encd']})
        res['pictures'] = pictures
    return res


# 软著上传
@admins_bp.route('/software', methods=(['POST']))
def create_software():
    data = request.json
    data['encd'] = ''
    picture = None
    if 'files' in data:
        picture = data['files'][0]
        data['encd'] = picture['title']
    res = Admin(Soft, 'software').upLoad(data)
    if picture is not None:
        save_Filebase64('software', base64.b64decode(handlebase64(picture['src'])),
                        os.path.join(str(res['id']), picture['title']))
    return res


# 修改
@admins_bp.route('/software/<int:id>', methods=["PUT"])
def modify_software(id):
    data = request.json
    modify_word = ["name", "author", "num", "way", "DOI", "limits", "times", "link"]
    update_data = dict()
    files = None
    if 'files' in data:
        files = data['files']
        picture = data['files'][0]
        update_data['encd'] = picture['title']
    else:
        if len(data['files_name']) > 1:
            update_data['encd'] = str(data['files_name'][0])
        else:
            update_data['encd'] = ''
    for item in modify_word:
        if item in request.json:
            update_data[item] = request.json[item]
    if files is not None:
        for item in files:
            save_Filebase64('software', base64.b64decode(handlebase64(item['src'])),
                            os.path.join(str(id), item['title']))
    return Admin(Soft, 'software').modify(update_data, id)


# 审批页面
@admins_bp.route('/sort_people/api', methods=('GET', 'POST'))
def sort_people_api():
    sessions = DBSession()
    sort = sessions.query(People).first()
    sort_faculty = eval(sort.faculty)  # [id,sort]
    curpage = int(request.args.get('page'))
    pagesize = int(request.args.get('limit'))
    response = dict()
    index = 0
    faculty = sessions.query(Tch).join(Account, Tch.account == Account.account).filter(
        or_(Tch.tch_classify == '博士生导师', Tch.tch_classify == '硕士生导师', Tch.tch_classify == '其他老师'),
        Account.examine == '1')
    print("-------------->")
    factory_list = list()
    pri_faculty = dict()
    for faculty_row in faculty:
        pri_faculty[faculty_row.id] = faculty_row
    for faculty_id in sort_faculty:
        factory_dict = dict()
        index += 1
        factory_dict['index'] = index
        factory_dict['id'] = faculty_id
        factory_dict['author'] = pri_faculty[faculty_id].name
        factory_dict['Eng_name'] = pri_faculty[faculty_id].Eng_name
        factory_dict['name'] = pri_faculty[faculty_id].account
        factory_dict['avatar'] = pri_faculty[faculty_id].avatar
        factory_dict['phone'] = pri_faculty[faculty_id].phone
        factory_dict['email'] = pri_faculty[faculty_id].email
        factory_dict['home_page'] = pri_faculty[faculty_id].home_page
        factory_list.append(factory_dict)
    print(factory_list)
    lenth = len(factory_list)
    response['code'] = 0
    response['data'] = factory_list[(curpage - 1) * pagesize:min((curpage) * pagesize, lenth)]
    response['msg'] = ""
    response['count'] = lenth
    sessions.close()
    return json.dumps(response, ensure_ascii=False)


@admins_bp.route('/sort_people', methods=('GET', 'POST'))
def sort_people():
    return render_template('sort_people.html')


# 审批页面
@admins_bp.route('/sort_people_back', methods=('GET', 'POST'))
def sort_people_back():
    sessions = DBSession()
    data = request.get_json()
    sort = sessions.query(People).first()
    sort.faculty = str(data['faculty'])
    sessions.commit()
    sessions.close()
    response = dict()
    response['message'] = "保存成功"
    response['error'] = 0
    return json.dumps(response, ensure_ascii=False)


# 审批页面
@admins_bp.route('/examine', methods=('GET', 'POST'))
def examine():
    sessions = DBSession()
    exm_account = sessions.query(Account).filter(Account.examine == '0').all()
    if request.method == 'POST':
        temp = request.form
        temp = temp.to_dict()
        for every_exm in temp:
            for row in exm_account:
                if str(row.id) in every_exm:
                    row.examine = '1'
        sessions.commit()
        exm_account = sessions.query(Account).filter(Account.examine == '0').all()
    return render_template('examine.html', exm_account=exm_account)


# 增加用户账户
@admins_bp.route('/user_add', methods=('GET', 'POST'))
def user_add():
    sessions = DBSession()
    all_users = sessions.query(Account).all()
    if request.method == 'POST':
        account = request.form.get('account', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        Eng_name = request.form.get('Eng_name', '').strip()
        classify = request.form.get('classify', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        profile = request.form.get('profile', '')
        address = request.form.get('address', '')
        direction = request.form.get('direction', '')
        avatar = request.files.get('avatar')
        teachers = ['博士生导师', '硕士生导师', '其他老师']
        if classify in teachers:
            new_account = Account(
                account=account,
                password=password,
                classify='教师',
                examine='1'
            )
            new_teacher = Tch(
                account=account,
                tch_classify=classify,
                name=name,
                Eng_name=Eng_name,
                profile=profile,
                avatar='../users/static/avatar/%s' % account,
                phone=phone,
                email=email,
                address=address,
                direction=direction
            )
            sessions.add(new_account)
            sessions.add(new_teacher)
            save_avatar(account, avatar)

        else:
            new_account = Account(
                account=account,
                password=password,
                classify='学生',
                examine='1'
            )
            new_student = Stu(
                account=account,
                stu_classify=classify,
                name=name,
                Eng_name=Eng_name,
                profile=profile,
                avatar='../users/static/avatar/%s' % account,
                phone=phone,
                email=email,
                address=address,
                direction=direction
            )
            sessions.add(new_account)
            sessions.add(new_student)
            save_avatar(account, avatar)
        sessions.commit()
        return render_template('examine.html')
    return render_template('user_add.html')


# 删除用户信息
@admins_bp.route('/user_delete/<account>/', methods=('GET', 'POST'))
def user_delete(account):
    sessions = DBSession()
    all_users = sessions.query(Account).all()
    if account != 'delete%--%':
        delete_account = sessions.query(Account).filter(Account.account == account).first()
        if delete_account.classify == '教师':
            sessions.query(Tch).filter(Tch.account == account).delete()
        else:
            sessions.query(Stu).filter(Stu.account == account).delete()
        sessions.query(Account).filter(Account.account == account).delete()
        sessions.commit()
        return redirect(url_for('admins.user_delete', account='delete%--%'))
    return render_template('user_delete.html', user_home=all_users)


# 修改用户信息
@admins_bp.route('/user_modify/<account>/', methods=('GET', 'POST'))
def user_modify(account):
    sessions = DBSession()
    account_modify = sessions.query(Account).filter(Account.account == account).first()
    classify = account_modify.classify
    if classify == "教师":
        user_home = sessions.query(Tch).filter(Tch.account == account).first()
        classify_name = user_home.tch_classify
    else:
        user_home = sessions.query(Stu).filter(Stu.account == account).first()
        classify_name = user_home.stu_classify
    all_users = sessions.query(Account).all()
    teachers = ['博士生导师', '硕士生导师', '其他老师']
    if request.method == 'POST':
        account_modify.account = request.form.get('account', '').strip()
        user_home.account = request.form.get('account', '').strip()
        if request.form.get('password', '').strip() != '':
            account_modify.password = request.form.get('password', '').strip()
        user_home.name = request.form.get('name', '').strip()
        user_home.Eng_name = request.form.get('Eng_name', '').strip()
        user_home.phone = request.form.get('phone', '').strip()
        user_home.email = request.form.get('email', '').strip()
        user_home.profile = request.form.get('profile', '')
        user_home.address = request.form.get('address', '')
        user_home.direction = request.form.get('direction', '')
        new_classify = request.form.get('classify', '')
        if new_classify in teachers:
            account_modify.classify = "教师"
            user_home.tch_classify = new_classify
        else:
            account_modify.classify = "学生"
            user_home.stu_classify = new_classify
        sessions.commit()
        return render_template('user_delete.html', user_home=all_users)
    return render_template('user_modify.html', user_home=user_home, classify_name=classify_name)


# 期刊论文上传
@admins_bp.route('/jn_upload_admin', methods=('GET', 'POST'))
def jn_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        jn_name = request.form.get('jn_name', '').strip()
        author_all = request.form.get('author', '').strip()
        author = author_all.split(',')
        dat = request.form.get('dat', '')
        if dat == '':
            dat = str_to_date('1990-1-1')
        num = request.form.get('num', '').strip()
        employ = request.form.get('employ', '').strip()
        employ_num = request.form.get('employ_num', '').strip()
        ccf = request.form.get('ccf', '').strip()
        cas = request.form.get('cas', '').strip()
        jcr = request.form.get('jcr', '').strip()
        times = request.form.get('times', '').strip()
        vol = request.form.get('vol', '').strip()
        no = request.form.get('no', '').strip()
        page = request.form.get('page', '').strip()
        DOI = request.form.get('DOI', '').strip()
        link = request.form.get('link', '').strip()
        code_link = request.form.get('code_link', '').strip()
        # author_classify_list = author_name('author_classify')
        encd = request.files.get('encd')
        code_encd = request.files.get('code_encd')
        summary = {}
        summary['name'] = name
        summary['author'] = author
        summary['DOI'] = DOI
        if sessions.query(Jn).filter(Jn.name == name).first() is not None:
            return render_template('jn_upload_admin.html', error='论文已存在')
        else:
            new_jn = Jn(
                name=name,
                author=author_all,
                summary=str(summary),
                jn_name=jn_name,
                dat=dat,
                page=page,
                num=num,
                DOI=DOI,
                employ=employ,
                employ_num=employ_num,
                ccf=ccf,
                cas=cas,
                jcr=jcr,
                times=times,
                vol=vol,
                no=no,
                link=link,
                code_link=code_link,
                encd='../journal/static/journal_encd/%s' % name + '.pdf',
                code_encd='../journal/static/journal_code/%s' % name,
            )
            sessions.add(new_jn)
            save_jn(name, encd)
            save_code(name, code_encd)
            sessions.commit()
            return redirect(url_for('admins.jn_delete_admin', jn_name='delete%--%'))
    return render_template('jn_upload_admin.html')


def save_jn(name, file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'journal', 'static', 'journal_encd', name + '.pdf')
    file.save(file_path)


# 上传会议
@admins_bp.route('/conf_upload_admin', methods=('GET', 'POST'))
def conf_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        conf_name = request.form.get('conf_name', '').strip()
        organizer = request.form.get('organizer', '').strip()
        author_all = request.form.get('author', '').strip()
        author = author_all.split(',')
        conf_dat = request.form.get('conf_dat', '')
        dat = request.form.get('dat', '')
        if dat == '':
            dat = str_to_date('1990-1-1')
        if conf_dat == '':
            conf_dat = str_to_date('1990-1-1')
        page = request.form.get('page', '').strip()
        address = request.form.get('address', '').strip()
        num = request.form.get('num', '').strip()
        DOI = request.form.get('DOI', '').strip()
        employ = request.form.get('employ', '').strip()
        employ_num = request.form.get('employ_num', '').strip()
        ccf = request.form.get('ccf', '').strip()
        times = request.form.get('times', '').strip()
        link = request.form.get('link', '').strip()
        code_link = request.form.get('code_link', '').strip()
        encd = request.files.get('encd')
        code_encd = request.files.get('code_encd')
        summary = {}
        summary['name'] = name
        summary['author'] = author
        summary['DOI'] = DOI
        if sessions.query(Conf).filter(Conf.name == name).first() is not None:
            return render_template('conf_upload_admin.html', error='论文已存在')
        else:
            new_conf = Conf(
                name=name,
                author=author_all,
                summary=str(summary),
                conf_name=conf_name,
                organizer=organizer,
                conf_dat=conf_dat,
                dat=dat,
                page=page,
                address=address,
                num=num,
                DOI=DOI,
                employ=employ,
                employ_num=employ_num,
                ccf=ccf,
                times=times,
                link=link,
                code_link=code_link,
                encd='../conference/static/conference_encd/%s' % name + '.pdf',
                code_encd='../conference/static/conference_code/%s' % name,
            )
            sessions.add(new_conf)
            # new_conf=sessions.query(Conf).filter(Conf.name == name).first()
            save_conf(name, encd)
            save_code(name, code_encd)
            sessions.commit()
            return redirect(url_for('admins.conf_delete_admin', conf_name='delete%--%'))
    return render_template('conf_upload_admin.html')


# 会议删除
@admins_bp.route('/conf_delete_admin/<conf_name>/', methods=('GET', 'POST'))
def conf_delete_admin(conf_name):
    sessions = DBSession()
    conf_home = sessions.query(Conf).all()
    if conf_name != 'delete%--%':
        sessions.query(Conf).filter(Conf.name == conf_name).delete()
        sessions.commit()
        return redirect(url_for('admins.conf_delete_admin', conf_name='delete%--%'))
    return render_template('conf_delete_admin.html', conf_home=conf_home)


# 期刊删除
@admins_bp.route('/jn_delete_admin/<jn_name>/', methods=('GET', 'POST'))
def jn_delete_admin(jn_name):
    sessions = DBSession()
    jn_home = sessions.query(Jn).all()
    if jn_name != 'delete%--%':
        sessions.query(Jn).filter(Jn.name == jn_name).delete()
        sessions.commit()
        return redirect(url_for('admins.jn_delete_admin', jn_name='delete%--%'))
    return render_template('jn_delete_admin.html', jn_home=jn_home)


# 期刊修改
@admins_bp.route('/jn_modify_admin/<jn_name>/', methods=('GET', 'POST'))
def jn_modify_admin(jn_name):
    sessions = DBSession()
    modify_jn = sessions.query(Jn).filter(Jn.name == jn_name).first()
    jn_home = sessions.query(Jn).filter(Jn.name == jn_name).first()
    if request.method == "POST":
        modify_jn.name = request.form.get('name', '').strip()
        modify_jn.jn_name = request.form.get('jn_name', '').strip()
        modify_jn.author = request.form.get('author', '').strip()
        modify_jn.dat = request.form.get('dat', '')
        modify_jn.num = request.form.get('num', '').strip()
        modify_jn.employ = request.form.get('employ', '').strip()
        modify_jn.employ_num = request.form.get('employ_num', '').strip()
        modify_jn.ccf = request.form.get('ccf', '').strip()
        modify_jn.cas = request.form.get('cas', '').strip()
        modify_jn.jcr = request.form.get('jcr', '').strip()
        modify_jn.times = request.form.get('times', '').strip()
        modify_jn.vol = request.form.get('vol', '').strip()
        modify_jn.no = request.form.get('no', '').strip()
        modify_jn.page = request.form.get('page', '').strip()
        modify_jn.DOI = request.form.get('DOI', '').strip()
        modify_jn.link = request.form.get('link', '').strip()
        modify_jn.code_link = request.form.get('code_link', '').strip()
        author = request.form.get('author', '').strip().split(',')
        summary = {}
        summary['name'] = request.form.get('name', '').strip()
        summary['author'] = author
        summary['DOI'] = request.form.get('DOI', '').strip()
        modify_jn.summary = str(summary)
        modify_jn.encd = '../journal/static/journal_encd/%s' % modify_jn.name,
        modify_jn.code_encd = '../journal/static/journal_code/%s' % modify_jn.name,
        encd = request.files.get('encd')
        code_encd = request.files.get('code_encd')
        save_jn(modify_jn.name, encd)
        save_code_jn(modify_jn.name, code_encd)
        sessions.commit()
        return redirect(url_for('admins.jn_delete_admin', jn_name='delete%--%'))
    return render_template('jn_modify_admin.html', jn_home=jn_home)


# 保存论文代码
def save_code_jn(name, file):
    # 规定头像的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'journal', 'static', 'journal_code', name)
    file.save(file_path)


# 会议修改
@admins_bp.route('/conf_modify_admin/<conf_name>/', methods=('GET', 'POST'))
def conf_modify_admin(conf_name):
    sessions = DBSession()
    conf_home = sessions.query(Conf).filter(Conf.name == conf_name).first()
    # author = eval(conf_home.author)
    modify_conf = sessions.query(Conf).filter(Conf.name == conf_name).first()
    if request.method == "POST":
        modify_conf.name = request.form.get('name', '').strip()
        modify_conf.conf_name = request.form.get('conf_name', '').strip()
        modify_conf.organizer = request.form.get('organizer', '').strip()
        modify_conf.author = request.form.get('author', '').strip()
        modify_conf.conf_dat = request.form.get('conf_dat', '').strip()
        modify_conf.dat = request.form.get('dat', '').strip()
        modify_conf.page = request.form.get('page', '').strip()
        modify_conf.address = request.form.get('address', '').strip()
        modify_conf.num = request.form.get('num', '').strip()
        modify_conf.DOI = request.form.get('DOI', '').strip()
        modify_conf.employ = request.form.get('employ', '').strip()
        modify_conf.employ_num = request.form.get('employ_num', '').strip()
        modify_conf.ccf = request.form.get('ccf', '').strip()
        modify_conf.times = request.form.get('times', '').strip()
        modify_conf.link = request.form.get('link', '').strip()
        author = request.form.get('author', '').strip().split(',')
        summary = {}
        summary['name'] = request.form.get('name', '').strip()
        summary['author'] = author
        summary['DOI'] = request.form.get('DOI', '').strip()
        modify_conf.summary = str(summary)
        modify_conf.code_link = request.form.get('code_link', '').strip()
        modify_conf.encd = '../conference/static/conference_encd/%s' % modify_conf.name,
        modify_conf.code_encd = '../conference/static/conference_code/%s' % modify_conf.name,
        encd = request.files.get('encd')
        code_encd = request.files.get('code_encd')
        save_conf(modify_conf.name, encd)
        save_code(modify_conf.name, code_encd)
        sessions.commit()
        return redirect(url_for('admins.conf_delete_admin', conf_name='delete%--%'))
    return render_template('conf_modify_admin.html', conf_home=conf_home)


# 专利管理员上传
@admins_bp.route('/patent_upload_admin', methods=('GET', 'POST'))
def patent_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        patentee = request.form.get('patentee', '').strip()
        country = request.form.get('country', '')
        level = request.form.get('level', '')
        application_num = request.form.get('application_num', '').strip()
        patent_num = request.form.get('patent_num', '').strip()
        IPC_num = request.form.get('IPC_num', '').strip()
        CPC_num = request.form.get('CPC_num', '').strip()
        application_dat = request.form.get('application_dat', '')
        if application_dat == '':
            application_dat = str_to_date('1990-1-1')
        effect_dat = request.form.get('effect_dat', '')
        if effect_dat == '':
            effect_dat = str_to_date('1990-1-1')
        DOI = request.form.get('DOI', '').strip()
        link = request.form.get('link', '').strip()
        encd = request.files.get('encd')
        summary = {}
        summary['name'] = name
        summary['patentee'] = patentee
        summary['effect_dat'] = effect_dat
        if sessions.query(Patent).filter(Patent.name == name).first() is not None:
            return render_template('patent_upload_admin.html', error='专利已存在')
        else:
            new_patent = Patent(
                name=name,
                patentee=patentee,
                level=level,
                country=country,
                application_num=application_num,
                patent_num=patent_num,
                IPC_num=IPC_num,
                CPC_num=CPC_num,
                application_dat=application_dat,
                effect_dat=effect_dat,
                DOI=DOI,
                summary=str(summary),
                link=link,
                encd='../patent/static/patent_encd/%s' % name,
            )
            sessions.add(new_patent)
            save_patent(name, encd)
            # all_patent = sessions.query(Patent).all()
            sessions.commit()
            return redirect(url_for('admins.patent_delete_admin', patent_name='delete%--%'))
    return render_template('patent_upload_admin.html')


# 软件著作管理员上传
@admins_bp.route('/soft_upload_admin', methods=('GET', 'POST'))
def soft_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        author = request.form.get('author', '')
        num = request.form.get('num', '').strip()
        way = request.form.get('way', '')
        DOI = request.form.get('DOI', '').strip()
        limits = request.form.get('limits', '')
        times = request.form.get('times', '')
        if times == '':
            times = str_to_date('1990-1-1')
        link = request.form.get('link', '').strip()
        encd = request.files.get('encd')
        if sessions.query(Soft).filter(Soft.name == name).first() is not None:
            return render_template('soft_upload_admin.html', error='软件著作已存在')
        else:
            new_soft = Soft(
                name=name,
                author=author,
                num=num,
                way=way,
                DOI=DOI,
                limits=limits,
                times=times,
                link=link,
                summary=str(name) + ' , ' + str(author) + ' , ' + str(times),
                encd='../software/static/software_encd/%s' % name
            )
            sessions.add(new_soft)
            save_File('software', encd, str(new_soft.id))
            # all_soft = sessions.query(Soft).all()
            sessions.commit()
            return redirect(url_for('admins.soft_delete_admin', soft_name='delete%--%'))
    return render_template('soft_upload_admin.html')


# 专利管理员修改
@admins_bp.route('/patent_modify_admin/<patent_name>/', methods=('GET', 'POST'))
def patent_modify_admin(patent_name):
    sessions = DBSession()
    modify_patent = sessions.query(Patent).filter(Patent.name == patent_name).first()
    if request.method == "POST":
        modify_patent.name = request.form.get('name', '').strip()
        modify_patent.patentee = request.form.get('patentee', '').strip()
        modify_patent.country = request.form.get('country', '')
        modify_patent.level = request.form.get('level', '')
        modify_patent.application_num = request.form.get('application_num', '').strip()
        modify_patent.patent_num = request.form.get('patent_num', '').strip()
        modify_patent.IPC_num = request.form.get('IPC_num', '').strip()
        modify_patent.CPC_num = request.form.get('CPC_num', '').strip()
        application_dat = request.form.get('application_dat', '')
        if application_dat == '':
            application_dat = str_to_date('1990-1-1')
        effect_dat = request.form.get('effect_dat', '')
        if effect_dat == '':
            effect_dat = str_to_date('1990-1-1')
        modify_patent.application_dat = application_dat
        modify_patent.effect_dat = effect_dat
        modify_patent.DOI = request.form.get('DOI', '').strip()
        modify_patent.link = request.form.get('link', '').strip()
        modify_patent.encd = '../patent/static/patent_encd/%s' % modify_patent.name
        encd = request.files.get('encd')
        summary = {}
        summary['name'] = request.form.get('name', '').strip()
        summary['patentee'] = request.form.get('patentee', '').strip()
        summary['effect_dat'] = request.form.get('effect_dat', '')
        modify_patent.summary = str(summary)
        save_patent(modify_patent.name, encd)
        all_patent = sessions.query(Patent).all()
        sessions.commit()
        return render_template('patent_delete_admin.html', patent_home=all_patent)
    return render_template('patent_modify_admin.html', patent_home=modify_patent)


# 软件著作管理员修改
@admins_bp.route('/soft_modify_admin/<soft_name>/', methods=('GET', 'POST'))
def soft_modify_admin(soft_name):
    sessions = DBSession()
    modify_soft = sessions.query(Soft).filter(Soft.name == soft_name).first()
    if request.method == "POST":
        modify_soft.name = request.form.get('name', '').strip()
        modify_soft.author = request.form.get('author', '').strip()
        modify_soft.num = request.form.get('num', '')
        modify_soft.way = request.form.get('way', '')
        modify_soft.DOI = request.form.get('DOI', '').strip()
        modify_soft.limits = request.form.get('limits', '').strip()
        modify_soft.times = request.form.get('times', '').strip()
        modify_soft.link = request.form.get('link', '').strip()
        modify_soft.encd = request.form.get('encd', '')
        all_soft = sessions.query(Soft).all()
        sessions.commit()
        return render_template('soft_delete_admin.html', soft_home=all_soft)
    return render_template('soft_modify_admin.html', soft_home=modify_soft)


# 专利删除
@admins_bp.route('/patent_delete_admin/<patent_name>/', methods=('GET', 'POST'))
def patent_delete_admin(patent_name):
    sessions = DBSession()
    patent_home = sessions.query(Patent).all()
    if patent_name != 'delete%--%':
        sessions.query(Patent).filter(Patent.name == patent_name).delete()
        sessions.commit()
        return redirect(url_for('admins.patent_delete_admin', patent_name='delete%--%'))
    return render_template('patent_delete_admin.html', patent_home=patent_home)


# 软著删除
@admins_bp.route('/soft_delete_admin/<soft_name>/', methods=('GET', 'POST'))
def soft_delete_admin(soft_name):
    sessions = DBSession()
    soft_home = sessions.query(Soft).all()
    if soft_name != 'delete%--%':
        sessions.query(Soft).filter(Soft.name == soft_name).delete()
        sessions.commit()
        return redirect(url_for('admins.soft_delete_admin', soft_name='delete%--%'))
    return render_template('soft_delete_admin.html', soft_home=soft_home)


# 学术专著删除
@admins_bp.route('/mono_delete_admin/<mono_name>/', methods=('GET', 'POST'))
def mono_delete_admin(mono_name):
    sessions = DBSession()
    mono_home = sessions.query(Mono).all()
    if mono_name != 'delete%--%':
        sessions.query(Mono).filter(Mono.name == mono_name).delete()
        sessions.commit()
        return redirect(url_for('admins.mono_delete_admin', mono_name='delete%--%'))
    return render_template('mono_delete_admin.html', mono_home=mono_home)


# 学术专著管理员上传
@admins_bp.route('/mono_upload_admin', methods=('GET', 'POST'))
def mono_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        language = request.form.get('language', '')
        employ = request.form.get('employ', '')
        editor = request.form.get('editor', '').strip()
        ISBN = request.form.get('ISBN', '').strip()
        country = request.form.get('country', '').strip()
        city = request.form.get('city', '').strip()
        page = request.form.get('page', '').strip()
        word = request.form.get('word', '').strip()
        press = request.form.get('press', '').strip()
        dat = request.form.get('dat', '')
        if dat == '':
            dat = str_to_date('1990-1-1')
        DOI = request.form.get('DOI', '').strip()
        link = request.form.get('link', '').strip()
        encd = request.files.get('encd')
        summary = {}
        summary['name'] = name
        summary['editor'] = editor
        if sessions.query(Mono).filter(Mono.name == name).first() is not None:
            return render_template('mono_upload_admin.html', error='学术专著已存在')
        else:
            new_mono = Mono(
                name=name,
                editor=editor,
                language=language,
                employ=employ,
                ISBN=ISBN,
                country=country,
                city=city,
                page=page,
                word=word,
                press=press,
                dat=dat,
                DOI=DOI,
                link=link,
                summary=str(summary),
                encd='../monograph/static/monograph_encd/%s' % name,
            )
            sessions.add(new_mono)
            save_File('monograph', encd, str(new_mono.id))

            # all_mono = sessions.query(Mono).all()
            sessions.commit()
            return redirect(url_for('admins.mono_delete_admin', mono_name='delete%--%'))
    return render_template('mono_upload_admin.html')


# 学术专著管理员修改
@admins_bp.route('/mono_modify_admin/<mono_name>/', methods=('GET', 'POST'))
def mono_modify_admin(mono_name):
    sessions = DBSession()
    modify_mono = sessions.query(Mono).filter(Mono.name == mono_name).first()
    if request.method == "POST":
        modify_mono.name = request.form.get('name', '').strip()
        modify_mono.language = request.form.get('language', '')
        modify_mono.employ = request.form.get('employ', '')
        modify_mono.editor = request.form.get('editor', '').strip()
        modify_mono.ISBN = request.form.get('ISBN', '').strip()
        modify_mono.country = request.form.get('country', '').strip()
        modify_mono.city = request.form.get('city', '').strip()
        modify_mono.page = request.form.get('page', '').strip()
        modify_mono.word = request.form.get('word', '').strip()
        modify_mono.press = request.form.get('press', '').strip()
        dat = request.form.get('dat', '')
        if dat == '':
            dat = str_to_date('1990-1-1')
        mono_name.dat = dat
        modify_mono.DOI = request.form.get('DOI', '').strip()
        modify_mono.link = request.form.get('link', '').strip()
        modify_mono.encd = '../monograph/static/monograph_encd/%s' % modify_mono.name,
        encd = request.files.get('encd')
        summary = {}
        summary['name'] = request.form.get('name', '').strip()
        summary['editor'] = request.form.get('editor', '').strip()
        modify_mono.summary = str(summary)
        save_File('monograph', encd, str(modify_mono.id))
        all_mono = sessions.query(Mono).all()
        sessions.commit()
        return render_template('mono_delete_admin.html', mono_home=all_mono)
    return render_template('mono_modify_admin.html', mono_home=modify_mono)


# 项目删除
@admins_bp.route('/prog_delete_admin/<prog_name>/', methods=('GET', 'POST'))
def prog_delete_admin(prog_name):
    sessions = DBSession()
    prog_home = sessions.query(Prog).all()
    if prog_name != 'delete%--%':
        sessions.query(Prog).filter(Prog.name == prog_name).delete()
        sessions.commit()
        return redirect(url_for('admins.prog_delete_admin', prog_name='delete%--%'))
    return render_template('prog_delete_admin.html', prog_home=prog_home)


# 项目修改
@admins_bp.route('/prog_modify_admin/<prog_name>/', methods=('GET', 'POST'))
def prog_modify_admin(prog_name):
    sessions = DBSession()
    modify_prog = sessions.query(Prog).filter(Prog.name == prog_name).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        principal = request.form.get('principal', '').strip()
        level = request.form.get('level', '')
        start_time = request.form.get('start_time', '')
        deadline = request.form.get('deadline', '')
        cost = request.form.get('cost', '').strip()
        summary = {}
        summary['name'] = name
        summary['principal'] = principal
        summary['level'] = level
        summary['start_time'] = start_time
        if start_time == '':
            start_time = str_to_date('1990-1-1')
        if deadline == '':
            deadline = str_to_date('1990-1-1')
        summary['deadline'] = deadline
        summary['cost'] = cost
        modify_prog.name = name
        modify_prog.principal = principal
        modify_prog.level = level
        modify_prog.start_time = start_time
        modify_prog.deadline = deadline
        modify_prog.cost = cost
        modify_prog.summary = str(summary)
        sessions.commit()
        all_prog = sessions.query(Prog).all()
        return render_template('prog_delete_admin.html', prog_home=all_prog)
    return render_template('prog_modify_admin.html', prog_home=modify_prog)


# 项目管理员上传
@admins_bp.route('/prog_upload_admin', methods=('GET', 'POST'))
def prog_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        principal = request.form.get('principal', '').strip()
        level = request.form.get('level', '')
        start_time = request.form.get('start_time', '')
        deadline = request.form.get('deadline', '')
        cost = request.form.get('cost', '').strip()
        summary = {}
        summary['name'] = name
        summary['principal'] = principal
        summary['level'] = level
        summary['start_time'] = start_time
        if start_time == '':
            start_time = str_to_date('1990-1-1')
        if deadline == '':
            deadline = str_to_date('1990-1-1')
        summary['deadline'] = deadline
        summary['cost'] = cost
        if sessions.query(Prog).filter(Prog.name == name).first() is not None:
            return render_template('prog_upload_admin.html', error='项目已存在')
        else:
            new_prog = Prog(
                name=name,
                principal=principal,
                level=level,
                start_time=start_time,
                deadline=deadline,
                cost=cost,
                summary=str(summary)
            )
            sessions.add(new_prog)
            sessions.commit()
            return redirect(url_for('admins.prog_delete_admin', prog_name='delete%--%'))
    return render_template('prog_upload_admin.html')


# 竞赛删除
@admins_bp.route('/comp_delete_admin/<comp_name>/', methods=('GET', 'POST'))
def comp_delete_admin(comp_name):
    sessions = DBSession()
    comp_home = sessions.query(Comp).all()
    if comp_name != 'delete%--%':
        sessions.query(Comp).filter(Comp.name == comp_name).delete()
        sessions.commit()
        return redirect(url_for('admins.comp_delete_admin', comp_name='delete%--%'))
    return render_template('comp_delete_admin.html', comp_home=comp_home)


# 课程删除
@admins_bp.route('/course_delete_admin/<course_name>/', methods=('GET', 'POST'))
def course_delete_admin(course_name):
    sessions = DBSession()
    course_home = sessions.query(Course).all()
    if course_name != 'delete%--%':
        sessions.query(Course).filter(Course.name == course_name).delete()
        sessions.commit()
        return redirect(url_for('admins.course_delete_admin', course_name='delete%--%'))
    return render_template('course_delete_admin.html', course_home=course_home)


# 课程管理员上传
@admins_bp.route('/course_upload_admin', methods=('GET', 'POST'))
def course_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        teacher = request.form.get('teacher', '')
        content = request.form.get('content', '')
        page = request.form.get('ranking', '')
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
        sessions.commit()
        return redirect(url_for('admins.course_delete_admin', course_name='delete%--%'))
    return render_template('course_upload_admin.html')


# 课程管理员修改
@admins_bp.route('/course_modify_admin/<course_name>/', methods=('GET', 'POST'))
def course_modify_admin(course_name):
    sessions = DBSession()
    modify_course = sessions.query(Course).filter(Course.name == course_name).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        teacher = request.form.get('teacher', '')
        modify_course.content = request.form.get('content', '')
        modify_course.page = request.form.get('ranking', '')
        modify_course.name = name
        modify_course.teacher = teacher
        summary = {}
        summary['name'] = name
        summary['teacher'] = teacher
        modify_course.summary = str(summary)
        all_course = sessions.query(Course).all()
        sessions.commit()
        return render_template('course_delete_admin.html', course_home=all_course)
    return render_template('course_modify_admin.html', course_home=modify_course)


# 竞赛修改
@admins_bp.route('/comp_modify_admin/<comp_name>/', methods=('GET', 'POST'))
def comp_modify_admin(comp_name):
    sessions = DBSession()
    modify_comp = sessions.query(Comp).filter(Comp.name == comp_name).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        modify_comp.name = name
        teachers = request.form.get('teachers', '')
        modify_comp.teachers = teachers
        participant = request.form.get('participant', '')
        modify_comp.participant = participant
        ranking = request.form.get('ranking', '').strip()
        modify_comp.ranking = ranking
        summary = {}
        summary['name'] = name
        summary['teachers'] = teachers
        summary['participant'] = participant
        summary['ranking'] = ranking
        modify_comp.summary = str(summary)
        sessions.commit()
        all_comp = sessions.query(Comp).all()
        return render_template('comp_delete_admin.html', comp_home=all_comp)
    return render_template('comp_modify_admin.html', comp_home=modify_comp)


# 荣誉称号管理员上传
@admins_bp.route('/honor_upload_admin', methods=('GET', 'POST'))
def honor_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        symmary = {}
        symmary['name'] = name
        symmary['title'] = title
        new_honor = Honor(
            name=name,
            title=title,
            summary=str(symmary)
        )
        sessions.add(new_honor)
        sessions.commit()
        return redirect(url_for('admins.honor_delete_admin', honor_title_name='delete%--%'))
    return render_template('honor_upload_admin.html')


# 荣誉称号删除
@admins_bp.route('/honor_delete_admin/<honor_title_name>/', methods=('GET', 'POST'))
def honor_delete_admin(honor_title_name):
    sessions = DBSession()
    honor_home = sessions.query(Honor).all()
    if honor_title_name != 'delete%--%':
        honor_title_name_list = honor_title_name.split(',')
        summary = {}
        summary['name'] = honor_title_name_list[1]
        summary['title'] = honor_title_name_list[0]
        sessions.query(Honor).filter(Honor.summary == str(summary)).delete()
        sessions.commit()
        return redirect(url_for('admins.honor_delete_admin', honor_title_name='delete%--%'))
    return render_template('honor_delete_admin.html', honor_home=honor_home)


# 新闻删除
@admins_bp.route('/news_delete_admin/<news_title_publisher>/', methods=('GET', 'POST'))
def news_delete_admin(news_title_publisher):
    sessions = DBSession()
    news_home = sessions.query(News).all()
    if news_title_publisher != 'delete%--%':
        news_title_name_list = news_title_publisher.split(',')
        summary = {}
        summary['title'] = news_title_name_list[0]
        summary['publisher'] = news_title_name_list[1]
        sessions.query(News).filter(News.summary == str(summary)).delete()
        sessions.commit()
        return redirect(url_for('admins.news_delete_admin', news_title_publisher='delete%--%'))
    return render_template('news_delete_admin.html', news_home=news_home)


# 新闻管理员上传
@admins_bp.route('/news_upload_admin', methods=('GET', 'POST'))
def news_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        title = request.form.get('name', '')
        publisher = request.form.get('publisher', '')
        classify = request.form.get('classify', '')
        content = request.form.get('content', '')
        dat = request.form.get('dat', '')
        if dat == '':
            dat = str_to_date('1990-1-1')
        summary = {}
        summary['title'] = title
        summary['publisher'] = publisher
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
        return redirect(url_for('admins.news_delete_admin', news_title_publisher='delete%--%'))
    return render_template('news_upload_admin.html')


# 新闻管理员修改
@admins_bp.route('/news_modify_admin/<news_title_publisher>/', methods=('GET', 'POST'))
def news_modify_admin(news_title_publisher):
    sessions = DBSession()
    news_title_name_list = news_title_publisher.split(',')
    summary = {}
    summary['title'] = news_title_name_list[0]
    summary['publisher'] = news_title_name_list[1]
    modify_news = sessions.query(News).filter(News.summary == str(summary)).first()
    if request.method == "POST":
        title = request.form.get('name', '').strip()
        modify_news.content = request.form.get('content', '')
        modify_news.classify = request.form.get('classify', '')
        publisher = request.form.get('publisher', '').strip()
        dat = request.form.get('dat', '')
        if dat == '':
            dat = str_to_date('1990-1-1')
        modify_news.dat = dat
        modify_news.title = title
        modify_news.publisher = publisher
        summary_new = {}
        summary_new['title'] = title
        summary_new['publisher'] = publisher
        modify_news.summary = str(summary_new)
        all_news = sessions.query(News).all()
        sessions.commit()
        return render_template('news_delete_admin.html', news_home=all_news)
    return render_template('news_modify_admin.html', news_home=modify_news)


# 荣誉称号管理员修改
@admins_bp.route('/honor_modify_admin/<honor_title_name>/', methods=('GET', 'POST'))
def honor_modify_admin(honor_title_name):
    sessions = DBSession()
    honor_title_name_list = honor_title_name.split(',')
    summary = {}
    summary['name'] = honor_title_name_list[1]
    summary['title'] = honor_title_name_list[0]
    modify_honor = sessions.query(Honor).filter(Honor.summary == str(summary)).first()
    print(modify_honor)
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        modify_honor.name = name
        modify_honor.title = title
        summary_new = {}
        summary_new['name'] = name
        summary_new['title'] = title
        modify_honor.summary = str(summary_new)
        all_honor = sessions.query(Honor).all()
        sessions.commit()
        return render_template('honor_delete_admin.html', honor_home=all_honor)
    return render_template('honor_modify_admin.html', honor_home=modify_honor)


# 竞赛上传
@admins_bp.route('/comp_upload_admin', methods=('GET', 'POST'))
def comp_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        teachers = request.form.get('teachers', '')
        participant = request.form.get('participant', '')
        ranking = request.form.get('ranking', '').strip()
        adds = request.form.get('adds', '').strip()
        summary = {}
        summary['name'] = name
        summary['teachers'] = teachers
        summary['participant'] = participant
        summary['ranking'] = ranking
        if sessions.query(Comp).filter(Comp.name == name).first() is not None:
            return render_template('comp_upload_admin.html', error='竞赛已存在')
        else:
            new_comp = Comp(
                name=name,
                teachers=teachers,
                participant=participant,
                ranking=ranking,
                summary=str(summary)
            )
        sessions.add(new_comp)
        sessions.commit()
        return redirect(url_for('admins.comp_delete_admin', comp_name='delete%--%'))
    return render_template('comp_upload_admin.html')


# 资源删除
@admins_bp.route('/resource_delete_admin/<resource_name>/', methods=('GET', 'POST'))
def resource_delete_admin(resource_name):
    sessions = DBSession()
    resource_home = sessions.query(Resource).all()
    if resource_name != 'delete%--%':
        sessions.query(Resource).filter(Resource.name == resource_name).delete()
        sessions.commit()
        return redirect(url_for('admins.resource_delete_admin', resource_name='delete%--%'))
    return render_template('resource_delete_admin.html', resource_home=resource_home)


# 资源上传
@admins_bp.route('/resource_upload_admin', methods=('GET', 'POST'))
def resource_upload_admin():
    sessions = DBSession()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        link = request.form.get('link', '')
        classes = request.form.get('classes', '')
        introduction = request.form.get('introduction')
        citation = request.form.get('citation')
        encd = request.files.get('encd')
        if sessions.query(Resource).filter(Resource.name == name).first() is not None:
            return render_template('resource_upload_admin.html', error='资源已存在')
        new_resource = Resource(
            name=name,
            link=link,
            classes=classes,
            introduction=introduction,
            citation=citation,
            encd='../resource/static/resource_encd/%s'
        )
        save_resource(name, encd)
        sessions.add(new_resource)
        sessions.commit()
        return redirect(url_for('admins.resource_delete_admin', resource_name='delete%--%'))
    return render_template('resource_upload_admin.html')


# 数据资源管理员修改
@admins_bp.route('/resource_modify_admin/<resource_name>/', methods=('GET', 'POST'))
def resource_modify_admin(resource_name):
    sessions = DBSession()
    modify_resource = sessions.query(Resource).filter(Resource.name == resource_name).first()
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        modify_resource.name = name
        modify_resource.link = request.form.get('link', '')
        modify_resource.classes = request.form.get('classes', '')
        modify_resource.introduction = request.form.get('introduction')
        modify_resource.citation = request.form.get('citation')
        encd = request.files.get('encd')
        modify_resource.encd = '../resource/static/resource_encd/%s' % modify_resource.name,
        all_resource = sessions.query(Resource).all()
        save_resource(name, encd)
        sessions.commit()
        return render_template('resource_delete_admin.html', resource_home=all_resource)
    return render_template('resource_modify_admin.html', resource_home=modify_resource)


# 问题界面
@admins_bp.route('/issue', methods=('GET', 'POST'))
def issue():
    sessions = DBSession()
    issues = sessions.query(Issues).filter(Issues.solve == '未解决').all()
    temp = request.form
    temp = temp.to_dict()
    for every_exm in temp:
        for row in issues:
            if str(row.id) in every_exm:
                row.solve = '已解决'
    sessions.commit()
    all_issue = sessions.query(Issues).filter(Issues.solve == '未解决').all()
    # if request.method == 'POST':

    return render_template('issue.html', issue=all_issue)


# 保存专利
def save_patent(name, file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'patent', 'static', 'patent_encd', name + '.pdf')
    file.save(file_path)


# 把作者的字符串转为列表
def author_list(author):
    author_list = []
    author = author.split(' and ')
    for row in author:
        row = row.split(',')
        for i in row:
            author_list.append(i)
    return author_list


def author_name(name):
    name_list = []
    for i in range(5):
        x = request.form.get(name + str(i + 1), '').strip()
        if x != '':
            name_list.append(x)
    return name_list


# 保存论文
def save_conf(name, file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'conference', 'static', 'conference_encd', name + '.pdf')
    file.save(file_path)


# 保存论文代码
def save_code(name, file):
    # 规定头像的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'conference', 'static', 'conference_code', name)
    file.save(file_path)


# 保存数据资源
def save_resource(name, file):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, 'resource', 'static', 'resource_encd', name)
    file.save(file_path)


def save_data_to_file(html, file_path, mode='wb', encoding='utf-8'):
    '''
    保存字符串到指定文件
    Args:
        html:       str   字符串数据
        file_path:  str   文件路径
        mode:       str   文件打开格式，[w,r,a...]
        encoding:   str   文件编码格式 [utf-8, gbk]
    Returns:        list  True/False, message
    '''
    # 文件目录
    file_path_dir = os.path.dirname(file_path)
    # 判断目录是否存在
    if not os.path.exists(file_path_dir):
        # 目录不存在创建，makedirs可以创建多级目录
        os.makedirs(file_path_dir)
    try:
        # 保存数据到文件
        with open(file_path, mode) as f:
            f.write(html)
        return True, '保存成功'
    except Exception as e:
        return False, '保存失败:{}'.format(e)


def handlebase64(str):
    index = str.find(';base64')
    return str[index + 8:]


def handlePic(picname):
    pos = str.rfind(picname, '.')
    return picname[pos + 1:]


def save_Filebase64(module_name, file, file_name):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, module_name, 'static', module_name + '_encd', file_name)
    file_path_dir = os.path.dirname(file_path)
    if not os.path.exists(file_path_dir):
        # 目录不存在创建，makedirs可以创建多级目录
        os.makedirs(file_path_dir)
    f = open(file_path, 'wb')
    f.write(file)
