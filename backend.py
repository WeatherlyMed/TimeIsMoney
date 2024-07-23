from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    screen_time = db.Column(db.Float, default=0.0)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=150)])
    submit = SubmitField('Sign Up')

class ScreenTimeForm(FlaskForm):
    screen_time = FloatField('Screen Time (minutes)', validators=[DataRequired(), NumberRange(min=0)])
    screenshot = FileField('Screenshot', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Screen Time')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    form = ScreenTimeForm()
    return render_template('dashboard.html', users=users, form=form)

@app.route('/update_screen_time', methods=['POST'])
@login_required
def update_screen_time():
    form = ScreenTimeForm()
    if form.validate_on_submit():
        screenshot = form.screenshot.data
        filename = secure_filename(screenshot.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        screenshot.save(filepath)
        
        user = current_user
        user.screen_time += form.screen_time.data
        user.last_checked = datetime.utcnow()
        db.session.commit()
        
        flash('Screen time updated successfully!', 'success')
    else:
        flash('Failed to update screen time. Please try again.', 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
