import sys
from main_window import *
from filters import *


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()