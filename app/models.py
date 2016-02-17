from app import db
from hashlib import md5
from app import app
import re
from config import WHOOSH_ENABLED
import bleach
from markdown import markdown
from flask import url_for

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = WHOOSH_ENABLED
    import flask.ext.whooshalchemy as whooshalchemy

"""
Since this is an auxiliary table that has no data other than the foreign keys,
we use the lower level APIs in flask-sqlalchemy to create the table without
an associated model.
"""
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
replies = db.Table('replies',
    db.Column('reply_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'))
)

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (Permission.ADMINISTER |
                              Permission.FOLLOW |
                              Permission.COMMENT |
                              Permission.WRITE_ARTICLES |
                              Permission.MODERATE_COMMENTS, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=True, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String)
    email = db.Column(db.String(120), index=True, unique=False, nullable=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic', order_by = 'Post.timestamp.desc()')
    about_me = db.Column(db.Text)
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def avatar(self, size):
        if self.email and not 'defaultemail_' in self.email:
            return 'http://www.gravatar.com/avatar/%s?d=wavatar&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)
        else:
            return 'http://www.gravatar.com/avatar/%s?d=wavatar&s=%d' % (md5(self.username.encode('utf-8')).hexdigest(), size)
        return None

    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id))\
            .filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    # Here we just take the username and remove any characters that
    # are not letters, numbers, the dot or the underscore.
    @staticmethod
    def make_valid_username(username):
        return re.sub('[^a-zA-Z0-9_\.]', '', username)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     last_seen=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def to_json(self, avatarsize=50):
        json_user = {
            'url': url_for('user', username=self.username, _external=True),
            'username': self.username,
            'last_seen': self.last_seen,
            'avatar_url': self.avatar(avatarsize),
            'posts': url_for('get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % (self.username)

class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))
    comments = db.relationship('Comment', backref='post', lazy='dynamic', order_by = 'Comment.timestamp.desc()')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('post', id=self.id, _external=True),
            'title': self.title,
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"),
            'author': url_for('get_user', id=self.user_id,
                              _external=True),
            'comments': url_for('get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        return Post(body=body)

    def __repr__(self):
        return '<Post %r>' % (self.body)

db.event.listen(Post.body, 'set', Post.on_changed_body)

class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    disabled = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    replied = db.relationship('Comment',
                               secondary=replies,
                               primaryjoin=(replies.c.reply_id == id),
                               secondaryjoin=(replies.c.comment_id == id),
                               backref=db.backref('replies', lazy='dynamic'),
                               lazy='dynamic')

    def has_replied(self, comment):
        return self.replied.filter(replies.c.reply_id == comment.id).count() > 0

    def reply(self, comment):
        if not self.has_replied(comment):
            self.replied.append(comment)
            return self

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('get_comment', id=self.id, _external=True),
            'post': url_for('get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('get_user', id=self.user_id,
                              _external=True)
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

if enable_search:
    whooshalchemy.whoosh_index(app, Post)