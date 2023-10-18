from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window

class PresentationLayer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, **kwargs)
        self.message_label = Label(text="Window Size: {}x{}\nMouse Coordinates: 0, 0".format(
            Window.width, Window.height), size_hint_y=None, height=60)
        self.add_widget(self.message_label)

    def update_message(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        self.message_label.text = "Window Size: {}x{}\nMouse Coordinates: {}, {}".format(
            Window.width, Window.height, int(mouse_x), int(mouse_y))

class MouseCoordinatesApp(App):
    def build(self):
        presentation_layer = PresentationLayer()

        def on_mouse_move(window, mouse_pos):
            presentation_layer.update_message(mouse_pos)

        # Bind the mouse motion event
        Window.bind(mouse_pos=on_mouse_move)

        return presentation_layer

if __name__ == '__main__':
    MouseCoordinatesApp().run()
