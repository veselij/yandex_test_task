import motor.motor_asyncio
import asyncio
import pymongo
from server.constant import MONGO_DETAILS
from fastapi.encoders import jsonable_encoder
import datetime as dt
import pytz


client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.delivery_service

couriers_collection = database.get_collection('couriers_collection')
couriers_collection.create_index('courier_id', unique=True)

async def add_courier(courier_data: dict) -> int:
    try:
        courier = await couriers_collection.insert_one(courier_data)
    except asyncio.CancelledError:
        raise
    except pymongo.errors.DuplicateKeyError:
        pass
    return courier_data['courier_id']

orders_collection = database.get_collection('orders_collection')
orders_collection.create_index('order_id', unique=True)

async def add_order(order_data: dict) -> int:
    try:
        order = await orders_collection.insert_one(order_data)
    except asyncio.CancelledError:
        raise
    except pymongo.errors.DuplicateKeyError:
        pass
    return order_data['order_id']

async def retrieve_courier(id:int ) -> dict:
    courier = await couriers_collection.find_one({'courier_id': id})
    if courier:
        return courier

async def retrieve_orders(max_weight: float, regions: list) -> list:
    orders = orders_collection.find({'region': {'$in': regions}, 'weight': {'$lte': max_weight}, 'assign_time': None}, sort=[('weight', pymongo.DESCENDING )])
    return orders

async def update_order(ids, courier_id):
    assign_time = dt.datetime.now(tz=pytz.timezone('Europe/Moscow')).isoformat()
    order = orders_collection.update_many({'order_id': {'$in': ids}}, {'$set': {'assign_time': assign_time, 'courier_id': courier_id}})
    return assign_time


