from flask import render_template, flash, redirect, url_for,request

from app import app,db  # 从app包导入其成员app变量

from app.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm

from flask_login import current_user,login_user,logout_user,login_required

from app.models import User,Post

from werkzeug.urls import url_parse

from datetime import datetime

from app.email import send_password_reset_email

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@login_required
def index():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(body=form.post.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('发布成功!')
        return redirect(url_for('index'))
    page=request.args.get('page',1,type=int)
    posts=current_user.followed_posts().paginate(page,app.config['POSTS_PER_PAGE'],False)
    # 第三个参数设为False，使得获取不到数据时返回为空，不报错
    next_url=url_for('index',page=posts.next_num) if posts.has_next else None
    prev_url=url_for('index',page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home',form=form,posts=posts.items,next_url=next_url,prev_url=prev_url)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # 执行form校验的工作,当浏览器发起GET请求的时候，它返回False
        # 当用户在浏览器点击提交按钮后，浏览器会发送POST请求。
        # form.validate_on_submit()就会获取到所有的数据，
        # 运行字段各自的验证器，全部通过之后就会返回True，这表示数据有效。
        user =User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误！')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        #将用户实例user赋给了flask_login类的current_user属性
        next_page=request.args.get('login')
        if not next_page or url_parse(next_page).netloc !='':
            #用Werkzeug的url_parse()函数来解析url，然后检查其netloc属性（服务器地址）
            #是否被设置，若被设置了则返回home页，放置被重定向到一个指向恶意站点的url
            next_page=url_for('index')
        return redirect(next_page)
        # 重定向
    return render_template('login.html', title='Sigh In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功啦!')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/user/<username>')
#<>号中接受任何文本，并将其赋给username
@login_required
def user(username):
    user=User.query.filter_by(username=username).first_or_404()#若无，则发送404给终端
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@app.before_request #注册在视图函数之前执行的函数
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('修改成功！')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET': #也就是刚打开时用的请求方式
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能关注你自己!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('你已成功关注 {}!'.format(username))
    return redirect(url_for('user', username=username))
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能取关你自己!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('你已成功取关 {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page=request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page,app.config['POSTS_PER_PAGE'],False)
    next_url=url_for('index',page=posts.next_num) if posts.has_next else None
    prev_url=url_for('index',page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,next_url=next_url,prev_url=prev_url)

@app.route('/reset_password_request',methods=['POST','GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=ResetPasswordRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('请查看你的邮箱来进行接下来的操作（若是没收到，请检查以下垃圾箱哦）')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',title='Reset Password',form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    # 验证令牌是否有效
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('密码重置成功')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    p=Post.query.get(post_id)
    if current_user.is_authenticated:
        db.session.delete(p)
        db.session.commit()
        return redirect(url_for('user',username=p.author.username))