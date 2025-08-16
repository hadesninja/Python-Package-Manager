import sys
import subprocess
import importlib.metadata
import requests
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QHeaderView, QLabel, QLineEdit,
    QProgressDialog, QMenuBar, QAction, QSplashScreen, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer


class PipWorker(QThread):
    finished = pyqtSignal(str, bool)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip"] + self.args,
                capture_output=True, text=True
            )
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            self.finished.emit(output, success)
        except Exception as e:
            self.finished.emit(str(e), False)


class PythonPackageManager(QWidget):
    VERSION = "1.2.0"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Package Manager")
        self.setWindowIcon(QIcon("assets/pypkgmgr.ico"))
        self.resize(950, 650)

        # ----- Menu Bar -----
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu("File")
        help_menu = self.menu_bar.addMenu("Help")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        layout = QVBoxLayout()
        layout.setMenuBar(self.menu_bar)

        # Installed Packages Section
        layout.addWidget(QLabel("Installed Packages"))

        self.filter_box = QLineEdit()
        self.filter_box.setPlaceholderText("Filter installed packages...")
        self.filter_box.textChanged.connect(self.filter_installed_packages)
        layout.addWidget(self.filter_box)

        self.installed_table = QTableWidget()
        self.installed_table.setColumnCount(4)
        self.installed_table.setHorizontalHeaderLabels(
            ["Name", "Installed Version", "Latest Version", "Manage"]
        )
        self.installed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.installed_table)

        # Available Packages Section
        layout.addWidget(QLabel("Search Packages on PyPI"))

        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter package name to search on PyPI...")
        self.search_box.returnPressed.connect(self.search_package)

        self.search_mode = QComboBox()
        self.search_mode.addItems(["Exact Match", "Contains"])

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_package)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_mode)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        self.available_table = QTableWidget()
        self.available_table.setColumnCount(3)
        self.available_table.setHorizontalHeaderLabels(["Name", "Latest Version", "Manage"])
        self.available_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.available_table)

        self.setLayout(layout)

        # Cache installed packages
        self.installed = {dist.metadata["Name"].lower(): dist.version
                          for dist in importlib.metadata.distributions()}

        # Load installed packages
        self.load_installed_packages()

    # ----- Menu About Dialog -----
    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Python Package Manager",
            f"""
            <h2>Python Package Manager</h2>
            <p><b>Version:</b> {self.VERSION}</p>
            <p>This tool allows you to manage Python packages:
            install, update, uninstall, and search from PyPI.</p>
            <p><b>Developed by:</b> Vaibhav Patil</p>
            """
        )

    def run_pip_command(self, args, action_msg, package_name):
        progress = QProgressDialog(f"{action_msg} {package_name}...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.setCancelButton(None)
        progress.show()

        self.thread = PipWorker(args)
        self.thread.finished.connect(
            lambda output, success:
            self.on_pip_finished(progress, action_msg, package_name, output, success)
        )
        self.thread.start()

    def on_pip_finished(self, progress, action_msg, package_name, output, success):
        progress.close()
        if success:
            QMessageBox.information(
                self, "Success", f"{package_name} {action_msg.lower()}ed successfully."
            )
        else:
            QMessageBox.critical(
                self, "Error", f"Failed to {action_msg.lower()} {package_name}.\n\n{output}"
            )
        self.load_installed_packages()
        self.search_package()  # refresh available list also

    def load_installed_packages(self):
        self.installed_table.setRowCount(0)
        self.installed = {dist.metadata["Name"].lower(): dist.version
                          for dist in importlib.metadata.distributions()}

        for row, (name, version) in enumerate(self.installed.items()):
            latest_version = self.get_latest_version(name)
            self.installed_table.insertRow(row)
            self.installed_table.setItem(row, 0, QTableWidgetItem(name))
            self.installed_table.setItem(row, 1, QTableWidgetItem(version))
            self.installed_table.setItem(row, 2, QTableWidgetItem(latest_version))

            # Manage buttons
            update_btn = QPushButton("Update")
            uninstall_btn = QPushButton("Uninstall")

            if latest_version == "-" or version == latest_version:
                update_btn.setDisabled(True)

            update_btn.clicked.connect(lambda _, pkg=name: self.update_package(pkg))
            uninstall_btn.clicked.connect(lambda _, pkg=name: self.uninstall_package(pkg))

            container = QWidget()
            inner_layout = QHBoxLayout(container)
            inner_layout.addWidget(update_btn)
            inner_layout.addWidget(uninstall_btn)
            inner_layout.setContentsMargins(0, 0, 0, 0)
            self.installed_table.setCellWidget(row, 3, container)

    def filter_installed_packages(self):
        text = self.filter_box.text().lower()
        for row in range(self.installed_table.rowCount()):
            item = self.installed_table.item(row, 0)
            self.installed_table.setRowHidden(row, text not in item.text().lower())

    def get_latest_version(self, package_name):
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()["info"]["version"]
        except Exception:
            pass
        return "-"

    def update_package(self, package_name):
        self.run_pip_command(["install", "--upgrade", package_name], "Updating", package_name)

    def uninstall_package(self, package_name):
        self.run_pip_command(["uninstall", "-y", package_name], "Uninstalling", package_name)

    def install_package(self, package_name):
        self.run_pip_command(["install", package_name], "Installing", package_name)

    def search_package(self):
        query = self.search_box.text().strip().lower()
        if not query:
            return

        self.available_table.setRowCount(0)

        mode = self.search_mode.currentText()

        if mode == "Exact Match":
            # Query only that package
            latest_version = self.get_latest_version(query)
            if latest_version == "-":
                QMessageBox.warning(self, "Not Found", f"No package found with exact name '{query}'.")
                return

            row = self.available_table.rowCount()
            self.available_table.insertRow(row)
            self.available_table.setItem(row, 0, QTableWidgetItem(query))
            self.available_table.setItem(row, 1, QTableWidgetItem(latest_version))

            if query in self.installed:
                installed_version = self.installed[query]
                if latest_version != "-" and installed_version == latest_version:
                    manage_btn = QPushButton("Installed")
                    manage_btn.setDisabled(True)
                else:
                    manage_btn = QPushButton("Update")
                    manage_btn.clicked.connect(lambda _, pkg=query: self.update_package(pkg))
            else:
                manage_btn = QPushButton("Install")
                manage_btn.clicked.connect(lambda _, pkg=query: self.install_package(pkg))

            self.available_table.setCellWidget(row, 2, manage_btn)

        else:  # Contains
            try:
                url = "https://pypi.org/simple/"
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", "Failed to fetch package list from PyPI.")
                    return

                matches = [line.split('>')[1].split('<')[0]
                           for line in response.text.splitlines()
                           if query in line.lower()]
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Search failed: {e}")
                return

            for row, pkg_name in enumerate(matches[:50]):
                latest_version = self.get_latest_version(pkg_name)
                self.available_table.insertRow(row)
                self.available_table.setItem(row, 0, QTableWidgetItem(pkg_name))
                self.available_table.setItem(row, 1, QTableWidgetItem(latest_version))

                if pkg_name.lower() in self.installed:
                    installed_version = self.installed[pkg_name.lower()]
                    if latest_version != "-" and installed_version == latest_version:
                        manage_btn = QPushButton("Installed")
                        manage_btn.setDisabled(True)
                    else:
                        manage_btn = QPushButton("Update")
                        manage_btn.clicked.connect(lambda _, pkg=pkg_name: self.update_package(pkg))
                else:
                    manage_btn = QPushButton("Install")
                    manage_btn.clicked.connect(lambda _, pkg=pkg_name: self.install_package(pkg))

                self.available_table.setCellWidget(row, 2, manage_btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Splash screen while loading packages
    splash_pix = QPixmap("assets/splash.png")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.showMessage("Fetching installed Python packages...",
                       Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    splash.show()

    def start_main():
        window = PythonPackageManager()
        window.show()
        splash.finish(window)

    QTimer.singleShot(1500, start_main)

    sys.exit(app.exec_())
