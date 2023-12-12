# 需求分析

一个实验室主页平台IMAG

## 1.需求描述

分为前台需求和后台需求。

### 1.1前台需求：

#### 1.1.1 登录

输入帐号密码，选中类别，分为教师登录，学生登陆，教师管理登录，学生管理登录。

#### 1.1.2  注册

注册信息包括：

账户account，密码password，用户姓名name，用户英文名Eng_name，类别classify（包括博士生导师，硕士生导师，其他老师，博士生，硕士生），电话phone，邮箱email，个人简介profile，研究方向direction，证件照avatar

其中，Account表存储 id，account，password，classify(教师，学生，教师管理，学生管理)，examine（是否审批，由管理员进行审批，未审批为0，审批通过为1）

```python
# 帐号表
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    account = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=True)
    classify = Column(String(20), nullable=False, default='unknown')
    examine = Column(String(20),default=0)
```

类别为博士生导师，硕士生导师和其他老师的存入teachers表中：

```python
# teacher表
class Tch(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False) # id
    account = Column(String(50), unique=True, nullable=False)  # 账户
    tch_classify = Column(String(20),  nullable=False)  # 用户类别
    name = Column(String(50), unique=True, nullable=False, index=True)  # 姓名
    Eng_name = Column(String(50), unique=True, nullable=False, index=True)  # 英文名
    avatar = Column(String(128), nullable=False)  # 证件照
    phone = Column(String(128),nullable=False)  # 电话号码
    email = Column(String(128), nullable=False)  # 邮箱
    home_page = Column(String(128))  # 主页
    profile = Column(Text, nullable=False)  # 简介
    address = Column(Text)  # 地址
    direction = Column(Text)  # 研究方向
    conference = Column(Text)  # 会议论文id和作者类别
    journal = Column(Text)  # 期刊论文id和作者类别
    competition = Column(Text)  # 竞赛
    course = Column(Text)  # 课程
    honor = Column(Text)  # 荣誉称号
    monograph = Column(Text)  # 学术专著
    patent = Column(Text)  # 专利
    program = Column(Text)  # 项目
    software = Column(Text)  # 软件著作
    others = Column(Text)  # 其他
```

类别是博士生和硕士生的个人信息存入students表中：

```python
# students 表
class Stu(Base):
    __tablename__ = 'students'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)  # id
    account = Column(String(50), unique=True, nullable=False)  # 账户
    stu_classify = Column(String(20),  nullable=False)  # 用户类别
    name = Column(String(50), unique=True, nullable=False, index=True)  # 姓名
    Eng_name = Column(String(50), unique=True, nullable=False, index=True)  # 英文名
    avatar = Column(String(128), nullable=False)  # 证件照
    phone = Column(String(128), nullable=False)  # 电话号码
    email = Column(String(128), nullable=False)  # 邮箱
    home_page = Column(String(128))  # 主页
    profile = Column(Text, nullable=False)  # 简介
    address = Column(Text)  # 地址
    direction = Column(Text)  # 研究方向
    conference = Column(Text)  # 会议论文id和作者类别
    journal = Column(Text)  # 期刊论文id和作者类别
    competition = Column(Text)  # 竞赛
    course = Column(Text)  # 课程
    honor = Column(Text)  # 荣誉称号
    monograph = Column(Text)  # 学术专著
    patent = Column(Text)  # 专利
    program = Column(Text)  # 项目
    software = Column(Text)  # 软件著作
    others = Column(Text)  # 其他
```

#### 1.1.3 Home

展示团队说明信息

#### 1.1.4 People

展示团队成员信息

包括Faculty教师，Associated Faculty关联教师，Ph.D Candidate博士生，M.E Students硕士生，Graduates已毕业学生

前四者展示 证件照，英文姓名，中文姓名，个人主页（包括中文版和英文版），邮箱，电话。

点每个团队人员时，跳到对应的个人主页上。

#### 1.1.5 News

展示新闻，包括新闻标题，内容，发布人，日期，类别。

#### 1.1.6 Publications

展示已发表的会议论文，期刊，专利，学术专著，软件著作。

##### Conference

展示实验室全部会议论文,包括 作者，论文标题，会议名称，DOI号，起止页码，发表时间。

##### Journal

展示实验室全部期刊论文，包括 作者，论文标题，会议名称，DOI号，起止页码，发表时间

##### Patent

展示实验室全部专利，包括专利名，专利权人，专利号，DOI号，生效日期

##### Monograph

展示实验室全部学术专著，包括专著题目，编辑，ISBN号，DOI号，出版日期

##### Software

展示实验室全部软件著作，包括软著名称，作者，登记号，DOI号

#### 1.1.7 Program

展示项目，包括项目名称，项目负责人，项目起始时间，项目费用

#### 1.1.8 Competition

展示竞赛获奖，包括竞赛名，奖项，获奖人，指导教师

#### 1.1.9 Course

展示课程，包括课程名字和授课教师

#### 1.1.10 Honor

展示荣誉称号，包括荣誉称号，获得人

#### 1.1.11 Resource

展示数据资源

#### 1.1.12 CONTACT US

联系方式和地址

### 2.1 教师后台需求：

还得加一个点击论文，看论文的界面。

用日志记录点击时间，user点击哪个paper

#### 2.1.1 修改个人信息

个人信息修改，包括 密码password，用户姓名name，用户英文名Eng_name，类别classify（包括博士生导师，硕士生导师，其他老师，博士生，硕士生），电话phone，邮箱email，个人简介profile，研究方向direction，证件照avatar 的修改

#### 2.1.2 上传Publications

##### 上传conference

上传会议论文

```python
# 会议论文对象
class Conf(Base):
    __tablename__ = 'conference'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=False)  # 综述，name+author+...的字符串
    name = Column(Text, unique=True, nullable=False)  # 论文题目
    author = Column(Text, nullable=False)  # 作者列表
    conf_name = Column(String(200))   # 会议名称
    organizer = Column(String(200))  # 会议组织者
    conf_dat = Column(DATE)  # 会议日期
    dat = Column(DATE)  # 发表日期    
    page = Column(String(200))  # 起止页码
    address = Column(Text)   # 会议地址
    num = Column(String(200))  # 文章号
    DOI = Column(String(200))  # DOI
    employ = Column(String(200))  # 收录情况，包括 'SCIE', 'SSCI', 'EI', 'ISTP', '北大中文核心期刊', '其他'
    employ_num = Column(String(200))  # 收录号
    ccf = Column(String(200))  # CCF分区，包括'A区', 'B区', 'C区', '无'
    times = Column(String(200))  # 引用数
    link = Column(Text)  # 论文链接
    code_link = Column(Text)  # 代码链接
    encd = Column(Text)  # 论文附件
    code_encd= Column(Text)  # 代码附件
    author_classify = Column(String(128))  # 作者分类，包括第一作者，第二作者，通讯作者和其他作者
    adds = Column(String(20), default='unknown')  # 是否添加到自己论文表中
```

将论文信息上传到数据库中，若adds为1，则将此论文和作者加到个人表的conference字典中，若adds为0，则仅上传到数据库中。

##### 上传Journal

上传期刊论文

```python
# 期刊论文对象
class Jn(Base):
    __tablename__ = 'journal'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=False)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 论文题目
    author = Column(Text, nullable=False)  # 作者列表
    jn_name = Column(String(200))   # 期刊名称
    dat = Column(DATE)  # 发表日期    
    num = Column(String(200))  # 文章号    
    employ = Column(String(200))  # 收录情况，包括 'SCIE', 'SSCI', 'EI', 'ISTP', '北大中文核心期刊', '其他'
    employ_num = Column(String(200))  # 收录号
    ccf = Column(String(200))  # CCF分区，包括 'A区', 'B区', 'C区', '无'
    cas = Column(String(200))  # 中科院分区，包括 '一区', '二区', '三区', '四区','无'
    jcr = Column(String(200))  # JCR分区， 包括 '一区', '二区', '三区', '四区','无'
    times = Column(String(200))  # 引用数
    vol = Column(String(200))  # 卷
    no =Column(String(200))  # 期号
    page = Column(String(200))  # 页码
    DOI = Column(String(200))  # DOI
    link = Column(Text)  # 论文链接
    code_link = Column(Text)  # 代码链接
    encd = Column(Text)  # 论文附件
    code_encd= Column(Text)  # 代码附件
    author_classify = Column(String(128))  # 作者分类，包括第一作者，第二作者，通讯作者和其他作者
    adds = Column(String(20), default='unknown')  # 是否添加到自己论文表中
```

将论文信息上传到数据库中，若adds为1，则将此论文和作者加到个人表的journal字典中，若adds为0，则仅上传到数据库中。

##### 上传Patent

上传专利

```python
# 专利对象
class Patent(Base):
    __tablename__ = 'patent'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 专利名称
    patentee = Column(Text, nullable=False)  # 专利权人
    country = Column(String(200))   # 专利国家, 包括'中国专利', '美国专利','欧洲专利', 'WIPO专利','日本专利','其他国家专利'
    level = Column(String(200),default='发明专利')  # 专利类别，包括 '发明专利', '实用新型','外观设计'
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
```

将专利信息上传到数据库中，若adds为1，则将此专利加到个人表的patent列表中，若adds为0，则仅上传到数据库中。

##### 上传Monograph

上传学术专著

```python
# 学术专著对象
class Mono(Base):
    __tablename__ = 'monograph'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 学术专著题目
    language = Column(String(200))  # 语种，包括 '中文', '外文'
    employ = Column(String(200))  # 出版状态，包括 '已出版', '待出版'
    ISBN = Column(String(200))  # ISBN号
    editor = Column(Text, nullable=False)  # 编辑
    country = Column(String(200))   # 国家或地区
    city = Column(String(200))  # 城市
    page = Column(String(200))  # 起止页码
    word = Column(String(200))  # 总字数      
    press = Column(String(200))  # 出版社
    dat = Column(DATE)  # 出版日期         
    DOI = Column(String(200))  # DOI
    link = Column(Text)  # 学术专著链接
    encd = Column(Text)  # 学术专著附件
    adds = Column(String(20), default='unknown')  # 是否添加到自己学术专著表中
```

将学术专著信息上传到数据库中，若adds为1，则将此专利加到个人表的monograph列表中，若adds为0，则仅上传到数据库中。

##### 上传Software

上传软件著作

```python
# 软件著作对象
class Soft(Base):
    __tablename__ = 'software'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 综述
    name = Column(Text, unique=True, nullable=False)  # 软著名称
    author = Column(Text, nullable=False)  # 作者
    num = Column(String(200))  # 登记号
    way = Column(String(200))  # 权利获得方式，包括 '原始取得', '终受取得'
    DOI = Column(String(200))  # DOI
    limits = Column(String(200))  # 权力或的范围，包括 '全部权力', '部分权力'
    times = Column(String(200))  # 开发完成时间             
    link = Column(Text)  # 专利链接
    encd = Column(Text)  # 专利附件
    adds = Column(String(20), default='unknown')  # 是否添加到自己专利表中
```

将软件著作信息上传到数据库中，若adds为1，则将此专利加到个人表的software列表中，若adds为0，则仅上传到数据库中。

#### 2.1.3 上传Program

增加项目

```python
# 新闻表
class Prog(Base):
    __tablename__ = 'program'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(Text, nullable=True)  # 项目名称
    principal = Column(Text, nullable=True)  # 项目负责人
    level = Column(String(128))  # 项目级别，包括 '国家级项目', '省级项目','横向项目'
    start_time = Column(DATE)  # 项目开始时间
    deadline = Column(DATE)  # 项目截止时间
    cost = Column(String(128))  # 项目费用
    adds = Column(String(20), default='unknown')  # 是否添加到自己新闻表中
```

将项目信息上传到数据库中，若adds为1，则将此专利加到个人表的program列表中，若adds为0，则仅上传到数据库中。

#### 2.1.4 上传News

增加新闻，包括新闻标题，内容，发布人，日期，类别

```python
# 新闻表
class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    title = Column(Text, nullable=True)  # 新闻标题
    content = Column(Text, nullable=True)  # 新闻内容
    classify = Column(String(128))  # 新闻类别
    publisher = Column(String(128))  # 发布人
    dat = Column(DATE)  # 日期
    adds = Column(String(20), default='unknown')  # 是否添加到自己新闻表中
```

将论文信息上传到数据库中，若adds为1，则将此专利加到个人表的news列表中，若adds为0，则仅上传到数据库中。

#### 2.1.5 上传Competition

增加竞赛

```python
# 竞赛表
class Comp(Base):
    __tablename__ = 'competition'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(String(128), nullable=True)  # 竞赛名字
    teachers = Column(Text)  # 指导教师
    participant = Column(String(128))  # 参与人员
    ranking = Column(String(128), nullable=True)  # 获得奖项
    adds = Column(String(20), default='unknown')  # 是否添加到自己竞赛表中
```

将论文信息上传到数据库中，若adds为1，则将此专利加到个人表的competition列表中，若adds为0，则仅上传到数据库中。

#### 2.1.6 上传Course

增加课程

```python
# 课程表
class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(Text, nullable=True)  # 课程名
    teacher = Column(String(128))  # 授课教师
    content = Column(Text, nullable=True)  # 授课内容
    page = Column(String(128))  # 相关主页
    adds = Column(String(20), default='unknown')  # 是否添加到自己课程表中
```

将论文信息上传到数据库中，若adds为1，则将此专利加到个人表的course列表中，若adds为0，则仅上传到数据库中。

#### 2.1.7 上传荣誉称号

增加荣誉称号

```python
# 新闻表
class Honor(Base):
    __tablename__ = 'honor4'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # 总述
    name = Column(Text, nullable=True)  # 获得人
    title = Column(Text, nullable=True)  # 荣誉称号
    adds = Column(String(20), default='unknown')  # 是否添加到自己荣誉称号表中
```

将论文信息上传到数据库中，若adds为1，则将此专利加到个人表的honor列表中，若adds为0，则仅上传到数据库中。

#### 2.1.8 上传数据资源

上传数据资源

```python
# 数据资源表
class Resource(Base):
    __tablename__ = 'resource'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(Text, nullable=True)  # 数据资源名
    link = Column(Text, nullable=True)  # 数据资源链接
    ##可能会加附件 encd = Column(Text)
```

#### 2.1.10 上传其他

里面加富文本编辑器，教师随意上传，展示在个人主页上

#### 2.1.11 选择Publications

选择数据库中属于自己的的会议论文，期刊，专利，学术专著，软件著作

##### Conference

选择会议论文论文和作者类别，将论文id和作者类别存为字典添加到teachers表中的conference列中。

##### Journal

选择期刊论文和作者类别，将论文id和作者类别存为字典添加到teachers表中的journal列中。

##### Patent

选择专利，将专利id存为列表添加到teachers表中的patent列中。

##### Monograph

选择学术著作，将学术专著id存为列表添加到teachers表中的monograph列中。

##### Software

选择软件专著，将软著id存为列表添加到teachers表中的software列中。

#### 2.1.12 选择Program

选择项目，将项目id存为列表添加到teachers表中的program列中。

#### 2.1.13 选择Competition

选择竞赛，将竞赛id存为列表添加到teachers表中的competition列中。

#### 2.1.14 选择Course

选择课程，将课程id存为列表添加到teachers表中的course列中。

#### 2.1.15 选择Honor

选择荣誉称号，将荣誉称号id存为列表添加到teachers表中的honor列中。

### 2.2 学生后台需求

上传：conference, journal, patent, software, monograph, news, resource

添加：conference,journal, patent, software, monograph, competition, program

### 2.3 学生管理后台需求

#### 2.3.1 审核用户权限

用户注册后，将account中的examine列由0变为1.

#### 2.3.2 增加、删除、修改用户信息

用户信息修改，包括 密码password，用户姓名name，用户英文名Eng_name，类别classify（包括博士生导师，硕士生导师，其他老师，博士生，硕士生），电话phone，邮箱email，个人简介profile，研究方向direction，证件照avatar 的修改。

增加或删除用户帐号及其余信息。

#### 2.3.3 增加、删除、修改 news、publications、program、competition、course、honor

论文、项目、新闻等所有信息的增删改。

### 2.4 教师管理后台需求

#### 2.4.1 学生管理帐号增删改

管理学生管理账户，增加、删除、修改账户

#### 2.4.2 其余操作与学生管理相同

增删改用户信息、论文信息、新闻、项目等所有内容的增删改。

# 架构分析

以下标题为里面包或目录名字，表格分别为模块和左右，模块包括views的函数和html页面。

## templates

存放全局的模板以及home界面

| 模块       | 作用               |
| ---------- | ------------------ |
| base       | 游客界面框架       |
| base_tch   | 教师登陆后界面框架 |
| base_stu   | 学生登陆后界面框架 |
| base_adstu | 学生管理界面框架   |
| base_adtch | 教师管理界面框架   |
| home       | home界面           |

## statas

存放全局的css和js

## admins

管理员文件夹

| 模块       | 作用                             |
| ---------- | -------------------------------- |
| examine    | 审批注册的教师和学生             |
| tch_edit   | 修改教师信息                     |
| stu_edit   | 修改学生信息                     |
| admin_edit | 修改密码                         |
| register   | 教师管理员注册学生管理员账户界面 |
| tch_add    | 增加教师帐号                     |
| stu_add    | 增加学生帐号                     |
| tch_delete | 删除教师帐号                     |
| stu_delete | 删除学生帐号                     |

## users

管理教师和学生信息

| 模块        | 作用                 |
| ----------- | -------------------- |
| people_page | PEOPLE展示页面       |
| tch_info    | 教师个人主页         |
| stu_info    | 学生个人主页         |
| tch_edit    | 教师修改个人信息界面 |
| stu_edit    | 学生修改个人信息界面 |

## login

登录和注册

| 模块     | 作用 |
| -------- | ---- |
| login    | 登录 |
| register | 注册 |

## news

新闻模块

| 模块        | 作用           |
| ----------- | -------------- |
| news        | 新闻展示       |
| news_upload | 上传新闻       |
| news_delete | 管理员删除新闻 |
| news_modify | 管理员修改新闻 |

## conference

会议论文模块

| 模块        | 作用                       |
| ----------- | -------------------------- |
| conference  | 展示                       |
| conf_add    | 添加(教师和学生)           |
| conf_delete | 删除（管理员）             |
| conf_modify | 修改（管理员）             |
| conf_upload | 上传（教师，学生，管理员） |

## journal

期刊论文模块

| 模块       | 作用                       |
| ---------- | -------------------------- |
| journal    | 展示                       |
| jn_add     | 添加(教师和学生)           |
| jn_delete  | 删除（管理员）             |
| jn_mondify | 修改（管理员）             |
| jn_upload  | 上传（教师，学生，管理员） |

## patent

专利模块

| 模块          | 作用                       |
| ------------- | -------------------------- |
| patent        | 展示                       |
| patent_add    | 添加(教师和学生)           |
| patent_delete | 删除（管理员）             |
| patent_modify | 修改（管理员）             |
| patent_upload | 上传（教师，学生，管理员） |

## monograph

学术专著模块

| 模块        | 作用                       |
| ----------- | -------------------------- |
| monograph   | 展示                       |
| mono_add    | 添加(教师和学生)           |
| mono_delete | 删除（管理员）             |
| mono_modify | 修改（管理员）             |
| mono_upload | 上传（教师，学生，管理员） |

## software

软件著作模块

| 模块        | 作用                       |
| ----------- | -------------------------- |
| software    | 展示                       |
| soft_add    | 添加(教师和学生)           |
| soft_delete | 删除（管理员）             |
| soft_modify | 修改（管理员）             |
| soft_upload | 上传（教师，学生，管理员） |

## program

项目模块

| 模块            | 作用               |
| --------------- | ------------------ |
| program         | 展示               |
| prog_add        | 添加（教师和学生） |
| prog_upload_tch | 上传（教师）       |
| prog_delete     | 删除（管理员）     |
| prog_modify     | 修改（管理员）     |
| prog_upload     | 上传（管理员）     |

## competition

竞赛论文模块

| 模块            | 作用             |
| --------------- | ---------------- |
| competition     | 展示             |
| conp_add        | 添加(教师和学生) |
| conp_upload_tch | 上传（教师）     |
| conp_delete     | 删除（管理员）   |
| conp_modify     | 修改（管理员）   |
| conp_upload     | 上传（管理员）   |

## course

课程模块

| 模块              | 作用           |
| ----------------- | -------------- |
| course            | 展示           |
| conrse_add        | 添加(教师)     |
| conrse_upload_tch | 上传（教师）   |
| conrsef_delete    | 删除（管理员） |
| conrse_modify     | 修改（管理员） |
| conrse_upload     | 上传（管理员） |

## honor

荣誉称号模块

| 模块             | 作用           |
| ---------------- | -------------- |
| honor            | 展示           |
| honor_add        | 添加(教师)     |
| honor_upload_tch | 上传（教师）   |
| honor_delete     | 删除（管理员） |
| honor_modify     | 修改（管理员） |
| honor_upload     | 上传（管理员） |

## resource

数据资源模块

| 模块            | 作用                       |
| --------------- | -------------------------- |
| resource        | 展示                       |
| resource_delete | 删除（管理员）             |
| resource_modify | 修改（管理员）             |
| resource_upload | 上传（教师，学生，管理员） |

## others

数据资源模块

| 模块          | 作用               |
| ------------- | ------------------ |
| others_upload | 上传（教师，学生） |

