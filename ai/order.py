from datetime import datetime

class OrderManager:
    """Manage monthly medicine orders for users (in-memory demo)."""
    orders = {}
    order_counter = 1

    def place_order(self, user, medicine, quantity):
        """Place a new medicine order for a user."""
        if user not in self.orders:
            self.orders[user] = []
        order = {
            'order_id': self.order_counter,
            'medicine': medicine,
            'quantity': quantity,
            'date': datetime.now().isoformat()
        }
        self.orders[user].append(order)
        self.order_counter += 1
        return {'status': 'success', 'order': order}

    def get_orders(self, user):
        """Get all orders for a user."""
        return self.orders.get(user, [])

    def repeat_order(self, user, order_id):
        """Repeat a previous order by order_id."""
        user_orders = self.orders.get(user, [])
        for order in user_orders:
            if order['order_id'] == order_id:
                return self.place_order(user, order['medicine'], order['quantity'])
        return {'error': 'Order not found.'} 