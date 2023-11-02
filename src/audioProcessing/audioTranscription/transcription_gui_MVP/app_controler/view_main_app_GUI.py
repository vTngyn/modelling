from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC

class view_main_app_gui(LEC):
    def __init__(self):
        self.initialize_gui()
        pass

    def initialize_gui(self):
        pass

    def run(self, presenter:PresentationMainAppGUI):
        # self.root.mainloop()
        # while True:
        #     time.sleep(1)
        self.presenter = presenter
        self.__initialize_module__()

