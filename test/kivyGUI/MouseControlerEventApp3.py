from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.event import EventDispatcher
from kivy.core.window import Window
from typing import Callable, List, Dict, Tuple
from functools import partial
class EventManager:
    event_dispatcher = EventDispatcher()
    event_handlers = {}

    @classmethod
    def register_listener(cls, event_name, callback, listener):
        if event_name not in cls.event_handlers:
            cls.event_handlers[event_name] = {'listeners': [], 'producers': []}

        cls.event_handlers[event_name]['listeners'].append((callback, listener))
        # cls.event_dispatcher.bind(**{event_name: partial(callback, event_name)})
        cls.event_dispatcher.bind(**{event_name: callback})

    @classmethod
    def unregister_listener(cls, event_name, callback, listener):
        if event_name in cls.event_handlers:
            handler = cls.event_handlers[event_name]
            listeners = handler['listeners']
            if (callback, listener) in listeners:
                listeners.remove((callback, listener))
                # Assuming `callback` is the function you want to unbind
                cls.event_dispatcher.unbind(**{event_name: callback})

    @classmethod
    def register_producer(cls, event_name, producer):
        if event_name not in cls.event_handlers:
            cls.event_handlers[event_name] = {'listeners': [], 'producers': []}

        cls.event_handlers[event_name]['producers'].append(producer)

    @classmethod
    def unregister_producer(cls, event_name, producer):
        if event_name in cls.event_handlers:
            cls.event_handlers[event_name]['producers'].remove(producer)

    @classmethod
    def dispatch(cls, event_name, *args):
        if event_name in cls.event_handlers:
            for callback, _ in cls.event_handlers[event_name]['listeners']:
                callback(*args)

            for producer in cls.event_handlers[event_name]['producers']:
                try:
                    producer.dispatch_event(*args)
                except Exception as e:
                    print(producer)
                    print(e)

class EventListener:
    def __init__(self, events: List[Tuple[str, Callable]]):
        self.event_names: List[Tuple[str, Callable]] = []
        if events:
            for event in events:
                event_name, callback = event[0], event[1]
                print(f"registering listener: {event_name}/{callback}")
                self.register_as_listener(event[0], event[1])

    def register_as_listener(self, event_name: str, callback: Callable):
        self.event_names.append((event_name, callback))
        EventManager.register_listener(event_name, callback, self)

    def unregister(self, event_name: str, callback: Callable):
        EventManager.unregister_listener(event_name, callback, self)
        self.event_names.remove((event_name, callback))


class EventProducer:
    def __init__(self, event_names: list):
        self.event_names = event_names
        if self.event_names:
            for event_name in event_names:
                EventManager.register_producer(event_name=event_name, producer=self)

    def dispatch_event(self, event_name, event_data):
        if (event_name in self.event_names):
            EventManager.event_dispatcher.dispatch(self.event_name, event_data)

    def register_as_producer(self,  event_names: list):
        self.event_names = event_names
        if self.event_names:
            for event_name in event_names:
                EventManager.register_producer(event_name=event_name, producer=self)

    def unregister(self, event_name: str):
        EventManager.unregister_producer(event_name, self)

class MouseMoveEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class GUIComponentDim:
    def __init__(self, **kwargs):
        self.height = kwargs.get('height', 30)
        self.width = kwargs.get('width', 100)
        self.spacing_v = kwargs.get('spacing_v', 10)
        self.spacing_h = kwargs.get('spacing_h', 10)
        self.font_name = kwargs.get('font_name', 'Arial')
        self.font_size = kwargs.get('font_size', 12)

class GUIDimCfg:
    def __init__(self, **kwargs):
        max_width = kwargs.get('max_width', 1080)
        max_height = kwargs.get('max_height', 1920)

        print(max_height)

        self.main_window_size = GUIComponentDim(width=max_width, height=max_height)
        self.main_menu_item_size = GUIComponentDim(width=10, height=30, spacing_h=10)
        self.submenu_item_size = GUIComponentDim(width=10, height=30, spacing_v=10)
        self.header_area_size = GUIComponentDim(width=max_width, height=max_height * 0.2)
        self.feature_area_size = GUIComponentDim(width=max_width, height=max_height * 0.7)
        self.footer_size = GUIComponentDim(width=max_width, height=max_height * 0.1)

class MenuArea(FloatLayout):
    def __init__(self, gui_dims:GUIDimCfg, **kwargs):
        super().__init__(**kwargs)
        self.height = gui_dims.main_menu_item_size.height
        self.spacing = gui_dims.main_menu_item_size.spacing_h

        left_menu_items_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
        self.add_widget(left_menu_items_anchor_layout)
        right_menu_items_anchor_layout = AnchorLayout(anchor_x='right', anchor_y='bottom')
        self.add_widget(right_menu_items_anchor_layout)

        left_menu_items_anchor_layout = self
        # right_menu_items_anchor_layout = self

        menu_items = ["Apps", "Config", "Help"]
        x_position = 0
        for item in menu_items:
            btn = Button(text=item, size_hint=(None, 1), width=self.width, pos=(x_position, 300))
            print (f"{item}: x_position={x_position}")
            x_position += btn.width + self.spacing
            left_menu_items_anchor_layout.add_widget(btn)

        print(f"{'Quit'}: x_position={self.width - 100}")
        quit_button = Button(text="Quit", size_hint=(None, 1), width=self.width, pos=(200, 200))
        quit_button.bind(on_release=self.quit_app)
        right_menu_items_anchor_layout.add_widget(quit_button)

    def quit_app(self, instance):
        App.get_running_app().stop()

class FeatureArea(EventProducer, BoxLayout):
    def __init__(self, gui_dims, event_name=None, **kwargs):
        EventProducer.__init__(self, event_names=list('on_mouse_move'))
        BoxLayout.__init__(self, **kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = gui_dims.feature_area_size.height

        # Register as a producer for 'on_mouse_move' event
        # EventManager.register_producer('on_mouse_move', self.on_touch_move)

    def on_touch_move(self, touch):
        print(f"on_touch_move: instance={''}, touch={touch or ''}")
        if self.collide_point(*touch.pos):
            # print(touch)
            # EventManager.event_dispatcher.dispatch('on_mouse_move', touch.pos)
            # self.dispatch_event(touch.pos)
            mouse_x, mouse_y = touch.pos
            self.dispatch_event('on_mouse_move', MouseMoveEvent(mouse_x, mouse_y))


class MessageArea(EventListener, BoxLayout):
    def __init__(self, gui_dims, event_name=None, **kwargs):
        EventListener.__init__(self, [('on_mouse_move', self.update_mouse_coordinates)])
        BoxLayout.__init__(self, **kwargs)
        # EventManager.register_listener('on_mouse_move', self.update_mouse_coordinates, self)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = gui_dims.footer_size.height
        self.label = Label(text='Mouse Coordinates: (0, 0)')
        self.add_widget(self.label)

        EventManager.event_dispatcher.bind(on_mouse_move=lambda instance, value: print(f"Lambda callback: Event value is {value}"))

    # def update_mouse_coordinates(self, mouseMoveEvent):
    def update_mouse_coordinates(self, **kwargs):
        print(f"update_mouse_coordinates:{''}")
        print(kwargs)
        # print(f"update_mouse_coordinates:{mouseMoveEvent}")
        # mouse_x, mouse_y = mouseMoveEvent.x, mouseMoveEvent.y
        # # self.label.text = 'Mouse Coordinates: ({:.2f}, {:.2f})'.format(mouse_pos[0], mouse_pos[1])
        # self.label.text = 'Mouse Coordinates: ({:.2f}, {:.2f})'.format(mouse_x, mouse_y)

    def unregister(self):
        # Unregister the event listener when needed
        EventManager.unregister_listener('on_mouse_move', self.on_mouse_move, self)

class MouseController(EventProducer):
    def __init__(self):


        # 1, étendre la class event dispatcher
        # class MyEventDispatcher(EventDispatcher):
        #     def __init__(self, **kwargs):
        #         self.register_event_type('on_mouse_move')
        #         super(MyEventDispatcher, self).__init__(**kwargs)
        #
        #     def do_something(self, value):
        #         # when do_something is called, the 'on_test' event will be
        #         # dispatched with the value
        #         self.dispatch('on_mouse_move', value)
        #
        #     def on_mouse_move(self, *args):
        #         print("I am dispatched", args)
        # 2, ds __init__ declarer le custom event
        # self.register_event_type('on_mouse_move')
        # 3. il faut créer une métjode qui a la meme nom que l'event name
        # def on_mouse_move(self, *args):
        # 4. faire le bind et triggerer l'event
        # def my_callback(value, *args):
        #     print("Hello, I got an event!", args)
        # ev = MyEventDispatcher()
        # ev.bind(on_test=my_callback)
        # ev.do_something('test')

        EventProducer.__init__(self, event_names=list('on_mouse_move'))
        # EventManager.register_producer(event_name='on_mouse_move', self.on_mouse_motion)

        # Bind the mouse motion event
        Window.bind(mouse_pos=self.on_mouse_motion)

    def on_mouse_motion(self, instance, pos):
        print(f"on_mouse_motion: instance={instance}, pos={pos}")
        mouse_x, mouse_y = pos
        self.dispatch_event('on_mouse_move', MouseMoveEvent(mouse_x, mouse_y))

class ApplicationLayout(BoxLayout):
    def __init__(self, gui_dims, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.event_manager = EventManager()
        self.event_dispatcher = self.event_manager.event_dispatcher

        self.menu_area = MenuArea(gui_dims=gui_dims)
        self.feature_area = FeatureArea(event_name=None, gui_dims=gui_dims)
        self.message_area = MessageArea(event_name=None, gui_dims=gui_dims)

        self.add_widget(self.menu_area)
        self.add_widget(self.feature_area)
        self.add_widget(self.message_area)

class MainApp(App):
    def build(self):
        gui_dims = GUIDimCfg()  # Provide necessary parameters here
        mouse_controller = MouseController()
        return ApplicationLayout(gui_dims=gui_dims)

if __name__ == '__main__':
    MainApp().run()
