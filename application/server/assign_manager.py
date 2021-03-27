from server.database import retrieve_courier, retrieve_orders, assign_order, set_processing_orders, unset_processing_order, create_basket, update_basket, retrieve_courier_orders, update_basket, update_courier
from server.constant import COURIER_MAX_WEIGHT, COURIER_K
import re
from time import sleep

class ManagerOfOrders:

    def __init__(self, courier_id: int, new_courier: dict = None) -> None:
        self.courier_id = courier_id
        self.orders_ids = []
        self.unlock_ids = []
        self.new_courier = new_courier
        self.modified = 0

    async def set_weight_and_region(self):
        self.max_weight = COURIER_MAX_WEIGHT[self.courier['courier_type']]
        self.regions = self.courier['regions']

    @staticmethod
    async def convert_hours_to_numbers(hours: str) -> int:
        numbers = re.split(':|-', hours)
        return (int(numbers[0])*60 + int(numbers[1]), int(numbers[2])*60 + int(numbers[3]))

    @staticmethod
    async def check_intervals(interval_courier: tuple, interval_order: tuple) -> bool:
        range_courier = set(range(interval_courier[0], interval_courier[1] + 1))
        range_order = range(interval_order[0], interval_order[1] + 1)
        intersec = range_courier.intersection(range_order)
        if intersec:
            return True
        return False

    async def get_courier(self):
        courier = await retrieve_courier(self.courier_id)
        if courier:
            self.courier = courier

    async def lock_orders(self):
        self.modified = await set_processing_orders(self.max_weight, self.regions, self.courier_id)

    async def unlock_orders(self):
        await unset_processing_order(self.unlock_ids)

    async def get_basket(self):
        self.basket = await create_basket(self.courier_id, self.courier['courier_type'])

    async def check_order(self, order):
        if await self.delivery_time_check(order):
            self.basket['actual_weight'] += order['weight']
            self.basket['n_orders'] += 1
            self.basket['orders'].append(order['order_id'])
            self.orders_ids.append(order['order_id'])
        else:
            self.unlock_ids.append(order['order_id'])

    async def assigned_orders(self):
        orders = await retrieve_orders(self.max_weight, self.regions, self.courier_id)
        for order in await orders.to_list(length=self.modified):
            print(order)
            if order['weight'] + self.basket['actual_weight'] > self.max_weight:
                self.unlock_ids.append(order['order_id'])
            elif order['weight'] + self.basket['actual_weight'] == self.max_weight:
                await self.check_order(order)
            else:
                await self.check_order(order)
        if self.orders_ids:
            self.assign_time = await assign_order(self.orders_ids, self.courier_id, self.basket['_id'])
            if not self.basket['created_time']:
                self.basket['created_time'] = self.assign_time
            await update_basket(self.basket['_id'], {'actual_weight': self.basket['actual_weight'], 'n_orders': self.basket['n_orders'], 'orders': self.basket['orders'], 'created_time': self.basket['created_time']})

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
            await self.assigned_orders()
            if self.unlock_ids:
                await self.unlock_orders()
            if self.basket['orders']:
                ids = [{"id": i} for i in self.basket['orders']]
                return {"orders": ids, "assign_time": self.basket['created_time'].replace('+00:00', 'Z')}
            else:
                return {"orders": []}
        return

    async def deassign_ordes(self):
        delta_region = []
        await self.get_courier()
        if self.courier:
            await self.get_basket()
            await self.set_weight_and_region()
            for k, v in self.new_courier.items():
                if k == 'regions' and v:
                    delta_region = list(set(self.courier['regions']) - set(self.new_courier['regions']))
                if v:
                    self.courier[k] = v
            async for order in await retrieve_courier_orders(self.courier_id):
                for key, val in self.new_courier.items():
                        if key == 'working_hours':
                            if not await self.delivery_time_check(order):
                                if order['order_id'] not in self.unlock_ids:
                                    self.unlock_ids.append(order['order_id'])
                                    self.basket['n_orders'] -= 1
                                    self.basket['actual_weight'] -= order['weight']
                                    self.basket['orders'].remove(order['order_id'])
                                    break
                        elif key == 'regions':
                            if order['region'] in delta_region:
                                if order['order_id'] not in self.unlock_ids:
                                    self.unlock_ids.append(order['order_id'])
                                    self.basket['n_orders'] -= 1
                                    self.basket['actual_weight'] -= order['weight']
                                    self.basket['orders'].remove(order['order_id'])
                                    break
            if self.new_courier['courier_type']:
                new_max_wieght = COURIER_MAX_WEIGHT[self.new_courier['courier_type']]
                delta_weight = new_max_wieght - self.max_weight
                if delta_weight < 0:
                    async for order in await retrieve_courier_orders(self.courier_id):
                        if order['order_id'] not in self.unlock_ids:
                            if self.basket['actual_weight'] > new_max_wieght:
                                self.unlock_ids.append(order['order_id'])
                                self.basket['actual_weight'] -= order['weight']
                                self.basket['orders'].remove(order['order_id'])
                                self.basket['n_orders'] -= 1
                            else:
                                break
            if self.unlock_ids:
                await self.unlock_orders()
                if self.basket['n_orders'] == self.basket['n_orders_finished']:
                    self.basket['basket_status'] = 1
                    self.courier['earnings'] += 500*COURIER_K[self.basket['start_courier_type']]
            basket_new = dict(self.basket)
            basket_new.pop('_id')
            courier_new = dict(self.courier)
            courier_new.pop('_id')
            await update_basket(self.basket['_id'], basket_new)
            await update_courier(self.courier['_id'], courier_new)
            return True
        return False



