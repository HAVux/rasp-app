from kivy.uix.vkeyboard import VKeyboard
from kivy.core.window import Window


class VirtualKeyboard(VKeyboard):
    def __init__(self, target_input=None, on_done=None, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.on_done = on_done
        self.shift_once = False
        self.caps_lock = False
        self.focused_input = target_input

        self.bind(on_key_up=self._on_key_up)
        Window.bind(on_key_down=self._disable_system_keyboard)

    def _disable_system_keyboard(self, *args):
        return True

    def _on_key_up(self, instance, keycode, *args):
        key_str = keycode[1] if isinstance(keycode, (list, tuple)) else keycode

        if not self.focused_input:
            return

        if key_str == 'shift':
            self.shift_once = True
            self._update_keys_case()
            return

        if key_str == 'capslock':
            self.caps_lock = not self.caps_lock
            print(f"[CAPSLOCK] {'ON' if self.caps_lock else 'OFF'}")
            self._update_keys_case()
            return

        if key_str == 'backspace':
            self.focused_input.do_backspace()
            return

        elif key_str in ('enter', 'escape'):
            if self.on_done:
                self.on_done()
            return

        elif isinstance(key_str, str) and len(key_str) == 1:
            char = (
                key_str.upper() 
                if (self.shift_once or self.caps_lock) and key_str.isalpha() 
                else key_str
            )
            self.focused_input.insert_text(char)

            if self.shift_once:
                self.shift_once = False
                self._update_keys_case()

    def _update_keys_case(self):
        """Cập nhật text trên các phím tùy theo trạng thái shift/capslock"""
        is_upper = self.shift_once or self.caps_lock

        for key in self.children:
            if hasattr(key, "keycode") and key.keycode:
                keycode = key.keycode[1] if isinstance(key.keycode, tuple) else key.keycode
                if isinstance(keycode, str) and len(keycode) == 1 and keycode.isalpha():
                    key.text = keycode.upper() if is_upper else keycode.lower()