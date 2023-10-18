from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock


class MouseController:
    def __init__(self, message_label):
        self.message_label = message_label

        # Bind the mouse motion event
        Window.bind(mouse_pos=self.on_mouse_motion)

    def on_mouse_motion(self, instance, pos):
        mouse_x, mouse_y = pos
        self.update_message(mouse_x, mouse_y)

    def update_message(self, mouse_x, mouse_y):
        self.message_label.text = "Window Size: {}x{}\nMouse Coordinates: {}, {}".format(
            Window.width, Window.height, int(mouse_x), int(mouse_y))


class PresentationLayer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, **kwargs)
        self.message_label = Label(text="Window Size: {}x{}\nMouse Coordinates: 0, 0".format(
            Window.width, Window.height), size_hint_y=None, height=60)
        self.add_widget(self.message_label)


class MouseCoordinatesApp(App):
    def build(self):
        presentation_layer = PresentationLayer()
        mouse_controller = MouseController(presentation_layer.message_label)

        # Schedule the update function to run every 0.1 seconds
        Clock.schedule_interval(lambda dt: mouse_controller.update_message(0, 0), 0.1)

        return presentation_layer


if __name__ == '__main__':
    MouseCoordinatesApp().run()
