from flask import Flask, render_template, request, flash, jsonify, redirect, url_for
# from flask.ext.session import Session
import json
from models import Schema
from services import RecordService
from services import UserService
import json
import os.path
from sys import platform
import flask_login

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# https://developers.google.com/sheets/api/quickstart/python?authuser=3
# import pickle
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

app = Flask(__name__)
app.secret_key = 'super secret key'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

Schema()
recordService = RecordService()
userService = UserService()

people_db = '/var/www/ows/people.json'

# sess = Session()

# @app.route("/")
# def home():
#     print(flask_login.current_user)
#     # data = get_papers()
#     data = {}
#     data['confs'], countries = recordService.list()
#     return render_template('index.html', data = data)
#     # return jsonify(data)

def get_categories(ret_type='array'):
    if 'linux' in platform:
        cat_file = '/var/www/conftracker/categories.json'
    else:
        cat_file = 'categories.json'
    with open(cat_file, 'r') as f:
        data = json.load(f)
    cates = []
    if ret_type == 'array':
        for u in data:
            cates.append([u['tag'], u['name']])
    else:
        cates = {}
        for u in data:
            cates[u['tag']] = u['name']
            cates.append([u['tag'], u['name']])
    return cates


@app.route("/", methods=['GET'])
def home():
    data = {}
    if request.method == 'GET':
        # user_id = request.args.get('user', default = -1, type = int)
        user_id = 0
        if flask_login.current_user.is_authenticated:
            user_id = flask_login.current_user.id
        star = request.args.get('star', default = 0, type = int)
        category = request.args.get('category', default = "all", type = str)
        sortby = request.args.get('sort', default = "subdate", type = str)
        data['confs'], data['countries'] = recordService.list(user_id=user_id, category=category, sort=sortby, star=star)        
    else:
        data['confs'], data['countries'] = recordService.list()
    
    data['cates'] = get_categories()
    return render_template('index.html', data = data)
    
    # return jsonify(data)

def home(user):
    # data = get_papers()
    data = {}
    data['confs'], countries = recordService.list()
    return render_template('index.html', data = data)
    # return jsonify(data)

@app.route("/star", methods=['POST'])
def star():
    res = {}
    if request.method == 'POST':
        if flask_login.current_user.is_authenticated:
            user_id = flask_login.current_user.id
        else:
            res['code'] = 3
            res['msg'] = "Please login for your star list!"
            return res
        conf_id = request.args.get('conf', default = -1, type = int)
        if conf_id < 0 or user_id < 0:
            res['code'] = 2
            res['msg'] = "Incorrect input information"
            return res
        else:
            status = recordService.subscribe(conf=conf_id, user=user_id)
            res['code'] = status
            res['msg'] = "You've starred a conference!"
            return res
    res['code'] = -1
    return res
        # data = {}
        # data['confs'], data['countries'] = recordService.list(user_id=user_id)
        # data['user'] = flask_login.current_user
        # # return render_template("index.html", data = data)
        # return redirect(url_for('home'))

@app.route("/addedit", methods=['GET', 'POST'])
# @flask_login.login_required
def addedit():
    if not flask_login.current_user.is_authenticated:
        flash("Please login first to edit.", 'warning')
        return redirect(url_for('home'))
    if request.method == 'POST':
        item = {}
        item['id'] = request.form.get('id')        
        item['abbr'] = request.form.get('abbr')
        item['title'] = request.form.get('title')
        item['category'] = ','.join(request.form.getlist('category'))
        item['publisher'] = request.form.get('publisher')
        item['ccfrank'] = request.form.get('ccfrank')
        item['year'] = request.form.get('year')
        item['startdate'] = request.form.get('startdate')
        item['enddate'] = request.form.get('enddate')
        item['absdate'] = request.form.get('absdate')
        item['subdate'] = request.form.get('subdate')
        item['notifdate'] = request.form.get('notifdate')
        item['city'] = request.form.get('city')
        item['country'] = request.form.get('country')
        item['link'] = request.form.get('homepage')
        item['crdate'] = request.form.get('crdate')
        # print(item)
        if item['id']:
            results = recordService.edit(item)
            flash("Record " + item['abbr'] + " updated successfully.", 'success')        
        else:
            item['uid'] = flask_login.current_user.id
            results = recordService.add(item)
            flash("Record " + item['abbr'] + " added successfully.", 'success')        
        # data = {}
        # data['confs'], data['countries'] = recordService.list()
        # data['user'] = flask_login.current_user
        # return render_template('index.html', data = data)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route("/edit", methods=['GET', 'POST'])
# @flask_login.login_required
def edit():
    res = {}
    if not flask_login.current_user.is_authenticated:        
        res['code'] = 3
        res['msg'] = "Please login to edit!"
        return res
    conf_id = -1
    if request.method == 'POST':
        conf_id = request.form.get('confid')
        # print(conf_id)
        if conf_id <=0 :
            res['code'] = 1
            res['msg'] = "Something wrong! No record found."
            return res
        res = recordService.get_item(conf_id)        
        res['code'] = 0
        return res
    res['code'] = 2
    res['msg'] = "Oops. Something unexpected."
    return res

@login_manager.user_loader
def load_user(user_id):
   user = userService.get_by_id(user_id)
   return user

@app.route("/login", methods=['POST'])
def login():
    u = {}
    u['first_name'] = str(request.form['first_name'])
    u['last_name'] = str(request.form['last_name'])
    u['email'] = str(request.form['email'])

    status, user = userService.login(u)
    if status == 0:
        flask_login.login_user(user)  
        flash("Welcome back,  " + u['first_name'] + "!", 'success')      
        return redirect(url_for('home', star=1))
    elif status == 2: # new user
        status, user = userService.add(u)
        flask_login.login_user(user)
        flash("Signed up successfully with email " + u['email'], 'success')
        return redirect(url_for('home', star=1))
    else:
        flash("Login failed: Existing email with incorrect first/last name.", 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('home'))


if __name__ == "__main__":    
    # app.config['SESSION_TYPE'] = 'filesystem'
    # sess.init_app(app)
    # Schema()
    app.run()


