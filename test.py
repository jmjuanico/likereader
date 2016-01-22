#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import unittest

from config import basedir
from app import app, db
from datetime import datetime, timedelta
from app.models import User, Post
from app.translate import microsoft_translate

from coverage import coverage
cov = coverage(branch=True, omit=['venv/*', 'tests.py'])
cov.start()

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_make_unique_username(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        username = User.make_unique_username('john')
        assert username != 'john'
        u = User(username=username, email='susan@example.com')
        db.session.add(u)
        db.session.commit()
        username2 = User.make_unique_username('john')
        assert username2 != 'john'
        assert username2 != username

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().username == 'susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().username == 'john'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='joey.juanico@traxtech.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body="post from john", author=u1, timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2, timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="post from mary", author=u3, timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4, timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)  # john follows himself
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u2)  # susan follows herself
        u2.follow(u3)  # susan follows mary
        u3.follow(u3)  # mary follows herself
        u3.follow(u4)  # mary follows david
        u4.follow(u4)  # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]

    def test_translation(self):
        # print microsoft_translate(u'English', 'en', 'es')
        # print type(microsoft_translate(u'Español', 'es', 'en'))
        # assert microsoft_translate(u'English', 'en', 'es') == u'Inglés'
        # assert microsoft_translate(u'Español', 'es', 'en') == u'Spanish'
        assert microsoft_translate(u'English', 'en', 'es') == 'Inglés'
        assert microsoft_translate(u'Español', 'es', 'en') == 'Spanish'

    def test_user(self):
        # make valid usernames
        n = User.make_valid_username('John_123')
        assert n == 'John_123'
        n = User.make_valid_username('John_[123]\n')
        assert n == 'John_123'
        # create a user
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        assert u.is_authenticated is True
        assert u.is_active is True
        assert u.is_anonymous is False
        assert u.id == int(u.get_id())

    def test_make_unique_username(self):
        # create a user and write it to the database
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        username = User.make_unique_username('susan')
        assert username == 'susan'
        username = User.make_unique_username('john')
        assert username != 'john'

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("HTML version: " + os.path.join(basedir, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()