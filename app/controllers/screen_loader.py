from kivy.lang import Builder

def load_all_screens():
    Builder.load_file("kv/waitingscreen.kv")
    Builder.load_file("kv/mainscreen.kv")
    Builder.load_file("kv/qrscreen.kv")
    Builder.load_file("kv/thankyouscreen.kv")
    Builder.load_file("kv/network_error.kv")
    Builder.load_file("kv/setting.kv")
    Builder.load_file("kv/lockscreen.kv")
    return Builder.load_file("kv/root.kv")