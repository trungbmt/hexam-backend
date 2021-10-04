from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import FileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Tên tài khoản', validators=[DataRequired(), Length(min=5, max=32)])
    email = StringField('Địa chỉ email', validators=[DataRequired(), Email(message="Địa chỉ email không hợp lệ!")])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm_password = PasswordField('Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password', message="Nhập lại mật khẩu không khớp!")])
    submit = SubmitField('Đăng ký')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember = BooleanField('Lưu đăng nhập')
    submit = SubmitField('Đăng nhập')

class UpdateAccountForm(FlaskForm):
    username = StringField('Tên tài khoản', validators=[DataRequired(), Length(min=5, max=32)])
    picture = FileField('Ảnh đại diện', validators=[FileAllowed(['png', 'jpg'], "Vui lòng chỉ chọn định dạng ảnh PNG hoặc JPG!")])
    submit = SubmitField('Cập nhật')