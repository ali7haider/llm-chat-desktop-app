import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QMouseEvent, QFont
from PyQt5 import QtCore, QtGui, QtWidgets
from main_ui import Ui_MainWindow
from chatModel import ChatModel  # type: ignore # Import the ChatModel class

class ChatWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, model):
        super().__init__()
        self.model = model

    def process_question(self, question):
        print("process_question called")
        try:
            response = self.model.generate_response(question)
            return response
        except Exception as e:
            print("Error:", e)
            self.finished.emit(str(e))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from the generated class
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)  # Add Qt.Window flag
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Set background color to transparent
        self.stackedWidget.setCurrentIndex(0)
        self.last_clicked_button=None

        self.resize(550, 800)  # Set the window size to 800x600 pixels

        # Initialize the chat model
        self.model = ChatModel(model_path="./stablelm-zephyr-3b.Q3_K_S.gguf", chat_format="llama-2")
        self.worker = ChatWorker(self.model)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.process_question)
        self.worker.finished.connect(self.on_response_received)

        # Set a flag to track if the thread has been started
        self.thread_started = False
        chat_history=[]

        # Connect the btnBrowse button to open file dialog
        self.btnClose.clicked.connect(self.close)
        self.btnModel.clicked.connect(self.btnModelClicked)
        self.btnChat.clicked.connect(self.btnChatClicked)
        self.btnHistory.clicked.connect(self.btnHistoryClicked)
        self.btnPlugins.clicked.connect(self.btnPluginsClicked)
        self.btnNext.clicked.connect(self.btnNextClicked)

        # Connect the sendMessage button to send the message for processing
        self.btnSendMessage.clicked.connect(self.send_message)

    def send_message(self):
        user_question = self.txtChat.text()
        self.create_message_frame("You",user_question)
        self.txtChat.clear()
        response=self.worker.process_question(user_question)
        self.on_response_received(response)
    def on_response_received(self, response):
        # Display the response in the chat window
        print("Model response:", response)  # Print the response to the console
        self.create_message_frame("AI",response)

    def create_message_frame(self, sender_name, message):
        # Create a new frame for the message
        message_frame = QtWidgets.QFrame()
        message_frame.setStyleSheet("background-color:white;")
        message_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        message_frame.setFrameShadow(QtWidgets.QFrame.Raised)
         # Set minimum height for the message frame
        message_frame.setMinimumHeight(50)  # Adjust the height as needed
        
        # Create a vertical layout for the message frame
        vertical_layout = QtWidgets.QVBoxLayout(message_frame)
        vertical_layout.setContentsMargins(8, 8, 8, 8)

        # Add label for sender name
        lbl_sender_name = QtWidgets.QLabel(sender_name)
        lbl_sender_name.setStyleSheet("color:black;")
        vertical_layout.addWidget(lbl_sender_name)

        # Add label for message
        lbl_message = QtWidgets.QLabel(message)
        lbl_message.setStyleSheet("font: 8pt \"Roboto\";\n"
                                "color:black;")
        lbl_message.setWordWrap(True)
        vertical_layout.addWidget(lbl_message)

        # Add the message frame to the ChatFrame
        self.chatFrame.layout().addWidget(message_frame)

        

    # Define the mousePressEvent method to handle mouse button press events
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def setBold(self, flag=None):
        # Get the button that triggered the event
        sender_button = self.sender()
        if flag == "Next":
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
