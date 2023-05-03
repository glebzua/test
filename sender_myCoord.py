from kivy.clock import Clock
from kivy.uix.image import Image
import socket
import cv2
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
import imutils
import struct
from kivymd.uix.filemanager import MDFileManager

KV = """
BoxLayout:
    size_hint_x: 1
    size_hint_y: 1 
    orientation: 'vertical'
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 0.5
        size_hint_y: 0.1

        MDTextField:
            id: server_address
            hint_text: 'Server Address'
            text: "192.168.3.52"
            required: True

        MDTextField:
            id: port
            hint_text: 'Port'
            text: "5000"
            required: True
            on_text: app.port = int(self.text) if self.text.isdigit() else 0

        MDTextField:
            id: error_message
            text: "No errors"
            required: False
            disabled: True


    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 0.5
        size_hint_y: 0.1

        MDRectangleFlatButton:
            text: 'send_my_command'
            on_press: app.send_my_command()
            
        MDRectangleFlatButton:
            text: 'send_target_command'
            on_press: app.send_target_command()

    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 1
        size_hint_y: 0.12


        MDTextField:
            id: my_latitude
            text: "0"
            hint_text: 'Mylatitude'
            required: True
            on_focus: if self.focus: self.text = ''
            on_text: app.my_latitude = int(self.text) if self.text.isdigit() else 0

        MDTextField:
            id: my_longitude
            text: "100"
            hint_text: 'Mylongitude'
            required: True
            on_text: app.my_longitude = int(self.text) if self.text.isdigit() else 0
        MDTextField:
            id: my_altitude
            text: "100"
            hint_text: 'Myaltitude'
            required: True
            on_text: app.my_altitude = int(self.text) if self.text.isdigit() else 0
    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 1
        size_hint_y: 0.12


        MDTextField:
            id: target_latitude
            text: "0"
            hint_text: 'Targetlatitude'
            required: True
            on_focus: if self.focus: self.text = ''
            on_text: app.target_latitude = int(self.text) if self.text.isdigit() else 0

        MDTextField:
            id: target_longitude
            text: "100"
            hint_text: 'Targetlongitude'
            required: True
            on_text: app.target_longitude = int(self.text) if self.text.isdigit() else 0
        MDTextField:
            id: target_altitude
            text: "100"
            hint_text: 'Targetaltitude'
            required: True
            on_text: app.target_altitude = int(self.text) if self.text.isdigit() else 0    
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 1
        size_hint_y: 0.12

        MDTextField:
            id: view_angle
            text: "0"
            hint_text: 'view_angle'
            required: True
            on_focus: if self.focus: self.text = ''
            on_text: app.view_angle = int(self.text) if self.text.isdigit() else 0
        MDRectangleFlatButton:
            text: 'send_view_angle_command'
            on_press: app.send_view_angle_command()
        
        MDTextField:
            id: angle_from_north
            text: "0"
            hint_text: 'angle_from_north'
            required: True
            on_focus: if self.focus: self.text = ''
            on_text: app.angle_from_north = int(self.text) if self.text.isdigit() else 0
        MDRectangleFlatButton:
            text: 'send_angle_from_north_command'
            on_press: app.send_angle_from_north_command()
        
        MDTextField:
            id: angle_from_ground
            text: "0"
            hint_text: 'look_vector'
            required: True
            on_focus: if self.focus: self.text = ''
            on_text: app.angle_from_ground = int(self.text) if self.text.isdigit() else 0
        MDRectangleFlatButton:
            text: 'send_angle_from_ground_command'
            on_press: app.send_angle_from_ground_command()
"""
video_widget_size = [0, 0]

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        self.app_window_width, self.app_window_height = Window.size
        self.app_window_texture_width = 0
        self.app_window_texture_height = 0
        self.app_window_delta_width = 0
        self.app_window_delta_height = 0
        self.screen = 0
        self.touch = None
        self.port = 0
        self.photo_count = 0
        self.targetX = 0
        self.targetY = 0
        self.flyHeight = 0
        self.trackBoxSize = 0
        self.selected_item_resolution = 0
        self.findIDTres = 0
        self.findInRecTres = 0
        self.file_path = 0
        self.cap = cv2.VideoCapture(self.file_path)
        self.photosArr = []

        self.my_latitude = 0
        self.my_longitude = 0
        self.my_altitude = 0

        self.target_latitude = 0
        self.target_longitude = 0
        self.target_altitude = 0
        self.angle_from_north = 30

    # def on_touch_down(self, window, touch):
    #     global video_widget_size
    #     video_widget = self.root.ids.video_widget
    #     if video_widget.collide_point(*touch.pos):
    #         self.app_window_texture_width = video_widget_size[0]
    #         self.app_window_texture_height = video_widget_size[1]
    #         self.app_window_width, self.app_window_height = Window.size
    #         self.touch = touch
    #         self.app_window_delta_width = self.app_window_width - self.app_window_texture_width
    #         self.app_window_delta_height = self.app_window_height - self.app_window_texture_height
    #         self.root.ids.targetX.text = f"{int(touch.pos[0]) - self.app_window_delta_width}"
    #         self.root.ids.targetY.text = f"{int(touch.pos[1]) - self.app_window_delta_height}"
    #     self.root.ids.selected_item_resolution.text = f"{self.app_window_width, self.app_window_texture_height}"

    def build(self):
        self.app_window_width, self.app_window_height = Window.size
        self.root = Builder.load_string(KV)

        # Window.bind(on_touch_down=self.on_touch_down)

        return self.root









    def send_my_command(self):
        message = f'my_pos:{self.root.ids.my_latitude.text}:{self.root.ids.my_longitude.text}:{self.root.ids.my_altitude.text}'
        print(message.encode())
        if all(v != '' for v in message.split(':')):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (
                self.root.ids.server_address.text,
                int(self.root.ids.port.text))
            try:
                sock.connect(server_address)
            # except ConnectionRefusedError:
            except:
                self.show_error("refused,try again")
                return
            try:
                sock.sendall(message.encode())
                confirmation = sock.recv(1024).decode()
                print("sendImg confirmed", confirmation)
            except:
                self.show_error("terminated,try again")
                return
            sock.close()

    def send_target_command(self):
        message = f'tr_pos:{self.root.ids.target_latitude.text}:{self.root.ids.target_longitude.text}:{self.root.ids.target_altitude.text}'
        print(message.encode())
        if all(v != '' for v in message.split(':')):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (
                self.root.ids.server_address.text,
                int(self.root.ids.port.text))
            try:
                sock.connect(server_address)
            # except ConnectionRefusedError:
            except:
                self.show_error("refused,try again")
                return
            try:
                sock.sendall(message.encode())
                confirmation = sock.recv(1024).decode()
                print("sendImg confirmed", confirmation)
            except:
                self.show_error("terminated,try again")
                return
            sock.close()
    def send_view_angle_command(self):
        message = f'my_v_a:{self.root.ids.view_angle.text}'
        print(message.encode())
        if all(v != '' for v in message.split(':')):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (
                self.root.ids.server_address.text,
                int(self.root.ids.port.text))
            try:
                sock.connect(server_address)
            # except ConnectionRefusedError:
            except:
                self.show_error("refused,try again")
                return
            try:
                sock.sendall(message.encode())
                confirmation = sock.recv(1024).decode()
                print("sendImg confirmed", confirmation)
            except:
                self.show_error("terminated,try again")
                return
            sock.close()
    def send_angle_from_north_command(self):
        message = f'my_afn:{self.root.ids.angle_from_north.text}'
        print(message.encode())
        if all(v != '' for v in message.split(':')):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (
                self.root.ids.server_address.text,
                int(self.root.ids.port.text))
            try:
                sock.connect(server_address)
            # except ConnectionRefusedError:
            except:
                self.show_error("refused,try again")
                return
            try:
                sock.sendall(message.encode())
                confirmation = sock.recv(1024).decode()
                print("sendImg confirmed", confirmation)
            except:
                self.show_error("terminated,try again")
                return
            sock.close()
    def send_angle_from_ground_command(self):
        message = f'my_afg:{self.root.ids.angle_from_ground.text}'
        print(message.encode())
        if all(v != '' for v in message.split(':')):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (
                self.root.ids.server_address.text,
                int(self.root.ids.port.text))
            try:
                sock.connect(server_address)
            # except ConnectionRefusedError:
            except:
                self.show_error("refused,try again")
                return
            try:
                sock.sendall(message.encode())
                confirmation = sock.recv(1024).decode()
                print("sendImg confirmed", confirmation)
            except:
                self.show_error("terminated,try again")
                return
            sock.close()
    def show_error(self, message):
        print('err', message)
        self.root.ids.error_message.text = f"{message}"

        # Clock.schedule_once(lambda dt: self.root.ids.error_message(str(message)), 0)


if __name__ == '__main__':
    MainApp().run()


