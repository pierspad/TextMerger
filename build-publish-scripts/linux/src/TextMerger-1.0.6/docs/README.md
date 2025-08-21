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

### From AUR

1. Install the package using `yay` or `paru`:
   ```bash
   yay -S textmerger
   ```
   or
   ```bash
   paru -S textmerger
   ```
   
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

## Contributing
Pull requests are welcome! 
I wouldn't mind some help in traslating the app properly in various languages and packaging it for Windows/MacOS and maybe other distributions like Debian, Ubuntu, Fedora, etc.
For major changes, please open an issue first to discuss your ideas.

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.