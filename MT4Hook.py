from pywinauto import application

class MT4Hook:
    def __init__(self):
        self.conn = False
        self.app = application.Application()


    def ConnectApp(self, appName):
        self.conn = self.app.connect(title_re=f".*{appName}*")


    def ConnectionStatus(self):
        if self.conn != False:
            return True
        else:
            return False

    def ClickButton(self, dialog, cls):
        self.app[dialog][cls].click()

    def GetWindowText(self, cls):
        return self.app.Dialog.child_window(class_name=cls).GetWindowText()

    def GetWindowTextStatus(self, cls):
        if self.app.Dialog.child_window(class_name=cls) is not 0:
            return True
        else:
            return False

    def print_control_identifiers_Status(self):
        if self.app.YourDialog.print_control_identifiers() is not 0:
            return True
        else:
            return False

    def getListTexts(self, cls):
        return self.app.Dialog.child_window(class_name=cls).texts()







