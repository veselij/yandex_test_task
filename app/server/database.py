import motor.motor_asyncio
import asyncio
import pymongo
from server.constant import MONGO_DETAILS
from fastapi.encoders import jsonable_encoder
import datetime as dt
import pytz
from bson.objectid import ObjectId


client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.delivery_service

couriers_collection = database.get_collection('couriers_collection')
couriers_collection.create_index('courier_id', unique=True)
orders_collection = database.get_collection('orders_collection')
orders_collection.create_index('order_id', unique=True)
basket_collection = database.get_collection('basket_collection')
basket_collection.create_index([('courier_id', pymongo.ASCENDING), ('basket_status', pymongo.ASCENDING)])

async def add_obect(object_data: list, collection):
    ids = []
    for data in object_data:
        data = jsonable_encoder(data)
        try:
            obj = await collection.insert_one(data)
        except asyncio.CancelledError:
            raise
        except pymongo.errors.DuplicateKeyError:
            pass
        if obj:
            ids.append(data)
    return ids

async def retrieve_courier(id:int ) -> dict:
    courier = await couriers_collection.find_one({'courier_id': id})
    if courier:
        return courier

async def retrieve_order(id:int, cid: int ) -> dict:
    courier = await orders_collection.find_one({'order_id': id, 'courier_id': cid})
    if courier:
        return courier

async def retrieve_orders(max_weight: float, regions: list, courier_id: int) -> list:
    orders = orders_collection.find({'region': {'$in': regions}, 'weight': {'$lte': max_weight} , 'processing': 1, 'complete_time': None, 'courier_id': courier_id, 'assign_time': None}, sort=[('weight', pymongo.DESCENDING )])
    return orders

async def set_processing_orders(max_weight: float, regions: list, courier_id: int) -> None:
    orders_collection.update_many({'region': {'$in': regions}, 'weight': {'$lte': max_weight}, 'processing': 0}, {'$set': {'processing': 1, 'courier_id': courier_id}})

async def unset_processing_order(ids: list) -> None:
    orders_collection.update_many({'order_id': {'$in': ids}}, {'$set': {'processing': 0, 'courier_id': None}})

async def assign_order(ids, courier_id, basket_id):
    assign_time = dt.datetime.now(tz=pytz.utc).isoformat()
    order = await orders_collection.update_many({'order_id': {'$in': ids}}, {'$set': {'assign_time': assign_time, 'courier_id': courier_id, 'basket_id': basket_id}})
    return assign_time

async def complete_order_db(order_id, complete_time):
    await orders_collection.update_one({'order_id': order_id}, {'$set': {'complete_time': complete_time}})

async def create_or_get_basket(courier_id: int, courier_type: str):
    basket = await basket_collection.find_one({'courier_id': courier_id}, {'basket_status': 0})
    if not basket:
        new_basket = await basket_collection.insert_one({'courier_id': courier_id, 'n_orders': 0, 'n_orders_finished': 0, 'basket_status': 0, 'start_courier_type': courier_type, 'last_delivery_time': None, 'actual_weight': 0, 'orders': []})
        return await basket_collection.find_one({'_id': new_basket.inserted_id})
    else:
        return basket

async def get_basket(courier_id: int):
    basket = await basket_collection.find_one({'courier_id': courier_id, 'basket_status': 0})
    if basket:
        return basket

async def update_basket(basket_id, values: dict):
    await basket_collection.update_one({'_id': ObjectId(basket_id)}, {'$set': values})

async def update_courier(courier_id, values: dict):
    await couriers_collection.update_one({'_id': ObjectId(courier_id)}, {'$set': values})
