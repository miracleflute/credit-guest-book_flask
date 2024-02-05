from flask import Flask, render_template, request, redirect, url_for, Response, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time
import json
from common import config
import flask
from flask import session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


DB_NAME = "app.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwer123!@#'
app.config.from_object(config)


app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# set flask_admin
admin = Admin(app, name='admin_page', template_mode='bootstrap3')



from models import model
db = model.db
Name = model.Name
db.init_app(app)


bp = Blueprint('main', __name__)

font_size = 24
animation_duration = 30
max_length = 10

# 데이터 삭제 함수
def delete_old_data():
    current_time = datetime.now()
    # 1일 이전의 시간
    data_ago = current_time - timedelta(days=1)
    # 하루가 지난 데이터 삭제
    deleted_count = Name.query.filter(Name.created_date <= data_ago).delete()
    db.session.commit()
    return deleted_count

@bp.route('/kiosk', methods=['GET', 'POST'])
def kiosk():
    if request.method == 'POST':
        if 'name' not in request.form:
            return 'Name field is missing', 400
        name = request.form['name']
        new_name = Name(name=name)
        db.session.add(new_name)
        db.session.commit()
        return redirect(url_for('main.kiosk'))

    return render_template('kiosk.html')

@bp.route('/display')
def display():

    return render_template('display.html')

@bp.route('/events')
def sse():
    def event_stream():
        last_event_id = 0
        while True:
            with app.app_context():  # 애플리케이션 컨텍스트 설정
                delete_old_data()
                new_names = Name.query.filter(Name.id > last_event_id).order_by(Name.id.asc()).all()
                for name in new_names:
                    data = {'name': name.name}
                    yield f"data: {json.dumps(data)}\n\n"
                    last_event_id = name.id
            time.sleep(1)

    return Response(event_stream(), content_type='text/event-stream')


# /main/settings 라우트에서 설정 변경 시, 세션에 설정 값을 저장
@bp.route('/settings', methods=['POST', 'GET'])
def settings():
    global font_size, animation_duration, max_length

    if request.method == 'POST':
        font_size = int(request.form['font-size'])
        animation_duration = int(request.form['animation-duration'])
        max_length = int(request.form['max-length'])

        # 변경된 설정 값을 세션에 저장
        session['font_size'] = font_size
        session['animation_duration'] = animation_duration
        session['max_length'] = max_length

        flask.flash("Settings updated successfully.", "success")
        return redirect(url_for('main.settings'))
    
    # GET 요청에서 이전 설정 값을 세션에서 가져옴 (없으면 기본값 사용)
    font_size = session.get('font_size', 24)
    animation_duration = session.get('animation_duration', 30)
    max_length = session.get('max_length', 10)
    
    return render_template('setting.html', font_size=font_size, animation_duration=animation_duration, max_length=max_length)


@bp.route('/update_settings', methods=['POST'])
def update_settings():
    global font_size, animation_duration, max_length

    if request.method == 'POST':
        font_size = int(request.form['font-size'])
        animation_duration = int(request.form['animation-duration'])
        max_length = int(request.form['max-length'])
        # 설정을 저장하거나 디스플레이 페이지에 전달하는 추가 로직을 구현합니다.

        # 예시: 설정을 디스플레이 페이지에 전달하고 설정 페이지로 리디렉션합니다.
        flask.flash("Settings updated successfully.", "success")
        return redirect(url_for('main.settings'))

    return redirect(url_for('main.settings'))

@bp.route('/get_settings', methods=['GET'])
def get_settings():
    global font_size, animation_duration
    settings = {
        'font_size': font_size,
        'animation_duration': animation_duration,
        'max_length': max_length
    }
    return flask.jsonify(settings)

admin.add_view(ModelView(Name, db.session))

if __name__ == '__main__':
    with app.app_context():
        # DB 생성
        db.create_all()
    app.register_blueprint(bp, url_prefix='/main')
    app.run(debug=True)
