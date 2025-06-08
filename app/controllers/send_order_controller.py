#app/controllers/send_order_controller.py
from kivy.clock import Clock
from threading import Thread
from app.services.send_order import send_order
from app.services.cancel_order import cancel_order
from app.services.check_order_status import check_order_status
from app.services.update_food import fetch_food_data

class SendOrderController:
    def __init__(self, app):
        self.app = app

    def process_checkout(self):
        self.app.root.current = "waiting"
        payload = {
            "items": [
                {"FoodId": fid, "Quantity": data["quantity"]}
                for fid, data in self.app.order_data.items()
            ]
        }
        print("📤 Payload gửi server:", payload)

        def _send():
            order_code, qr_url = send_order(payload["items"])
            if order_code and qr_url:
                self.app.order_code = order_code
                self.app.qr_url = qr_url
                Clock.schedule_once(self.app.go_to_qr_code)
            else:
                print("❌ Gửi đơn thất bại hoặc không nhận được QR")
                Clock.schedule_once(self.app.reset_to_main)

        Thread(target=_send).start()

    def cancel_transaction(self):
        def _cancel():
            if self.app.order_code:
                cancel_order(self.app.order_code)
            # Sau khi hủy đơn, khôi phục số lượng available
            self.app.order_controller.restore_ordered_items()
            # Trả về UI chính sau khi xử lý xong
            def update_ui(_):
                self.app.page_controller.reset_to_main(None)
            Clock.schedule_once(update_ui)
        
        Thread(target=_cancel).start()
    

    # def go_to_qr_code(self, dt):
    #     qr_screen = self.app.root.get_screen("qr_code")
    #     qr_screen.ids.qr_total_label.text = f"Tổng: {self.app.total:,} VND"
    #     qr_screen.ids.qr_image.source = self.app.qr_url
    #     self.app.root.current = "qr_code"
    #     self.app.poll_status_event = Clock.schedule_interval(self.poll_order_status, 2)

    # def poll_order_status(self, dt):
    #     if not self.app.order_code:
    #         return

    #     def _poll():
    #         status = check_order_status(self.app.order_code)
    #         print(f"🔄 Trạng thái đơn hàng {self.app.order_code}: {status}")

    #         def handle_status(_):
    #             if status == 2:
    #                 print("✅ Đơn hàng đã thanh toán.")
    #                 if hasattr(self.app, "poll_status_event"):
    #                     self.app.poll_status_event.cancel()
    #                 self.go_to_thank_you(None)
    #             elif status == 4:
    #                 print("❌ Đơn hàng đã bị hủy.")
    #                 if hasattr(self.app, "poll_status_event"):
    #                     self.app.poll_status_event.cancel()
    #                 self.reset_to_main(None)

    #         Clock.schedule_once(handle_status)

    #     Thread(target=_poll).start()

    # def go_to_thank_you(self, dt):
    #     thank_screen = self.app.root.get_screen("thank_you")
    #     thank_screen.ids.order_code_label.text = self.app.order_code
    #     self.app.root.current = "thank_you"
    #     Clock.schedule_once(self.reset_to_main, 7)

    # def reset_to_main(self, dt):
    #     self.app.order_data.clear()
    #     self.app.total = 0
    #     self.app.order_code = ""
    #     self.app.qr_url = ""

    #     main_screen = self.app.root.get_screen("main")
    #     main_screen.ids.order_box.clear_widgets()
    #     main_screen.ids.total_label.text = "0 VND"

    #     self.app.root.current = "main"

    #     def fetch_and_update():
    #         new_data = fetch_food_data()
    #         if new_data != self.app.food_data:
    #             def update_ui(_):
    #                 self.app.food_data = new_data
    #                 self.app.page_controller.update_page()
    #                 print("🔄 Cập nhật món ăn sau khi reset")
    #             Clock.schedule_once(update_ui)

    #     Thread(target=fetch_and_update).start()