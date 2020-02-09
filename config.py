import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 密钥被定义成由or运算符连接两个项的表达式。
    # 第一个项查找环境变量SECRET_KEY的值，
    # 第二个项是一个硬编码的字符串。
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    #对SQLAlchemy库的一个环境变量进行配置，告诉其数据库文件所放置的位置
    #使用这种配置方式可以使得应用首先从环境中去获取环境变量，如果没获取到就使用默认值
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #不需要在数据库数据发生变动时发送信号给应用
    DEBUG=True

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.163.com'
    #服务器
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 994)
    #端口，163邮箱非SSL端口为25，SSL协议端口为465/994
    MAIL_USE_SSL=os.environ.get('MAIL_USE_SSL') or True
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or False
    #电子邮件服务器凭证，默认不使用
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '13540592967@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '123456cumt'

    ADMINS = ['13540592967@163.com']
    # 发件人

    POSTS_PER_PAGE=10 #一页显示的数量