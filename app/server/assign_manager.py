from server.database import retrieve_courier, retrieve_orders, assign_order, set_processing_orders, unset_processing_order, create_or_get_basket, update_basket
from server.constant import COURIER_MAX_WEIGHT
import re

class ManagerOfOrders:

    def __init__(self, courier_id: int) -> None:
        self.courier_id = courier_id

    async def set_weight_and_region(self):
        self.max_weight = COURIER_MAX_WEIGHT[self.courier['courier_type']]
        self.regions = self.courier['regions']

    @staticmethod
    async def convert_hours_to_numbers(hours: str) -> int:
        numbers = re.split(':|-', hours)
        return (int(numbers[0])*60 + int(numbers[1]), int(numbers[2])*60 + int(numbers[3]))

    @staticmethod
    async def check_intervals(interval_courier: tuple, interval_order: tuple) -> bool:
        r = range(interval_order[0], interval_order[1]+1)
        if interval_courier[0] in r and interval_courier[1] in r:
            return True
        return False

    async def get_courier(self):
        courier = await retrieve_courier(self.courier_id)
        if courier:
            self.courier = courier

    async def lock_orders(self):
        await set_processing_orders(self.max_weight, self.regions, self.courier_id)

    async def unlock_orders(self, ids):
        if ids:
            await unset_processing_order(ids)

    async def get_basket(self):
        self.basket = await create_or_get_basket(self.courier_id, self.courier['courier_type'])

    async def assigned_orders(self):
        orders_ids = []
        unlock_ids = []
        orders = await retrieve_orders(self.max_weight, self.regions, self.courier_id)
        async for order in orders:
            if order['weight'] + self.basket['actual_weight'] > self.max_weight:
                unlock_ids.append(order['order_id'])
            else:
                if await self.delivery_time_check(order):
                    self.basket['actual_weight'] += order['weight']
                    self.basket['n_orders'] += 1
                    self.basket['orders'].append(order['order_id'])
                    orders_ids.append(order['order_id'])
                else:
                    unlock_ids.append(order['order_id'])
        if orders_ids:
            self.assign_time = await assign_order(orders_ids, self.courier_id, self.basket['_id'])
            await update_basket(self.basket['_id'], {'actual_weight': self.basket['actual_weight'], 'n_orders': self.basket['n_orders'], 'orders': self.basket['orders']})
        return unlock_ids

    async def delivery_time_check(self, order) -> bool:
        delivery_possible = False
        for delivery_interval in order['delivery_hours']:
            for courier_working_hour in self.courier['working_hours']:
                delivery_interval_int = await self.convert_hours_to_numbers(delivery_interval)
                courier_working_hour_int = await self.convert_hours_to_numbers(courier_working_hour)
                delivery_possible = await self.check_intervals(courier_working_hour_int, delivery_interval_int)
                if delivery_possible:
                    return delivery_possible
        return delivery_possible

    async def get_result(self):
        await self.get_courier()
        if self.courier:
            await self.get_basket()
            await self.set_weight_and_region()
            await self.lock_orders()
            to_unlock_order_ids = await self.assigned_orders()
            await self.unlock_orders(to_unlock_order_ids)
            if self.basket['orders']:
                return {"orders": self.basket['orders'], "assign_time": self.assign_time}
            else:
                return {"orders": []}
        return
