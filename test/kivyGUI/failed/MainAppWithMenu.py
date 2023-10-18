from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.clock import Clock

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

class TransparentPopup(Popup):
    pass

class MenuItem(Button):
    def __init__(self, text, on_release_callback, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint = (None, None)
        self.size = (BUTTON_WIDTH, BUTTON_HEIGHT)
        self.bind(on_release=on_release_callback)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the message label
        self.message_label = Label(
            text="Window Size: {}x{}\nMouse Coordinates: 0, 0".format(
                Window.width, Window.height),
            size_hint=(None, None), height=100,
        )

        layout = BoxLayout(orientation='horizontal', spacing=5)  # Reduced spacing

        for menu_item_text, callback in [('Apps', self.show_apps_menu),
                                         ('Config', self.show_config_menu),
                                         ('Help', self.show_help_menu)]:
            menu_item = MenuItem(menu_item_text, callback)
            anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
            anchor_layout.add_widget(menu_item)
            layout.add_widget(anchor_layout)

        quit_button = Button(text='Quit', on_release=self.quit_app,
                             size_hint=(None, None), size=(BUTTON_WIDTH, BUTTON_HEIGHT))
        quit_anchor_layout = AnchorLayout(anchor_x='right', anchor_y='top')
        quit_anchor_layout.add_widget(quit_button)

        layout.add_widget(quit_anchor_layout)
        self.add_widget(self.message_label)
        self.add_widget(layout)

        # Schedule the update of mouse coordinates every 0.1 seconds
        Clock.schedule_interval(self.update_mouse_coordinates, 0.1)

    def update_mouse_coordinates(self, dt):
        # Update mouse coordinates in the message label
        mouse_pos = Window.mouse_pos
        self.message_label.text = "Window Size: {}x{}\nMouse Coordinates: {}, {}".format(
            Window.width, Window.height, int(mouse_pos[0]), int(mouse_pos[1]))

    def show_apps_menu(self, instance):
        # Add code to display the Apps menu and handle item selection
        pass

    def show_config_menu(self, instance):
        # Add code to display the Config menu and handle item selection
        pass

    def show_help_menu(self, instance):
        # Add code to display the Help menu and handle item selection
        pass

    def quit_app(self, instance):
        App.get_running_app().stop()

class MenuApp(App):
    def build(self):
        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        sm.add_widget(main_screen)
        return sm

if __name__ == '__main__':
    MenuApp().run()
