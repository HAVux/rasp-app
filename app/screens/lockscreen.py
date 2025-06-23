
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from os import environ
from dotenv import load_dotenv
from kivy.app import App

# Load biến môi trường
load_dotenv()

class LockScreen(Screen):
    password = StringProperty("")
    
    def append_number(self, number):
        """Thêm số vào password_input"""
        self.ids.password_input.text += number

    def delete_last(self):
        """Xóa ký tự cuối cùng"""
        self.ids.password_input.text = self.ids.password_input.text[:-1]

    def unlock_app(self):
        """Check password and unlock the app"""
        # Replace with your actual password checking logic
        correct_pin = environ.get("APP_PIN")  # Example password - store this securely in production!
        app = App.get_running_app()
        if self.ids.password_input.text == correct_pin:
            app.root.current = 'main'
            self.ids.password_input.text = ""
        else:
            self.show_error_dialog()
    
    def show_error_dialog(self):
        """Show incorrect password dialog"""
        dialog = MDDialog(
            title="Mật khẩu không đúng",
            text="Vui lòng nhập lại mật khẩu.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()