from server.app import app
import pytest
from fastapi.testclient import TestClient
from server.constant import MONGO_DETAILS
from pymongo import MongoClient
import datetime as dt
import pytz


client = TestClient(app)
clientMDB = MongoClient(MONGO_DETAILS)
database = clientMDB.delivery_service
couriers_collection = database.get_collection('couriers_collection')
orders_collection = database.get_collection('orders_collection')
basket_collection = database.get_collection('basket_collection')
assign_time = dt.datetime.now(tz=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
complete_time = (dt.datetime.now(tz=pytz.utc) + dt.timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')


def test_delete_all_data_from_db():
    couriers_collection.delete_many({})
    orders_collection.delete_many({})
    basket_collection.delete_many({})
    assert couriers_collection.count_documents({}) == 0
    assert orders_collection.count_documents({}) == 0
    assert basket_collection.count_documents({}) == 0

def test_insert_couriers():
    response = client.post('/couriers', data='''{
        "data": [
                        {
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, 12, 22],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                        },
                        {
                        "courier_id": 2,
                        "courier_type": "bike",
                        "regions": [22],
                        "working_hours": ["09:00-18:00"]
                        },
                        {
                        "courier_id": 3,
                        "courier_type": "car",
                        "regions": [12, 22, 23, 33],
                        "working_hours": []
                        }
                ]
        }''',)
    assert response.status_code == 201
    assert response.json() == {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}

def test_insert_bad_couriers():
    response = client.post('/couriers', data='''{
        "data": [
                        {
                        "courier_id": 1,
                        "courier_type": "foot",
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                        },
                        {
                        "courier_id": 2,
                        "regions": [22],
                        "working_hours": ["09:00-18:00"]
                        },
                        {
                        "courier_id": 3,
                        "courier_type": "car",
                        "regions": [12, 22, 23, 33],
                        "working_hours": [],
                        "tes": 1
                        }
                ]
        }''',)
    assert response.status_code == 400
    assert response.json() == {"validation_error": {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}}

def test_insert_orders():
    response = client.post('/orders', data='''{
                        "data": [
                        {
                        "order_id": 1,
                        "weight": 0.23,
                        "region": 12,
                        "delivery_hours": ["09:00-18:00"]
                        },
                        {
                        "order_id": 2,
                        "weight": 15,
                        "region": 1,
                        "delivery_hours": ["09:00-18:00"]
                        },
                        {
                        "order_id": 3,
                        "weight": 0.01,
                        "region": 22,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                        }
                        ]
        }''',)
    assert response.status_code == 201
    assert response.json() == {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]}


def test_insert_bad_orders():
    response = client.post('/orders', data='''{
                        "data": [
                        {
                        "order_id": 1,
                        "weight": 0.23,
                        "delivery_hours": ["09:00-18:00"]
                        },
                        {
                        "order_id": 2,
                        "region": 1,
                        "delivery_hours": ["09:00-18:00"]
                        },
                        {
                        "order_id": 3,
                        "weight": 0.01,
                        "region": 22,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"],
                        "test": 1
                        }
                        ]
        }''',)
    assert response.status_code == 400
    assert response.json() == {"validation_error": {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]}}

def time_format(dt):
    return "%s:%.3f%s" % (
        dt.strftime('%Y-%m-%dT%H:%M'),
        float("%.3f" % (dt.second + dt.microsecond / 1e6)),
        dt.strftime('%z')
    )

def test_assign_order():
    response = client.post('/orders/assign', data='''{
                        "courier_id": 1
        }''',)
    assert response.status_code == 200
    assert response.json() == {"orders": [{"id": 1}, {"id": 3} ], "assign_time": assign_time}

def test_compleate_order():
    response = client.post('/orders/complete', data='''{
                        "courier_id": 1,
                        "order_id": 3,
                        "complete_time":"''' + str(complete_time) + '''"}  ''',)
    assert response.status_code == 200
    assert response.json() == {"order_id": 3}

def test_get_courier():
    r = round((60*60-5*60)/(60*60)*5,2)
    response = client.get('/couriers/1')
    assert response.status_code == 200
    assert response.json() == {"courier_id": 1, "courier_type": "foot", "regions": [1, 12, 22], "working_hours": ["11:35-14:05", "09:00-11:00"], "rating": r, "earnings": 0  }

def test_get_courier2():
    response = client.get('/couriers/2')
    assert response.status_code == 200
    assert response.json() == {"courier_id": 2, "courier_type": "bike", "regions": [22], "working_hours": ["09:00-18:00"], "earnings": 0  }

def test_patch_courier():
    response = client.patch('/couriers/1', data='''{"regions": [100], "courier_type": "bike"}''')
    assert response.status_code == 200
    assert response.json() == {"courier_id": 1, "courier_type": "bike", "regions": [100], "working_hours": ["11:35-14:05", "09:00-11:00"]}


def test_delete_all_data_from_db_after():
    couriers_collection.delete_many({})
    orders_collection.delete_many({})
    basket_collection.delete_many({})
    assert couriers_collection.count_documents({}) == 0
    assert orders_collection.count_documents({}) == 0
    assert basket_collection.count_documents({}) == 0
