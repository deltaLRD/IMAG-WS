import datetime

from sqlalchemy import Column, String, create_engine, Integer, Text, DATE,BOOLEAN
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time
from flask_sqlalchemy import SQLAlchemy

import os

db_url = os.environ.get("DATABASE_URL", "localhost")
db_port = os.environ.get("DATABASE_PORT", "5433")
db_user = os.environ.get("DATABASE_USER", "dbuser")
db_pwd = os.environ.get("DATABASE_PWD", "12345678")
db_name = os.environ.get("DATABASE_NAME", "imag001")

db_full_url = "postgresql://{}:{}@{}:{}/{}".format(db_user, db_pwd, db_url, db_port, db_name)

# 创建对象的基类:
Base = declarative_base()
 
# 初始化数据库连接:
engine = create_engine(db_full_url,pool_size=100)
# engine = create_engine('postgresql://dbuser:12345678@10.10.109.100:5432/imag001',pool_size=100)
#engine = create_engine('postgresql://dbuser:12345678@localhost:12345/imag001', echo=True, pool_size=100)
# engine = create_engine('postgresql://dbuser:12345678@10.10.109.100:5432/imag001',echo=True,pool_size=100)
# 创建DBSession工厂:
DBSession = sessionmaker(bind=engine)


# 用户账户登录表
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    account = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=True)
    classify = Column(String(20), nullable=False, default='unknown')
    examine = Column(String(20), default='1')


class People(Base):
    __tablename__ = 'people'
    faculty = Column(Text, default='[]', primary_key=True)


# 论文对象
class Conf(Base):
    __tablename__ = 'conference'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 论文题目
    author = Column(Text, nullable=False)  # 作者列表
    conf_name = Column(String(200))  # 会议名称
    organizer = Column(String(200))  # 会议组织者
    conf_dat = Column(Text)  # 会议日期
    dat = Column(Text)  # 发表日期
    page = Column(String(200))  # 起止页码
    address = Column(Text)  # 会议地址
    num = Column(String(200))  # 文章号
    DOI = Column(String(200))  # DOI
    employ = Column(String(200))  # 收录情况，包括 'SCIE', 'SSCI', 'EI', 'ISTP', '北大中文核心期刊', '其他'
    employ_num = Column(String(200))  # 收录号
    ccf = Column(String(200))  # CCF分区，包括'A区', 'B区', 'C区', '无'
    times = Column(String(200))  # 引用数
    link = Column(Text)  # 论文链接
    code_link = Column(Text)  # 代码链接
    encd = Column(Text)  # 论文附件
    code_encd = Column(Text)  # 代码附件
    author_classify = Column(String(128))  # 作者分类，包括第一作者，第二作者，通讯作者和其他作者
    adds = Column(String(20), default='unknown')  # 是否添加到自己论文表中
    bibtex = Column(BOOLEAN, default=True)  # 是否是由bibtex上传的

    def __init__(self, data):
        self.name = data['name']
        self.author = data['author']
        self.conf_name = data['conf_name']
        self.organizer = data['organizer']
        self.conf_dat = data['conf_dat']
        self.dat = data['dat']
        self.page = data['page']
        self.address = data['address']
        self.num = data['num']
        self.DOI = data['DOI']
        self.employ = data['employ']
        self.employ_num = data['employ_num']
        self.ccf = data['ccf']
        self.times = data['times']
        self.link = data['link']
        self.code_link = data['code_link']
        if 'bibtex' in data:
            self.bibtex = data["bibtex"]
        self.encd=data['encd']
        if 'code_encd' in data and data['code_encd'] != '':
            self.code_encd = str(data['code_encd'])
        else:
            self.code_encd = str([])
        self.summary = str({'name': data['name'], 'author': data['author'], 'DOI': data['DOI']})

    def keys(self):
        return ["id", "name", "author", "conf_name", "organizer", "conf_dat", "dat", "page", "address", "num", "DOI",
                "employ", "employ_num", "ccf", "times", "link", "code_link", "author_classify", "encd", "code_encd",
                "bibtex"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 期刊
class Jn(Base):
    __tablename__ = 'journal'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 论文题目
    author = Column(Text, nullable=False)  # 作者列表
    jn_name = Column(String(200))  # 期刊名称
    dat = Column(Text)  # 发表日期
    num = Column(String(200))  # 文章号
    employ = Column(String(200))  # 收录情况，包括 'SCIE', 'SSCI', 'EI', 'ISTP', '北大中文核心期刊', '其他'
    employ_num = Column(String(200))  # 收录号
    ccf = Column(String(200))  # CCF分区，包括 'A区', 'B区', 'C区', '无'
    cas = Column(String(200))  # 中科院分区，包括 '一区', '二区', '三区', '四区','无'
    jcr = Column(String(200))  # JCR分区， 包括 '一区', '二区', '三区', '四区','无'
    times = Column(String(200))  # 引用数
    vol = Column(String(200))  # 卷
    no = Column(String(200))  # 期号
    page = Column(String(200))  # 页码
    DOI = Column(String(200))  # DOI
    link = Column(Text)  # 论文链接
    code_link = Column(Text)  # 代码链接
    encd = Column(Text)  # 论文附件
    code_encd = Column(Text)  # 代码附件
    author_classify = Column(String(128))  # 作者分类，包括第一作者，第二作者，通讯作者和其他作者
    adds = Column(String(20), default='unknown')  # 是否添加到自己论文表中
    bibtex = Column(Text, default=False)  # 是否是由bibtex上传的

    def __init__(self, data):
        self.name = data['name']
        self.author = data['author']
        self.jn_name = data['jn_name']
        self.dat = data['dat']
        self.num = data['num']
        self.employ = data['employ']
        self.employ_num = data['employ_num']
        self.ccf = data['ccf']
        self.cas = data['cas']
        self.jcr = data['jcr']
        self.times = data['times']
        self.vol = data['vol']
        self.no = data['no']
        self.page = data['page']
        self.DOI = data['DOI']
        self.link = data['link']
        self.code_link = data['code_link']
        self.summary = str({'name': data['name'], 'author': data['author'], 'DOI': data['DOI']})
        self.encd = data['encd']
        if 'code_encd' in data and data['code_encd'] != '':
            self.code_encd = str(data['code_encd'])
        else:
            self.code_encd = str([])
        if 'bibtex' in data:
            self.bibtex = data["bibtex"]

    def keys(self):
        return ["id", "name", "author", "jn_name", "dat", "num", "employ", "employ_num", "ccf", "cas", "jcr", "times",
                "vol", "no", "page", "DOI", "link", "code_link", "bibtex","encd","code_encd"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 专利
class Patent(Base):
    __tablename__ = 'patent'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)  # 专利名称
    patentee = Column(Text, nullable=False)  # 专利权人
    country = Column(String(200))  # 专利国家，包括 '中国专利', '美国专利','欧洲专利', 'WIPO专利','日本专利','其他国家专利'
    level = Column(String(200), default='发明专利')  # 专利类别，包括 '发明专利', '实用新型','外观设计'
    application_num = Column(String(200))  # 申请（专利）号
    patent_num = Column(String(200))  # 公开（公告）号
    IPC_num = Column(String(200))  # IPC号
    CPC_num = Column(String(200))  # CPC号
    application_dat = Column(DATE)  # 申请日期
    effect_dat = Column(DATE)  # 生效日期
    DOI = Column(String(200))  # DOI
    link = Column(Text)  # 专利链接
    encd = Column(Text)  # 专利附件
    adds = Column(String(20), default='unknown')  # 是否添加到自己专利表中

    def __init__(self, data):
        self.name = data['name']
        self.patentee = data['patentee']
        self.country = data['country']
        self.level = data['level']
        self.application_num = data['application_num']
        self.patent_num = data['patent_num']
        self.IPC_num = data['IPC_num']
        self.CPC_num = data['CPC_num']
        if 'application_dat' in data:
            self.application_dat = data['application_dat']
        if 'effect_dat' in data:
            self.effect_dat = data['effect_dat']
        self.DOI = data['DOI']
        self.link = data['link']
        if 'encd' in data:
            self.encd = data['encd']

    def keys(self):
        return ["id", "name", "patentee", "country", "level", "application_num", "patent_num", "IPC_num", "CPC_num",
                "application_dat", "effect_dat", "DOI", "link", "encd"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 荣誉称号
class Honor(Base):
    __tablename__ = 'honor'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(Text, nullable=False)  # 获得人
    title = Column(Text, nullable=False)  # 荣誉称号
    dat = Column(Text)  # 获得时间
    encd = Column(Text)  # 证书文件

    def __init__(self, data):
        self.name = data['name']
        self.author = data['title']
        self.dat = data['dat']
        self.title = data['title']
        if 'encd' in data:
            self.encd = data['encd']

    def keys(self):
        return ["id", "name", "title", "dat", "encd"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 社会、学会及学术兼职
class Socialwork(Base):
    __tablename__ = 'socialwork'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(Text, nullable=False)  # 获得人
    title = Column(Text, nullable=False)  # 社会、学会及学术兼职
    adds = Column(String(20), default='unknown')  # 是否添加到自己荣誉称号表中


# 项目
class Prog(Base):
    __tablename__ = 'program'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述 **
    name = Column(Text, nullable=False)  # 项目名称
    principal = Column(Text, nullable=False)  # 项目负责人
    member = Column(Text)  # 项目成员
    level = Column(String(128))  # 项目级别，包括 '国家级项目', '省级项目','横向项目'
    start_time = Column(DATE)  # 项目开始时间
    deadline = Column(DATE)  # 项目截止时间
    cost = Column(String(128))  # 项目费用
    fund = Column(String(128))  # 直接经费
    adds = Column(String(20), default='unknown')  # 是否添加到自己新闻表中**
    prog_num = Column(String(200), default='')  # 项目号
    pro_source = Column(String(200), default='')  # 项目来源
    application = Column(Text)  # 申请书
    file = Column(String(128), default='[]')  # 项目文件名
    role=Column(String(128))  # 负责人角色

    def __init__(self, data):
        self.name = data['name']
        self.principal = data['principal']
        self.level = data['level']
        self.start_time = data['start_time']
        self.deadline = data['deadline']
        self.cost = data['cost']
        self.prog_num = data['prog_num']
        self.pro_source = data['pro_source']
        self.member = data['member']
        self.fund = data['fund']
        self.role = data['role']
        self.file = str(data['file'])
        self.summary = str({'name': data['name'], 'principal': data['principal'], 'level': data['level'],
                            'start_time': data['start_time']})

    def keys(self):
        return ["id", "name", "principal", "level", "start_time", "deadline", "cost", "prog_num", "pro_source", "file",
                "member", "fund",'role']

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 课程
class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(Text, nullable=False)  # 课程名
    teacher = Column(String(128), nullable=False)  # 授课教师
    content = Column(Text, nullable=True)  # 授课内容
    page = Column(String(128))  # 相关主页
    adds = Column(String(20), default='unknown')  # 是否添加到自己课程表中


# 竞赛
class Comp(Base):
    __tablename__ = 'competition'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(String(128), nullable=False)  # 竞赛名字
    teachers = Column(Text)  # 指导教师
    participant = Column(String(128), nullable=False)  # 参与人员
    ranking = Column(String(128), nullable=True)  # 获得奖项
    adds = Column(String(20), default='unknown')  # 是否添加到自己竞赛表中
    pic = Column(String(128), default='')  # 竞赛图片名
    file = Column(String(128), default='[]')  # 竞赛文件名
    year = Column(String(64))  # 获奖年份
    dat = Column(DATE)  # 上传时间

    def __init__(self, data):
        self.name = data['name']
        self.teachers = data['teachers']
        self.participant = data['participant']
        self.ranking = data['ranking']
        self.pic = data['pic']
        self.file = str(data['file'])
        self.year = data['year']
        self.dat = data['dat']
        self.summary = str({'name': data['name'], 'teachers': data['teachers'], 'participant': data['participant'],
                            'ranking': data['ranking']})

    def keys(self):
        return ["id", "name", "teachers", "participant", "ranking", "pic", "file", "year", "dat"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 软件著作
class Soft(Base):
    __tablename__ = 'software'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)  # 软著名称
    author = Column(Text, nullable=False)  # 作者
    num = Column(String(200))  # 登记号
    way = Column(String(200))  # 权利获得方式，包括 '原始取得', '终受取得'
    DOI = Column(String(200))  # DOI
    limits = Column(String(200))  # 权利范围，包括 '全部权力', '部分权力'
    times = Column(DATE)  # 开发完成时间
    link = Column(Text)  # 链接
    encd = Column(Text)  # 附件
    adds = Column(String(20), default='unknown')  # 是否添加到自己软件著作表中

    def __init__(self, data):
        self.name = data['name']
        self.author = data['author']
        self.num = data['num']
        self.way = data['way']
        self.DOI = data['DOI']
        self.limits = data['limits']
        if 'times' in data:
            self.times = data['times']
        self.link = data['link']
        if 'encd' in data:
            self.encd = data['encd']

    def keys(self):
        return ["id", "name", "author", "num", "way", "DOI", "limits", "times", "link", "encd"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


# 学术专著
class Mono(Base):
    __tablename__ = 'monograph'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 学术专著题目
    language = Column(String(200))  # 语种，包括 '中文', '外文'
    employ = Column(String(200))  # 出版状态，包括 '已出版', '待出版'
    ISBN = Column(String(200))  # ISBN号
    editor = Column(Text, nullable=False)  # 编辑
    country = Column(String(200))  # 国家或地区
    city = Column(String(200))  # 城市
    page = Column(String(200))  # 起止页码
    word = Column(String(200))  # 总字数
    press = Column(String(200))  # 出版社
    dat = Column(DATE)  # 出版日期
    DOI = Column(String(200))  # DOI
    link = Column(Text)  # 学术专著链接
    encd = Column(Text)  # 学术专著附件
    adds = Column(String(20), default='unknown')  # 是否添加到自己学术专著表中


# 新闻
class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    title = Column(Text, nullable=False)  # 新闻标题
    content = Column(Text, nullable=False)  # 新闻内容
    classify = Column(String(128))  # 新闻类别
    publisher = Column(String(128))  # 发布人
    dat = Column(DATE)  # 日期
    adds = Column(String(20), default='unknown')  # 是否添加到自己新闻表中


# 数据资源
class Resource(Base):
    __tablename__ = 'resource'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(Text, nullable=False)  # 数据资源名
    classes = Column(String(128))  # 数据资源类别
    link = Column(Text)  # 数据资源链接
    introduction = Column(Text)  # 简介
    citation = Column(Text)  # 引用
    encd = Column(Text)  # 附件


# # Others 其他表
# class Others(Base):
#     __tablename__ = 'others'
#     id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
#
#     content = Column(Text, nullable=True)  # 内容


# teacher表
class Tch(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)  # id
    account = Column(String(50), unique=True, nullable=False)  # 账户
    tch_classify = Column(String(20), nullable=False)  # 用户类别
    name = Column(String(50), unique=True, nullable=False, index=True)  # 姓名
    Eng_name = Column(String(50), unique=True, nullable=False, index=True)  # 英文名
    avatar = Column(String(128), nullable=False)  # 证件照
    phone = Column(String(128), nullable=False)  # 电话号码
    email = Column(String(128), nullable=False)  # 邮箱
    home_page = Column(String(128))  # 主页
    profile = Column(Text, nullable=False)  # 简介
    address = Column(Text)  # 地址
    direction = Column(Text)  # 研究方向
    conference = Column(Text, default='{}')  # 会议论文id和作者类别
    journal = Column(Text, default='{}')  # 期刊论文id和作者类别
    competition = Column(Text, default='[]')  # 竞赛
    course = Column(Text, default='[]')  # 课程
    honor = Column(Text, default='[]')  # 荣誉称号
    social = Column(Text, default='[]')  # 社会兼职
    monograph = Column(Text, default='[]')  # 学术专著
    patent = Column(Text, default='[]')  # 专利
    program = Column(Text, default='[]')  # 项目
    software = Column(Text, default='[]')  # 软件著作
    others = Column(Text)  # 其他
    profile_c = Column(Text, nullable=False)  # 中文简介
    display = Column(Text)  # 不显示的id
    job_title = Column(String(20), nullable=False)  # 职称
    
    def __init__(self, data):
        self.account = data['account']
        self.tch_classify = data['tch_classify']
        self.name = data['name']
        self.Eng_name = data['Eng_name']
        self.avatar = data['avatar']
        self.phone = data['phone']
        self.email = data['email']
        # self.tch_classify = data['tch_classify']
        # self.name = data['name']
        # self.Eng_name = data['Eng_name']
        # self.avatar = data['avatar']
        # self.phone = data['phone']
        if 'times' in data:
            self.times = data['times']
        self.link = data['link']
        if 'encd' in data:
            self.encd = data['encd']

    def keys(self):
        return ["id", "account", "tch_classify", "name", "Eng_name", "phone", "email", "avatar", "address", "direction",
                "conference", "journal", "competition", "course", "honor", "social", "monograph", "patent", "program",
                "software", "display"]

    def __getitem__(self, item):
        return self.__getattribute__(item)    
    


# students 表
class Stu(Base):
    __tablename__ = 'students'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)  # id
    account = Column(String(50), unique=True, nullable=False)  # 账户
    stu_classify = Column(String(20), nullable=False)  # 用户类别
    name = Column(String(50), unique=True, nullable=False, index=True)  # 姓名
    Eng_name = Column(String(50), unique=True, nullable=False, index=True)  # 英文名
    avatar = Column(String(128), nullable=False)  # 证件照
    phone = Column(String(128), nullable=False)  # 电话号码
    email = Column(String(128), nullable=False)  # 邮箱
    # resume = Column(String(128), nullable=False)  # 个人简历
    home_page = Column(String(128))  # 主页
    profile = Column(Text, nullable=False)  # 简介
    address = Column(Text)  # 地址
    direction = Column(Text)  # 研究方向
    conference = Column(Text, default='{}')  # 会议论文id和作者类别
    journal = Column(Text, default='{}')  # 期刊论文id和作者类别
    competition = Column(Text, default='[]')  # 竞赛
    course = Column(Text, default='[]')  # 课程
    honor = Column(Text, default='[]')  # 荣誉称号
    monograph = Column(Text, default='[]')  # 学术专著
    patent = Column(Text, default='[]')  # 专利
    program = Column(Text, default='[]')  # 项目
    software = Column(Text, default='[]')  # 软件著作
    others = Column(Text)  # 其他
    display = Column(Text)  # 不显示的id
    tutor = Column(Text)  # 导师
    instructor = Column(Text)  # 指导老师
    graduated = Column(Text, default='0')  # 是否毕业,默认未毕业
    admission = Column(Text)


# Graduate 毕业生
class Gra(Base):
    __tablename__ = 'graduates'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)  # id
    name = Column(String(50), nullable=False, index=True)  # 姓名
    Eng_name = Column(String(50), nullable=False, index=True)  # 英文名
    admission = Column(DATE)  # 入学时间
    graduation = Column(DATE)  # 离校时间
    work = Column(String(100))  # 就职


# issues
class Issues(Base):
    __tablename__ = 'issues'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)  # id
    issue = Column(Text, nullable=False)  # 问题
    solve = Column(String(50), nullable=False, default='未解决')  # 是否解决
    time = Column(DATE)
    name = Column(String(50))  # 姓名
    phone = Column(String(100))  # 联系方式

class Code(Base):
    __tablename__ = 'code'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)  # id
    name = Column(Text, nullable=False)  # 文章名称
    dat = Column(Text)  # 发表时间
    article = Column(Text)  # 发表刊物
    article_short = Column(String(50))  # 刊物缩写
    article_link = Column(String(100))  # 文章链接
    code_link = Column(String(100))  # 代码链接
    user = Column(Text, nullable=False)

    def __init__(self, data):
        self.name = data['name']
        if 'dat' in data:
            self.dat = data['dat']
        if 'article' in data:
            self.article = data['article']
        if 'article_short' in data:
            self.article_short = data['article_short']
        if 'article_link' in data:
            self.article_link = data['article_link']
        if 'code_link' in data:
            self.code_link = data['code_link']
        self.user = data['user']

    def keys(self):
        return ["id", "name", "dat", "article", "article_short", "article_link", "code_link", "user"]

    def __getitem__(self, item):
        return self.__getattribute__(item)

# 创建表
def createTable():
    Base.metadata.create_all(engine)


# session插入语句
def session_db(new_class):
    sessions = DBSession()
    sessions.add(new_class)
    sessions.commit()
    sessions.close()


# 插入论文
def insertConf():
    new_conf = Conf(
        name='ask-Oriented Network for Image Dehazing',
        author='Runde Li',
        conf_name='IEEE',
        conf_summary='Runde Li, Jinshan Pan, Ming He, Zechao Li, Jinhui Tang. Task-Oriented Network for Image Dehazing. IEEE Trans. Image Process. 29: 6523-6534 (2020)',
    )
    session_db(new_conf)


# 插入用户账号密码
def insertAccount():
    new_account = Account(
        account='9',
        password='1',
        classify='学生',
        examine='0'
    )
    session_db(new_account)


# 插入期刊
def insertJn():
    new_jn = Jn(
        name='Deblurring Images via Dark Channel Prior',
        author='Jinshan Pan',
        jn_summary='Jinshan Pan, Deqing Sun, Hanspeter Pfister, Ming-Hsuan Yang. Deblurring Images via Dark Channel Prior, IEEE Transactions on Pattern Analysis and Machine Intelligence, 40(10): 2315-2328, 2018.',
    )
    session_db(new_jn)


# 插入专利
def insertPatent():
    new_patent = Patent(
        name='专利名11',
        patentee='作者2',
        country='中国',
        level='发明专利',
        application_num='12322',
        DOI='1234522',
        link='www.baidu.com'
    )
    session_db(new_patent)


# 插入项目
def insertProg():
    new_prog = Prog(
        name='三维视频编码中容错技术研究',
        principal='项欣光',
        prog_sum='三维视频编码中容错技术研究，BK2012397，江苏省自然科学基金（青年基金项目），2012.07-2015.06，20万，主持（项欣光）'
    )
    session_db(new_prog)


# 插入竞赛
def insertComp():
    new_comp = Comp(
        name='CCF',
        participant='李四'
    )
    session_db(new_comp)


# 插入软件著作
def insertSoft():
    new_soft = Soft(
        name='软件著作15',
        author='张三'
    )
    session_db(new_soft)


# 插入学术专著
def insertMono():
    new_mono = Mono(
        name='学术专著15',
        editor='张三'
    )
    session_db(new_mono)


# 插入新闻
def insertNews():
    new_news = News(
        title='巨作！',
        content='Dec. 2019: Two papers are accepted by AAAI 2020.'
    )
    session_db(new_news)


# insertSoft()
# insertMono()
# insertProg()
# insertComp()
# insertJn()
createTable()
# insertConf()
# insertAccount()
# insertPatent()
# insertNews()
