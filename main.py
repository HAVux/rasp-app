from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from food_data import get_items_for_tab


class FoodItem(MDBoxLayout):
    food_name = StringProperty("")
    price = NumericProperty(0)
    image_source = StringProperty("")
    price_text = StringProperty("0 VND")
    available = NumericProperty(0)
    available_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_price_text)

    def _init_price_text(self, *args):
        try:
            self.price_text = "{:,} VND".format(int(self.price))
            self.available_text = "{:,} VND".format(int(self.available))
        except (ValueError, TypeError):
            self.price_text = "0 VND"
            self.available_text = "0"

    def add_to_order(self):
        app = MDApp.get_running_app()
        main_screen = app.root.get_screen("main")

        if self.food_name in app.order_data:
            for item in main_screen.ids.order_box.children:
                if hasattr(item, 'food_name') and item.food_name == self.food_name:
                    item.increase()
                    break
        else:
            item = OrderItem(food_name=self.food_name, quantity=1, price=self.price)
            main_screen.ids.order_box.add_widget(item)
            app.order_data[self.food_name] = {'quantity': 1, 'price': self.price}
            app.update_total()


class OrderItem(MDBoxLayout):
    food_name = StringProperty()
    quantity = NumericProperty()
    price = NumericProperty()

    def increase(self):
        self.quantity += 1
        self.update_order()

    def decrease(self):
        self.quantity -= 1
        if self.quantity <= 0:
            self.parent.remove_widget(self)
            MDApp.get_running_app().order_data.pop(self.food_name, None)
        else:
            self.update_order()
        MDApp.get_running_app().update_total()

    def update_order(self):
        app = MDApp.get_running_app()
        app.order_data[self.food_name] = {'quantity': self.quantity, 'price': self.price}
        app.update_total()

class WaitingScreen(MDScreen):
    pass

class MainApp(MDApp):
    order_data = DictProperty({})
    total = NumericProperty(0)

    current_page = NumericProperty(0)
    items_per_page = NumericProperty(4)
    current_tab = StringProperty("do_an")

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        Builder.load_file("kv/waitingscreen.kv")
        Builder.load_file("kv/mainscreen.kv")
        Builder.load_file("kv/qrscreen.kv")
        Builder.load_file("kv/thankyouscreen.kv")
        return Builder.load_file("kv/root.kv")

    def on_start(self):
        Clock.schedule_once(self.delayed_update_page, 0.1)

    def delayed_update_page(self, dt):
        self.update_page()

    def update_total(self):
        self.total = sum(item['quantity'] * item['price'] for item in self.order_data.values())
        main_screen = self.root.get_screen("main")
        main_screen.ids.total_label.text = f"{self.total:,} VND"

    def create_invoice_payload(self):
        return {
            "items": self.order_data,
            "total": self.total
        }
    
    def process_checkout(self):
        self.root.current = "waiting"
        payload = self.create_invoice_payload()
        print(payload)
        # Chờ 5 giây rồi chuyển sang màn hình QR
        Clock.schedule_once(self.go_to_qr_code, 5)

    def change_tab(self, tab_name):
        self.current_tab = tab_name
        self.current_page = 0
        main_screen = self.root.get_screen("main")
        main_screen.ids.screen_manager.current = tab_name
        self.update_page()

    def update_page(self):
        main_screen = self.root.get_screen("main")
        screen = main_screen.ids.screen_manager.get_screen(self.current_tab)
        grid = screen.ids.get(f"{self.current_tab}_grid")
        grid.clear_widgets()

        all_items = get_items_for_tab(self.current_tab)
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page

        for item in all_items[start:end]:
            grid.add_widget(FoodItem(
                food_name=item["name"],
                price=item["price"],
                image_source=item["image"],
                available=item["available"]
            ))

    def next_page(self):
        all_items = get_items_for_tab(self.current_tab)
        if (self.current_page + 1) * self.items_per_page < len(all_items):
            self.current_page += 1
            self.update_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
    
    def cancel_transaction(self):
        self.order_data = {}
        self.total = 0
        main_screen = self.root.get_screen("main")
        main_screen.ids.order_box.clear_widgets()
        main_screen.ids.total_label.text = "0 VND"
        self.root.current = "main"

    def go_to_qr_code(self, dt):
        qr_screen = self.root.get_screen("qr_code")
        qr_screen.ids.qr_total_label.text = f"Tổng: {self.total:,} VND"
        self.root.current = "qr_code"
        Clock.schedule_once(self.go_to_thank_you, 5)
    
    def go_to_thank_you(self, dt):
        # Tạo mã đơn giả (ví dụ: A001 - A999)
        order_code = "123"

        thank_screen = self.root.get_screen("thank_you")
        thank_screen.ids.order_code_label.text = order_code
        self.root.current = "thank_you"

if __name__ == "__main__":
    MainApp().run()
