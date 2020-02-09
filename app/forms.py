from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
# 从WTForms包中导入了四个表示表单字段的类
from wtforms.validators import DataRequired,ValidationError,Email,EqualTo,Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    # validators:验证器
    # DateRequired:验证输入是否为空
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登录')
    # 每个字段类都接受一个描述或别名作为第一个参数，并生成一个实例来作为LoginForm的类属性

class RegistrationForm(FlaskForm):
    username=StringField('用户名',validators=[DataRequired()])
    email=StringField('邮箱',validators=[DataRequired(),Email()])
    password=PasswordField('密码',validators=[DataRequired()])
    password2=PasswordField('再输入一次密码',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('注册')

    def validate_username(self,username): 
        #WTForms将validate_<field_name>的方法作为自定义验证器，
        #并在已设置验证其之后调用它们，
        #异常中的参数将在对应字段旁边显示
        user=User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已经被使用啦，请换一个吧！')

    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已经被使用啦，请换一个吧！')
    
class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    about_me = TextAreaField('简介', validators=[Length(min=0, max=140)])
    submit = SubmitField('确认修改')
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # super()  调用父类的方法，此处不明为何
        self.original_username = original_username
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('该用户名已经被使用啦，请换一个吧！')
    
class PostForm(FlaskForm):
    post = TextAreaField('发点推送吧', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('发表')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('申请重置密码')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '请再输入一次密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('确认重置')