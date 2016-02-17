
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from flask.ext.mail import Mail
from momentjs import momentjs
from flask.ext.babel import Babel, lazy_gettext
from flask.ext.bcrypt import Bcrypt
from flask.ext.mobility import Mobility

app = Flask(__name__)
Mobility(app)
bcrypt = Bcrypt(app)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'index'
lm.login_message = lazy_gettext('Please log in to access this page.')
oid = OpenID(app, os.path.join(basedir, 'tmp'))
mail = Mail(app)
babel = Babel(app)

from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

# will send email in case of errors
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER
                               , ADMINS[0], 'microblog failure'
                               , credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# logs into a file
if not app.debug and os.environ.get('HEROKU') is None:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')

# logs into stdout which heroku will pickup
if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')

# initiliazes primary data and views
app.jinja_env.globals['momentjs'] = momentjs
from app import views, models, posts, users, comments, angular

# make sure admin account is setup
from models import User, Role, Permission

"""
@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)
"""
# will throw an error if database or the table doesnt exist yet
try:
    # initialize roles
    Role.insert_roles()

    # add admin if not yet added
    admin_email = ADMINS[0]
    # this returns result object
    admin_user = User.query.filter_by(email=admin_email).first()
    # this returns object values
    admin_role = db.session.query(Role).filter(Role.permissions==Permission.ADMINISTER).first()

    if not admin_user:
        defaultpassword = bcrypt.generate_password_hash('1234')
        user = User(username='admin', email=admin_email, role=admin_role, password = defaultpassword)
        db.session.add(user)
        db.session.commit()

        # follow yourself
        db.session.add(user.follow(user))
        db.session.commit()
except:
    pass