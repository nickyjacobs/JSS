# File Type Identifier (FTI)

A powerful Python tool for file type identification using magic numbers, designed for malware analysis and security research. FTI reads file headers to determine the real file type regardless of extension, helping detect spoofed files and potential threats.

## Features

- 🔍 **Magic Number Detection**: Identifies file types by reading file headers and matching against a comprehensive database
- 🚨 **Mismatch Detection**: Flags files where the extension doesn't match the actual file type (potential spoofing)
- 🔐 **Hash Calculation**: Calculates MD5 and SHA256 hashes for files
- 📊 **Entropy Analysis**: Calculates Shannon entropy to detect encrypted/obfuscated files
- 🦠 **VirusTotal Integration**: Automatically checks file hashes against VirusTotal's database
- 🌐 **Modern Web GUI**: Beautiful, responsive web interface with drag-and-drop support
- 🌍 **Multi-language**: Supports Dutch (NL) and English (EN)
- 📤 **Export**: Export results to JSON or CSV format
- 💻 **CLI Support**: Full command-line interface for automation and large files

## Installation

### Requirements

- Python 3.9 or higher
- `requests` library (for VirusTotal integration)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd FTI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

   Or install as a package (optional):
```bash
pip install -e .
```

3. (Optional) Configure VirusTotal API key:
   - Copy `config.py.example` to `config.py`:
   ```bash
   cp config.py.example config.py
   ```
   - Edit `config.py` and add your VirusTotal API key:
   ```python
   VIRUSTOTAL_API_KEY = "your-api-key-here"
   ```
   - Get your API key from [VirusTotal](https://www.virustotal.com/)

## Usage

### Web GUI

Launch the web interface:
```bash
python3 main.py --gui
```

Then open your browser to `http://localhost:8000` (or the port shown in the terminal).

**Features:**
- Drag and drop files or click to browse
- Maximum upload size: 25MB (use CLI for larger files)
- Real-time analysis with VirusTotal integration
- Export results to JSON or CSV
- Switch between Dutch and English

### Command Line Interface

Analyze a single file:
```bash
python3 main.py <filepath>
```

Example:
```bash
python3 main.py suspicious_file.exe
```

**CLI Options:**
- `--gui`: Launch web GUI instead of CLI
- `--vt-api-key <key>`: Override VirusTotal API key from config
- `--no-file-cmd`: Don't use system `file` command

**Example Output:**
```
File Type Identifier
----------------------------------------
File: /path/to/file.exe
Size: 1.23 MB
Raw hex: 4D5A900003000000...
Detected: PE executable (Windows)
File extension: .exe
file command: PE32 executable (GUI) Intel 80386
MD5: 7a3e54f8ec550318ec79d780ab55c912
SHA256: 3551ebd2ce09ccfa692ea0818b64cf60df32cb9d59752aaec17801a92e633de2
Entropy: 7.89 (high — possibly encrypted/obfuscated)
VirusTotal: ⚠️ 5/68 engines detected malware

Note: Check if magic number matches the extension — possible spoofing.
```

## File Type Detection

FTI uses magic numbers (file signatures) to identify file types. The database includes:

- **Executables**: PE (Windows), ELF (Linux), Mach-O (macOS)
- **Archives**: ZIP, RAR, 7z, GZIP, BZIP2, XZ
- **Documents**: PDF, Microsoft Office (OLE), Office Open XML
- **Images**: PNG, JPEG, GIF, BMP, TIFF, WebP
- **Audio/Video**: MP3, MP4, OGG, FLAC, MKV, WebM
- **And more...**

## Security Features

### Mismatch Detection
FTI flags files where the extension doesn't match the detected file type. This is useful for detecting:
- Executables disguised as documents/images
- Malware with spoofed extensions
- Suspicious file type changes

### Entropy Analysis
High entropy (>7.5) indicates:
- Encrypted files
- Compressed/archived files
- Obfuscated code
- Possible malware

### VirusTotal Integration
Automatically checks file hashes against VirusTotal's database to detect known malware.

## Project Structure

```
FTI/
├── main.py              # CLI entry point
├── setup.py             # Package setup (optional)
├── requirements.txt     # Python dependencies
├── config.py.example   # Example configuration
├── .gitignore          # Git ignore rules
├── .gitattributes      # Git attributes
├── LICENSE             # MIT License
├── README.md           # This file
├── src/                # Source code
│   ├── __init__.py
│   ├── main.py         # CLI logic
│   ├── identifier.py   # Core file analysis logic
│   ├── magic_db.py     # Magic numbers database
│   └── gui_web.py       # Web GUI server
├── tests/              # Test files (optional)
└── docs/                # Documentation (optional)
```

## Configuration

### VirusTotal API Key

Create a `config.py` file in the project root:

```python
VIRUSTOTAL_API_KEY = "your-api-key-here"
```

**Note:** `config.py` is in `.gitignore` and will not be committed to git.

### File Size Limits

- **Web GUI**: Maximum 25MB per file
- **CLI**: No limit (handles files of any size)

For large files, use the CLI:
```bash
python3 main.py large_file.zip
```

## Export Formats

### JSON Export
```json
{
  "filepath": "/path/to/file",
  "file_size": 1234567,
  "file_size_formatted": "1.18 MB",
  "detected_type": "PE executable (Windows)",
  "file_extension": ".exe",
  "md5": "7a3e54f8ec550318ec79d780ab55c912",
  "sha256": "3551ebd2ce09ccfa692ea0818b64cf60df32cb9d59752aaec17801a92e633de2",
  "entropy": 7.89,
  "mismatch": false,
  "virustotal": {
    "detected": 5,
    "total": 68,
    "permalink": "https://..."
  }
}
```

### CSV Export
Exports all fields in comma-separated format for easy analysis in spreadsheet applications.

## Use Cases

- **Malware Analysis**: Detect spoofed executables and suspicious files
- **Forensics**: Identify file types regardless of extension
- **Security Research**: Analyze file entropy and detect obfuscation
- **File Validation**: Verify file types match their extensions
- **Automation**: Integrate into security pipelines via CLI

## Limitations

- Web GUI limited to 25MB files (use CLI for larger files)
- Requires `file` command for enhanced text file detection (optional)
- VirusTotal API has rate limits (free tier: 4 requests/minute)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Magic numbers database compiled from various sources
- VirusTotal API for malware detection
- Python standard library for core functionality

## Troubleshooting

### "No module named 'requests'"
Install dependencies:
```bash
pip install -r requirements.txt
```

### "Address already in use" (Web GUI)
The server will automatically try ports 8000-8010. If all are in use, stop other servers or change the port in `gui_web.py`.

### VirusTotal errors
- Check your API key in `config.py`
- Verify you haven't exceeded rate limits
- Ensure you have internet connectivity

### Large files crash the web GUI
Use the CLI for files larger than 25MB:
```bash
python3 main.py large_file.zip
```

## Development

### Running Tests

Basic syntax check:
```bash
python3 -m py_compile src/*.py
```

Import check:
```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from identifier import identify; print('OK')"
```

### Project Layout

The project uses a `src/` layout:
- Root `main.py` is the entry point that imports from `src/`
- All source code is in `src/` directory
- Tests go in `tests/` directory
- Documentation goes in `docs/` directory

### Project Structure

- `main.py` - CLI entry point and argument parsing
- `identifier.py` - Core file analysis logic (magic numbers, hashes, entropy, VirusTotal)
- `magic_db.py` - Database of magic number signatures
- `gui_web.py` - Web-based GUI server
- `config.py` - User configuration (not in git)
- `config.py.example` - Example configuration file

## Support

For issues, questions, or contributions, please open an issue on GitHub.
