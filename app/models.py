from datetime import datetime
from app import app,db,login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from hashlib import md5
from time import time

import jwt
#用于生成令牌


# 关联表
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin,db.Model):
    #db是从app中引入的，在app的__init__.py中，db是建立的一个SQLAlchemy类的对象
    #然而，此处又继承db中的Model类来创建了User类！
    #一个对象也有子类，如何解释？如何定义？
    id = db.Column(db.Integer, primary_key=True)
    # primary_key  主键
    username = db.Column(db.String(64), index=True, unique=True)
    # index=True 为这列创建索引，提升查询效率
    # unique=True 不允许出现重复的值
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    # 定义了一个用来表示用户和动态之间的高级视图的字段，此字段不是实际的数据库字段
    # relationship可用于定义这种“一对多”的关系，在“一”这边进行定义，被用作访问“多”的便捷方式
    # backref属性定义了代表“多”的类的实例反向调用“一”的时候的属性名称，即每条动态都有了一个属性author
    # lazy 定义了这个关系调用是如何执行的
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    followed = db.relationship(
        'User', 
        secondary=followers,
        #指定该关系的关联表
        primaryjoin=(followers.c.follower_id == id),
        #关联到左侧实体的条件
        secondaryjoin=(followers.c.followed_id == id),
        #关联到右侧实体的条件
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def avatar(self,size):
        digest=md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)

    def __repr__(self):
        return '<User {}>'.format(self.username)
        #直接打印对象名即可得到，返回某用户的用户名，一个类的__repr()__方法即返回指定的该对象的说明

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
            # fileter()方法比filter_by()方法更偏向底层，可以包含任意的过滤条件
            # filter_by()方法只能检查是否等于一个常量值
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        # = ？
        return followed.union(own).order_by(Post.timestamp.desc())
        #将被该用户关注者的动态和该用户自己的动态合并起来，做了一个联合查询
        # 使用数据库索引来查询，效率大大高于取出数据后再排序

    def get_reset_password_token(self,expirws_in=600):
        return jwt.encode(
            {'reset_password':self.id,'exp':time()+expirws_in},
            app.config['SECRET_KEY'],algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
    # 静态方法可以直接从类中调用，其与类方法的唯一区别在于它不用接受self作为第一个参数
        try:
            id=jwt.decode(token,app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return 
        return User.query.get(id)


class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.String(140))
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    # datetime.utcnow  世界时间
    # 传递的是函数本身，而不是调用它的结果，因此没有加入'()'
    # default  默认值
    # 将timestamp编入索引，将有利于按照时间顺序索引用户动态。
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #建立外键关系，本字段关联到用户表的id字段
    # 问题：如何通过'user.id'对应过去？
    # user是数据库表的名称？定义在何处呀？


    def __repr__(self):
        return '<Post {}>'.format(self.body)

#用户加载函数？
@login.user_loader
def load_user(id):
    return User.query.get(int(id))