from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

from admins.views import admins_bp
from competition.views import competition_bp
from conference.views import conference_bp
from course.views import course_bp
from honor.views import honor_bp
from journal.views import journal_bp
from login.views import login_bp
from monograph.views import monograph_bp
from news.views import news_bp
from others.views import others_bp
from patent.views import patent_bp
from program.views import program_bp
from resource.views import resource_bp
from software.views import software_bp
from users.views import users_bp

app = Flask(__name__)
db = SQLAlchemy(app)

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

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5433/imag'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbuser:12345678@10.10.109.100:5432/imag001'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config["SECRET_KEY"] = 'TPmi4aLWRbyVq8zu9v82dWYW1'


# 自定义过滤器
@app.template_filter('stringtodic')
def stringtodic(dic):
    author = eval(dic)['author']
    author_final = ""
    for item in author:
        author_final += item
        author_final += " "
    return author_final


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    #app.run(host='172.17.0.8', port=80)
