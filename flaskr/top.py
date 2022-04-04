import flask
import functools
from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.auth import login_required
import subprocess
from subprocess import PIPE
import time
import psutil
import os
#for password-reset feature
import flask_wtf
from flask_mail import Mail
from flask_mail import Message
import wtforms
from wtforms import validators
from itsdangerous.url_safe import URLSafeTimedSerializer
import sqlite3

#for db connection
import click
from flask.cli import with_appcontext

bp = Blueprint('top', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/admin/top', methods=['GET']) 
@login_required
def top():
    #result = subprocess.run(['ps'], stdout=subprocess.PIPE)
    result = subprocess.run(['ps aux | grep "python"'], stdout=subprocess.PIPE, shell=True)
    #result = subprocess.run(['ps aux | grep "python" | grep "WeatherTweet.py"'], stdout=subprocess.PIPE, shell = True)
    #print("result.stdout1=",result.stdout)
    if "WeatherTweet.py" in str(result.stdout):
        running = True
        tweet_status = "Running Auto-Tweet"
        stt_bt_st = "disabled"
        stp_bt_st = ""
    else:
        running = False
        tweet_status = "Disabled Auto-Tweet"
        stt_bt_st = ""
        stp_bt_st = "disabled"

    print("WeathetTweet.py is ", running)
    return render_template('admin/top.html',tweet_status=tweet_status, stt_bt_st=stt_bt_st, stp_bt_st=stp_bt_st ) #renders HTML file for top page

@bp.route('/admin/top', methods=['POST'])
def TweetBot():
    db = get_db()
    tweets = db.execute(
        ' SELECT tt.id, tw_type, tw_memo, tw_dow, tw_rdm, tw_time, weather_condition, temp_condition, tweet1, tweet2,tweet3,tweet4,tweet5,tweet6,tweet7,tweet8,tweet9,tweet10, created_at, author_id, username'
        ' FROM tweet_table tt JOIN user u ON tt.author_id = u.id '
        ' ORDER BY '
        ' CASE tw_dow '
        ' WHEN "Monday" THEN 1 '
        ' WHEN "Tuesday" THEN 2 '
        ' WHEN "Wednesday" THEN 3 '
        ' WHEN "Thursday" THEN 4 '
        ' WHEN "Friday" THEN 5 '
        ' WHEN "Saturday" THEN 6 '
        ' WHEN "Sunday" THEN 7 '
        ' END '
        ' ,tw_time ASC '
    ).fetchall()

    #check WeatherTweet.py's running status
    result = subprocess.run(['ps aux | grep "python"'], stdout=subprocess.PIPE, shell=True) 
    #result = subprocess.run(['ps aux | grep "python" | grep "WeatherTweet.py"'], stdout=subprocess.PIPE, shell = True) 
    stt_bt_st = ""
    stp_bt_st = ""
    #print("result.stdout2=",result.stdout)
    if "WeatherTweet.py" in str(result.stdout):
        running = True
    else: running = False 
    print("WeathetTweet.py is ", running)
    #if WeatherTweet.py isn't running
    #disable "stop auto-tweet" button & wait for request from "start auto-tweet" button 
    while running == False:
        tweet_status = "Disabled Auto-Tweet"
        if request.form.get('button_run') == 'Start Auto-Tweet':
            tweet_status = "Running Auto-Tweet"
            print("tweet_status=",tweet_status)
            #python3=os.getenv("PYTHON3")
            WeatherTweet=os.getenv("WEATHERTWEET")
            p = subprocess.Popen(['python3',WeatherTweet])
            print("WeatherTweet.py started.")
            stt_bt_st = "disabled"
            stp_bt_st = ""
        else:
            pass
        return render_template('admin/top.html',tweet_status=tweet_status,stt_bt_st=stt_bt_st,stp_bt_st=stp_bt_st) #renders HTML file for top page
    #If WeatherTweet.py process is running,     
    #disable "start auto-tweet" button & wait for request from "stop auto-tweet" button
    while running == True:
        tweet_status = "Running Auto-Tweet"
        if request.form.get('button_stop') == 'Stop Auto-Tweet':
            tweet_status = "Disabled Auto-Tweet"
            print("tweet_status=",tweet_status)
            #get running WeatherTweet.py's process id & terminate it
            tmp1 = subprocess.Popen(['pgrep','-f','WeatherTweet.py'], stdout=subprocess.PIPE)
            tmp2 = subprocess.run(['tr','-d','\n'],stdin=tmp1.stdout,stdout=subprocess.PIPE)
            tmp3 = str(tmp2.stdout).replace("b'", "")
            tmp4 = tmp3.replace("'", "")
            pid = int(tmp4)
            #print("tmp1=",tmp1)
            #print("tmp2=",tmp2)
            #print("tmp3=",tmp3)
            #print("tmp4=",tmp4)
            #print("pid=",pid)
            p=psutil.Process(pid)
            p.terminate()
            print("WeatherTweet.py is tereminated.")
            stt_bt_st = ""
            stp_bt_st = "disabled"
        else:
            pass
        return render_template('admin/top.html',tweet_status=tweet_status,stt_bt_st=stt_bt_st,stp_bt_st=stp_bt_st) #renders HTML file for top page

def create_token(user_id, secret_key, salt):
    #generate token from user_id
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(user_id, salt=salt)

def load_token(token, secret_key, salt):
    #get user_id and time from token
    serializer = URLSafeTimedSerializer(secret_key)
    #return serializer.loads(token, salt=salt, return_timestamp=True)
    return serializer.loads(token, salt=salt, max_age=1800)

bp.secret_key = os.getenv("BP_SECRET_KEY")
SALT = 'shio'
@bp.route('/forgot_pass', methods=['GET', 'POST'])
def reset():
    mail = Mail(current_app)
    form = EmailForm()
    email=str(form.mail.data)
    # ask users to input email address
    # and let them URL for password-reset
    if request.method == 'POST' and form.validate_on_submit():
    # check db whether the address exists
        db = get_db()
        rows = db.execute(
            ' SELECT * FROM user WHERE username = ? LIMIT 1 ',
            (email,)
            ).fetchall()
        if len(rows) >= 1:
        #generate token using create_token method
            token = create_token(form.mail.data, bp.secret_key,SALT)
            url = url_for('top.new_pwd', token=token, _external= True)
            # send email
            msg = Message(subject="Password Reset",sender=os.getenv("SENDER"), recipients=[email])
            msg.html = render_template('email_content.html', url=url)

            with mail.connect() as conn:
                conn.send(msg)
            #display message
            flash('Password reset email is sent to: %s' % email)
        else:
            flash("Email address doesn't exist!")
    #display page
    return render_template('mail.html', form=form)

@bp.route('/forgot_pass/new_pwd', methods=['GET','POST'])
def new_pwd():
    #set new password
    if request.method == 'GET':
        #get email address
        try:
            token = request.args.get('token')
            mail_address = load_token(token, bp.secret_key, SALT)
        except Exception as e:
            return abort(400)
        #display page
        form = NewPwdForm(token=token)
        return render_template('new_pwd.html', form=form,mail_address=mail_address)
    else:
        form = NewPwdForm()
        #get email address
        try:
            mail_address = load_token(form.token.data, bp.secret_key, SALT)
        except Exception as e:
            return abort(400)
        if form.validate_on_submit():
            password = form.new_pwd2.data
            error = None
            if not password:
                error = 'New password is required.'
            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'UPDATE user SET password = ?'
                    ' WHERE username = ?',
                    (generate_password_hash(password), mail_address)
                    )
                db.commit()
            flash('Your password is successfully updated.')
            return redirect(url_for('top.index'))
        return render_template('new_pwd.html', form=form,mail_address=mail_address)

class EmailForm(flask_wtf.FlaskForm):
    mail = wtforms.StringField('mail',[validators.Email(message='Email address format is wrong.'),
    validators.InputRequired(message='Please input email address.')])

class NewPwdForm(flask_wtf.FlaskForm):
    token = wtforms.HiddenField('token',[validators.InputRequired()])
    new_pwd1 = wtforms.PasswordField('password', [validators.EqualTo('new_pwd2')])
    new_pwd2 = wtforms.PasswordField('password(confirm)',[validators.InputRequired()])
#for SSL acme-challenge
@bp.route('/.well-known/acme-challenge/<filename>')
def acme_challenge(filename):
    return render_template('.well-known/acme-challenge/'+filename)

if __name__ == "__main__":
    bp.run()
#    port = int(os.getenv('PORT', 5000))
#    bp.run(debug=True, host='127.0.0.1', port=port)
