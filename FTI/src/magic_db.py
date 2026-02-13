"""
Magic numbers database for file type identification.
Each entry: (offset, hex_signature, description, typical_extensions)
"""

MAGIC_DATABASE = [
    # Executables (critical for malware analysis)
    (0, "4D5A", "PE executable (Windows)", [".exe", ".dll", ".sys", ".scr"]),
    (0, "7F454C46", "ELF executable (Linux/Unix)", [".elf", ".bin", ".so", ""]),
    (0, "FEEDFACE", "Mach-O executable (macOS)", [".o", ".dylib", ""]),
    (0, "FEEDFACF", "Mach-O executable 64-bit (macOS)", [".o", ".dylib", ""]),
    (0, "CEFAEDFE", "Mach-O executable (macOS)", [".o", ".dylib", ""]),
    (0, "CFAEDFEF", "Mach-O executable 64-bit (macOS)", [".o", ".dylib", ""]),
    
    # Archives
    (0, "504B0304", "ZIP archive", [".zip", ".jar", ".docx", ".xlsx", ".pptx", ".apk"]),
    (0, "504B0506", "ZIP archive (empty)", [".zip"]),
    (0, "504B0708", "ZIP archive (spanned)", [".zip"]),
    (0, "526172211A07", "RAR archive", [".rar"]),
    (0, "377ABCAF271C", "7z archive", [".7z"]),
    (0, "1F8B08", "GZIP archive", [".gz", ".tgz"]),
    (0, "425A68", "BZIP2 archive", [".bz2"]),
    (0, "FD377A585A00", "XZ archive", [".xz"]),
    
    # Documents
    (0, "255044462D", "PDF document", [".pdf"]),
    (0, "D0CF11E0A1B11AE1", "Microsoft Office (OLE)", [".doc", ".xls", ".ppt", ".msi"]),
    
    # Images
    (0, "89504E470D0A1A0A", "PNG image", [".png"]),
    (0, "FFD8FF", "JPEG image", [".jpg", ".jpeg"]),
    (0, "474946383761", "GIF image (GIF87a)", [".gif"]),
    (0, "474946383961", "GIF image (GIF89a)", [".gif"]),
    (0, "52494646", "RIFF container", [".wav", ".avi", ".webp"]),
    (0, "424D", "BMP image", [".bmp"]),
    (0, "49492A00", "TIFF image (little-endian)", [".tif", ".tiff"]),
    (0, "4D4D002A", "TIFF image (big-endian)", [".tif", ".tiff"]),
    (0, "57454250", "WebP image", [".webp"]),
    
    # Audio/Video
    (0, "4F676753", "OGG container", [".ogg", ".ogv", ".oga"]),
    (0, "664C6143", "FLAC audio", [".flac"]),
    (0, "494433", "MP3 with ID3 tag", [".mp3"]),
    (0, "FFFB", "MP3 audio", [".mp3"]),
    (0, "FFF3", "MP3 audio", [".mp3"]),
    (0, "FFF2", "MP3 audio", [".mp3"]),
    
    # Video
    (0, "0000001866747970", "MP4 video", [".mp4", ".m4v"]),
    (0, "1A45DFA3", "Matroska (MKV/WebM)", [".mkv", ".webm"]),
    (0, "464C5601", "FLV video", [".flv"]),
    (0, "3026B2758E66CF11", "WMV/ASF video", [".wmv", ".asf"]),
    
    # Scripts/Text
    (0, "2321", "Script with shebang", [".sh", ".py", ".pl", ".rb", ".php"]),
    (0, "EFBBBF", "UTF-8 BOM", [".txt", ".csv"]),
    
    # Other
    (0, "7B5C727466", "RTF document", [".rtf"]),
    (0, "255044462D312E", "PDF document (version 1)", [".pdf"]),
    (0, "504B030414000600", "Office Open XML (docx/xlsx/pptx)", [".docx", ".xlsx", ".pptx"]),
]


def get_all_signatures():
    """Return all signatures from the database."""
    return MAGIC_DATABASE
