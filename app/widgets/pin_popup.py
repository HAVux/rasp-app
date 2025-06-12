from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PinPopup(MDDialog):
    _pin_attempts = 0
    _max_attempts = 3

    def __init__(self, on_success=None, **kwargs):
        self.on_success = on_success
        
        # Create content layout
        content = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            padding=20,
            size_hint_y=None,
            height=130
        )
        
        # PIN input field
        self.pin_input = MDTextField(
            hint_text="Nhập mã PIN",
            password=True,
            mode="rectangle",
            font_size=20
        )
        content.add_widget(self.pin_input)

        # Dialog buttons
        buttons = [
            MDFlatButton(
                text="HỦY",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.5, 1],
                on_release=lambda x: self.dismiss()
            ),
            MDFlatButton(
                text="XÁC NHẬN",
                theme_text_color="Custom",
                text_color=[0.2, 0.7, 0.3, 1],
                on_release=lambda x: self.verify_pin()
            ),
        ]

        super().__init__(
            title="Xác thực mã PIN",
            type="custom",
            content_cls=content,
            buttons=buttons,
            size_hint=(0.4, None),
            **kwargs
        )

    def verify_pin(self):
        if self._pin_attempts >= self._max_attempts:
            self.pin_input.error = True
            self.pin_input.helper_text = "Quá số lần thử! Vui lòng thử lại sau."
            return

        correct_pin = environ.get("APP_PIN")  # Default to '0000' if not set
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