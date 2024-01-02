# IMAG实验室页面

## admins 管理员

## competition 竞赛

## conference 会议论文

## course 课程

## honor 荣誉称号

## journal 期刊论文

## monograph 学术专著

## news 新闻

## patent 专利

## program 项目

## resource 数据资源

## software 软件著作

## users 用户


# 项目概况
- 该项目是一个复杂的项目，该项目本身是一个前后端不分离的项目，后端使用flask框架，前端使用Jinja模板引擎。该Jinja前端对应的是IMAG内网的展示页面(教师可以更改自己的展示项目)。
- 与此同时，该后端还是另一个管理界面的后端，那个管理页面使用React框架，主要负责论文，著作等的添加。
- 该项目的环境已使用docker-compose记录(即该项目根目录下的`docker-compose.yaml`)，启动这个docker-compose会同时部署后端，IMAG内网展示页面，后台管理界面。
**注意：要启动数据库，数据库单独使用另一个docker文件进行部署**

## 项目结构
接下来对项目结构进行一下阐述。
项目根目录下有多个文件夹，其中`users`文件夹对应的是内网的用户编辑页面(用户在该页面进行不同条目的收录以及展示设置)，其中的`template`文件夹下是用于Jinja引擎进行渲染的前端页面，`view.py`文件中是前端页面用到的渲染函数以及对于前端一些请求的api。
> 其他诸如software,program文件夹下的template文件夹和view.py文件的作用同上

其他文件夹则为对应其文件夹名的页面的展示，如成员，论文等，均可在IMAG内网页面中看到。