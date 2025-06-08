#app/screens/components/order_item.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp

class OrderItem(MDBoxLayout):
    food_name = StringProperty()
    quantity = NumericProperty()
    price = NumericProperty()
    food_id = StringProperty()

    def increase(self):
        app = MDApp.get_running_app()
        food = self._find_food(app)

        if food and food["available"] > 0:
            food["available"] -= 1
            self.quantity += 1
            self._sync()
        else:
            print("⚠️ Không thể thêm: hết hàng.")

    def decrease(self):
        app = MDApp.get_running_app()
        food = self._find_food(app)

        if food:
            food["available"] += 1

        self.quantity -= 1
        if self.quantity <= 0:
            self.parent.remove_widget(self)
            app.order_data.pop(self.food_id, None)
        else:
            self._sync()

        app.update_total()
        app.page_controller.update_page()

    def _sync(self):
        app = MDApp.get_running_app()
        if self.food_id in app.order_data:
            app.order_data[self.food_id]["quantity"] = self.quantity
        app.update_total()
        app.page_controller.update_page()

    def _find_food(self, app):
        for food in app.food_data:
            if food.get("food_id") == self.food_id:
                return food
        return None
    
    def update_order(self):
        app = MDApp.get_running_app()
        if self.food_id in app.order_data:
            app.order_data[self.food_id]["quantity"] = self.quantity
            app.update_total()