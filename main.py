# import ssl
# import certifi
# ssl._create_default_https_context = ssl._create_unverified_context

# from kivymd.app import MDApp
# from kivy.lang import Builder
# from kivy.properties import StringProperty, NumericProperty, DictProperty
# from kivy.clock import Clock
# from kivy.core.window import Window
# from kivy.uix.screenmanager import SlideTransition

# from app.services.update_food import fetch_food_data
# from app.screens.mainscreen import FoodItem, OrderItem
# from app.screens.waitingscreen import WaitingScreen
# from app.screens.qrscreen import QRCodeScreen
# from app.screens.thankyouscreen import ThankYouScreen
# from app.services.send_order import send_order
# from app.services.cancel_order import cancel_order
# from app.services.check_order_status import check_order_status


# class MainApp(MDApp):

#     food_data = []

#     order_data = DictProperty({})
#     total = NumericProperty(0)

#     current_page = NumericProperty(0)
#     items_per_page = NumericProperty(4)
#     current_tab = StringProperty("do_an")

#     order_code = StringProperty("")
#     qr_url = StringProperty("")

#     def build(self):
#         #Window.fullscreen = 'auto'
#         self.theme_cls.primary_palette = "Teal"
#         Builder.load_file("kv/waitingscreen.kv")
#         Builder.load_file("kv/mainscreen.kv")
#         Builder.load_file("kv/qrscreen.kv")
#         Builder.load_file("kv/thankyouscreen.kv")
#         return Builder.load_file("kv/root.kv")

#     def on_start(self):
#         Clock.schedule_once(self.delayed_update_page, 0.1)

#     def on_stop(self):
#         if hasattr(self, "poll_event"):
#             self.poll_event.cancel()

#     def delayed_update_page(self, dt):
#         self.food_data = fetch_food_data()
#         print("📦 Số món đồ ăn:", len(self.get_items_for_tab("do_an")))
#         print("📦 Số món thức uống:", len(self.get_items_for_tab("thuc_uong")))
#         self.update_page()
#         # Poll mỗi 5 giây
#         self.poll_event = Clock.schedule_interval(self.poll_food_data, 5)

#     def get_items_for_tab(self, tab_name):
#         return [item for item in self.food_data if item.get("type") == tab_name]

#     def update_total(self):
#         self.total = sum(item['quantity'] * item['price'] for item in self.order_data.values())
#         main_screen = self.root.get_screen("main")
#         main_screen.ids.total_label.text = f"{self.total:,} VND"

#     def change_tab(self, tab_name):
#         direction = "left" if tab_name == "thuc_uong" else "right"
#         self.current_tab = tab_name
#         self.current_page = 0
#         main_screen = self.root.get_screen("main")
        
#         main_screen.ids.screen_manager.transition = SlideTransition(direction=direction, duration=0.3)
#         main_screen.ids.screen_manager.current = tab_name
#         self.update_page()

#     # def update_page(self):
#     #     main_screen = self.root.get_screen("main")
#     #     screen = main_screen.ids.screen_manager.get_screen(self.current_tab)
#     #     grid = screen.ids.get(f"{self.current_tab}_grid")
#     #     grid.clear_widgets()

#     #     all_items = self.get_items_for_tab(self.current_tab)
#     #     start = self.current_page * self.items_per_page
#     #     end = start + self.items_per_page

#     #     for item in all_items[start:end]:
#     #         grid.add_widget(FoodItem(
#     #             food_id=item["food_id"],
#     #             food_name=item["name"],
#     #             price=item["price"],
#     #             image_source=item["image"],
#     #             available=item["available"]
#     #         ))

#     def update_page(self):
#         main_screen = self.root.get_screen("main")
#         screen = main_screen.ids.screen_manager.get_screen(self.current_tab)
#         rv = screen.ids.get(f"{self.current_tab}_rv")
#         if not rv:
#             print(f"⚠️ Không tìm thấy RecycleView cho tab {self.current_tab}")
#             return

#         all_items = self.get_items_for_tab(self.current_tab)
#         start = self.current_page * self.items_per_page
#         end = start + self.items_per_page

#         rv.data = [
#             {
#                 "food_id": item["food_id"],
#                 "food_name": item["name"],
#                 "price": item["price"],
#                 "image_source": item["image"],
#                 "available": item["available"]
#             }
#             for item in all_items[start:end]
#         ]

#     def next_page(self):
#         all_items = self.get_items_for_tab(self.current_tab)
#         if (self.current_page + 1) * self.items_per_page < len(all_items):
#             self.current_page += 1
#             self.update_page()

#     def prev_page(self):
#         if self.current_page > 0:
#             self.current_page -= 1
#             self.update_page()
    
#     def create_invoice_payload(self):
#         return {
#             "items": [
#                 {
#                     "FoodId": food_id,
#                     "Quantity": data["quantity"]
#                 }
#                 for food_id, data in self.order_data.items()
#             ]
#         }
    
#     def process_checkout(self):
#         self.root.current = "waiting"
#         payload = self.create_invoice_payload()
#         print("📤 Payload gửi server: ", payload)
#         # Gửi đơn đến server
#         order_code, qr_url = send_order(payload["items"])

#         if order_code and qr_url:
#             print(order_code, "\n", qr_url)
#             self.order_code = order_code
#             self.qr_url = qr_url
#             self.go_to_qr_code(None)

#     def cancel_transaction(self):
#         # Nếu có mã đơn thì gọi API hủy
#         if self.order_code:
#             cancel_order(self.order_code)

#         self.reset_to_main(None)

#     def go_to_qr_code(self, dt):
#         qr_screen = self.root.get_screen("qr_code")
#         qr_screen.ids.qr_total_label.text = f"Tổng: {self.total:,} VND"

#         # ✅ Load ảnh QR từ URL
#         qr_screen.qr_url = self.qr_url

#         self.root.current = "qr_code"

#         # ✅ Bắt đầu polling trạng thái đơn hàng mỗi 3s
#         self.poll_status_event = Clock.schedule_interval(self.poll_order_status, 2)
    
#     def go_to_thank_you(self, dt):
#         thank_screen = self.root.get_screen("thank_you")
#         thank_screen.ids.order_code_label.text = self.order_code
#         self.root.current = "thank_you"

#         # ✅ Sau 5 giây: reset và về lại main
#         Clock.schedule_once(self.reset_to_main, 7)
    
#     def reset_to_main(self, dt):
#         self.order_data.clear()
#         self.total = 0
#         self.order_code = ""
#         self.qr_url = ""

#         main_screen = self.root.get_screen("main")
#         main_screen.ids.order_box.clear_widgets()
#         main_screen.ids.total_label.text = "0 VND"

#         # Quay lại màn hình chính
#         self.root.current = "main"

#     def poll_food_data(self, dt):
#         if self.root.current != "main":
#             return  # Chỉ gọi khi ở màn hình chính
#         new_data = fetch_food_data()
#         if new_data != self.food_data:
#             self.food_data = new_data
#             self.update_page()
#             print("🔄 Đã cập nhật món ăn từ server")
    
#     def poll_order_status(self, dt):
#         if not self.order_code:
#             return

#         status = check_order_status(self.order_code)
#         print(f"🔄 Trạng thái đơn hàng {self.order_code}: {status}")

#         if status == 2:  # Đã thanh toán
#             print("✅ Đơn hàng đã thanh toán.")
#             if hasattr(self, "poll_status_event"):
#                 self.poll_status_event.cancel()
#             self.go_to_thank_you(None)

#         elif status == 4:
#             print("❌ Đơn hàng đã bị hủy.")
#             if hasattr(self, "poll_status_event"):
#                 self.poll_status_event.cancel()


# if __name__ == "__main__":
#     MainApp().run()

from app.controllers.main_controller import MainApp

if __name__ == "__main__":
    MainApp().run()
