from app import app,db
from flask import render_template

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
    #第二个返回参数是状态码，对于默认返回为200的不用设置此码

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
    #为确保失败的数据库会话不会干扰模板出发的其他数据库访问，此处将会话回滚使其被重置为干净的状态