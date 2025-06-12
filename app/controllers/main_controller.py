#app/controllers/main_controller.py
from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'borderless', '1')

from kivymd.app import MDApp
from kivy.properties import DictProperty, NumericProperty, StringProperty
from kivy.clock import Clock
import os
import shutil
from time import time
from app.controllers.page_controller import PageController
from app.controllers.order_controller import OrderController
from app.controllers.send_order_controller import SendOrderController
from app.controllers.screen_loader import load_all_screens
from app.widgets.pin_popup import PinPopup
from kivy.lang import Builder
#from kivy.uix.popup import Popup

class MainApp(MDApp):

    hold_start_time = NumericProperty(0)

    order_data = DictProperty({})
    total = NumericProperty(0)
    current_tab = StringProperty("do_an")
    current_page = NumericProperty(0)
    items_per_page = NumericProperty(4)

    order_code = StringProperty("")
    qr_url = StringProperty("")
    qr_image_path = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_data = {}
        self.food_data = []
        self.total = 0
        self.clear_cache_and_data()

# === APP LIFECYCLE ===
    def build(self):
        # Khởi tạo các controller
        self.page_controller = PageController(self)
        self.order_controller = OrderController(self)
        self.send_order_controller = SendOrderController(self)
        return load_all_screens()

    def on_start(self):
        Clock.schedule_once(self.page_controller.load_initial_data, 0.1)

    def on_stop(self):
        if hasattr(self, "poll_event"):
            self.poll_event.cancel()
        if hasattr(self, "poll_status_event"):
            self.poll_status_event.cancel()
        self.clear_cache_and_data()
    
# === UI ACTIONS ===
    def update_total(self):
        self.order_controller.update_total()

    def change_tab(self, tab_name):
        self.page_controller.change_tab(tab_name)

    def next_page(self):
        self.page_controller.next_page()

    def prev_page(self):
        self.page_controller.prev_page()

# === ORDER FLOW ===
    def process_checkout(self):
        self.send_order_controller.process_checkout()

    def cancel_transaction(self):
        self.send_order_controller.cancel_transaction()

    def go_to_qr_code(self, dt):
        self.page_controller.go_to_qr_code(dt)

    def go_to_thank_you(self, dt):
        self.send_order_controller.go_to_thank_you(dt)

    def reset_to_main(self, dt):
        self.page_controller.reset_to_main(dt)

# === POLLING ===
    def poll_food_data(self, dt):
        self.page_controller.poll_food_data(dt)

    def poll_order_status(self, dt):
        self.send_order_controller.poll_order_status(dt)

# === DATA ===
    # def subtract_ordered_items(self):
    #     self.order_controller.subtract_ordered_items()

    def clear_cache_and_data(self):
        cache_dir = "cache_images"
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("🧹 Đã xóa cache ảnh khi khởi động")

        self.order_data.clear()
        self.total = 0
        print("🔁 Đã reset order_data và total")

# === UTILS ===
    def start_hold_timer(self):
            self.hold_start_time = time()

    def check_hold_duration(self):
        hold_duration = time() - self.hold_start_time
        if hold_duration >= 7:  # Nếu nhấn giữ >= 7 giây
            self.show_pin_popup()

    def show_pin_popup(self):
        """Show PIN entry popup for settings access"""
        def on_success():
            self.root.current = 'settings'
        
        pin_popup = PinPopup(on_success=on_success)
        pin_popup.open()