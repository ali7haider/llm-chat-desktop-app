import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QMessageBox
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread,QTimer
from PyQt5.QtGui import QMouseEvent, QFont
from PyQt5 import QtCore, QtGui, QtWidgets
from main_ui import Ui_MainWindow
from chatModel import ChatModel     
from database import DatabaseManager
import datetime

  # Import create_database from database.py
class ModelFrame(QtWidgets.QFrame):
    modelFrameClicked = pyqtSignal(str, str)  # Custom signal with title and path as parameters

    def mousePressEvent(self, event):
        # Emit the custom signal when the frame is clicked
        self.modelFrameClicked.emit(self.title, self.path)
class ChatHistoryFrame(QtWidgets.QFrame):
    chatHistoryFrameClicked = pyqtSignal(str, str, str)  # Custom signal with message, date, and id as parameters

    def mousePressEvent(self, event):
        # Emit the custom signal when the frame is clicked
        self.chatHistoryFrameClicked.emit(self.message, self.date, self.id)

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
        self.model_path = None  # Initialize model path
        self.active_model_name = None  # Initialize active model
        self.active_model_path=None
        # Call the function to create the database and table
        self.db_manager = DatabaseManager()
        self.db_manager.create_database()
        self.resize(550, 800)  # Set the window size to 800x600 pixels
        # Add frames for all models
        self.add_model_frames()
        self.add_chat_frames()
        # Initialize the chat model
        # Fetch active model path
        self.active_model_path = self.db_manager.get_active_model_path() 
        self.active_model_name = self.get_active_model_name_without_extension()
        # Use active model path to initialize ChatModel and ChatWorker
        self.initialize_chat()
        # Connect the btnAddModel button to open file dialog
        self.btnAddModel.clicked.connect(self.open_file_dialog)
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

    def initialize_chat(self):
        # Check if active model path exists
        if self.active_model_path:
            # Initialize ChatModel and ChatWorker with active model path
            self.model = ChatModel(model_path=self.active_model_path, chat_format="llama-2")
            self.worker = ChatWorker(self.model)
            self.active_model_name = self.get_active_model_name_without_extension()
            self.btnModel.setText(self.active_model_name)

        else:
            print("No active model found!")
    def add_chat_frames(self):
        # Remove any existing model frames
        # for i in reversed(range(self.verticalLayout_42.count())):
        #     self.verticalLayout_42.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.histroyFrame.layout().count())):
            widget = self.histroyFrame.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
       
        chat_history = self.db_manager.fetch_chat_history()
        for chat in chat_history:
            frame = self.create_chat_history_frame(chat)
            frame.chatHistoryFrameClicked.connect(self.handle_history_frame_clicked)
            self.histroyFrame.layout().addWidget(frame)

    def add_model_frames(self):
        # Remove any existing model frames
        for i in reversed(range(self.verticalLayout_42.count())):
            self.verticalLayout_42.itemAt(i).widget().setParent(None)

        # Fetch all models from the database
        models = self.db_manager.fetch_all_models()

        # Add frames for each model
        for model in models:
            frame = self.create_model_frame(model)
            # Connect the model frame's clicked signal to a custom slot
            frame.modelFrameClicked.connect(self.handle_model_frame_clicked)
            self.verticalLayout_42.addWidget(frame)

    def get_active_model_name_without_extension(self):
        active_model_name = self.db_manager.get_active_model_name()  
        if active_model_name:
            model_name_parts = active_model_name.split(".")
            return ".".join(model_name_parts[:-1])
        return None
    
    def handle_history_frame_clicked(self, message, date, id):
        for i in reversed(range(self.specificHistoryFrame.layout().count())):
            widget = self.specificHistoryFrame.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        messages = self.db_manager.fetch_messages_by_session_id(int(id))
        
        for message in messages:
            frame=self.create_chat_message_frame(message[0],message[1])
            self.specificHistoryFrame.layout().addWidget(frame)
            self.stackedWidget.setCurrentIndex(6)


    def handle_model_frame_clicked(self, title, path):
        # Update isActive flag for all models to 0
        self.db_manager.update_all_models_inactive()
        # Set isActive flag to 1 for the clicked model
        self.db_manager.set_model_active(title)
        self.active_model_path = self.db_manager.get_active_model_path()  
        self.active_model_name = self.get_active_model_name_without_extension()

        # Use active model path to initialize ChatModel and ChatWorker
        self.initialize_chat()
        # Update the model frames to reflect the changes
        self.add_model_frames()
    def remove_model(self, model_name):
        # Remove the model from the database
        self.db_manager.remove_model(model_name)
        # Check if any model is active after removal
        self.add_model_frames()
        if not self.db_manager.is_any_model_active():
            self.show_no_active_model_message()
            self.active_model_path=None
            self.active_model_name="No Active Model"
        # Recreate the model frames
    def show_no_active_model_message(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("No Active Model")
        msg_box.setText("No active model found. Please select a model.")
        msg_box.exec_()
    def create_chat_history_frame(self, model):
        # Create the frame for the chat history message
        frame = ChatHistoryFrame()  # Use custom QFrame subclass
        frame.setObjectName("historyFrame")  # Set an object name for the frame
        frame.setStyleSheet("QFrame#historyFrame {background-color:white; border: 2px solid transparent;}")  # Initial styling
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        frame.message = model[1]
        frame.date = model[0]
        frame.id=str(model[2])

        # Create a vertical layout for the frame
        layout = QtWidgets.QVBoxLayout(frame)

        # Create a frame for the message and date
        message_frame = QtWidgets.QFrame()
        message_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        message_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        message_frame.setStyleSheet("background-color: white;")  # Set background color to white

        # Create a horizontal layout for the message frame
        message_layout = QtWidgets.QHBoxLayout(message_frame)
        message_layout.setContentsMargins(0, 0, 0, 0)

        # Create a label for the chat message
        lbl_message = QtWidgets.QLabel(model[1])  # Assuming model[0] is the message
        lbl_message.setStyleSheet("background-color: white;color:black; font: bold 9pt \"Roboto Black\";")
        lbl_message.setWordWrap(True)  # Enable word wrap for the message
        message_layout.addWidget(lbl_message, 3)  # Stretch factor of 3 to take 75% of the space

        # Add spacing between the message and date
        message_layout.addSpacing(10)

        # Create a label for the date
        lbl_date = QtWidgets.QLabel(model[0])  # Assuming model[1] is the date
        lbl_date.setStyleSheet("background-color: white;font: 8pt \"Roboto\"; color:black;")
        lbl_date.setWordWrap(True)  # Enable word wrap for the date
        message_layout.addWidget(lbl_date)

        # Add the message frame to the vertical layout
        layout.addWidget(message_frame)

        return frame

    
    def create_model_frame(self, model):
        # Create the frame for the model message template
        frame = ModelFrame()  # Use custom QFrame subclass
        frame.setObjectName("modelFrame")  # Set an object name for the frame
        frame.setStyleSheet("QFrame#modelFrame {background-color:white; border: 2px solid transparent;}")  # Initial styling
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        frame.title = model[1]
        frame.path = model[2]

        # Check if the model is active (assuming model[3] contains the isActive value)
        is_active = bool(model[3])  # Convert to boolean

        if is_active:
            frame.setStyleSheet("QFrame#modelFrame {background-color:white; border: 2px solid grey;}")  # Add a blue border if active

        # Create a vertical layout for the frame
        layout = QtWidgets.QVBoxLayout(frame)

        # Create a frame for the model name and remove button
        name_frame = QtWidgets.QFrame()
        name_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        name_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        name_frame.setStyleSheet("background-color: white;")  # Set background color to white


        # Create a horizontal layout for the name frame
        name_layout = QtWidgets.QHBoxLayout(name_frame)
        name_layout.setContentsMargins(0, 0, 0, 0)

        # Create a label for the model name
        lbl_model_name = QtWidgets.QLabel(model[1])  # Assuming model[1] is the title/name
        lbl_model_name.setStyleSheet("background-color: white;color:black; font: bold 9pt \"Roboto Black\";")
        lbl_model_name.setWordWrap(True)  # Enable word wrap for the title
        name_layout.addWidget(lbl_model_name, 3)  # Stretch factor of 3 to take 75% of the space


        # Add spacing between the name and remove button
        name_layout.addSpacing(10)

        # Create a button to remove the model
        btn_remove = QtWidgets.QPushButton("Remove")
        btn_remove.setMaximumSize(QtCore.QSize(55, 22))
        btn_remove.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_remove.setStyleSheet("color:#606268; font: 8pt \"Roboto\";")
        btn_remove.setFlat(True)
        name_layout.addWidget(btn_remove, 0, QtCore.Qt.AlignRight)

        # Connect the clicked signal of the remove button to the remove_model function
        btn_remove.clicked.connect(lambda _, model_name=model[1]: self.remove_model(model_name))

        # Add the name frame to the vertical layout
        layout.addWidget(name_frame)

        # Create a label for the model path
        lbl_model_path = QtWidgets.QLabel("Path: " + model[2])  # Assuming model[2] is the path
        lbl_model_path.setStyleSheet("background-color: white;font: 8pt \"Roboto\"; color:black;")
        lbl_model_path.setWordWrap(True)  # Enable word wrap for the title
        layout.addWidget(lbl_model_path)

        return frame



    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # Create a QFileDialog instance with the file filter for .gguf files
        file_dialog = QFileDialog(self, "Select Model File", "", "Model Files (*.gguf)", options=options)

        # Set the background color to white
        file_dialog.setStyleSheet("background-color: white;")

        # Set the file mode to existing files
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        # Get the selected file name and path
        file_name, _ = file_dialog.getOpenFileName()

        if file_name:
            # Extract the file name and path
            file_path = file_name
            file_name = file_name.split('/')[-1]  # Get just the file name

            # Insert the file name and path into the Model table
            self.db_manager.insert_model_into_database(file_name, file_path)
            self.add_model_frames()


    def send_message(self):
        user_question = self.txtChat.text()
        # Check if the user question is blank
        if not user_question:
            self.show_blank_question_message()
            return
        # Check if active_model_path is None
        if self.active_model_path is None:
            self.show_no_active_model_message()
            return
        session_id = self.db_manager.get_or_create_session_id()
        timestamp = datetime.datetime.now()
        
        # Assuming session_id, sender, message_text, and timestamp are available
        self.db_manager.save_message(session_id, "You", user_question, timestamp)
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
        session_id = self.db_manager.get_or_create_session_id()
        timestamp = datetime.datetime.now()
        
        # Assuming session_id, sender, message_text, and timestamp are available
        self.db_manager.save_message(session_id, "AI", response, timestamp)
        self.create_message_frame("AI", response)

        # Remove the loading frame if it exists
        if self.loading_frame:
            self.loading_frame.setParent(None)

        self.txtChat.setReadOnly(False)
        self.chatScroll.updateGeometry()
        self.chatScroll.verticalScrollBar().setValue(self.chatScroll.verticalScrollBar().maximum())  # Scroll to the bottom
        print(self.chatScroll.verticalScrollBar().maximum())  # Print the maximum scroll position
       
    def show_blank_question_message(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Blank Question")
        msg_box.setText("Please enter a question.")
        msg_box.exec_()
    def create_chat_message_frame(self, sender_name, message):
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

        return message_frame

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

            # Load the GIF animation
            loading_movie = QtGui.QMovie(":/images/images/loading.gif")

            # Create a label for the movie
            loading_movie_label = QtWidgets.QLabel()
            loading_movie_label.setMovie(loading_movie)

            # Start the GIF animation
            loading_movie.start()

            # Add the movie label to the loading layout
            loading_layout.addWidget(loading_movie_label)
            loading_layout.setAlignment(Qt.AlignCenter) 

            # Add the loading frame below the message frame
            self.chatFrame.layout().addWidget(loading_frame)

            # Return the loading frame so it can be removed later
            self.loading_frame=loading_frame


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
        self.add_chat_frames()

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
