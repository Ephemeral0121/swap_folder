from PyQt5 import QtWidgets, QtCore
from pathlib import Path
import json
import os
import shutil


class FolderManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.directories = self.load_directories()
        self.all_keywords = self.load_keywords()
        self.keywords = self.all_keywords.copy()
        self.current_keyword = None
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.center()

        layout = QtWidgets.QVBoxLayout()

        select_target_folder_button = QtWidgets.QPushButton('Select target directory')
        select_target_folder_button.clicked.connect(lambda: self.select_directory("target"))
        layout.addWidget(select_target_folder_button)

        self.target_folder_label = QtWidgets.QLabel(self.directories.get("target", ""))
        layout.addWidget(self.target_folder_label)

        select_source_folder_button = QtWidgets.QPushButton('Select source directory')
        select_source_folder_button.clicked.connect(lambda: self.select_directory("source"))
        layout.addWidget(select_source_folder_button)

        self.source_folder_label = QtWidgets.QLabel(self.directories.get("source", ""))
        layout.addWidget(self.source_folder_label)

        self.keyword_entry = QtWidgets.QLineEdit()
        self.keyword_entry.returnPressed.connect(self.register_keyword)
        layout.addWidget(self.keyword_entry)

        register_keyword_button = QtWidgets.QPushButton('Register keyword')
        register_keyword_button.clicked.connect(self.register_keyword)
        layout.addWidget(register_keyword_button)

        sort_layout = QtWidgets.QHBoxLayout()
        sort_alphabet_button = QtWidgets.QPushButton('Sort by alphabet')
        sort_alphabet_button.clicked.connect(self.sort_by_alphabet)
        sort_layout.addWidget(sort_alphabet_button)

        sort_register_button = QtWidgets.QPushButton('Sort by register')
        sort_register_button.clicked.connect(self.sort_by_register)
        sort_layout.addWidget(sort_register_button)

        layout.addLayout(sort_layout)

        self.keyword_search_entry = QtWidgets.QLineEdit()
        self.keyword_search_entry.textChanged.connect(self.search_keyword)
        layout.addWidget(self.keyword_search_entry)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.keywords_widget = QtWidgets.QWidget()
        self.keywords_layout = QtWidgets.QGridLayout(self.keywords_widget)

        self.rearrange_keywords()

        self.scrollArea.setWidget(self.keywords_widget)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def select_directory(self, type):
        selected_directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select the directory', '', QtWidgets.QFileDialog.ShowDirsOnly)

        if selected_directory:
            self.directories[type] = selected_directory
            if type == "target":
                self.target_folder_label.setText(selected_directory)
            else:
                self.source_folder_label.setText(selected_directory)
            self.save_directories()

    def register_keyword(self):
        new_keyword = self.keyword_entry.text().lower()

        if new_keyword and new_keyword not in self.all_keywords:
            self.all_keywords.append(new_keyword)
            self.keywords = self.all_keywords.copy()
            self.keyword_search_entry.clear()
            self.rearrange_keywords()
            self.save_keywords()
            self.keyword_entry.clear()

    def search_keyword(self):
        search_keyword = self.keyword_search_entry.text().lower()

        if search_keyword:
            self.keywords = [keyword for keyword in self.all_keywords if search_keyword in keyword.lower()]
        else:
            self.keywords = self.all_keywords.copy()

        self.rearrange_keywords()

    def sort_by_alphabet(self):
        self.keywords.sort(key=str.lower)
        self.rearrange_keywords()

    def sort_by_register(self):
        self.keywords = self.load_keywords()
        self.rearrange_keywords()

    def rearrange_keywords(self):
        for i in reversed(range(self.keywords_layout.count())): 
            self.keywords_layout.itemAt(i).widget().setParent(None)

        for keyword in self.keywords:
            self.add_keyword_button(keyword)

    def add_keyword_button(self, keyword):
        keyword_button = QtWidgets.QPushButton(keyword)
        keyword_button.clicked.connect(lambda: self.handle_keyword_click(keyword))
        keyword_button.setFixedSize(200, 50)

        delete_button = QtWidgets.QPushButton("X")
        delete_button.clicked.connect(lambda: self.delete_keyword(keyword))
        delete_button.setFixedSize(50, 50)

        index = self.keywords.index(keyword)
        row, col = divmod(index, 2)
        self.keywords_layout.addWidget(keyword_button, row, 2*col)
        self.keywords_layout.addWidget(delete_button, row, 2*col+1)

    def delete_keyword(self, keyword):
        self.keywords.remove(keyword)
        self.all_keywords.remove(keyword) 
        self.rearrange_keywords()
        self.save_keywords()

    def handle_keyword_click(self, keyword):
        if "source" not in self.directories or "target" not in self.directories:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select the source and target directories first.")
            return

        self.current_keyword = keyword
        self.checkbox_window = CheckboxWindow(self.directories, self.current_keyword)
        self.checkbox_window.show()

    def load_directories(self):
        if not os.path.isfile('directories.json'):
            return {}

        with open('directories.json', 'r') as file:
            return json.load(file)

    def save_directories(self):
        with open('directories.json', 'w') as file:
            json.dump(self.directories, file)

    def load_keywords(self):
        if not os.path.isfile('keywords.json'):
            return []

        with open('keywords.json', 'r') as file:
            return json.load(file)

    def save_keywords(self):
        with open('keywords.json', 'w') as file:
            json.dump(self.all_keywords, file)



class CheckboxWindow(QtWidgets.QWidget):
    def __init__(self, directories, current_keyword):
        super().__init__()

        self.directories = directories
        self.current_keyword = current_keyword
        self.checkboxes = []
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 400, 600)
        self.center()

        layout = QtWidgets.QVBoxLayout()

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollAreaWidget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(scrollAreaWidget)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        scrollArea.setWidget(scrollAreaWidget)
        layout.addWidget(scrollArea)
        self.setLayout(layout)

        self.load_checkboxes()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_checkboxes(self):
        target_folder = Path(self.directories["target"])
        source_folder = Path(self.directories["source"])

        target_folders = {folder.name: folder for folder in target_folder.iterdir() if self.current_keyword.lower() in folder.name.lower()}
        source_folders = {folder.name: folder for folder in source_folder.iterdir() if self.current_keyword.lower() in folder.name.lower()}

        folders_dict = {**source_folders, **target_folders}

        for checkbox in self.checkboxes:
            checkbox.setParent(None)

        self.checkboxes.clear()

        for folder_name, folder_path in folders_dict.items():
            checkbox = QtWidgets.QCheckBox(folder_name)
            checkbox.setChecked(folder_path in target_folders.values())

            checkbox.stateChanged.connect(lambda state, f_path=folder_path: self.handle_checkbox_state(state, f_path))

            self.checkboxes.append(checkbox)
            self.layout.addWidget(checkbox)

    def handle_checkbox_state(self, state, folder_path):
        target_folder = Path(self.directories["target"])
        source_folder = Path(self.directories["source"])

        if state == QtCore.Qt.Checked:
            if (source_folder / folder_path.name).exists():
                shutil.move(str(source_folder / folder_path.name), str(target_folder / folder_path.name))

            for checkbox in self.checkboxes:
                if checkbox.text() != folder_path.name and checkbox.isChecked():
                    checkbox.setChecked(False)
        else:
            if (target_folder / folder_path.name).exists():
                shutil.move(str(target_folder / folder_path.name), str(source_folder / folder_path.name))


def main():
    app = QtWidgets.QApplication([])

    window = FolderManager()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()