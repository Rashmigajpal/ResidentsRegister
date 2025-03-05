import requests
import os
from kivy.resources import resource_find
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivy.uix.image import AsyncImage

# Kivy Layout as String
KV = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        spacing: "10dp"
        padding: "20dp"

        # Logo
        AsyncImage:
            source: app.get_image_path()
            size_hint_y: None
            height: "150dp"
            pos_hint: {"center_x": 0.5}

        # Welcome Title
        MDLabel:
            text: "Welcome to Residence Register"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0, 0.6, 0.6, 1
            theme_text_color: "Primary"
            size_hint_y: None
            height: "40dp"

        MDLabel:
            text: "Secure Entry and Management"
            halign: "center"
            theme_text_color: "Primary"
            size_hint_y: None
            height: "30dp"

        # Navigation Buttons
        MDBoxLayout:
            orientation: "vertical"
            spacing: "15dp"
            size_hint_y: None
            height: self.minimum_height
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "View Hostels"
            md_bg_color: 0, 0.6, 0.6, 1
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_x: 0.7
            pos_hint: {"center_x": 0.5}
            on_release: app.view_hostels()

        MDRaisedButton:
            text: "Login"
            md_bg_color: 0, 0.6, 0.6, 1
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_x: 0.7
            pos_hint: {"center_x": 0.5}
            on_release: app.login()

        MDRaisedButton:
            text: "Register"
            md_bg_color: 0, 0.6, 0.6, 1
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_x: 0.7
            pos_hint: {"center_x": 0.5}
            on_release: app.register()

        MDRaisedButton:
            text: "Scan QR Code"
            md_bg_color: 0, 0.6, 0.6, 1
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_x: 0.7
            pos_hint: {"center_x": 0.5}
            on_release: app.scan_qr_code()

        MDRaisedButton:
            text: "Admin Dashboard"
            md_bg_color: 0, 0.6, 0.6, 1
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_x: 0.7
            pos_hint: {"center_x": 0.5}
            on_release: app.admin_dashboard()
'''

class ResidenceRegisterApp(MDApp):

    BASE_URL = "http://127.0.0.1:8000/api"  # Adjust this URL if necessary

    def build(self):
        self.theme_cls.primary_palette = "Teal"  # Set theme color
        return Builder.load_string(KV)

    def get_image_path(self):
        """ Return the absolute image path for AsyncImage """
        image_path = os.path.join(os.getcwd(), "static/clg_image/logo.png")
        return resource_find(image_path) if resource_find(image_path) else image_path

    def view_hostels(self):
        # Send GET request to fetch the list of hostels
        response = requests.get(f"{self.BASE_URL}/api/hostellers/")
        if response.status_code == 200:
            hostels = response.json()  # Assuming the API returns JSON data
            print("Hostels Data:", hostels)
        else:
            print(f"Failed to retrieve hostels data: {response.status_code}")

    def login(self):
        # Send GET request to login (replace with actual login API if needed)
        response = requests.get(f"{self.BASE_URL}/api/hostellers/")
        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Failed to login: {response.status_code}")

    def register(self):
        # Send GET request to register (replace with actual register API if needed)
        response = requests.get(f"{self.BASE_URL}/api/hostellers/")
        if response.status_code == 200:
            print("Registration successful")
        else:
            print(f"Failed to register: {response.status_code}")

    def scan_qr_code(self):
        # Assuming QR code is scanned and we need to fetch details
        response = requests.get(f"{self.BASE_URL}/api/hostellers/")  # Replace with actual QR code API if needed
        if response.status_code == 200:
            print("QR Code scan successful")
        else:
            print(f"Failed to scan QR Code: {response.status_code}")

    def admin_dashboard(self):
        # Send GET request for admin dashboard (replace with actual admin dashboard API)
        response = requests.get(f"{self.BASE_URL}/api/hostellers/")  # Replace with actual admin dashboard API
        if response.status_code == 200:
            print("Admin Dashboard loaded")
        else:
            print(f"Failed to load Admin Dashboard: {response.status_code}")

if __name__ == "__main__":
    ResidenceRegisterApp().run()
