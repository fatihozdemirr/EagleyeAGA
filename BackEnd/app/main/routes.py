from .helpers import *
from . import main_bp

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
    return render_template('Chart.html', get_logged_in_user=get_logged_in_user)

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
        elif input_id == 'spannewvalue':
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
                        globalVars.CO_Referance = 10000
                        SensorReferanceValues.query.filter_by(id=1).update({'COReferance': globalVars.CO_Referance})
                    elif value_name == 'value2': 
                        calibration_type = 'RESET-%CO2'
                        globalVars.CO2_Referance = 10000
                        SensorReferanceValues.query.filter_by(id=1).update({'CO2Referance': globalVars.CO2_Referance})
                    elif value_name == 'value3':
                        calibration_type = 'RESET-%CH4'
                        globalVars.CH4_Referance = 10000
                        SensorReferanceValues.query.filter_by(id=1).update({'CH4Referance': globalVars.CH4_Referance})
                    db.session.commit() 
                    calibration_value = 10000
                    timestamp = datetime.now()
                    recent_logs = CalibrationLogs.query.filter_by(username=get_logged_in_user(), calibration_type=calibration_type).order_by(desc(CalibrationLogs.timestamp)).all()
                    
                    if len(recent_logs) >= MAX_LOGS_TO_KEEP:
                        logs_to_delete = recent_logs[MAX_LOGS_TO_KEEP - 1:]
                        for log in logs_to_delete:
                            db.session.delete(log)
                    
                    log_entry = CalibrationLogs(username=get_logged_in_user(), calibration_type=calibration_type, calibration_value=calibration_value, timestamp=timestamp)
                    db.session.add(log_entry)
                    db.session.commit()

            return jsonify({'status': 'success', 'message': 'Reset calibration is done'})
        
        if button_id in ['CObuttonspan', 'CO2buttonspan', 'CH4buttonspan']:
            smartGas.span_calibration_queries(button_id, True, float(conc_cal))
            calibration_type = f'SPAN-{button_id.replace("buttonspan", "")}'
            calibration_value = float(conc_cal)
            timestamp = datetime.now()
            # Veritabanından, bu kullanıcının ve belirli bir kalibrasyon tipinin loglarını tarih sırasına göre al
            recent_logs = CalibrationLogs.query.filter_by(username=get_logged_in_user(), calibration_type=calibration_type).order_by(desc(CalibrationLogs.timestamp)).all()
            
            # Eğer log sayısı MAX_LOGS_TO_KEEP'e ulaştıysa, en eski logları sil
            if len(recent_logs) >= MAX_LOGS_TO_KEEP:
                logs_to_delete = recent_logs[MAX_LOGS_TO_KEEP - 1:]
                for log in logs_to_delete:
                    db.session.delete(log)
            
            log_entry = CalibrationLogs(username=get_logged_in_user(), calibration_type=calibration_type, calibration_value=calibration_value, timestamp=timestamp)
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'{calibration_type} calibration is done'})
            
        if zero_start is not None and zero_start is True:
            smartGas.zero_calibration_queries(True)
            calibration_type = 'ZERO CO-CO2-CH4'
            calibration_value = 0.0  # Bu değeri isteğe bağlı olarak ayarlayabilirsiniz.
            timestamp = datetime.now()

            # Veritabanından, bu kullanıcının ve belirli bir kalibrasyon tipinin loglarını tarih sırasına göre al
            recent_logs = CalibrationLogs.query.filter_by(username=get_logged_in_user(), calibration_type=calibration_type).order_by(desc(CalibrationLogs.timestamp)).all()
            
            # Eğer log sayısı MAX_LOGS_TO_KEEP'e ulaştıysa, en eski logları sil
            if len(recent_logs) >= MAX_LOGS_TO_KEEP:
                logs_to_delete = recent_logs[MAX_LOGS_TO_KEEP - 1:]
                for log in logs_to_delete:
                    db.session.delete(log)
            
            log_entry = CalibrationLogs(username=get_logged_in_user(), calibration_type=calibration_type, calibration_value=calibration_value, timestamp=timestamp)
            db.session.add(log_entry)
            db.session.commit()
            # zero_alert = True
            # return redirect('/Calibration')
            return jsonify({'status': 'success', 'message': f'{calibration_type} calibration is done'})

        else:
            return jsonify({'status': 'error', 'message': 'Invalid data'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid method'})

def get_calibration_logs(limit=6):
    return CalibrationLogs.query.order_by(desc(CalibrationLogs.timestamp)).limit(limit).all()
    
@main_bp.route('/calibration_logs', methods=['GET'])
def calibration_logs():
    logs = get_calibration_logs() 
    return render_template('calibration_logs.html', logs=logs, get_logged_in_user=get_logged_in_user)

@main_bp.route('/show_calibration_logs', methods=['GET'])
def show_calibration_logs():
    return redirect(url_for('main.calibration_logs'))
    

##Operation 

@main_bp.route('/start_stop_recording', methods=['POST'])
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
    return render_template('history_chart.html',operation=operation, chartData = chartData, get_logged_in_user=get_logged_in_user)

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
    return render_template('operation_detail.html', operation=operation, get_logged_in_user=get_logged_in_user)

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
    if platform.system().lower() == "windows":
        result = subprocess.run(['ipconfig'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')  
        output = result.stdout
        print(output)
        if 'Wireless' in output or 'LAN adapter' in output:
            print('WindowsWifi')
            return 'Wi-Fi'
        elif 'Ethernet' in output or 'Ethernet Adapter' in output:
            print('Windowseth')
            return 'Ethernet'
        else:
            return 'Unknown'
    elif platform.system().lower() == "linux":
        result = subprocess.run(['iwconfig'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        output = result.stdout.lower()
        if 'wi-fi' in output:
            print('linuxWifi')
            return 'Wi-Fi'
        elif 'eth' in output or 'ethernet' in output:
            print('linuxeth')
            return 'Ethernet'
        else:
            return 'Unknown'
    else:
        return 'Unknown'

def get_wifi_info():
    connection_type = get_connection_type()

    if connection_type == 'Wi-Fi':
        if platform.system().lower() == "windows":
            result = subprocess.run(['netsh', 'interface', 'ip', 'show', 'config'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        elif platform.system().lower() == "linux":
            result = subprocess.run(['ifconfig'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        else:
            return {'ip': None, 'mask': None, 'gateway': None}

        output = result.stdout

        # Regex kullanarak IP, mask ve gateway bilgilerini çıkartma
        ip_pattern = re.compile(r'IPv4 Address[^\r\n:]+:\s*([^\s]+)')
        mask_pattern = re.compile(r'Subnet Mask[^\r\n:]+:\s*([^\s]+)')
        gateway_pattern = re.compile(r'Default Gateway[^\r\n:]+:\s*([^\s]+)')

        ip_match = ip_pattern.search(output)
        mask_match = mask_pattern.search(output)
        gateway_match = gateway_pattern.search(output)

        ip = ip_match.group(1) if ip_match else None
        mask = mask_match.group(1) if mask_match else None
        gateway = gateway_match.group(1) if gateway_match else None

        return {'ip': ip, 'mask': mask, 'gateway': gateway}

    elif connection_type == 'Ethernet':
        if platform.system().lower() == "windows":
            result = subprocess.run(['ipconfig'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        elif platform.system().lower() == "linux":
            result = subprocess.run(['ifconfig'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        else:
            return {'ip': None, 'mask': None, 'gateway': None}

        output = result.stdout

        # Regex kullanarak IP, mask ve gateway bilgilerini çıkartma
        ip_pattern = re.compile(r'IPv4 Address[^\r\n:]+:\s*([^\s]+)')
        mask_pattern = re.compile(r'Subnet Mask[^\r\n:]+:\s*([^\s]+)')
        gateway_pattern = re.compile(r'Default Gateway[^\r\n:]+:\s*([^\s]+)')

        ip_match = ip_pattern.search(output)
        mask_match = mask_pattern.search(output)
        gateway_match = gateway_pattern.search(output)

        ip = ip_match.group(1) if ip_match else None
        mask = mask_match.group(1) if mask_match else None
        gateway = gateway_match.group(1) if gateway_match else None

        return {'ip': ip, 'mask': mask, 'gateway': gateway}

    else:
        return {'ip': None, 'mask': None, 'gateway': None}

@main_bp.route('/connect_wifi', methods=['POST'])
def connect_wifi():
    selected_wifi = request.form.get('selected_wifi')
    wifi_password = request.form.get('wifi_password')

    connection_result = connect_to_wifi(selected_wifi, wifi_password)
    
    if connection_result['success']:
        flash('Connected to Wi-Fi: {}'.format(selected_wifi), 'success')
        session['connecting_wifi'] = False
    else:
        flash('Failed to connect to Wi-Fi: {}. Error: {}'.format(selected_wifi, connection_result['error']), 'danger')

    return redirect(url_for('main.wifi_info'))

def connect_to_wifi(ssid, password):
    if platform.system() == 'Windows':
        # Windows'ta bağlantı işlemleri
        result = subprocess.run(['netsh', 'wlan', 'connect', 'name="{}"'.format(ssid), 'keyMaterial="{}"'.format(password)], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        success = 'successfully' in result.stdout
        return {'success': success, 'error': result.stdout if not success else None}

    elif platform.system() == 'Linux':
        # Raspberry Pi'de bağlantı işlemleri
        # Bu bölümü gerekli komutlarla güncelleyin (örneğin: wpa_supplicant)
        # Bu işlem için gerekli izinlere sahip olmanız gerekebilir.
        # Bu örnekte wpa_supplicant komutu kullanılmıştır, ancak sisteminize bağlı olarak farklı olabilir.
        result = subprocess.run(['wpa_passphrase', ssid, password], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        config = result.stdout
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as file:
            file.write(config)
        subprocess.run(['wpa_cli', '-i', 'wlan0', 'reconfigure'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        return {'success': True, 'error': None}
    else:
        return {'success': False, 'error': 'Unsupported platform'}

@main_bp.route('/get_available_wifis', methods=['GET'])
def get_available_wifis():
    if platform.system() == 'Windows':
        result = subprocess.run(['netsh', 'wlan', 'show', 'network'], stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        wifi_pattern = re.compile(r'SSID [^\r\n:]+:\s*([^\s]+)')
        wifi_matches = wifi_pattern.findall(result.stdout)
        return jsonify({'wifis': wifi_matches})
    else:
        # Raspberry Pi üzerinde yapılacak işlemler
        result = subprocess.run(['iwlist', 'wlan0', 'scan'], stdout=subprocess.PIPE, text=True)
        output = result.stdout
        wifi_pattern = re.compile(r'ESSID:"(.*)"')
        wifi_matches = wifi_pattern.findall(output)
        return jsonify({'wifis': wifi_matches})

@main_bp.route('/wifi_info', methods=['GET', 'POST'])
def wifi_info():
    wifi_info = get_wifi_info()
    connecting_wifi = session.get('connecting_wifi', False)
    return render_template('wifi_info.html',wifi_info=wifi_info, get_logged_in_user=get_logged_in_user, connecting_wifi=connecting_wifi)

@main_bp.route('/Restart')
def Restart():
    return render_template('Restart.html', get_logged_in_user=get_logged_in_user)

@main_bp.route('/Shutdown')
def Shutdown():
    return render_template('Shutdown.html', get_logged_in_user=get_logged_in_user)

