# TextMerger [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TextMerger is a Python application built with PyQt5 that lets you easily merge content from multiple files into one.

## Features
- **Drag & Drop** support for files and folders
- **One-click Copy** of merged text
- **Save** merged content to a new file
- **Light/Dark Mode**
- **Multilanguage** support
- **Customizable Shortcuts**

## Supported Formats
TextMerger works with a wide range of file types, including source code, web scripts, markup/configuration files, project files, and special formats (e.g., Jupyter Notebooks, PDFs, CSVs).

## Installation for Arch Linux

### From Source
1. Ensure you have Python 3.13+ and pip installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/pierspad/TextMerger.git
   cd TextMerger
   ```
3. Build the application and print the command to install it:
   ```bash
   cd build-scripts/
   sh build-arch.sh 2>&1 | tail -n 1
   ```
4. Execute the output of the previous command, e.g.:
   ```bash
   sudo pacman -U textmerger.*******-pkg.tar.zst
   ```

## Installation for Windows

### Build Executable 
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Create the executable:
   ```bash
      py -m PyInstaller `
      --onefile `
      --noconsole `
      --name TextMerger `
      --icon=assets/logo/logo.png `
      --add-data "assets;assets" `
      --add-data "translations;translations" `
      __main__.py
   ```
3. The executable will be located in the `dist` folder.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.