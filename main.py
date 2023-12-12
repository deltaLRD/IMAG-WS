from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from admins.views import admins_bp
from competition.views import competition_bp
from conference.views import conference_bp
from course.views import course_bp
from honor.views import honor_bp
from journal.views import journal_bp
from libs.db import DBSession, News
from login.views import login_bp
from monograph.views import monograph_bp
from news.views import news_bp
from others.views import others_bp
from code_resource.views import code_resource_bp
from patent.views import patent_bp
from program.views import program_bp
from resource.views import resource_bp
from social.views import social_bp
from software.views import software_bp
from users.views import users_bp
from flask_cors import CORS
import markdown

import os

db_url = os.environ.get("DATABASE_URL", "localhost")
db_port = os.environ.get("DATABASE_PORT", "5433")
db_user = os.environ.get("DATABASE_USER", "dbuser")
db_pwd = os.environ.get("DATABASE_PWD", "12345678")
db_name = os.environ.get("DATABASE_NAME", "imag001")

db_full_url = "postgresql://{}:{}@{}:{}/{}".format(db_user, db_pwd, db_url, db_port, db_name)

app = Flask(__name__)

# 蓝图
app.register_blueprint(admins_bp, url_prefix='/admins')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(conference_bp, url_prefix='/conference')
app.register_blueprint(journal_bp, url_prefix='/journal')
app.register_blueprint(patent_bp, url_prefix='/patent')
app.register_blueprint(program_bp, url_prefix='/program')
app.register_blueprint(software_bp, url_prefix='/software')
app.register_blueprint(monograph_bp, url_prefix='/monograph')
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(competition_bp, url_prefix='/competition')
app.register_blueprint(course_bp, url_prefix='/course')
app.register_blueprint(honor_bp, url_prefix='/honor')
app.register_blueprint(others_bp, url_prefix='/others')
app.register_blueprint(resource_bp, url_prefix='/resource')
app.register_blueprint(social_bp, url_prefix='/social')
app.register_blueprint(code_resource_bp, url_prefix='/code_resource')
print(db_full_url)
app.config['SQLALCHEMY_DATABASE_URI'] = db_full_url

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbuser:12345678@10.10.109.100:5432/imag001'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbuser:12345678@localhost:12345/imag001'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbuser:12345678@localhost:12345/imag001'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config["SECRET_KEY"] = 'TPmi4aLWRbyVq8zu9v82dWYW1'
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
db = SQLAlchemy(app)

# 自定义过滤器
@app.template_filter('stringtodic')
def stringtodic(dic):
    author = eval(dic)['author']
    author_final = ""
    for item in author:
        author_final += item
        author_final += " "
    return author_final

# 自定义过滤器
@app.template_filter('ishide_bg')
def ishide_bg(dic):
    if dic==0:
        return 'white'
    else:
        return 'rgb(169, 169, 169)'


@app.route('/')
def home():
    sessions = DBSession()
    all_news = sessions.query(News).all()
    for item in all_news:
        item.content = markdown.markdown(item.content)
    return render_template('home.html', all_news=all_news)


host = '0.0.0.0'
port = 5000
if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
