# 此处便是整个flask程序的入口，整个框架里，我们定义了一个app包
# 在app包里边，我们存放了程序运行需要的一些支持
# 此处导入app，即是运行app包内的__init__.py文件
from app import app,db
from app.models import User,Post


@app.shell_context_processor
def make_shell_context():
	return {'db':db,'User':User,'Post':Post}

