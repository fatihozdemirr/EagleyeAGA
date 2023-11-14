from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Reel Bilgisayar/python/EagleyeAGA/BackEnd/users.db'
db = SQLAlchemy(app)
db.create_all()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)   
    password = db.Column(db.String(120), nullable=False)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class registrationform(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Admin')
    
logged_in = False

@app.route('/')
def ana_sayfa():
    if logged_in:
        return render_template('anasayfa.html')
    return redirect(url_for('login'))

@app.route('/anasayfa', methods=['GET', 'POST'])
def anasayfa():
    if logged_in:
        return render_template('anasayfa.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            global logged_in
            logged_in = True
            return render_template('anasayfa.html')
        else:
            flash('Username or password is wrong!', 'danger')

    return render_template('login.html', form=form)

@app.route('/Admin', methods=['get', 'post'])
def Admin():
    form = registrationform()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already in use!' , 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration Successful! You can log in now.', 'success')

    return render_template('Admin.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global logged_in
    logged_in = False
    return redirect(url_for('login'))


##### MENU PAGE #####

@app.route('/LıveData')
def LıveData():
    return render_template('LıveData.html')

@app.route('/Chart')
def Chart():
    return render_template('Chart.html')

@app.route('/Calibration')
def Calibration():
    return render_template('Calibration.html')

@app.route('/Operation')
def Operation():
    return render_template('Operation.html')

@app.route('/Setting')
def Setting():
    return render_template('Setting.html')

@app.route('/Info')
def Info():
    return render_template('Info.html')


##### SETTING PAGE #####

@app.route('/SetTime')
def SetTime():
    return render_template('SetTime.html')

@app.route('/Ethernet/Wifi')
def EthernetWifi():
    return render_template('EthernetWifi.html')

@app.route('/Restart')
def Restart():
    return render_template('Restart.html')

@app.route('/Shutdown')
def Shutdown():
    return render_template('Shutdown.html')

@app.route('/Logout')
def Logout():
    return render_template('Logout.html')



if __name__ == '__main__':
    app.run(debug=False)
