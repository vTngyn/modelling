from kivy.event import EventDispatcher

class CustomEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_params = {}

    def bind_event(self, event_name, callback, event_params=None):
        if event_params is None:
            event_params = {}
        self.event_params[event_name] = event_params
        self.bind(**{event_name: callback})

    def on_my_event(self, value):
        event_name = self.event_params.get('on_event', 'Unknown Event')
        print(f"My event '{event_name}' triggered with value: {value}")

# Instantiate the custom event dispatcher
event_dispatcher = CustomEventDispatcher()

# Bind the callback function
event_dispatcher.bind_event('on_event', event_dispatcher.on_my_event, event_params={'on_event': 'My Event'})

# Trigger the event
EventDispatcher().dispatch('on_event', 42)
# event_dispatcher.dispatch('on_event', 42)
