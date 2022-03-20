import os
from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('tweet', __name__)

@bp.route('/tweet', methods=('GET','POST'))
def index():
    tweet_types = ["Daily", "Weekly", "Weather"]
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
    return render_template('tweet/index.html',tweet_types=tweet_types,tweets=tweets)

@bp.route('/tweet/create', methods=('GET', 'POST'))
@login_required #requires login. redirects login page if not logged in 
def create_tweet():
    return render_template('tweet/create_tweet.html')

#create's view
@bp.route('/tweet/create_daily_tweet', methods=('GET', 'POST'))
@login_required #requires login. redirects login page if not logged in 
def create_daily_tweet():
    print("g.user['id']=",g.user['id'])
    if request.method == 'POST':
        tw_type = "Daily"
        tw_memo = request.form.get('tw_memo') 
        tw_rdm =request.form.get('random_setting') 
        tw_time=request.form.get('tw_time')
        tweets=[""]*11
        for i in range(1,11):
            tweets[i] = request.form.get("tweet"+str(i))
        error = None
        if not tw_time:
            error = 'Tweet time is required.'
        if all( x == '' for x in tweets): 
            error = 'At least 1 tweet content is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tweet_table (tw_type, tw_memo, tw_rdm, tw_time, tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8, tweet9, tweet10,author_id)' 
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (tw_type, tw_memo, tw_rdm, tw_time, tweets[1], tweets[2], tweets[3], tweets[4], tweets[5], tweets[6], tweets[7], tweets[8], tweets[9], tweets[10], g.user['id'])
            )
            db.commit()
            flash('New Daily Tweet is added', category='alert alert-info')
            return redirect(url_for('tweet.index'))
    return render_template('tweet/create_daily_tweet.html')

@bp.route('/tweet/create_weekly_tweet', methods=('GET', 'POST'))
@login_required #requires login. redirects login page if not logged in 
def create_weekly_tweet():
    if request.method == 'POST':
        tw_type="Weekly"
        tw_memo = request.form.get('tw_memo') 
        tw_dow= request.form.get('tw_dow')
        tw_rdm =request.form.get('random_setting') 
        tw_time = request.form.get('tw_time')
        tweets=[""]*11
        for i in range(1,11):
            tweets[i] = request.form.get("tweet"+str(i))
        error = None
        if not tw_time:
            error = 'Tweet time is required.'
        if all( x == '' for x in tweets): 
            error = 'At least 1 tweet content is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tweet_table (tw_type, tw_memo,  tw_dow, tw_rdm, tw_time, tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8, tweet9, tweet10, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (tw_type, tw_memo, tw_dow, tw_rdm, tw_time, tweets[1], tweets[2], tweets[3], tweets[4], tweets[5], tweets[6], tweets[7], tweets[8], tweets[9], tweets[10], g.user['id'])
            )
            db.commit()
            flash('New Weekly Tweet is added', category='alert alert-info')
            return redirect(url_for('tweet.index'))
    return render_template('tweet/create_weekly_tweet.html')

@bp.route('/tweet/create_weather_tweet', methods=('GET', 'POST'))
@login_required #requires login. redirects login page if not logged in 
def create_weather_tweet():
    if request.method == 'POST':
        tw_type = "Weather"
        tw_memo = request.form.get('tw_memo') 
        tw_dow = request.form.get('tw_dow')
        tw_rdm =request.form.get('random_setting') 
        tw_time = request.form.get('tw_time')
        weather_condition = request.form.get('weather_condition')
        temp_condition = request.form.get('temp_condition')
        tweets=[""]*11
        for i in range(1,11):
            tweets[i] = request.form.get("tweet"+str(i))
        error = None
        if not tw_time:
            error = 'Tweet time is required.'
        if all( x == '' for x in tweets): 
            error = 'At least 1 tweet content is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tweet_table (tw_type, tw_memo, tw_dow, tw_rdm, tw_time, weather_condition, temp_condition, tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8, tweet9, tweet10, author_id)'
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (tw_type, tw_memo, tw_dow, tw_rdm, tw_time, weather_condition, temp_condition, tweets[1], tweets[2], tweets[3], tweets[4], tweets[5], tweets[6], tweets[7], tweets[8], tweets[9], tweets[10], g.user['id'])
            )
            db.commit()
            flash('New Weather Tweet is added', category='alert alert-info')
            return redirect(url_for('tweet.index'))
    return render_template('tweet/create_weather_tweet.html')

#defining get_tweet function for update&delete view
def get_tweet(id, check_author=True):
    tweet = get_db().execute(
        'SELECT tt.id, tw_type, tw_memo,  tw_dow, tw_rdm, tw_time, weather_condition, temp_condition, tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8, tweet9, tweet10, created_at, author_id, username'
        ' FROM tweet_table tt JOIN user u ON tt.author_id = u.id'
        ' WHERE tt.id = ?',
        (id,)
    ).fetchone()
    if tweet is None:
        abort(404, f"Tweet id {id} doesn't exist.")

    if check_author and tweet['author_id'] != g.user['id']:
        abort(403)

    return tweet

#update view
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id): # receives id 
    tweet = get_tweet(id)
    if tweet['tw_rdm'] == "random_hour":
        rdm_setting1 = "checked"
        rdm_setting2 = " "
        rdm_setting3 = " "
        rdm_setting4 = " "
    elif tweet['tw_rdm'] == "random_minute":
        rdm_setting1 = " "
        rdm_setting2 = "checked"
        rdm_setting3 = " "
        rdm_setting4 = " "
    elif tweet['tw_rdm'] == "random_hour_minute":
        rdm_setting1 = " "
        rdm_setting2 = " "
        rdm_setting3 = "checked"
        rdm_setting4 = " "
    else:
        rdm_setting1 = " "
        rdm_setting2 = " "
        rdm_setting3 = " "
        rdm_setting4 = "checked"

    if request.method == 'POST':
        tw_memo = request.form.get('tw_memo')
        tw_dow = request.form.get('tw_dow')
        tw_rdm =request.form.get('random_setting') 
        tw_time = request.form.get('tw_time')
        weather_condition = request.form.get('weather_condition')
        temp_condition = request.form.get('temp_condition')
        tweets=[""]*11
        for i in range(1,11):
            tweets[i] = request.form.get('tweet'+str(i))
        error = None
        if not tw_time:
            error = 'Tweet time is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tweet_table SET tw_memo = ?, tw_dow = ?, tw_rdm = ?, tw_time = ?, weather_condition = ?, temp_condition = ?, tweet1 = ?, tweet2 = ?, tweet3 = ?, tweet4 = ?, tweet5 = ?, tweet6 = ?, tweet7 = ?, tweet8 = ?, tweet9 = ?, tweet10 = ?'
                ' WHERE id = ?',
                (tw_memo, tw_dow, tw_rdm, tw_time, weather_condition, temp_condition, tweets[1], tweets[2], tweets[3], tweets[4], tweets[5], tweets[6], tweets[7], tweets[8], tweets[9], tweets[10], id)
            )
            db.commit()
            flash('Tweet is successfully edited.', category='alert alert-info')
            return redirect(url_for('tweet.index'))

    return render_template('tweet/update.html', tweet=tweet, rdm_setting1=rdm_setting1,rdm_setting2=rdm_setting2, rdm_setting3=rdm_setting3,rdm_setting4=rdm_setting4)

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/tweet/upload', methods=['GET','POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if request.form.get('sample_dl') == 'Sample file download':
            return redirect(url_for('tweet.download_file'))
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
            flash('Successfully uploaded .xlsx file!')
        else:
            flash('File is invalid, please upload Shibu_Tweet.xlsx!')
    return render_template('tweet/upload_file.html')


@bp.route('/tweet/upload/sample_dl')
def download_file():
    sample_file_name = "Shibu_Tweet.xlsx"
    return send_from_directory(current_app.config['SAMPLE_FOLDER'],sample_file_name)

#delete view
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM tweet_table WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('tweet.index'))

@bp.route('/tweet/delete_all', methods=('POST',))
@login_required
def delete_all():
    db = get_db()
    db.execute('DELETE FROM tweet_table')
    db.commit()
    return redirect(url_for('tweet.index'))

