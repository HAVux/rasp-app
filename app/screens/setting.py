from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.vkeyboard import VKeyboard
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from app.utils.keyboard import VirtualKeyboard
from kivy.clock import Clock
import re
from shlex import quote
import subprocess
from config import WIFI_CONFIG_PATH


class SettingsScreen(Screen):
    ssid = StringProperty("")
    password = StringProperty("")
    _loading_dialog = ObjectProperty(None, allownone=True)

# ------------------------------------------------------------------
# Init / focus / keyboard handling
# ------------------------------------------------------------------

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard = None
        self.current_input = None
        self.original_y = 0
        #bind to window touch events
        Window.bind(on_touch_down=self._handle_window_touch)

    def _handle_window_touch(self, instance, touch):
        """Handle touches outside keyboard area"""
        if self.keyboard and self.current_input:
            # Get keyboard area
            kbd = self.keyboard
            # Nếu không có input hiện tại thì chỉ kiểm tra va chạm với bàn phím
            if not self.current_input:
                if not kbd.collide_point(*touch.pos):
                    self.hide_keyboard()
                    return True

            # Nếu có cả input và touch nằm ngoài cả hai thì ẩn keyboard
            elif not kbd.collide_point(*touch.pos) and not self.current_input.collide_point(*touch.pos):
                self.hide_keyboard()
                return True
        return False

        
    def show_keyboard(self, textfield):
        """Show virtual keyboard for input field"""
        if self.keyboard:
            self.hide_keyboard()
        
        self.current_input = textfield

        self.original_y = textfield.y

        self.keyboard = VirtualKeyboard(
            target_input=textfield,
            on_done=self.hide_keyboard,
            size_hint=(1, 0.4),
            pos_hint={'x': 0, 'y': 0},
            layout='qwerty'
        )
        Window.add_widget(self.keyboard)

        # Animate textfield to move above the keyboard
        keyboard_height = Window.height * 0.4
        textfield_y = Window.height - keyboard_height - dp(100)
        anim = Animation(y=textfield_y, duration=0.2)
        anim.start(textfield)
        
    def hide_keyboard(self, *args):
        """Hide and remove keyboard"""
        if self.keyboard and self.keyboard.parent:
            self.keyboard.parent.remove_widget(self.keyboard)
        self.keyboard = None

        # Reset textfield position
        if self.current_input:
            anim = Animation(y=self.original_y, duration=0.2)
            anim.start(self.current_input)
        
        self.current_input = None
        self.original_y = None

    def on_leave(self):
        self.hide_keyboard()
        super().on_leave()

    def _scroll_to_widget(self, widget):
        scrollview = self.ids.get('scrollview')
        if scrollview:
            # Convert local position to scrollview
            scrollview.scroll_to(widget, padding=dp(60), animate=True)

# ------------------------------------------------------------------
# Popup helpers
# ------------------------------------------------------------------
    def _show_loading(self):
        if self._loading_dialog:
            return
        self._loading_dialog = MDDialog(title="Đang kết nối Wi‑Fi…", text="Vui lòng đợi…")
        self._loading_dialog.open()

    def _close_loading(self):
        if self._loading_dialog:
            self._loading_dialog.dismiss()
            self._loading_dialog = None
    
    def _popup(self, ok: bool, msg: str):
        title = "Thành công" if ok else "Lỗi"
        color = [0.2, 0.7, 0.3, 1] if ok else [1, 0, 0, 1]
        MDDialog(title=title, text=msg, buttons=[MDFlatButton(text="Đóng", theme_text_color="Custom", text_color=color, on_release=lambda x: x.parent.parent.dismiss())]).open()

# ------------------------------------------------------------------
# Wi‑Fi worker (thread)
# ------------------------------------------------------------------

    def _run_secure_command(self, command, *args, timeout=15):
        """Execute command securely with sanitized arguments"""
        try:
            # Validate command and arguments
            if not isinstance(command, str) or not all(isinstance(arg, str) for arg in args):
                raise ValueError("Invalid command or arguments")

            # Run command without shell
            result = subprocess.run(
                [command, *args],
                timeout=timeout,
                capture_output=True,
                shell=False,  # Prevent shell injection
                check=False
            )
            return result
        except subprocess.SubprocessError as e:
            print(f"❌ Lỗi thực thi lệnh: {e}")
            return None

    def apply_wifi(self):
        if not self.ssid.strip():
            self._show_error_popup("Vui lòng nhập tên mạng (SSID) để kết nối.")
            return False
        
        try:
            config = self._generate_wifi_config()
            # Write config using sudo and tee
            write_cmd = f'echo "{config}" | sudo tee {WIFI_CONFIG_PATH}'
            result = subprocess.run(
                ['bash', '-c', write_cmd],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Không thể ghi file cấu hình: {result.stderr}")
                return False
            
            # Connect to network
            result = self._run_secure_command(
                "sudo", "nmcli", "device", "wifi", 
                "connect", self.ssid,
                "password", self.password,
                "hidden", "yes",
                timeout=15
            )

            if result and result.returncode == 0:
                print("✅ WiFi kết nối thành công. Đợi kiểm tra internet...")
                # Đợi và kiểm tra internet
                
                self.ssid = ""
                self.password = ""
                
                self._check_network_and_restart_tailscale()
                return True
            else:
                error = result.stderr.decode('utf-8') if result else "Unknown error"
                print(f"❌ Không thể kết nối WiFi: {error}")
                self._run_secure_command("sudo", "systemctl", "restart", "networking")
                return False
            
        except Exception as e:
            print(f"❌ Lỗi khi cấu hình Wi-Fi: {e}")
            # Try to recover network
            self._run_secure_command("sudo", "systemctl", "restart", "networking")
            return False
        
    def _check_network_and_restart_tailscale(self):
        """Đợi 5s và kiểm tra kết nối Internet"""
        Clock.schedule_once(self._do_network_check, 2)

    def _do_network_check(self, dt):
        try:
            result = self._run_secure_command("ping", "-c", "2", "8.8.8.8", timeout=10)
            if result.returncode == 0:
                print("✅ Internet OK - restart tailscale")

                # Restart tailscaled bằng systemctl
                restart_result = self._run_secure_command("sudo", "systemctl", "restart", "tailscaled", timeout=20)
                
                if restart_result and restart_result.returncode == 0:
                    print("✅ Tailscaled đã được restart")
                    self._show_success_popup("Kết nối Wi-Fi")
                else:
                    print("⚠️ Không thể restart tailscaled")
                    self._show_error_popup("Wi-Fi OK nhưng không thể restart Tailscale.")
        except Exception as e:
            print(f"⚠️ Lỗi kiểm tra mạng: {e}")
            self._show_error_popup("Lỗi kiểm tra kết nối mạng.")

    def _generate_wifi_config(self):
        """Generate sanitized WiFi config"""
        return f"""
        network={{
            ssid="{quote(self.ssid)}"
            psk="{quote(self.password)}"
        }}
        """

    def toggle_password_visibility(self):
        """Toggle password visibility in the password field"""
        password_input = self.ids.password_input
        password_input.password = not password_input.password
