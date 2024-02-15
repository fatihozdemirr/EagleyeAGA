from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask import Flask, jsonify
import smartGas
import threading 
from threading import Thread
import time
from flask_socketio import SocketIO
from GlobalVars import globalVars
from Datalogger import dataLogger
import os
from datetime import datetime
from excel_operations import create_excel_file
from Models import db, User, LiveTableDatas, CalibrationTableDatas, Operations
from FlaskForms import LoginForm, registrationform

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.secret_key = 'mysecretkey'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + globalVars.DatabasePath 
db.init_app(app)

with app.app_context():
    db.create_all()

lock = threading.Lock()
logged_in = False

def background_thread():
    while True:
        time.sleep(1)
        socketio.emit('chart_sensor_data', {
            'time': time.strftime('%H:%M:%S'),
            'valueCO': globalVars.CO_Read + globalVars.CO_Offset,
            'valueCO2': globalVars.CO2_Read + globalVars.CO2_Offset,
            'valueCH4': globalVars.CH4_Read + globalVars.CH4_Offset,
        })

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
        zero_start = request.json.get('zerostart', None)
         
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
            
        last_conc_cal = conc_cal
        db.session.commit() 
        
        if button_id in ['CObuttonspan', 'CO2buttonspan', 'CH4buttonspan']:
            smartGas.span_calibration_queries(button_id, True, float(conc_cal))
            
        if zero_start is not None and zero_start is True:
            smartGas.zero_calibration_queries(True)
            zero_alert = True
            print('zero_alert:',zero_alert)
            return redirect('/Calibration')
        else:
            return jsonify({'status': 'error', 'message': 'Invalid data'})
        
    else:
        return jsonify({'status': 'error', 'message': 'Invalid method'})

##Operation 

@app.route('/start_stop_recording', methods=['POST'])
def start_stop_recording():
    data = request.json
    globalVars.isRecording = data.get('isRecording', 0)
    if globalVars.isRecording:
        dataLogger.start()
        response = {"message": "Recording started successfully.", "status": "success"}
        status_code = 200
    else:
        dataLogger.stop()
        response = {"message": "Recording stopped successfully.", "status": "success"}
        status_code = 200
    
    return jsonify(response), status_code

def get_history_chart_data(operationId):
    operation = get_operation_by_id(operationId)  # Bu fonksiyonun tanımını sağlamanız gerekir
    start_date = operation.start_date.strftime('%Y-%m-%d %H:%M:%S')
    stop_date = operation.stop_date.strftime('%Y-%m-%d %H:%M:%S')

    rows = dataLogger.get_data(start_date, stop_date)
    labels = []
    co_data = []
    co2_data = []
    ch4_data = []
    
    for row in rows:
        labels.append(datetime.strptime(row['Datetime'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))
        co_data.append(row['CO'])
        co2_data.append(row['CO2'])
        ch4_data.append(row['CH4'])
    
    chart_data = {
        'labels': labels,
        'datasets': [
            {'label': 'CO', 'data': co_data},
            {'label': 'CO2', 'data': co2_data},
            {'label': 'CH4', 'data': ch4_data},
        ],
        'name': operation.name,
        'company': operation.company,
        'furnace': operation.furnace,
        'operator': operation.operator,
        'start_date': operation.start_date,
        'stop_date': operation.stop_date
    }
    
    return chart_data

@app.route('/export_data/<int:operation_id>')
def export_data(operation_id):
    # Veritabanından belirli tarih aralığındaki verileri seçin
    operation = get_operation_by_id(operation_id)
    start_date = operation.start_date.strftime('%Y-%m-%d %H:%M:%S')
    stop_date = operation.stop_date.strftime('%Y-%m-%d %H:%M:%S')
    rows = dataLogger.get_data(start_date, stop_date)

    # Veriyi Excel dosyasına yazın
    excel_file = create_excel_file(rows)

    # Excel dosyasını istemciye gönderin
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='ExportedData.xlsx',
        as_attachment=True
    )

@app.route('/history_chart/<int:operation_id>')
def history_chart(operation_id):   
    chartData = get_history_chart_data(operation_id)       
    operation = get_operation_by_id(operation_id)    
    return render_template('history_chart.html',operation=operation, chartData = chartData)

def get_operation_by_id(operation_id):
    operation = Operations.query.get(operation_id)
    return operation

@app.route('/update_or_insert_operation', methods=['POST'])
def update_or_insert_operation():
    data = request.json
    operation_id = data.get('id')
    status = 'success'  # Başlangıç durumu başarılı olarak ayarla

    try:
        if operation_id:
            operation = Operations.query.get(operation_id)
            if operation:
                # Operasyon güncelleme
                operation.name = data.get('name', operation.name)
                operation.company = data.get('company', operation.company)
                operation.furnace = data.get('furnace', operation.furnace)
                operation.operator = data.get('operator', operation.operator)
                if data.get('start_date'):
                    operation.start_date = datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M:%S')
                if data.get('stop_date'):
                    operation.stop_date = datetime.strptime(data['stop_date'], '%Y-%m-%dT%H:%M:%S')
                message = 'Operation updated successfully'
            else:
                # ID var ama operasyon bulunamadı, hata döndür
                return jsonify({'status': 'error', 'message': 'Operation not found'}), 404
        else:
            # Yeni operasyon ekleme
            new_operation = Operations(
                name=data['name'],
                company=data.get('company', ''),
                furnace=data.get('furnace', ''),
                operator=data.get('operator', ''),
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M:%S') if data.get('start_date') else None,
                stop_date=datetime.strptime(data['stop_date'], '%Y-%m-%dT%H:%M:%S') if data.get('stop_date') else None
            )
            db.session.add(new_operation)
            db.session.flush()  # ID'yi alabilmek için flush kullanılır
            operation_id = new_operation.id  # Yeni eklenen operasyonun ID'sini al
            message = 'Operation added successfully'
        
        db.session.commit()
        return jsonify({'status': status, 'message': message, 'operation_id': operation_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_operation/<int:operation_id>', methods=['POST'])
def delete_operation(operation_id):
    operation = Operations.query.get_or_404(operation_id)
    db.session.delete(operation)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Operation deleted successfully'})


@app.route('/Operation')
def Operation():       
    page = request.args.get('page', 1, type=int)
    per_page = 6
    pagination = Operations.query.order_by(Operations.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    operations = pagination.items
    return render_template('Operation.html', operations=operations, pagination=pagination)


@app.route('/operation/<int:operation_id>')
def operation_detail(operation_id):
    operation = get_operation_by_id(operation_id)
    return render_template('operation_detail.html', operation=operation)

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
    port = 5000
    kill_process_on_port(port)
    start_sensor_reading()
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    # dataLogger.start()
    app.run(debug=False, host ='0.0.0.0')
            
    
