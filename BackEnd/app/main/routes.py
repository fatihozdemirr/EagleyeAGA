from .helpers import *
from . import main_bp
from flask_socketio import emit

lock = threading.Lock()
logged_in = False

@main_bp.route('/')
def ana_sayfa():
    return redirect(url_for('main.login'))

@main_bp.route('/mainmenu')
def mainmenu():
    if not logged_in:
        return redirect(url_for('main.login'))  
    return render_template('mainmenu.html' ,get_logged_in_user=get_logged_in_user)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    all_users = User.query.all()
    form.username.choices = [(user.username) for user in all_users]
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['username'] = username
            global logged_in
            logged_in = True
            return redirect(url_for('main.mainmenu'))
        else:
            flash('Username or password is wrong!', 'danger')

    return render_template('login.html', form=form)


@main_bp.route('/Admin', methods=['get', 'post'])
def Admin():
    form = registrationform()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already in use!' , 'danger')
        else:
            new_user = User(username=username, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()
            # flash('Registration Successful! You can log in now.', 'success')
    # users = User.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = 4
    users = pagination = User.query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    operations = pagination.items
    return render_template('Admin.html', pagination=pagination, operations=operations, form=form, get_logged_in_user=get_logged_in_user, users=users)

@main_bp.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    user = User.query.get(user_id)

    if user:
        user.username = request.form['username']
        user.password = request.form['password']
        user.role = request.form['role']
        db.session.commit()

    return redirect(url_for('main.Admin'))

@main_bp.route("/delete_user/<int:user_id>", methods=['POST'])
# @login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.Admin'))

@main_bp.route('/AddNewUser/')
def AddNewUser():
    form = registrationform()
    return render_template('AddNewUser.html',form=form, get_logged_in_user=get_logged_in_user)

@main_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    global logged_in
    logged_in = False
    return redirect(url_for('main.login'))

##### MENU PAGE #####

@socketio.on('connect')
def test_connect():
    socketio.start_background_task(target=smartGas.update_ui, socketio=socketio)
    socketio.start_background_task(target=globalVars.update_ui, socketio=socketio)


def get_toggle_status():
    return LiveTableDatas.query.filter_by(id=1).first().TempUnit

def update_sensor_thread():
    if not smartGas.calibration_in_progress:
        smartGas.read_sensors()
        
def start_sensor_reading():
    sensor_thread = threading.Thread(target=update_sensor_thread)
    sensor_thread.start()

@main_bp.route('/livedata')
def livedata():
    all_data = LiveTableDatas.query.all()
    toggle_status = get_toggle_status()
    return render_template('livedata.html',  all_data=all_data, toggle_status=toggle_status, get_logged_in_user=get_logged_in_user)

@main_bp.route('/update_data', methods=['POST'])
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

@main_bp.route('/Chart')
def Chart():           
    labels = []
    co_data = []
    co2_data = []
    ch4_data = []
        
    if globalVars.StartedDate != "":          
        rows = dataLogger.get_data(globalVars.StartedDate, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for row in rows:
            labels.append(row['Datetime'])
            co_data.append(row['CO'])
            co2_data.append(row['CO2'])
            ch4_data.append(row['CH4'])
    else :
        rows = dataLogger.get_data_by_time_range(globalVars.TimeRangeMin)
        for row in rows:
            labels.append(row['Datetime'])
            co_data.append(row['CO'])
            co2_data.append(row['CO2'])
            ch4_data.append(row['CH4'])
            
    chartdata = {
        'labels': labels,
        'datasets': [
            {'label': 'CO', 'data': co_data},
            {'label': 'CO2', 'data': co2_data},
            {'label': 'CH4', 'data': ch4_data},
        ]}
    
    return render_template('ChartPlotly.html',chartData = chartdata, get_logged_in_user=get_logged_in_user)

@main_bp.route('/Calibration')
def Calibration():
    return render_template('Calibration.html', get_logged_in_user=get_logged_in_user)

last_conc_cal = None
MAX_LOGS_TO_KEEP = 6
@main_bp.route('/update_calibration_data', methods=['POST'])
def update_calibration_data():
    global last_conc_cal
    if request.method == 'POST':
        data = request.get_json()
        input_id = data.get('input_id')  
        new_value = data.get('new_value')  
        button_id = request.json.get('buttonId', None)
        zero_start = request.json.get('zerostart', None)
        reset_start = request.json.get('resetstart', None)
         
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
        elif input_id in ['spannewvalue1', 'spannewvalue2', 'spannewvalue3']:
            conc_cal = data.get('new_value') 
            
        last_conc_cal = conc_cal
        db.session.commit() 

        if reset_start:
            value1 = globalVars.CO_Referance
            value2 = globalVars.CO2_Referance
            value3 = globalVars.CH4_Referance
            
            range1 = { "min": 5000, "max": 15000 }     
            
            for value_name, value in [("value1", value1), ("value2", value2), ("value3", value3)]:
                if range1["min"] <= value <= range1["max"]:
                    print(f"{value_name} belirtilen aralık içinde.")
                else:
                    smartGas.Reset_Calibration(value_name)
                    if value_name == 'value1': 
                        calibration_type = 'RESET-%CO'
                        old_value = globalVars.CO_Referance
                        globalVars.CO_Referance = 10000
                        SensorReferanceValues.query.filter_by(id=1).update({'COReferance': globalVars.CO_Referance})
                    elif value_name == 'value2': 
                        calibration_type = 'RESET-%CO2'
                        old_value = globalVars.CO2_Referance
                        globalVars.CO2_Referance = 10000
                        SensorReferanceValues.query.filter_by(id=1).update({'CO2Referance': globalVars.CO2_Referance})
                    elif value_name == 'value3':
                        calibration_type = 'RESET-%CH4'
                        old_value = globalVars.CH4_Referance
                        globalVars.CH4_Referance = 10000
                        SensorReferanceValues.query.filter_by(id=1).update({'CH4Referance': globalVars.CH4_Referance})
                    
                    db.session.commit() 
                    calibration_value = 10000
                    timestamp = datetime.now()
                    username, _ = get_logged_in_user()
                    recent_logs = CalibrationLogs.query.filter_by(username=username, calibration_type=calibration_type).order_by(desc(CalibrationLogs.timestamp)).all()
                    
                    if len(recent_logs) >= MAX_LOGS_TO_KEEP:
                        logs_to_delete = recent_logs[MAX_LOGS_TO_KEEP - 1:]
                        for log in logs_to_delete:
                            db.session.delete(log)
                    
                    log_entry = CalibrationLogs(username=username, calibration_type=calibration_type, old_value=old_value, calibration_value=calibration_value, timestamp=timestamp)
                    db.session.add(log_entry)
                    db.session.commit()

            return jsonify({'status': 'success', 'message': 'Reset calibration is done'})
        
        if button_id in ['CObuttonspan', 'CO2buttonspan', 'CH4buttonspan']:
            smartGas.span_calibration_queries(button_id, True, float(conc_cal))
            calibration_type = f'SPAN-%{button_id.replace("buttonspan", "")}'
            calibration_value = float(conc_cal)
            timestamp = datetime.now()
            # formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            # print(timestamp)
            username, _ = get_logged_in_user()
            
            if button_id == 'CObuttonspan':
                old_value = globalVars.CO_Read
            elif button_id == 'CO2buttonspan':
                old_value = globalVars.CO2_Read
            elif button_id == 'CH4buttonspan':
                old_value = globalVars.CH4_Read
    
            recent_logs = CalibrationLogs.query.filter_by(username=username, calibration_type=calibration_type).order_by(desc(CalibrationLogs.timestamp)).all()
            
            # Eğer log sayısı MAX_LOGS_TO_KEEP'e ulaştıysa, en eski logları sil
            if len(recent_logs) >= MAX_LOGS_TO_KEEP:
                logs_to_delete = recent_logs[MAX_LOGS_TO_KEEP - 1:]
                for log in logs_to_delete:
                    db.session.delete(log)
            
            log_entry = CalibrationLogs(username=username, calibration_type=calibration_type, old_value=old_value, calibration_value=calibration_value, timestamp=timestamp)
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'{calibration_type} calibration is done'})
            
        if zero_start is not None and zero_start is True:
            smartGas.zero_calibration_queries(True)
            calibration_type = 'ZERO %CO|%CO2|%CH4'
            calibration_value = 0.0  
            timestamp = datetime.now()
            username, _ = get_logged_in_user()
            
            current_CO_Read = globalVars.CO_Read
            current_CO2_Read = globalVars.CO2_Read
            current_CH4_Read = globalVars.CH4_Read
    
            old_value = f"CO:{current_CO_Read}-CO2:{current_CO2_Read}-CH4:{current_CH4_Read}"
            
            # Veritabanından, bu kullanıcının ve belirli bir kalibrasyon tipinin loglarını tarih sırasına göre al
            recent_logs = CalibrationLogs.query.filter_by(username=username, calibration_type=calibration_type).order_by(desc(CalibrationLogs.timestamp)).all()
            
            # Eğer log sayısı MAX_LOGS_TO_KEEP'e ulaştıysa, en eski logları sil
            if len(recent_logs) >= MAX_LOGS_TO_KEEP:
                logs_to_delete = recent_logs[MAX_LOGS_TO_KEEP - 1:]
                for log in logs_to_delete:
                    db.session.delete(log)
            
            log_entry = CalibrationLogs(username=username, calibration_type=calibration_type, old_value=old_value, calibration_value=calibration_value, timestamp=timestamp)
            db.session.add(log_entry)
            db.session.commit()
            # zero_alert = True
            # return redirect('/Calibration')
            return jsonify({'status': 'success', 'message': f'{calibration_type} calibration is done'})

        else:
            return jsonify({'status': 'error', 'message': 'Invalid data'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid method'})

# def get_calibration_logs(limit=6):
#     return CalibrationLogs.query.order_by(desc(CalibrationLogs.timestamp)).limit(limit).all()
    
@main_bp.route('/calibration_logs', methods=['GET'])
def calibration_logs():
    # logs = get_calibration_logs() 
    page = request.args.get('page', 1, type=int)
    per_page = 6
    Log_tableform = pagination = CalibrationLogs.query.order_by(CalibrationLogs.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    return render_template('calibration_logs.html',pagination=pagination, logs=logs, get_logged_in_user=get_logged_in_user, Log_tableform=Log_tableform)

@main_bp.route('/show_calibration_logs', methods=['GET'])
def show_calibration_logs():
    return redirect(url_for('main.calibration_logs'))
    
##Operation 

@main_bp.route('/start_stop_recording', methods=['POST'])
def start_stop_recording():
    data = request.json
    hasRecorded = data.get('isRecording', 0)
    
    if hasRecorded:
        globalVars.StartedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        globalVars.update_app_parameters('StartedDate', globalVars.StartedDate)         
        dataLogger.start() 
        globalVars.OperationWorking = 1
        response = {"message": "Recording started successfully.", "status": "success"}
        status_code = 200
    else:
        globalVars.StartedDate = ""
        if not globalVars.DefaultRecording:
            dataLogger.stop()
            globalVars.OperationWorking = 0     
            response = {"message": "Recording stopped successfully.", "status": "success"}
            
        globalVars.update_app_parameters('StartedDate', "")    
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

@main_bp.route('/export_data/<int:operation_id>')
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

@main_bp.route('/history_chart/<int:operation_id>')
def history_chart(operation_id):   
    chartData = get_history_chart_data(operation_id)       
    operation = get_operation_by_id(operation_id)    
    return render_template('history_chart_plotly.html',operation=operation, chartData = chartData, get_logged_in_user=get_logged_in_user)

def get_operation_by_id(operation_id):
    operation = Operations.query.get(operation_id)
    return operation

@main_bp.route('/update_or_insert_operation', methods=['POST'])
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

@main_bp.route('/delete_operation/<int:operation_id>', methods=['POST'])
def delete_operation(operation_id):
    operation = Operations.query.get_or_404(operation_id)
    db.session.delete(operation)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Operation deleted successfully'})


@main_bp.route('/Operation')
def Operation():       
    page = request.args.get('page', 1, type=int)
    per_page = 6
    pagination = Operations.query.order_by(Operations.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    operations = pagination.items
    return render_template('Operation.html', operations=operations, pagination=pagination, get_logged_in_user=get_logged_in_user)


@main_bp.route('/operation/<int:operation_id>')
def operation_detail(operation_id):
    operation = get_operation_by_id(operation_id)
    
    return render_template('operation_detail.html', operation=operation, operationWorking=globalVars.OperationWorking, get_logged_in_user=get_logged_in_user)
    
@main_bp.route('/Setting')
def Setting():
    return render_template('Setting.html', get_logged_in_user=get_logged_in_user)

@main_bp.route('/Info')
def Info():
    return render_template('Info.html', get_logged_in_user=get_logged_in_user)


##### SETTING PAGE #####

@main_bp.route('/SetTime', methods=['GET','POST'])
def SetTime():
    timezones = [(tz, tz) for tz in pytz.all_timezones]
    username, _ = get_logged_in_user()
    user = User.query.filter_by(username=username).first()
    user_timezone = user.timezone if user else None
    return render_template('SetTime.html', timezones=timezones,user_timezone=user_timezone, get_logged_in_user=get_logged_in_user)

@main_bp.route('/update_timezone', methods=['POST'])
def update_timezone():
    utc_time = request.form.get('utcTime')
    timezone = request.form.get('timezone')

    datetime_utc = datetime.fromisoformat(utc_time[:-1])

    user_timezone = pytz.timezone(timezone)
    datetime_local = datetime_utc.replace(tzinfo=pytz.utc).astimezone(user_timezone)
    print('datetime_local:', datetime_local)
    
    timezone_str = str(timezone)
    
    username, _ = get_logged_in_user()

    if username:
        user = User.query.filter_by(username=username).first() 
        if user:
            user.timezone = timezone_str
            db.session.commit()
            return 'Başarıyla alındı'
        else:
            return 'Kullanıcı bulunamadı'
    else:
        return 'Kullanıcı adı bulunamadı'

@main_bp.route('/Ethernet/Wifi')
def EthernetWifi():
    return render_template('EthernetWifi.html', get_logged_in_user=get_logged_in_user)

def get_connection_type():
    if platform.system().lower() == "linux":
        result = subprocess.run(['ifconfig'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        output = result.stdout.lower()
        
        if 'wlan0' in output:
            return 'Wi-Fi'
        elif 'eth0' in output or 'ethernet' in output:
            return 'Ethernet'
    else:
        return 'Unknown'

def get_wifi_info():
    connection_type = get_connection_type()
    
    if connection_type == 'Wi-Fi':
        result = subprocess.run(['ifconfig', 'wlan0'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        output = result.stdout
        
        ip_pattern = re.compile(r'inet\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')
        mask_pattern = re.compile(r'netmask\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')
        gateway_pattern = re.compile(r'broadcast\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')
        
        ip_match = ip_pattern.search(output)
        mask_match = mask_pattern.search(output)
        gateway_match = gateway_pattern.search(output)

        ip = ip_match.group(1) if ip_match else None
        mask = mask_match.group(1) if mask_match else None
        gateway = gateway_match.group(1) if gateway_match else None

        return {'ip': ip, 'mask': mask, 'gateway': gateway}

    elif connection_type == 'Ethernet':
        if platform.system().lower() == "windows":
            # Windows'ta Ethernet bağlantı bilgileri alınamıyor.
            return {'ip': None, 'mask': None, 'gateway': None}
        elif platform.system().lower() == "linux":
            result = subprocess.run(['netstat', '-ie'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
            output = result.stdout.lower()
            ip_pattern = re.compile(r'inet\s+([^\s]+)\s+netmask\s+([^\s]+)\s+broadcast\s+([^\s]+)')
            ip_match = ip_pattern.search(output)
            ip = ip_match.group(1) if ip_match else None
            mask = ip_match.group(2) if ip_match else None
            gateway = ip_match.group(3) if ip_match else None
            print('ip:',ip)
            return {'ip': ip, 'mask': mask, 'gateway': gateway}

@main_bp.route('/connect_wifi', methods=['POST'])
def connect_wifi():
    selected_wifi = request.json.get('selected_wifi')
    wifi_password = request.json.get('wifi_password')

    connection_result = connect_to_wifi(selected_wifi, wifi_password)
    
    if connection_result[0]:  # Bağlantı başarılıysa
        return jsonify({'success': True, 'message': connection_result[1]}), 200
    else:  # Bağlantı başarısızsa
        return jsonify({'success': False, 'message': connection_result[1]}), 500
    
    # return redirect(url_for('main.wifi_info'))

def connect_to_wifi(ssid, password):
    try:
        print('ssid:', ssid)
        print('password:', password)
        # # wpa_supplicant.conf dosyasına yeni ağ bilgilerini ekleyin
        # subprocess.run(['sudo', 'sh', '-c', f'echo -e "\\nnetwork={{\\n\\tssid=\\"{ssid}\\"\\n\\tpsk=\\"{password}\\"\\n\\tkey_mgmt=WPA-PSK\\n}}" >> /etc/wpa_supplicant/wpa_supplicant.conf'], capture_output=True, text=True)

        # # Wi-Fi yapılandırmasını güncellemek için wpa_cli kullanın
        # subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'], capture_output=True, text=True)

        # # DHCP isteği gönder
        # subprocess.run(['sudo', 'dhclient', '-v', 'wlan0'], capture_output=True, text=True)

        return True, "Bağlantı başarıyla kuruldu."
    except Exception as e:
        return False, f"Bağlantı kurulurken bir hata oluştu: {str(e)}"
    
@main_bp.route('/disconnect_wifi', methods=['POST'])
def disconnect_wifi():
    result = subprocess.run(['sudo', 'iwconfig', 'wlan0'], capture_output=True, text=True)
    print('result.stdout:',result.stdout)
    if 'ESSID' in result.stdout:
        # Wi-Fi bağlıysa bağlantıyı kes
        result = subprocess.run(['sudo', 'ifconfig', 'wlan0', 'down'], capture_output=True, text=True)
        time.sleep(2)  # İşlem tamamlanması için bir süre bekle
        if result.returncode == 0:
            print('result.returncode:',result.returncode)
            return jsonify({'message': 'Wi-Fi bağlantısı başarıyla kesildi.'}), 200
        else:
            return jsonify({'message': 'Wi-Fi bağlantısı kesilirken bir hata oluştu.'}), 500
    else:
        return jsonify({'message': 'Bağlı bir Wi-Fi ağı bulunamadı.'}), 200

@main_bp.route('/get_available_wifis', methods=['GET'])
def get_available_wifis():
    result = subprocess.run(['iwgetid', 'wlan0'], stdout=subprocess.PIPE, text=True)
    connected_wifi = result.stdout.strip()
    
    result = subprocess.run(['iwlist', 'wlan0', 'scan'], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    wifi_pattern = re.compile(r'ESSID:"(.*)"')
    wifi_matches = wifi_pattern.findall(output)
    
    if connected_wifi in wifi_matches:
        wifi_matches.remove(connected_wifi)
        wifi_matches.insert(0, connected_wifi)
        
    return jsonify({'wifis': wifi_matches})

def get_wifi_signal_level():
    result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
    output = result.stdout

    signal_level_pattern = re.compile(r'Link Quality=(\d+)/(\d+)')
    match = signal_level_pattern.search(output)

    if match:
        signal_level = int(match.group(1))
        return signal_level
    else:
        return 0

@main_bp.route('/get_wifi_signal_strength', methods=['GET'])
def get_wifi_signal_strength():
    signal_level = get_wifi_signal_level()  
    signal_strength_percent = int((signal_level / 100) * 100)
    
    return jsonify({'signal_strength': signal_strength_percent})

@main_bp.route('/wifi_info', methods=['GET', 'POST'])
def wifi_info():
    wifi_info = get_wifi_info()
    connection_type = get_connection_type()
    connecting_wifi = session.get('connecting_wifi', False)
    return render_template('wifi_info.html',wifi_info=wifi_info,connection_type=connection_type, get_logged_in_user=get_logged_in_user, connecting_wifi=connecting_wifi)

def restart_pi():
    subprocess.run(["sudo", "reboot"])
    return redirect(url_for('main.mainmenu'))

@main_bp.route('/Restart')
def Restart():
    restart_pi()
    return "Raspberry Pi is Restart..."

def shutdown_pi():
    subprocess.run(["sudo", "shutdown", "-h", "now"])

@main_bp.route('/shutdown_pi_route')
def shutdown_pi_route():
    shutdown_pi()
    return "Raspberry Pi is shutting down..."


@main_bp.route('/ChartSettingParameter')
def ChartSettingParameter():
    default_recording = globalVars.DefaultRecording
    started_date = globalVars.StartedDate
    record_interval = globalVars.RecordInterval
    value_update_interval = globalVars.ValueUpdateInterval
    time_Range_Min = globalVars.TimeRangeMin
    
    return render_template('ChartSettingParameter.html',
                            default_recording=default_recording,
                            started_date=started_date,
                            record_interval=record_interval,
                            value_update_interval=value_update_interval,
                            time_Range_Min=time_Range_Min,
                            get_logged_in_user=get_logged_in_user)

@main_bp.route('/savevalues', methods=['POST'])
def save_values():
    data = request.get_json()
    default_recording = data.get('defaultrecording')
    record_interval = data.get('recordInterval')
    value_update_interval = data.get('valueupdateInterval')
    time_Range_Min = data.get('timeRangeMin')
    
    globalVars.update_app_parameters('DefaultRecording', default_recording)
    globalVars.update_app_parameters('RecordInterval', record_interval)
    globalVars.update_app_parameters('ValueUpdateInterval', value_update_interval)
    globalVars.update_app_parameters('TimeRangeMin', time_Range_Min)
    
    globalVars.DefaultRecording = int(default_recording)
    globalVars.RecordInterval = int(record_interval)
    globalVars.ValueUpdateInterval = int(value_update_interval)
    globalVars.TimeRangeMin = int(time_Range_Min)

    return jsonify({'status': 'success', 'message': 'Reset calibration is done'})

def get_row_size():
    id_size_bytes = 4
    datetime_size_bytes = 25
    real_size_bytes = 8
    row_size_bytes = id_size_bytes + datetime_size_bytes + 3 * real_size_bytes
    return row_size_bytes

def get_total_data_size():
    row_size_bytes = get_row_size()
    
    total_data = Datalogger.query.count()
    total_operation_data = Operations.query.count()
    
    total_data_size_bytes = total_data * row_size_bytes
    total_data_size_mb = total_data_size_bytes / (1024 * 1024)
    total_data_size_mb = round(total_data_size_mb, 2)
    
    total_operation_data_size_bytes = total_operation_data * row_size_bytes
    total_operation_data_size_mb = total_operation_data_size_bytes / (1024 * 1024)
    total_operation_data_size_mb = round(total_operation_data_size_mb, 2)
    
    return total_data_size_mb,total_data,total_operation_data,total_operation_data_size_mb

@main_bp.route('/system_info')
def system_info():
    total_data_size_mb,total_data,total_operation_data_size_mb,total_operation_data = get_total_data_size()
    # Disk bilgilerini al
    disk_usage = psutil.disk_usage('/')
    disk_total = disk_usage.total / (1024 ** 3)  
    disk_total = round(disk_total, 2)
    disk_used = disk_usage.used / (1024 ** 3)  
    disk_used = round(disk_used, 2)
    disk_space = disk_total - disk_used
    disk_space = round(disk_space, 2)
    disk_percent = disk_usage.percent

    # Uptime bilgisini al (saniye cinsinden)
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time()) - boot_time

    # Uptime'ı gün, saat ve dakika olarak hesaplayın
    uptime_days = uptime_seconds // (24 * 3600)
    uptime_hours = (uptime_seconds % (24 * 3600)) // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60

    # İnsan tarafından okunabilir bir formata dönüştürün
    uptime_human_readable = f"{uptime_days} gün, {uptime_hours} saat, {uptime_minutes} dakika"

    # Opsiyonel olarak saat ve dakikaları ayrı değişkenler olarak da saklayabilirsiniz
    hours = uptime_hours
    minutes = uptime_minutes

    print("Uptime (Saat):", hours)
    print("Uptime (Dakika):", minutes)
    
    # print("Cihaz Modeli:", model)

    # # Raspberry Pi model bilgisini al 
    # with open('/proc/cpuinfo', 'r') as file:
    #     for line in file:
    #         if line.startswith('Hardware'):
    #             hardware = line.split(':')[1].strip()
    #         elif line.startswith('Model'):
    #             model = line.split(':')[1].strip()
    
    return render_template('system_info.html',
                           total_operation_data_size_mb=total_operation_data_size_mb,
                           total_operation_data=total_operation_data,
                           total_data=total_data, 
                           total_data_size_mb=total_data_size_mb,
                           disk_total=disk_total,
                           disk_used=disk_used,
                           disk_space=disk_space,
                           disk_percent=disk_percent,
                           hours=hours,
                           minutes=minutes,
                        #    model=model,
                           get_logged_in_user=get_logged_in_user)

@main_bp.route('/deletehistory', methods=['POST'])
def deletehistory():
    try:
        data = request.get_json()
        historyDateTime_str =  data.get('historyDateTime')
        history_datetime = datetime.fromisoformat(historyDateTime_str)

        db.session.query(Datalogger).filter(Datalogger.Datetime < history_datetime).delete()
        db.session.query(CalibrationLogs).filter(CalibrationLogs.timestamp < history_datetime).delete()
        db.session.query(Operations).filter(Operations.stop_date < history_datetime).delete()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Geçmiş veriler başarıyla silindi.'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Veritabanı işlemleri sırasında bir hata oluştu. Lütfen tekrar deneyin.'}), 500



@main_bp.route('/company-furnace-relations')
def manage_company_furnace():
    companies = Company.query.all()
    selected_company_id = request.args.get('company_id')
    
    if selected_company_id:
        furnaces = Furnace.query.filter_by(company_id=selected_company_id).all()
    else:
        furnaces = Furnace.query.all()

    furnaces_serializable = [{'id': furnace.id, 'name': furnace.name, 'company_id': furnace.company_id} for furnace in furnaces]

    return render_template('company-furnace-relations.html', companies=companies, furnaces=furnaces_serializable, selected_company_id=selected_company_id, get_logged_in_user=get_logged_in_user)


#Company Add
@main_bp.route('/add_company', methods=['POST'])
def add_company():
    data = request.get_json()  # Gelen JSON verisini al
    if not data or 'companyName' not in data:
        return jsonify({'status': 'error', 'message': 'Company name is required'}), 400

    company_name = data['companyName'] 
    new_company = Company(name=company_name)
    db.session.add(new_company)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Company added successfully'}), 201

#Company Modify
@main_bp.route('/modify_company', methods=['POST'])
def modify_company():
    data = request.get_json()  # Gelen JSON verisini al

    if not data or 'companyName' not in data or 'companyId' not in data:
        return jsonify({'status': 'error', 'message': 'Company name and company ID are required'}), 400

    company_name = data['companyName']
    company_id = data['companyId']
    
    company = Company.query.filter_by(id=company_id).first()  # Örnek bir sorgu ile şirketi alıyoruz
    
    if company:  # Şirket varsa
        company.name = company_name  # Yeni adı atıyoruz
        db.session.commit()  # Değişiklikleri veritabanına kaydediyoruz
        return jsonify({'status': 'success', 'message': 'Company name updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Company not found'})

#Furnace Add
@main_bp.route('/add_furnace', methods=['POST'])
def add_furnace():
    data = request.get_json()  # Gelen JSON verisini al

    if not data or 'furnaceName' not in data or 'Id' not in data:
        return jsonify({'status': 'error', 'message': 'Furnace name and company ID are required'}), 400

    furnace_name = data['furnaceName']
    company_id = data['Id']

    new_furnace = Furnace(name=furnace_name, company_id=company_id)

    db.session.add(new_furnace)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Furnace added successfully'}), 201

#Furnace Modify
@main_bp.route('/modify_furnace', methods=['POST'])
def modify_furnace():
    data = request.get_json()  # Gelen JSON verisini al

    if not data or 'furnaceName' not in data or 'Id' not in data:
        return jsonify({'status': 'error', 'message': 'Furnace name and furnace ID are required'}), 400

    furnace_name = data['furnaceName']
    furnace_id = data['Id']
    
    furnace = Furnace.query.filter_by(id=furnace_id).first()  # Örnek bir sorgu ile şirketi alıyoruz
    
    if furnace:  # Şirket varsa
        furnace.name = furnace_name  # Yeni adı atıyoruz
        db.session.commit()  # Değişiklikleri veritabanına kaydediyoruz
        return jsonify({'status': 'success', 'message': 'Furnace name updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Furnace not found'})


#Furnace Delete
@main_bp.route('/delete_furnace/<int:furnaceid>', methods=['POST'])
def delete_furnace(furnaceid):
    furnace = Furnace.query.get_or_404(furnaceid)
    db.session.delete(furnace)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Furnace deleted successfully'})


#Company Delete
@main_bp.route('/delete_company/<int:companyid>', methods=['POST'])
def delete_company(companyid):
      
    furnaces = Furnace.query.filter_by(company_id=companyid).all()   
    for furnace in furnaces:
        db.session.delete(furnace)
        db.session.commit()
        
    company = Company.query.get_or_404(companyid)
    db.session.delete(company)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Company deleted successfully'})


@main_bp.route('/get_companies', methods=['GET'])
def get_companies():
    companies = [{'id': company.id, 'name': company.name} for company in Company.query.all()]
    return jsonify(companies)



@main_bp.route('/select_company', methods=['POST'])
def select_company():
    selected_company = request.json['company']
    # Seçilen şirketi işleyin, örneğin veritabanına kaydedebilirsiniz
    return jsonify({"message": "Company selected successfully"})


@main_bp.route('/get_furnaces', methods=['GET','POST'])
def get_furnaces():
    data = request.get_json() 
    selectedCompanyid = data['companyId']
    
    furnaces = [{'id': furnace.id, 'name': furnace.name} for furnace in Furnace.query.filter_by(company_id=selectedCompanyid).all() ]
    return jsonify(furnaces)



@main_bp.route('/select_furnace', methods=['POST'])
def select_furnace():
    selected_frunace = request.json['furnace']
    # Seçilen şirketi işleyin, örneğin veritabanına kaydedebilirsiniz
    return jsonify({"message": "Furnace selected successfully"})