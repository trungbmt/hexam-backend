from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import validators
from wtforms.fields.core import BooleanField, DateField, RadioField
from wtforms.fields.simple import FileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Địa chỉ email không hợp lệ!")])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Nhập lại mật khẩu không khớp!")])
    submit = SubmitField('Sign-Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    displayname = StringField('Họ và tên', validators=[DataRequired(), Length(min=5, max=50)])
    email = StringField('Địa chỉ email', validators=[DataRequired(), Email(message="Địa chỉ email không hợp lệ!")])
    picture = FileField('Ảnh đại diện', validators=[FileAllowed(['png', 'jpg', 'gif'], "Vui lòng chỉ chọn định dạng ảnh PNG hoặc JPG!")])
    phone = StringField('Số điện thoại', validators=[Length(min=9, max=12)])
    address = StringField('Địa chỉ', validators=[Length(min=5, max=128)])
    dob = StringField('Ngày sinh', validators=[DataRequired()])
    gender = RadioField('Giới tính', choices=[(1, 'Nam'), (2, 'Nữ'), (0, 'Khác')], validators=[DataRequired()])
    submit = SubmitField('Cập nhật')
