import sys
from main_window import *
from filters import *


app = QApplication(sys.argv)

window = Main()
window.show()

app.exec_()