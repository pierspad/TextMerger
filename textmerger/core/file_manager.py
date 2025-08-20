import os
import mimetypes
import concurrent.futures

try:
    import nbformat
    NBFORMAT_AVAILABLE = True
except ImportError:
    NBFORMAT_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

DASH_LINE = "-------------------"


def get_supported_formats():
    formats = {
        'Programming': ['.py', '.java', '.cs', '.cpp', '.c', '.go', '.rs', '.rb',
                        '.php', '.swift', '.kt', '.scala', '.groovy', '.lua', '.pl', '.r'],
        'Web & Scripting': ['.html', '.htm', '.css', '.scss', '.sass', '.less',
                            '.js', '.jsx', '.ts', '.tsx', '.vue'],
        'Markup & Config': ['.xml', '.yaml', '.yml', '.json', '.toml', '.ini',
                            '.md', '.rst', '.tex', '.csv', '.sql', '.gitignore',
                            '.dockerignore', '.env', '.conf'],
        'Project Files': ['.gradle', '.maven', '.pom', '.project',
                          '.eslintrc', '.prettierrc', '.babelrc'],
        'Special Formats': ['.ipynb', '.pdf', '.rtf', '.log', '.txt']
    }
    return formats


def _get_metadata(path, mime_type):
    return {
        'name': os.path.basename(path),
        'size': os.path.getsize(path),
        'type': mime_type
    }


def _read_notebook_content(path):
    if not NBFORMAT_AVAILABLE:
        return "# Jupyter Notebook support not available\n# Install nbformat: pip install nbformat"

    try:
        with open(path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)
        lines = []
        cell_num = 1
        for cell in notebook.cells:
            tipo_label = "CODE" if cell.cell_type == "code" else "MARKDOWN"
            lines.append(f"{DASH_LINE}\nBegin Cell {cell_num} - {tipo_label}")
            source = cell['source']
            if isinstance(source, list):
                source = "\n".join(source)
            lines.append(source)
            lines.append(f"End Cell {cell_num} - {tipo_label}\n{DASH_LINE}")
            cell_num += 1
        return "\n".join(lines)
    except Exception:
        return None


def _read_pdf_content(path):
    try:
        reader = PdfReader(path)
        lines = []
        for i, page in enumerate(reader.pages):
            lines.append(f"{DASH_LINE}\nBegin Page {i + 1}")
            extracted_text = page.extract_text()
            if extracted_text:
                lines.append(extracted_text)
            lines.append("\nPossible images on this page (placeholder).\n")
            lines.append(f"End Page {i + 1}\n{DASH_LINE}")
        return "\n".join(lines)
    except:
        return None


def _process_file(path):
    if os.path.isdir(path):
        return path, {'content': None, 'metadata': {'name': os.path.basename(path), 'size': 0, 'type': 'folder'}}

    ext = os.path.splitext(path)[1].lower()
    if ext == '.ipynb':
        content = _read_notebook_content(path)
        return path, {'content': content, 'metadata': _get_metadata(path, 'application/x-ipynb+json')}
    if ext == '.pdf':
        content = _read_pdf_content(path)
        return path, {'content': content, 'metadata': _get_metadata(path, 'application/pdf')}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        mime_type, _ = mimetypes.guess_type(path)
        return path, {
            'content': content,
            'metadata': _get_metadata(path, mime_type if mime_type else 'text/plain')
        }
    except (UnicodeDecodeError, IOError):
        mime_type, _ = mimetypes.guess_type(path)
        return path, {
            'content': None,
            'metadata': _get_metadata(path, mime_type if mime_type else 'non testuale')
        }


def load_files(file_paths):
    all_files = []
    for path in file_paths:
        if os.path.isdir(path):
            for root, dirs, filenames in os.walk(path):
                dirs[:] = [d for d in dirs if not (d.startswith('.') or d == '__pycache__')]
                filtered_files = [
                    os.path.join(root, f) for f in filenames
                    if not (f.startswith('.') or f.endswith('.pyc') or f == '.DS_Store')
                ]
                all_files.extend(filtered_files)
        else:
            all_files.append(path)

    all_files = list(dict.fromkeys(all_files))
    files_content = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for path, data in executor.map(_process_file, all_files):
            files_content[path] = data

    return files_content
