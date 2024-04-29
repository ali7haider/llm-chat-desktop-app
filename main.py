import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QFont

from main_ui import Ui_MainWindow  # Import the generated class

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from the generated class
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)  # Add Qt.Window flag
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Set background color to transparent
        self.resize(550, 800)  # Set the window size to 800x600 pixels

        # Connect the btnBrowse button to open file dialog
        self.btnClose.clicked.connect(self.close)
        self.btnModel.clicked.connect(self.btnModelClicked)
        self.btnChat.clicked.connect(self.btnChatClicked)
        self.btnHistory.clicked.connect(self.btnHistoryClicked)
        self.btnPlugins.clicked.connect(self.btnPluginsClicked)
        self.btnNext.clicked.connect(self.btnNextClicked)

        
        # Initialize variables to keep track of the last clicked button
        self.last_clicked_button = None

        # Set the default page of the stack widget
        self.stackedWidget.setCurrentIndex(0)

    # Define the mousePressEvent method to handle mouse button press events
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def setBold(self,flag=None):
        # Get the button that triggered the event
        sender_button = self.sender()
        if flag=="Next":
            sender_button = self.btnChat
        

        # Create a style sheet string by combining existing style sheet with font-weight: bold
        existing_stylesheet = sender_button.styleSheet()
        bold_stylesheet = existing_stylesheet + "font-weight: bold;"

        # Set the style sheet of the clicked button to include font-weight: bold
        sender_button.setStyleSheet(bold_stylesheet)

        # Reset the style sheet of the last clicked button to its original state
        if self.last_clicked_button and self.last_clicked_button != sender_button:
            self.last_clicked_button.setStyleSheet(existing_stylesheet)

        # Update the last clicked button
        self.last_clicked_button = sender_button

    # Method to handle btnModel click event
    def btnModelClicked(self):
        self.setBold()
        self.stackedWidget.setCurrentIndex(4)

    # Method to handle btnChat click event
    def btnChatClicked(self):
        self.setBold()
        self.stackedWidget.setCurrentIndex(1)

    # Method to handle btnHistory click event
    def btnHistoryClicked(self):
        self.setBold()
        self.stackedWidget.setCurrentIndex(2)

    # Method to handle btnPlugins click event
    def btnPluginsClicked(self):
        self.setBold()
        self.stackedWidget.setCurrentIndex(3)
    def btnNextClicked(self):
        # Make btnChat bold
        self.setBold("Next")
        # Set the current index of the stacked widget
        self.stackedWidget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
