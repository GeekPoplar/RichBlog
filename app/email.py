from flask_mail import Message
from app import app,mail
from flask import render_template
from threading import Thread

def send_async_email(app,msg):#为何要传递app，而不是直接使用上边导入的app呢？
    with app.app_context():
    # 通过创建此应用上下文，使得mail实例可以通过current_app来访问app的config(特别是给邮件系统配置的那几个)
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,args=(app,msg)).start()

def send_password_reset_email(user):
    token=user.get_reset_password_token()
    send_email('【渊博(RichBlog)重置密码】',
        sender=app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt',
        user=user,token=token),
        html_body=render_template('email/reset_password.html',
        user=user, token=token)
    )