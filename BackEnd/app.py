from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, jsonify
import plotly.express as px

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
    
class LiveTableDatas(db.Model):
    __tablename__ = 'livetabledatas'
    id = db.Column(db.Integer, primary_key=True)
    TempUnit = db.Column(db.String(80), nullable=False)
    Temperature = db.Column(db.Integer, nullable=False)
    CH4Factor = db.Column(db.Integer, nullable=False)
    AlloyFactor = db.Column(db.Integer,  nullable=False)
    H2 = db.Column(db.Integer,  nullable=False)

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

# Veritabanından toggle switch durumunu çeken yardımcı fonksiyon
def get_toggle_status():
    return LiveTableDatas.query.filter_by(id=1).first().TempUnit

@app.route('/abc')
def abc():
    all_data = LiveTableDatas.query.all()
    
    # Veritabanından toggle switch durumunu al
    toggle_status = get_toggle_status()
    return render_template('abc.html', all_data=all_data, toggle_status=toggle_status)

@app.route('/update_data', methods=['POST'])
def update_data():
    if request.method == 'POST':
        data = request.get_json()
        input_id = data.get('input_id')  # Bu, hangi input alanının güncelleneceğini belirlemek için kullanılabilir
        new_value = data.get('new_value')  # Numpad'den alınan yeni değer
        toggle_status = data.get('toggle_status')  # Toggle durumu
        
        print("input_id:",input_id)
        print("new_value:",new_value)
        
        # Burada ilgili input alanının güncellenmesi işlemini gerçekleştirin
        if input_id == 'input7':
            LiveTableDatas.query.filter_by(id=1).update({'Temperature': new_value})
            if toggle_status == 'C':
                LiveTableDatas.query.filter_by(id=1).update({'TempUnit': toggle_status})
            elif toggle_status == 'F':
                LiveTableDatas.query.filter_by(id=1).update({'TempUnit': toggle_status})
        elif input_id == 'input8':
            LiveTableDatas.query.filter_by(id=1).update({'CH4Factor': new_value})
        elif input_id == 'input9':
            LiveTableDatas.query.filter_by(id=1).update({'AlloyFactor': new_value})
        elif input_id == 'input10':
            LiveTableDatas.query.filter_by(id=1).update({'H2': new_value})

        db.session.commit()  # Değişiklikleri kaydet
        #return redirect(url_for('abc'))  # İlgili ana sayfaya yönlendirme
         # JSON formatında yanıt döndür
        return jsonify({'status': 'success', 'message': 'Data updated successfully'})

@app.route('/Chart')
def Chart():
    data = {'X': [1, 2, 3, 4, 5], 'Y': [10, 20, 25, 30, 35]}

    # Plotly ile çizim
    fig = px.line(data, x='X', y='Y', title='Sample Chart')

    # HTML olarak çıktıyı al
    plot_html = fig.to_html(full_html=False)

    return render_template('Chart.html', plot_html=plot_html)

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

def get_wifi_info():
    # Burada gerçek Wi-Fi bilgilerini alabilirsiniz
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

if __name__ == '__main__':
    app.run(debug=False)
