from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout


class GUIComponentDim:
    def __init__(self, **kwargs):
        self.height:int = self.__get_param_by_key__('height', **kwargs)
        self.width:int = self.__get_param_by_key__('width', **kwargs)
        self.spacing_v:int = self.__get_param_by_key__('spacing_v', **kwargs)
        self.spacing_h:int = self.__get_param_by_key__('spacing_h', **kwargs)
        self.font_name:int = self.__get_param_by_key__('font_name', **kwargs)
        self.font_size:int = self.__get_param_by_key__('font_size', **kwargs)

    def get_width(self)->int:
        return self.width
    def get_height(self)->int:
        return self.height

    def get_spacing_v(self)->int:
        return self.spacing_v
    def get_spacing_h(self)->int:
        return self.spacing_h

    def __get_param_by_key__(self, key, default=None, **kwargs):
        if (kwargs):
            if key in kwargs.keys():
                return kwargs[key]
        return default
class GUIDimCfg:

    def __init__(self):
        max_width=1080
        max_height=1920
        self.main_window_size: GUIComponentDim = GUIComponentDim(width=max_width, height=max_height)
        self.main_menu_item_size: GUIComponentDim = GUIComponentDim(width=10, height=30, spacing_h=10)
        self.submenu_item_size: GUIComponentDim = GUIComponentDim(width=10, height=30, spacing_v=10)
        self.header_area_size: GUIComponentDim = GUIComponentDim(width=max_width, height=max_height * 0.2)
        self.feature_area_size: GUIComponentDim = GUIComponentDim(width=max_width, height=max_height * 0.7)
        self.footer_size: GUIComponentDim = GUIComponentDim(width=max_width, height=max_height * 0.1)
        # self._size = GUIComponentDimension(width=, height=)
        # self._size = GUIComponentDimension(width=, height=)
        # self._size = GUIComponentDimension(width=, height=)

        self.general_font = GUIComponentDim(font_name='Arial', fonst_size=12)
        self.main_menu_item_font = GUIComponentDim(font_name='Arial', fonst_size=12)
        self.submenu_item_font = GUIComponentDim(font_name='Arial', fonst_size=12)



class MenuArea(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gui_dims: GUIDimCfg = kwargs['gui_dims']

        self.size_hint_y = None
        self.height = self.gui_dims.main_menu_item_size.get_height()
        self.width = self.gui_dims.main_menu_item_size.get_width()
        self.spacing = 10

        # Requirement 1.a.2: Three main menu items grouped on the left side
        left_menu_items_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
        self.add_widget(left_menu_items_anchor_layout)
        right_menu_items_anchor_layout = AnchorLayout(anchor_x='right', anchor_y='top')
        self.add_widget(right_menu_items_anchor_layout)
        menu_items = ["Apps", "Config", "Help"]
        x_position = 0
        for item in menu_items:
            btn = Button(text=item, size_hint=(None, 1), width=self.width, pos=(x_position, 0))
            x_position += btn.width + self.spacing
            left_menu_items_anchor_layout.add_widget(btn)

        # Requirement 1.a.3: Quit button set on the top right
        quit_button = Button(text="Quit", size_hint=(None, 1), width=self.width, pos=(self.width - 100, 0))
        quit_button.bind(on_release=self.quit_app)
        self.add_widget(quit_button)
        right_menu_items_anchor_layout.add_widget(quit_button)

    # Requirement 1.a.4: Quit button closes the application
    def quit_app(self, instance):
        App.get_running_app().stop()

class FeatureArea(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gui_dims: GUIDimCfg = kwargs['gui_dims']

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 300

        # Requirement A.6: Event messages can be used between components
        self.bind(on_touch_move=self.on_touch_move)

    def on_touch_move(self, instance, touch):
        # Example of event handling (printing touch coordinates)
        if self.collide_point(*touch.pos):
            print('Touch coordinates:', touch.pos)

class MessageArea(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gui_dims: GUIDimCfg = kwargs['gui_dims']

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 30
        self.add_widget(Label(text='Message Area'))

class ApplicationLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gui_dims: GUIDimCfg = kwargs['gui_dims']

        self.orientation = 'vertical'

        self.menu_area = MenuArea(gui_dims=self.gui_dims)
        self.feature_area = FeatureArea(gui_dims=self.gui_dims)
        self.message_area = MessageArea(gui_dims=self.gui_dims)

        self.add_widget(self.menu_area)
        self.add_widget(self.feature_area)
        self.add_widget(self.message_area)

class MainApp(App):
    def __init__(self):
        self.gui_dims: GUIDimCfg = GUIDimCfg()
    def build(self):
        return ApplicationLayout(gui_dims=self.gui_dims)

if __name__ == '__main__':
    MainApp().run()
