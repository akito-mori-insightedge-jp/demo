import os
from datetime import datetime, date
from typing import Optional

from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


db = SQLAlchemy()


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False, index=True)
    work_date = db.Column(db.Date, nullable=False, index=True)
    clock_in_at = db.Column(db.DateTime, nullable=True)
    clock_out_at = db.Column(db.DateTime, nullable=True)

    def is_open(self) -> bool:
        return self.clock_in_at is not None and self.clock_out_at is None


def find_or_create_today_record(employee_name: str) -> AttendanceRecord:
    today = date.today()
    record: Optional[AttendanceRecord] = (
        AttendanceRecord.query
        .filter_by(employee_name=employee_name, work_date=today)
        .order_by(AttendanceRecord.id.desc())
        .first()
    )
    if record is None:
        record = AttendanceRecord(
            employee_name=employee_name,
            work_date=today,
        )
        db.session.add(record)
        db.session.commit()
    return record


def register_routes(app: Flask) -> None:
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/clock-in', methods=['POST'])
    def clock_in():
        employee_name = request.form.get('employee_name', '').strip()
        if not employee_name:
            flash('社員名を入力してください', 'error')
            return redirect(url_for('index'))

        record = find_or_create_today_record(employee_name)
        if record.clock_in_at is None:
            record.clock_in_at = datetime.utcnow()
            db.session.commit()
            flash(f'{employee_name} さんが出勤しました', 'success')
        else:
            flash('本日は既に出勤済みです', 'info')
        return redirect(url_for('index'))

    @app.route('/clock-out', methods=['POST'])
    def clock_out():
        employee_name = request.form.get('employee_name', '').strip()
        if not employee_name:
            flash('社員名を入力してください', 'error')
            return redirect(url_for('index'))

        record = find_or_create_today_record(employee_name)
        if record.clock_in_at is None:
            flash('出勤していません', 'error')
        elif record.clock_out_at is None:
            record.clock_out_at = datetime.utcnow()
            db.session.commit()
            flash(f'{employee_name} さんが退勤しました', 'success')
        else:
            flash('本日は既に退勤済みです', 'info')
        return redirect(url_for('index'))

    @app.route('/records', methods=['GET'])
    def records():
        employee_name = request.args.get('employee_name', '').strip()
        query = AttendanceRecord.query.order_by(
            AttendanceRecord.work_date.desc(), AttendanceRecord.id.desc()
        )
        if employee_name:
            query = query.filter_by(employee_name=employee_name)
        items = query.limit(200).all()
        return render_template('records.html', items=items, employee_name=employee_name)


app = create_app()


if __name__ == '__main__':
    debug_enabled = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug_enabled)

