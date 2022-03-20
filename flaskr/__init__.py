import os
from flask import Flask
from flask_mail import Mail
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    mail = Mail()
    app.config.from_mapping(
        SECRET_KEY = os.getenv("SECRET_KEY"),
        DATABASE = os.path.join(app.instance_path,'flaskr.sqlite3'),
        )
    #for file uploading feature
    app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
    app.config['SAMPLE_FOLDER'] = os.getenv("SAMPLE_FOLDER")
    app.config['ALLOWED_EXTENSIONS'] = os.getenv("ALLOWED_EXTENSIONS")
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000
    #for flask_mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import top
    app.register_blueprint(top.bp)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import tweet
    app.register_blueprint(tweet.bp)
    app.add_url_rule('/',endpoint='index')

    return app
