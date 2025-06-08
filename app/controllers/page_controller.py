#app/controllers/page_controller.py
from kivy.uix.screenmanager import NoTransition
from kivy.clock import Clock
from threading import Thread
import shutil
import os
from app.services.update_food import fetch_food_data
from app.services.check_order_status import check_order_status
from app.utils.qr import download_qr_image

class PageController:
    def __init__(self, app):
        self.app = app

    def load_initial_data(self, dt):
        def _load():
            data = fetch_food_data()
            def update_ui(_):
                self.app.food_data = fetch_food_data()
                print("📦 Số món đồ ăn:", len(self.get_items_for_tab("do_an")))
                print("📦 Số món thức uống:", len(self.get_items_for_tab("thuc_uong")))
                self.update_page()
            Clock.schedule_once(update_ui)

        Thread(target=_load).start()

    def get_items_for_tab(self, tab_name):
        return [item for item in self.app.food_data if item.get("type") == tab_name]

    def change_tab(self, tab_name):
        direction = "left" if tab_name == "thuc_uong" else "right"
        self.app.current_tab = tab_name
        self.app.current_page = 0
        main_screen = self.app.root.get_screen("main")
        main_screen.ids.screen_manager.transition = NoTransition()
        main_screen.ids.screen_manager.current = tab_name
        self.update_page()

    def update_page(self):
        main_screen = self.app.root.get_screen("main")
        screen = main_screen.ids.screen_manager.get_screen(self.app.current_tab)
        rv = screen.ids.get(f"{self.app.current_tab}_rv")
        if not rv:
            print(f"⚠️ Không tìm thấy RecycleView cho tab {self.app.current_tab}")
            return

        all_items = self.get_items_for_tab(self.app.current_tab)
        start = self.app.current_page * self.app.items_per_page
        end = start + self.app.items_per_page

        rv.data = [
            {
                "food_id": item["food_id"],
                "food_name": item["name"],
                "price": item["price"],
                "image_source": item["image"],
                "available": item["available"]
            }
            for item in all_items[start:end]
        ]

    def next_page(self):
        all_items = self.get_items_for_tab(self.app.current_tab)
        if (self.app.current_page + 1) * self.app.items_per_page < len(all_items):
            self.app.current_page += 1
            self.update_page()

    def prev_page(self):
        if self.app.current_page > 0:
            self.app.current_page -= 1
            self.update_page()


    def go_to_qr_code(self, dt):
        self.app.qr_image_path = download_qr_image(self.app.qr_url)
        if not self.app.qr_image_path:
            print("❌ Không thể tải QR code.")
            return
        qr_screen = self.app.root.get_screen("qr_code")
        qr_screen.ids.qr_total_label.text = f"Tổng: {self.app.total:,} VND"
        qr_screen.ids.qr_image.source = self.app.qr_image_path
        self.app.root.current = "qr_code"
        self.app.poll_status_event = Clock.schedule_interval(self.poll_order_status, 2)

    def go_to_thank_you(self, dt):
        self.app.order_controller.subtract_ordered_items()
        # 🧹 Xóa ảnh QR đã lưu
        if self.app.qr_image_path and os.path.exists(self.app.qr_image_path):
            os.remove(self.app.qr_image_path)
            print("🧹 Đã xóa ảnh QR sau thanh toán:", self.app.qr_image_path)
            self.app.qr_image_path = ""
        thank_screen = self.app.root.get_screen("thank_you")
        thank_screen.ids.order_code_label.text = self.app.order_code
        self.app.root.current = "thank_you"
        Clock.schedule_once(self.reset_to_main, 7)

    def reset_to_main(self, dt):
        self.load_initial_data(0)
        self.app.order_data.clear()
        self.app.total = 0
        self.app.order_code = ""
        self.app.qr_url = ""

        main_screen = self.app.root.get_screen("main")
        main_screen.ids.order_box.clear_widgets()
        main_screen.ids.total_label.text = "0 VND"

        self.app.root.current = "main"
    
    def poll_order_status(self, dt):
        if not self.app.order_code:
            return

        def _poll():
            status = check_order_status(self.app.order_code)
            print(f"🔄 Trạng thái đơn hàng {self.app.order_code}: {status}")

            def handle_status(_):
                if status == 2:
                    print("✅ Đơn hàng đã thanh toán.")
                    if hasattr(self.app, "poll_status_event"):
                        self.app.poll_status_event.cancel()
                    self.go_to_thank_you(None)
                elif status == 4:
                    print("❌ Đơn hàng đã bị hủy.")
                    if hasattr(self.app, "poll_status_event"):
                        self.app.poll_status_event.cancel()
                    self.reset_to_main(None)

            Clock.schedule_once(handle_status)

        Thread(target=_poll).start()

    def poll_food_data(self, dt):
        if self.app.root.current != "main":
            return
        
        def _poll():
            new_data = fetch_food_data()
            if new_data != self.app.food_data:
                # 🧹 Xóa thư mục cache ảnh cũ
                cache_dir = "cache_images"
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                    print("🧹 Đã xóa cache ảnh cũ")
                def update_ui(_):
                    self.app.food_data = new_data
                    self.update_page()
                    print("🔄 Đã cập nhật món ăn từ server")
                Clock.schedule_once(update_ui)
        
        Thread(target=_poll).start()