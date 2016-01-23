# from flask.ext.mail import Message
from flask.ext.mail import Message
from app import mail
from app import app
from flask import render_template
from config import ADMINS

from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def follower_notification(followed, follower):
    send_email("[username] %s is now following you!" % follower.username,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.txt",
                               user=followed, follower=follower),
               render_template("follower_email.html",
                               user=followed, follower=follower))

def reply_notification(commentuser, replyuser, commenturl):
    send_email("[username] %s has replied to your comment!" % replyuser.username,
               ADMINS[0],
               [commentuser.email],
               render_template("reply_email.txt",
                               commentuser=commentuser, replyuser=replyuser, commenturl=commenturl),
               render_template("reply_email.html",
                               commentuser=commentuser, replyuser=replyuser, commenturl=commenturl))

def update_notification(user, confirm_update_url):
    send_email("You have requested a change of your password",
               ADMINS[0],
               [user.email],
               render_template("update_email.txt", user=user, confirm_update_url=confirm_update_url),
               render_template("update_email.html", user=user, confirm_update_url=confirm_update_url))