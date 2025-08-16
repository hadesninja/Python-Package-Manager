# 🐍 Python Package Manager (GUI)

A simple yet powerful **PyQt5-based GUI application** to manage Python packages on your system.  
With this tool, you can:

- ✅ View installed Python packages with version info  
- 🔍 Search packages on **PyPI** (Exact match or Contains search)  
- ⬆️ Update packages to the latest version  
- 📦 Install new packages  
- ❌ Uninstall existing packages  
- ⚡ Progress dialogs for install/uninstall/update actions  
- 🎨 Splash screen + application icon support  

---

## 📸 Screenshots
> *(Add screenshots here after running the app, e.g. main window and search view)*

---

## ⚙️ Features
- Displays installed packages with **installed version** and **latest version** side-by-side.  
- Automatically disables the **Update** button when the package is already up to date.  
- Search PyPI for packages in **two modes**:
  - **Exact Match** → Faster, queries only one package.  
  - **Contains** → Lists all packages containing the search string (limited to 50 for performance).  
- Displays proper buttons depending on package state:
  - `Update` → If installed but outdated.  
  - `Installed` (disabled) → If installed and up-to-date.  
  - `Install` → If not installed.  
- Progress dialog with contextual message, e.g.:
  - *Installing frida...*  
  - *Updating requests...*  
  - *Uninstalling numpy...*  
- Splash screen on startup: *“Fetching installed Python packages...”*  

---

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/python-package-manager.git
   cd python-package-manager
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt**
   ```
   PyQt5
   requests
   ```

3. Run the app:
   ```bash
   python PyPackageManager.pyw
   ```

---

## 📂 Project Structure

```
python-package-manager/
│
├── PyPackageManager.pyw   # Main program
├── assets/
│   ├── pypkgmgr.ico       # App icon
│   └── splash.png         # Splash screen image
└── requirements.txt
```

---

## 🖥️ Usage

- On launch, a splash screen appears while fetching installed packages.  
- Use the **Installed Packages** section to filter, update, or uninstall existing packages.  
- Use the **Search Packages** section to find new packages from PyPI and install them.  
- Use the **menu bar**:
  - `File → Exit` → Close the application  
  - `Help → About` → View version & developer info  

---

## 📌 Requirements
- Python **3.7+**
- `pip` installed and available in PATH
- Internet connection (for PyPI lookups)

---

## 👨‍💻 Author
Developed by **Vaibhav Patil** ✨  
Feel free to contribute, suggest improvements, or open issues.

---

## 📜 License
This project is licensed under the **MIT License**.  
See [LICENSE](LICENSE) for more details.
