import PySide2
from main_window import *

class MainInterface(QtWidgets.QMainWindow, Ui_Vinny):
    def __init__(self):
        super().__init__()
        self.setupUi(Vinny)

        QtCore.QObject.connect(self.quick_search, QtCore.SIGNAL("clicked()"), MainInterface.quick_search_slot)

    @QtCore.Slot()
    def quick_search_slot():
        print('search pressed!')

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Vinny = QtWidgets.QMainWindow()
    ui = MainInterface()
    Vinny.show()
    sys.exit(app.exec_())