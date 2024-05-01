import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread,QTimer
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
        try:
            response = self.model.generate_response(question)
            return response
        except Exception as e:
            print("Error:", e)
            self.finished.emit(str(e))

class TimerThread(QThread):
    timeout_signal = pyqtSignal(str)

    def __init__(self, user_question, worker):
        super().__init__()
        self.user_question = user_question
        self.worker = worker

    def run(self):
        try:
            response = self.worker.process_question(self.user_question)
            self.timeout_signal.emit(response)
        except Exception as e:
            print("Error:", e)
            self.timeout_signal.emit("Error occurred while processing the question.")


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
        self.flag=False
        # Initialize loading_frame to None
        self.loading_frame = None

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
        print(user_question)
        self.create_message_frame("You", user_question,True)
        self.chatScroll.updateGeometry()
        self.chatScroll.verticalScrollBar().setValue(self.chatScroll.verticalScrollBar().maximum())  # Scroll to the bottom
        print(self.chatScroll.verticalScrollBar().maximum())  # Print the maximum scroll position

        self.txtChat.clear()
        self.txtChat.setReadOnly(True)
        if self.flag==False:
            self.lblQuery.deleteLater() 
            self.flag=True


        # Create a timer thread
        self.timer_thread = TimerThread(user_question, self.worker)
        self.timer_thread.timeout_signal.connect(self.on_timer_timeout)

        # Start the timer thread
        self.timer_thread.start()

    def on_timer_timeout(self, response):
        # Pass the response to on_response_received method
        self.on_response_received(response)
    def on_response_received(self, response):
        # Remove leading and trailing spaces from the response
        response = response.strip()

        # Display the response in the chat window
        print("Model response:", response)  # Print the response to the console
        self.create_message_frame("AI", response)

        # Remove the loading frame if it exists
        if self.loading_frame:
            self.loading_frame.setParent(None)

        self.txtChat.setReadOnly(False)
        self.chatScroll.updateGeometry()
        self.chatScroll.verticalScrollBar().setValue(self.chatScroll.verticalScrollBar().maximum())  # Scroll to the bottom
        print(self.chatScroll.verticalScrollBar().maximum())  # Print the maximum scroll position
       
    def create_message_frame(self, sender_name, message, loading=False):
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

        if loading:
            # Create a new frame for the loading label
            loading_frame = QtWidgets.QFrame()
            loading_frame.setStyleSheet("background-color: transparent;")
            loading_frame.setFrameShape(QtWidgets.QFrame.NoFrame)

            # Create a vertical layout for the loading frame
            loading_layout = QtWidgets.QVBoxLayout(loading_frame)
            loading_layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins here to reduce space


            # Load the image
            logo_image = QtGui.QPixmap(":/images/images/loading.png")

            # Create a label for the image
            loading_image_label = QtWidgets.QLabel()
            loading_image_label.setPixmap(logo_image)
            loading_image_label.setPixmap(logo_image.scaled(100, 30))  # Set the desired size (64x64)

            loading_image_label.setAlignment(QtCore.Qt.AlignCenter)  # Align the image to the center

            # Add the image label to the loading layout
            loading_layout.addWidget(loading_image_label)

            # Add the loading frame below the message frame
            self.chatFrame.layout().addWidget(loading_frame)

            

            # Return the loading frame so it can be removed later
            self.loading_frame = loading_frame

        return None



        

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
