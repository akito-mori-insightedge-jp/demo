import os
import pytest

os.environ['FLASK_DEBUG'] = '0'

from app import create_app, db, AttendanceRecord  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    os.environ['DATABASE_URL'] = f"sqlite:///{tmp_path/'test.db'}"
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client


def test_index_ok(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'\xe5\x8b\xa4\xe6\x80\xa0\xe3\x82\xa2\xe3\x83\x97\xe3\x83\xaa' in res.data  # 勤怠アプリ


def test_clock_in_and_out_flow(client):
    res = client.post('/clock-in', data={'employee_name': 'Taro'}, follow_redirects=True)
    assert res.status_code == 200

    res = client.get('/records?employee_name=Taro')
    assert b'Taro' in res.data
    assert AttendanceRecord.query.count() == 1
    rec = AttendanceRecord.query.first()
    assert rec.clock_in_at is not None
    assert rec.clock_out_at is None

    res = client.post('/clock-out', data={'employee_name': 'Taro'}, follow_redirects=True)
    assert res.status_code == 200
    rec = AttendanceRecord.query.first()
    assert rec.clock_out_at is not None

