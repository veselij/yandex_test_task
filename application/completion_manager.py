from database import retrieve_courier, retrieve_order, get_basket, complete_order_db, update_basket, update_courier
from dateutil import parser
import datetime as dt
from constant import COURIER_K


class OrderComplitionManager:

    def __init__(self, courier_id, order_id, finish_time):
        self.courier_id = courier_id
        self.order_id = order_id
        self.finish_time = parser.isoparse(finish_time).isoformat()
        self.courier = None
        self.order = None
        self.basket = None

    @staticmethod
    async def calc_delta_time(t1, t2) -> int:
        delta = dt.datetime.fromisoformat(t1) - dt.datetime.fromisoformat(t2)
        return int(delta.total_seconds())

    async def get_order(self):
        order = await retrieve_order(self.order_id, self.courier_id)
        if order:
            self.order = order

    async def get_courier(self):
        courier = await retrieve_courier(self.courier_id)
        if courier:
            self.courier = courier

    async def get_courier_basket(self):
        basket = await get_basket(self.order['basket_id'])
        if basket:
            self.basket = basket

    async def finish_order(self):
        await complete_order_db(self.order_id, self.finish_time)

    async def calculate_basket(self):
        if self.basket['n_orders'] == (self.basket['n_orders_finished'] + 1):
            self.basket['basket_status'] = 1
        self.basket['n_orders_finished'] += 1
        self.basket['actual_weight'] -= self.order['weight']
        self.basket['orders'].remove(self.order_id)

    async def calculate_courier(self):
        if self.basket['last_delivery_time']:
            delivery_time = await self.calc_delta_time(self.finish_time, self.basket['last_delivery_time'])
        else:
            delivery_time = await self.calc_delta_time(self.finish_time, self.order['assign_time'])
        n = 1
        if delivery_time <= 0:
            return
        self.basket['last_delivery_time'] = self.finish_time
        if str(self.order['region']) not in self.courier['n_deliverys_per_regions'].keys():
            self.courier['n_deliverys_per_regions'][str(self.order['region'])] = n
        else:
            self.courier['n_deliverys_per_regions'][str(self.order['region'])] += n
        if str(self.order['region']) not in self.courier['delivery_times_per_regions'].keys():
            self.courier['delivery_times_per_regions'][str(self.order['region'])] = delivery_time
        else:
            self.courier['delivery_times_per_regions'][str(self.order['region'])] += delivery_time

    async def calculate_earning(self):
        if self.basket['basket_status'] == 1:
            self.courier['earnings'] += 500*COURIER_K[self.basket['start_courier_type']]

    async def calculate_rating(self):
        t = 3601
        for del_time, n_del in zip(self.courier['delivery_times_per_regions'].values(), self.courier['n_deliverys_per_regions'].values()):
            t = del_time/n_del if del_time/n_del < t else t
        self.courier['rating'] = round((60*60 - min(t, 60*60))/(60*60) * 5, 2)

    async def compleate_order(self):
        await self.get_courier()
        await self.get_order()
        if not self.courier or not self.order:
            return
        await self.get_courier_basket()
        if not self.basket:
            return
        await self.calculate_basket()
        await self.calculate_courier()
        await self.calculate_earning()
        await self.calculate_rating()
        await self.finish_order()
        basket_new = dict(self.basket)
        basket_new.pop('_id')
        courier_new = dict(self.courier)
        courier_new.pop('_id')
        await update_basket(self.basket['_id'], basket_new)
        await update_courier(self.courier['_id'], courier_new)
        return self.order_id

