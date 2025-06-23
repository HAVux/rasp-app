from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from app.utils.keyboard import VirtualKeyboard
from kivy.uix.vkeyboard import VKeyboard
from kivy.core.window import Window
from os import environ
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

class PinPopup(MDDialog):
    _pin_attempts = 0
    _max_attempts = 3

    def __init__(self, on_success=None, **kwargs):
        self.on_success = on_success
        self.keyboard = None

        # Layout nội dung chỉ gồm TextField
        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            padding=20,
            size_hint_y=None,
            height=100
        )

        self.pin_input = MDTextField(
            hint_text="Nhập mã PIN",
            password=True,
            mode="rectangle",
            font_size=20,
            size_hint_y=None,
            height=60
        )
        self.pin_input.bind(focus=self._on_focus)
        content_layout.add_widget(self.pin_input)

        # Lưu lại tham chiếu để controller bên ngoài sử dụng
        self.content_layout = content_layout

        buttons = [
            MDFlatButton(text="HỦY", on_release=lambda x: self.dismiss()),
            MDFlatButton(text="XÁC NHẬN", on_release=lambda x: self.verify_pin())
        ]

        super().__init__(
            title="Xác thực mã PIN",
            type="custom",
            content_cls=content_layout,
            buttons=buttons,
            size_hint=(0.4, None),
            auto_dismiss=False,
            **kwargs
        )
    
    def _on_focus(self, instance, value):
        """Handle input focus changes"""
        if value:  # Input gained focus
            self._show_keyboard()

    def _show_keyboard(self):
        if self.keyboard:
            return

        # Tạo bàn phím ảo với layout QWERTY
        self.keyboard = VKeyboard(layout='qwerty', size_hint=(1, None), height=300)
        self.keyboard.bind(on_key_up=self._on_key_up)
        Window.add_widget(self.keyboard)
        self.keyboard.pos = (0, 0)

    def _on_key_up(self, instance, keycode, *args):
        """Xử lý khi người dùng nhấn phím trên bàn phím ảo"""
        key_str = keycode[0] if isinstance(keycode, (list, tuple)) else keycode

        if key_str == 'backspace':
            self.pin_input.do_backspace()
        elif key_str == 'enter':
            self.verify_pin()
        elif isinstance(key_str, str) and len(key_str) == 1:
            self.pin_input.insert_text(key_str)


    def _hide_keyboard(self, *args):
        """Hide and remove keyboard"""
        if self.keyboard:
            if self.keyboard.parent:
                self.keyboard.parent.remove_widget(self.keyboard)
            self.keyboard = None

    def on_dismiss(self):
        """Clean up when dialog is dismissed"""
        self._hide_keyboard()
        super().on_dismiss()

    def verify_pin(self):
        if self._pin_attempts >= self._max_attempts:
            self.pin_input.error = True
            self.pin_input.helper_text = "Quá số lần thử! Vui lòng thử lại sau."
            return

        correct_pin = environ.get("APP_PIN")
        if self.pin_input.text == correct_pin:
            self._pin_attempts = 0
            if self.on_success:
                self.on_success()
            self.dismiss()
        else:
            self._pin_attempts += 1
            remaining = self._max_attempts - self._pin_attempts
            self.pin_input.error = True
            self.pin_input.helper_text = f"Mã PIN không đúng! Còn {remaining} lần thử"
            self.pin_input.text = ""