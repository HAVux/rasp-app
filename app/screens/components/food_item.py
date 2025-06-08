#app/screens/components/food_item.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp

class FoodItem(MDBoxLayout):
    food_name = StringProperty("")
    price = NumericProperty(0)
    image_source = StringProperty("")
    price_text = StringProperty("0 VND")
    available = NumericProperty(0)
    available_ui = NumericProperty(0) 
    available_text = StringProperty("")
    food_id = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.available_ui = self.available
        self.update_texts()

    def on_price(self, instance, value):
        self.update_texts()

    def on_available(self, instance, value):
        self.available_ui = value  # Sync lại mỗi khi load mới
        self.update_texts()

    def on_available_ui(self, instance, value):
        self.update_texts()

    def update_texts(self):
        try:
            self.price_text = f"{int(self.price):,} VND"
            self.available_text = f"{int(self.available):,}"
        except (ValueError, TypeError):
            self.price_text = "0 VND"
            self.available_text = "0"

    def add_to_order(self):
        if self.available_ui <= 0:
            print(f"⚠️ Món {self.food_name} đã hết hàng.")
            return
        
        MDApp.get_running_app().order_controller.add_to_order(
            food_id=self.food_id,
            food_name=self.food_name,
            price=self.price
        )
        self.available_ui -= 1  # Trừ hiển thị ngay
