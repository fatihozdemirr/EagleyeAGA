from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, jsonify
from smartGas import app, db
import smartGas
import threading 
from threading import Thread
import time
from flask_socketio import SocketIO
from GlobalVars import globalVars
from Datalogger import dataLogger
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

app.secret_key = 'mysecretkey'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + globalVars.DatabasePath 
db = SQLAlchemy(app)
db.create_all()

lock = threading.Lock()

def background_thread():
    while True:
        time.sleep(0.5)
        socketio.emit('chart_sensor_data', {
            'time': time.strftime('%H:%M:%S'),
            'valueCO': globalVars.CO_Result,
            'valueCO2': globalVars.CO2_Result,
            'valueCH4': globalVars.CH4_Result,
        })

        
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)   
    password = db.Column(db.String(120), nullable=False)
    
class LiveTableDatas(db.Model):
    __tablename__ = 'livetabledatas'
    id = db.Column(db.Integer, primary_key=True)
    TempUnit = db.Column(db.String(80), nullable=False)
    Temperature = db.Column(db.Integer, nullable=False)
    CH4Factor = db.Column(db.Integer, nullable=False)
    AlloyFactor = db.Column(db.Integer,  nullable=False)
    H2 = db.Column(db.Integer,  nullable=False)
    
class CalibrationTableDatas(db.Model):
    __tablename__ = 'calibration'
    id = db.Column(db.Integer, primary_key=True)
    GAS = db.Column(db.String, nullable=False)
    OFFSET = db.Column(db.Float, nullable=False)
    READING = db.Column(db.Float, nullable=False)
    VALUE = db.Column(db.Float,  nullable=False)

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
    # if logged_in:
    #     return render_template('mainmenu.html')
    return redirect(url_for('login'))

@app.route('/mainmenu')
def mainmenu():
    if not logged_in:
        return redirect(url_for('login'))  # Kullanıcı giriş yapmadıysa login sayfasına yönlendir
    return render_template('mainmenu.html')

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
            return redirect(url_for('mainmenu'))
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

@socketio.on('connect')
def test_connect():
    socketio.start_background_task(target=smartGas.update_ui, socketio=socketio)

# Veritabanından toggle switch durumunu çeken yardımcı fonksiyon
def get_toggle_status():
    return LiveTableDatas.query.filter_by(id=1).first().TempUnit

def update_sensor_thread():
    if not smartGas.calibration_in_progress:
        smartGas.read_sensors()
        
def start_sensor_reading():
    sensor_thread = threading.Thread(target=update_sensor_thread)
    sensor_thread.start()

@app.route('/livedata')
def livedata():
    all_data = LiveTableDatas.query.all()
    toggle_status = get_toggle_status()
    return render_template('livedata.html',  all_data=all_data, toggle_status=toggle_status)

@app.route('/update_data', methods=['POST'])
def update_data():
    if request.method == 'POST':
        data = request.get_json()
        input_id = data.get('input_id')  
        new_value = data.get('new_value')  
        toggle_status = data.get('toggle_status') 
        
        if input_id == 'input7':
            LiveTableDatas.query.filter_by(id=1).update({'Temperature': new_value})
            globalVars.temp = float(new_value)
            if toggle_status == 'C':
                LiveTableDatas.query.filter_by(id=1).update({'TempUnit': toggle_status})
            elif toggle_status == 'F':
                LiveTableDatas.query.filter_by(id=1).update({'TempUnit': toggle_status})
        elif input_id == 'input8':
            LiveTableDatas.query.filter_by(id=1).update({'CH4Factor': new_value})
            globalVars.ch4factor = float(new_value)
        elif input_id == 'input9':
            LiveTableDatas.query.filter_by(id=1).update({'AlloyFactor': new_value})
            globalVars.alloyfactor = float(new_value)
        elif input_id == 'input10':
            LiveTableDatas.query.filter_by(id=1).update({'H2': new_value})
            globalVars.h2 = float(new_value)

        db.session.commit()  
        return jsonify({'status': 'success', 'message': 'Data updated successfully'})

@app.route('/Chart')
def Chart():
    return render_template('Chart.html')

@app.route('/Calibration')
def Calibration():  
    return render_template('Calibration.html')

last_conc_cal = None
@app.route('/update_calibration_data', methods=['POST'])
def update_calibration_data():
    global last_conc_cal
    if request.method == 'POST':
        data = request.get_json()
        input_id = data.get('input_id')  
        new_value = data.get('new_value')  
        button_id = request.json.get('buttonId', None)
        
        conc_cal = last_conc_cal    
        if input_id == 'CO_inputoffset':
            CalibrationTableDatas.query.filter_by(id=1).update({'OFFSET': new_value})
            globalVars.CO_Offset = float(new_value)
        elif input_id == 'CO2_inputoffset':
            CalibrationTableDatas.query.filter_by(id=2).update({'OFFSET': new_value})
            globalVars.CO2_Offset = float(new_value)
        elif input_id == 'CH4_inputoffset':
            CalibrationTableDatas.query.filter_by(id=3).update({'OFFSET': new_value})
            globalVars.CH4_Offset = float(new_value)
        elif input_id == 'spannewvalue':
            conc_cal = data.get('new_value') 
            # smartGas.update_conc_cal(conc_cal)
        last_conc_cal = conc_cal
        
        if button_id in ['CObuttonspan', 'CO2buttonspan', 'CH4buttonspan']:
            smartGas.span_calibration_queries(button_id, True, float(conc_cal))
       
        db.session.commit()  
        return jsonify({'status': 'success', 'message': 'Data updated successfully'})

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

def get_wifi_info():
    wifi_info = {
        'SSID': 'MyWiFiNetwork',
        'Password': 'MyPassword',
        'SignalStrength': 'Excellent'
    }
    return wifi_info

@app.route('/wifi_info', methods=['GET', 'POST'])
def wifi_info():
    if request.method == 'POST':
        wifi_info = get_wifi_info()
        return render_template('wifi_info.html', wifi_info=wifi_info)
    return render_template('wifi_info.html')

@app.route('/Restart')
def Restart():
    return render_template('Restart.html')

@app.route('/Shutdown')
def Shutdown():
    return render_template('Shutdown.html')

def kill_process_on_port(port):
    command = f"lsof -t -i:{port}"
    pid = os.popen(command).read().strip()
    if pid:
        print(f"Port {port} üzerinde çalışan süreç PID: {pid}, sonlandırılıyor...")
        os.system(f"kill -9 {pid}")
    else:
        print(f"Port {port} boş.")
        
if __name__ == '__main__':
    #port = 5000
    #kill_process_on_port(port)
    start_sensor_reading()
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    dataLogger.start()
    
    app.run(debug=False, host ='0.0.0.0')
            
    
