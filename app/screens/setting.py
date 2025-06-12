from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import re
from shlex import quote
import subprocess
from kivy.properties import StringProperty, NumericProperty
from config import WIFI_CONFIG_PATH


class SettingsScreen(Screen):
    ssid = StringProperty("")
    password = StringProperty("")

    def _run_secure_command(self, command, *args, timeout=15):
        """Execute command securely with sanitized arguments"""
        try:
            # Validate command and arguments
            if not isinstance(command, str) or not all(isinstance(arg, str) for arg in args):
                raise ValueError("Invalid command or arguments")
                
            # Sanitize inputs
            safe_args = [quote(arg) for arg in args]
            
            # Run command without shell
            result = subprocess.run(
                [command, *safe_args],
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
        try:
            config = self._generate_wifi_config()
            with open((WIFI_CONFIG_PATH), "w") as f:
                f.write(config)

            if not self._run_secure_command("sudo", "nmcli", "networking", "off", timeout=5):
                raise RuntimeError("Failed to disable networking")
            
            if not self._run_secure_command("sudo", "nmcli", "networking", "on", timeout=5):
                raise RuntimeError("Failed to enable networking")
            
            # Connect to network
            result = self._run_secure_command(
                "sudo", "nmcli", "device", "wifi", 
                "connect", self.ssid,
                "password", self.password,
                timeout=15
            )

            if result and result.returncode == 0:
                print("✅ Kết nối WiFi thành công!")
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
        
    def _generate_wifi_config(self):
        """Generate sanitized WiFi config"""
        return f"""
        network={{
            ssid="{quote(self.ssid)}"
            psk="{quote(self.password)}"
        }}
        """
            
    def show_error_popup(self, message):
        """Show error popup with the given message"""
        dialog = MDDialog(
            title="Lỗi",
            text=message,
            buttons=[
                MDFlatButton(
                    text="ĐÓNG",
                    theme_text_color="Custom",
                    text_color=[0.2, 0.7, 0.3, 1],
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()