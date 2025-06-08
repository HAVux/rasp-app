#app/controllers/order_controller.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from app.screens.components.order_item import OrderItem

class OrderController:
    def __init__(self, app):
        self.app = app

    def update_total(self):
        self.app.total = sum(
            item['quantity'] * item['price'] for item in self.app.order_data.values()
        )
        main_screen = self.app.root.get_screen("main")
        main_screen.ids.total_label.text = f"{self.app.total:,} VND"

    def add_to_order(self, food_id, food_name, price):
        main_screen = self.app.root.get_screen("main")

        # Kiểm tra còn hàng trước khi thêm
        for food in self.app.food_data:
            if food["food_id"] == food_id and food["available"] <= 0:
                print(f"🚫 Món {food_name} đã hết hàng!")
                return

        if food_id in self.app.order_data:
            for item in main_screen.ids.order_box.children:
                if hasattr(item, 'food_id') and item.food_id == food_id:
                    item.increase()
                    break
        else:
            order_item = OrderItem(
                food_id=food_id,
                food_name=food_name,
                quantity=0,  # Quantity sẽ tăng lên trong `increase()`
                price=price
            )
            main_screen.ids.order_box.add_widget(order_item)
            self.app.order_data[food_id] = {
                "name": food_name,
                "price": price,
                "quantity": 0
            }
            order_item.increase()

        self.update_total()

    def restore_ordered_items(self):
        for food_id, item in self.app.order_data.items():
            quantity = item.get("quantity", 0)
            for food in self.app.food_data:
                if food["food_id"] == food_id:
                    food["available"] += quantity
                    print(f"♻️ Hoàn tác {quantity} cho món: {food['name']} (ID={food_id}) → Mới: {food['available']}")
        print("✅ Đã hoàn tác tất cả món trong order_data.")
        self.app.page_controller.update_page()
