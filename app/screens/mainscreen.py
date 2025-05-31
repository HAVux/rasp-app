from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

class FoodItem(MDBoxLayout):
    food_name = StringProperty("")
    price = NumericProperty(0)
    image_source = StringProperty("")
    price_text = StringProperty("0 VND")
    available = NumericProperty(0)
    available_text = StringProperty("")
    food_id = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_texts()

    def on_price(self, instance, value):
        self.update_texts()

    def on_available(self, instance, value):
        self.update_texts()

    def update_texts(self):
        try:
            self.price_text = f"{int(self.price):,} VND"
            self.available_text = f"{int(self.available):,}"
        except (ValueError, TypeError):
            self.price_text = "0 VND"
            self.available_text = "0"

    def add_to_order(self):
        app = MDApp.get_running_app()
        add_to_order(
            food_id = self.food_id,
            food_name = self.food_name,
            price = self.price
        )



class OrderItem(MDBoxLayout):
    food_name = StringProperty()
    quantity = NumericProperty()
    price = NumericProperty()
    food_id = StringProperty()

    def increase(self):
        self.quantity += 1
        self.update_order()

    def decrease(self):
        self.quantity -= 1
        if self.quantity <= 0:
            self.parent.remove_widget(self)
            MDApp.get_running_app().order_data.pop(self.food_id, None)
        else:
            self.update_order()
        MDApp.get_running_app().update_total()

    def update_order(self):
        app = MDApp.get_running_app()
        if self.food_id in app.order_data:
            app.order_data[self.food_id]["quantity"] = self.quantity
            app.update_total()


def add_to_order(food_id, food_name, price):
    app = MDApp.get_running_app()
    main_screen = app.root.get_screen("main")

    if food_id in app.order_data:
        for item in main_screen.ids.order_box.children:
            if hasattr(item, 'food_id') and item.food_id == food_id:
                item.increase()
                break
    else:
        order_item = OrderItem(
            food_id = food_id,
            food_name = food_name,
            quantity = 1,
            price = price
        )
        main_screen.ids.order_box.add_widget(order_item)

        app.order_data[food_id] = {
            "name": food_name,
            "price": price,
            "quantity": 1 
        }

    app.update_total()