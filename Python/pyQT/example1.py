from PyQt5.QtWidgets import *

app = QApplication([])
app.setApplicationName("Text Editor")
text = QPlainTextEdit()

window = QMainWindow()
window.setWindowTitle("Text Editor")
window.setCentralWidget(text)

menu = window.menuBar().addMenu("&File")
close = QAction("&Close")

close.triggered.connect(window.close)
menu.addAction(close)

window.show()
app.exec()
