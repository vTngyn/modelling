from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.event import EventDispatcher


class EventDispatcherExample(EventDispatcher):
    pass


class MouseController:
    def __init__(self, event_dispatcher):
        self.event_dispatcher = event_dispatcher

        # Bind the mouse motion event
        Window.bind(mouse_pos=self.on_mouse_motion)

    def on_mouse_motion(self, instance, pos):
        mouse_x, mouse_y = pos
        self.event_dispatcher.dispatch('on_mouse_move', mouse_x, mouse_y)


class PresentationLayer(BoxLayout):
    def __init__(self, event_dispatcher, **kwargs):
        super().__init__(orientation='vertical', padding=10, **kwargs)
        self.message_label = Label(text="Window Size: {}x{}\nMouse Coordinates: 0, 0".format(
            Window.width, Window.height), size_hint_y=None, height=60)
        self.add_widget(self.message_label)
        event_dispatcher.bind(on_mouse_move=self.update_message)

    def update_message(self, instance, mouse_x, mouse_y):
        self.message_label.text = "Window Size: {}x{}\nMouse Coordinates: {}, {}".format(
            Window.width, Window.height, int(mouse_x), int(mouse_y))


class MouseCoordinatesApp(App):
    def build(self):
        event_dispatcher = EventDispatcherExample()
        mouse_controller = MouseController(event_dispatcher)
        presentation_layer = PresentationLayer(event_dispatcher)

        return presentation_layer


if __name__ == '__main__':
    MouseCoordinatesApp().run()
