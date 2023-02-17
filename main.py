import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, \
	QLineEdit, QDialog, QVBoxLayout, QComboBox, QMainWindow, \
	QTableWidget, QStatusBar, QTableWidgetItem, QToolBar, \
	QGridLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import mysql.connector


class DatabaseConnection:
	def __init__(self, host="localhost", user="root", password="BhasUS!2", database="school"):
		self.host = host
		self.user = user
		self.password = password
		self.database = database
	
	def connect(self):
		conn = mysql.connector.connect(host=self.host, user=self.user,
		                               password=self.password, database=self.database)
		return conn


# Main Window class
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Student Management System. Peak State')
		self.setMinimumSize(500, 500)

		file_menu_item = self.menuBar().addMenu('&File')
		help_menu_item = self.menuBar().addMenu('&Help')

		add_student_action = QAction(QIcon("icons/add.png"), 'Add Student', self)
		add_student_action.triggered.connect(self.add_student)
		file_menu_item.addAction(add_student_action)

		refresh_students_action = QAction(QIcon("icons/refresh-button.png"), 'Refresh Students', self)
		refresh_students_action.triggered.connect(self.refresh_students)
		file_menu_item.addAction(refresh_students_action)

		about_action = QAction('About', self)
		about_action.triggered.connect(self.about)
		help_menu_item.addAction(about_action)

		support_action = QAction('Support', self)
		help_menu_item.addAction(support_action)

		search_action = QAction(QIcon("icons/search.png"), 'Search', self)
		search_action.triggered.connect(self.search)
		file_menu_item.addAction(search_action)

		self.table = QTableWidget()
		self.table.setColumnCount(4)
		self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Course', 'Phone Number'])
		self.table.verticalHeader().setVisible(False)
		self.setCentralWidget(self.table)

		toolbar = QToolBar()
		toolbar.setMovable(True)
		toolbar.addAction(add_student_action)
		toolbar.addAction(search_action)
		toolbar.addAction(refresh_students_action)

		self.addToolBar(toolbar)
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)
		self.table.cellClicked.connect(self.cell_clicked)

	def cell_clicked(self):
		edit_button = QPushButton('Edit Record')
		edit_button.clicked.connect(self.edit)

		delete_button = QPushButton('Delete Record')
		delete_button.clicked.connect(self.delete)

		children = self.findChildren(QPushButton)
		if children:
			for child in children:
				self.status_bar.removeWidget(child)

		self.status_bar.addWidget(edit_button)
		self.status_bar.addWidget(delete_button)

	@staticmethod
	def edit():
		edit_dialog = EditDialog()
		edit_dialog.exec()

	@staticmethod
	def delete():
		delete_dialog = DeleteDialog()
		delete_dialog.exec()

	def load_data(self):
		connection = DatabaseConnection().connect()
		cursor = connection.cursor()
		cursor.execute('SELECT * FROM students')
		results = cursor.fetchall()
		self.table.setRowCount(0)
		for result_number, result_data in enumerate(results):
			self.table.insertRow(result_number)
			for cell_number, cell_data in enumerate(result_data):
				self.table.setItem(result_number, cell_number, QTableWidgetItem(str(cell_data)))
		connection.close()

	@staticmethod
	def add_student():
		dialog = InsertDialog()
		dialog.exec()

	@staticmethod
	def search():
		search_dialog = SearchDialog()
		search_dialog.exec()

	@staticmethod
	def about():
		about_dialog = AboutDialog()
		about_dialog.exec()

	@staticmethod
	def refresh_students():
		main_window.load_data()


# All Dialog Classes
# This class is used to add students
class InsertDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Add Student')
		self.setFixedSize(300, 400)

		layout = QVBoxLayout()

		self.student_name = QLineEdit()
		self.student_name.setPlaceholderText('Student Name')
		layout.addWidget(self.student_name)

		self.student_course = QComboBox()
		courses = ["Biology", "Math", "Astronomy", "Physics"]
		self.student_course.addItems(courses)
		layout.addWidget(self.student_course)

		self.student_phone = QLineEdit()
		self.student_phone.setPlaceholderText('Student Phone Number')
		layout.addWidget(self.student_phone)

		button = QPushButton('Add Student')
		button.clicked.connect(self.add_student)
		layout.addWidget(button)

		self.setLayout(layout)

	def add_student(self):
		connection = DatabaseConnection().connect()
		cursor = connection.cursor()
		cursor.execute('INSERT INTO students (name, course, mobile) VALUES (%s,%s,%s)',
		               (self.student_name.text(), self.student_course.itemText(self.student_course.currentIndex()),
		                self.student_phone.text()))
		connection.commit()
		cursor.close()
		connection.close()
		main_window.load_data()
		self.close()


# This class is used to search for students
class SearchDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Search Student')
		self.setFixedSize(300, 300)

		layout = QVBoxLayout()

		self.student_name = QLineEdit()
		self.student_name.setPlaceholderText('Student Name')
		layout.addWidget(self.student_name)

		button = QPushButton('Search Student')
		button.clicked.connect(self.search_student)
		layout.addWidget(button)

		self.setLayout(layout)

	def search_student(self):
		name = self.student_name.text()
		connection = DatabaseConnection().connect()
		cursor = connection.cursor()
		cursor.execute('SELECT * FROM students WHERE name = %s', (name,))
		result = cursor.fetchall()
		items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
		for item in items:
			main_window.table.item(item.row(), 1).setSelected(True)

		cursor.close()
		connection.close()
		self.close()


# This class is used to edit students
class EditDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Edit Record')
		self.setFixedSize(300, 300)

		layout = QVBoxLayout()

		index = main_window.table.currentRow()
		student_name = main_window.table.item(index, 1).text()
		self.student_name = QLineEdit(student_name)
		self.student_name.setPlaceholderText('Student Name')
		layout.addWidget(self.student_name)

		course = main_window.table.item(index, 2).text()
		self.student_course = QComboBox()
		courses = ["Biology", "Math", "Astronomy", "Physics"]
		self.student_course.addItems(courses)
		self.student_course.setCurrentText(course)
		layout.addWidget(self.student_course)

		phone = main_window.table.item(index, 3).text()
		self.student_phone = QLineEdit(phone)
		self.student_phone.setPlaceholderText('Student Phone Number')
		layout.addWidget(self.student_phone)

		self.student_id = main_window.table.item(index, 0).text()

		button = QPushButton('Edit Record')
		button.clicked.connect(self.edit_student)
		layout.addWidget(button)

		self.setLayout(layout)

	def edit_student(self):
		connection = DatabaseConnection().connect()
		cursor = connection.cursor()
		cursor.execute('UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s',
		               (self.student_name.text(),
		                self.student_course.itemText(self.student_course.currentIndex()),
		                self.student_phone.text(), self.student_id))
		connection.commit()
		cursor.close()
		connection.close()
		self.close()
		main_window.load_data()


# This class is used to delete students
class DeleteDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Delete Record')
		layout = QGridLayout()

		confirmation_message = QLabel('Are you sure you want to delete this record?')
		layout.addWidget(confirmation_message, 0, 0, 1, 2)

		button = QPushButton('Yes, Delete Record')
		button.clicked.connect(self.delete_student)
		layout.addWidget(button, 1, 0)

		button = QPushButton('No, Cancel')
		button.clicked.connect(self.close)
		layout.addWidget(button, 1, 1)

		self.setLayout(layout)

	def delete_student(self):
		connection = DatabaseConnection().connect()
		cursor = connection.cursor()
		index = main_window.table.currentRow()
		student_id = main_window.table.item(index, 0).text()
		cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
		connection.commit()
		cursor.close()
		connection.close()
		self.close()
		main_window.load_data()

		confirmation_widget = QMessageBox()
		confirmation_widget.setWindowTitle("Success")
		confirmation_widget.setText('Record Deleted')


# This is the about page
class AboutDialog(QMessageBox):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('About')
		content = """
This is a simple application that allows you to add, edit and delete students from the database. This application was built using PyQt6, the professional Python Desktop GUI development library. This application was developed by GamerXZEN as an open-source project. Feel free to create your own application, and feel free to contribute.

Author: GamerXZEN"""
		self.setText(content)


# This is the execution code
if __name__ == "__main__":
	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.load_data()
	main_window.show()
	sys.exit(app.exec())
