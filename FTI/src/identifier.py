"""
File type identification using magic numbers.
Reads file header, matches against known signatures, flags extension mismatches.
"""

import os
import subprocess
from pathlib import Path
from typing import Union, Optional, List, Dict
import hashlib
import math
import time

# Use absolute imports when run as script, relative when imported as package
try:
    from .magic_db import MAGIC_DATABASE, get_all_signatures
except ImportError:
    from magic_db import MAGIC_DATABASE, get_all_signatures

# How many bytes to read from the start of the file (enough for all signatures)
HEADER_SIZE = 64

# Common text file extensions that shouldn't trigger mismatch warnings
TEXT_EXTENSIONS = {".txt", ".csv", ".json", ".xml", ".html", ".htm", ".css", ".js", ".log", ".md", ".yml", ".yaml"}


def read_header(filepath: Union[str, Path], size: int = HEADER_SIZE) -> Optional[bytes]:
    """Read the first `size` bytes of the file. Returns None on error."""
    try:
        with open(filepath, "rb") as f:
            return f.read(size)
    except OSError:
        return None


def bytes_to_hex(b: bytes, max_len: int = 32) -> str:
    """Format bytes as uppercase hex string; optionally truncate for display."""
    h = b.hex().upper()
    if max_len and len(h) > max_len:
        return h[:max_len] + "..."
    return h


def match_magic(header: bytes) -> List[tuple]:
    """
    Match header against magic database. Returns list of (description, extensions).
    Longest matching signature wins when multiple match (e.g. ZIP vs empty ZIP).
    """
    if not header:
        return []

    results = []
    for offset, hex_sig, description, extensions in get_all_signatures():
        sig_len = len(hex_sig) // 2
        end = offset + sig_len
        if end > len(header):
            continue
        chunk = header[offset:end]
        if chunk.hex().upper() == hex_sig.upper():
            results.append((description, extensions))

    # Special case: RIFF + WEBP at offset 8
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        # Remove generic RIFF if present, prefer WebP
        results = [(d, e) for (d, e) in results if "WEBP" in d or "RIFF" not in d]
        if not any("WEBP" in d for d, _ in results):
            results.append(("WebP image (RIFF container)", [".webp"]))

    # Prefer longer/more specific matches (e.g. PDF over generic)
    if not results:
        return []
    # Return best: prefer exact type over "Script with shebang" when we have both
    return results[:1] if len(results) == 1 else _pick_best(results)


def _pick_best(results: List[tuple]) -> List[tuple]:
    """Prefer more specific description (longer or executable/docs over shebang)."""
    executable_or_binary = ("PE", "ELF", "Mach-O", "PDF", "ZIP", "PNG", "JPEG", "GIF", "Office")
    for desc, exts in results:
        if any(k in desc for k in executable_or_binary):
            return [(desc, exts)]
    return [results[0]]


def get_extension(filepath: Union[str, Path]) -> str:
    """Return lowercase extension including the dot, or empty string."""
    p = Path(filepath)
    suf = p.suffix
    return suf.lower() if suf else ""


def extension_matches_detected(ext: str, detected_extensions: List[str]) -> bool:
    """Check if file extension is in the list of typical extensions for this magic."""
    if not ext:
        return True  # No extension to mismatch
    ext = ext.lower()
    return ext in [e.lower() for e in detected_extensions if e]


def run_file_command(filepath: Union[str, Path]) -> Optional[str]:
    """Run system `file` command if available. Returns one-line output or None."""
    try:
        r = subprocess.run(
            ["file", "-b", str(filepath)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def calculate_hashes(filepath: Union[str, Path], timeout_seconds: int = 30) -> Dict[str, str]:
    """Calculate MD5 and SHA256 hashes. Returns dict with 'md5' and 'sha256' keys."""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    try:
        file_size = os.path.getsize(filepath)
        # Skip very large files (>1GB) to avoid memory issues
        if file_size > 1024 * 1024 * 1024:
            return {"md5": "(file too large)", "sha256": "(file too large)"}
        
        # For large files (>500MB), sample first 100MB
        sample_size = 100 * 1024 * 1024 if file_size > 500 * 1024 * 1024 else file_size
        
        start_time = time.time()
        with open(filepath, "rb") as f:
            bytes_read = 0
            while bytes_read < sample_size:
                chunk = f.read(8192)
                if not chunk:
                    break
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
                bytes_read += len(chunk)
                
                # Timeout check
                if time.time() - start_time > timeout_seconds:
                    return {"md5": "(timeout)", "sha256": "(timeout)"}
        
        return {
            "md5": md5_hash.hexdigest(),
            "sha256": sha256_hash.hexdigest()
        }
    except (OSError, MemoryError):
        return {"md5": "(error)", "sha256": "(error)"}


def calculate_entropy(filepath: Union[str, Path], header_bytes: int = 1024) -> Optional[float]:
    """Calculate Shannon entropy of file header. Returns float between 0-8."""
    try:
        with open(filepath, "rb") as f:
            data = f.read(header_bytes)
        if not data:
            return None
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        for count in byte_counts:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        
        return entropy
    except (OSError, MemoryError):
        return None


def format_file_size(size_bytes: int) -> str:
    """Format file size to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def check_virustotal(sha256_hash: str, api_key: str) -> Dict:
    """Check file hash on VirusTotal. Returns dict with results."""
    if not api_key:
        return {}
    
    try:
        import requests
        url = f"https://www.virustotal.com/api/v3/files/{sha256_hash}"
        headers = {"x-apikey": api_key}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            permalink = data.get("data", {}).get("links", {}).get("self", "")
            return {
                "detected": stats.get("malicious", 0),
                "total": stats.get("malicious", 0) + stats.get("undetected", 0),
                "permalink": permalink.replace("/api/v3/files/", "/gui/file/") if permalink else None
            }
        elif response.status_code == 404:
            return {"status": "not_found"}
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def export_to_json(data: Dict, output_path: Union[str, Path]) -> None:
    """Export analysis results to JSON file."""
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_to_csv(data: Dict, output_path: Union[str, Path]) -> None:
    """Export analysis results to CSV file."""
    import csv
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filepath", "file_size", "detected_type", "file_extension", "md5", "sha256", "entropy", "mismatch", "file_cmd_output"])
        writer.writerow([
            data.get("filepath", ""),
            data.get("file_size", ""),
            data.get("detected_type", ""),
            data.get("file_extension", ""),
            data.get("md5", ""),
            data.get("sha256", ""),
            data.get("entropy", ""),
            data.get("mismatch", False),
            data.get("file_cmd_output", "")
        ])


def identify(
    filepath: Union[str, Path],
    use_file_cmd: bool = True,
    virustotal_api_key: Optional[str] = None,
) -> Dict:
    """
    Identify file type by magic number and optional `file` command.
    Returns dict with: raw_hex, detected_type, extensions, file_extension,
    file_cmd_output, mismatch (bool), message, file_size, md5, sha256, entropy, virustotal.
    """
    path = Path(filepath)
    if not path.exists():
        return {
            "error": "File not found",
            "filepath": str(path),
        }

    header = read_header(path)
    if header is None:
        return {
            "error": "Could not read file",
            "filepath": str(path),
        }

    raw_hex = bytes_to_hex(header, max_len=32)
    matches = match_magic(header)

    if matches:
        detected_type, detected_exts = matches[0]
    else:
        detected_type = "Unknown or Text File"
        detected_exts = []

    ext = get_extension(path)
    file_cmd_out = run_file_command(path) if use_file_cmd else None
    
    # Refine detected_type using file command output for text files
    if detected_type == "Unknown or Text File" and file_cmd_out:
        # Use file command output for more specific type
        detected_type = file_cmd_out
    
    # Check for mismatch (but suppress warnings for common text files)
    match_ok = extension_matches_detected(ext, detected_exts)
    # Don't flag mismatch for common text extensions when detected as text
    if not match_ok and ext.lower() in TEXT_EXTENSIONS and "text" in detected_type.lower():
        match_ok = True
    
    mismatch = not match_ok

    # Get file size
    try:
        file_size = os.path.getsize(path)
        file_size_formatted = format_file_size(file_size)
    except OSError:
        file_size = 0
        file_size_formatted = "—"

    # Calculate hashes
    hashes = calculate_hashes(path)
    
    # Calculate entropy
    entropy = calculate_entropy(path)

    # Check VirusTotal
    virustotal_result = {}
    if virustotal_api_key and hashes.get("sha256") and hashes["sha256"] not in ["(error)", "(timeout)", "(file too large)"]:
        virustotal_result = check_virustotal(hashes["sha256"], virustotal_api_key)

    result = {
        "filepath": str(path),
        "file_size": file_size,
        "file_size_formatted": file_size_formatted,
        "raw_hex": raw_hex,
        "detected_type": detected_type,
        "detected_extensions": detected_exts,
        "file_extension": ext or "(none)",
        "file_cmd_output": file_cmd_out,
        "md5": hashes.get("md5", ""),
        "sha256": hashes.get("sha256", ""),
        "entropy": entropy,
        "mismatch": mismatch,
        "virustotal": virustotal_result if virustotal_result else None,
        "message": (
            "Note: Check if magic number matches the extension — possible spoofing."
            if mismatch
            else None
        ),
    }
    
    return result


def print_report(data: Dict) -> None:
    """Print a human-readable report to stdout."""
    if "error" in data:
        print(f"Error: {data['error']} — {data.get('filepath', '')}")
        return

    print("File Type Identifier")
    print("-" * 40)
    print(f"File: {data['filepath']}")
    print(f"Size: {data.get('file_size_formatted', '—')}")
    print(f"Raw hex: {data['raw_hex']}")
    print(f"Detected: {data['detected_type']}")
    print(f"File extension: {data['file_extension']}")
    if data.get("file_cmd_output"):
        print(f"file command: {data['file_cmd_output']}")
    if data.get("md5"):
        print(f"MD5: {data['md5']}")
    if data.get("sha256"):
        print(f"SHA256: {data['sha256']}")
    if data.get("entropy") is not None:
        entropy_note = " (high — possibly encrypted/obfuscated)" if data['entropy'] > 7.5 else ""
        print(f"Entropy: {data['entropy']:.2f}{entropy_note}")
    if data.get("virustotal"):
        vt = data["virustotal"]
        if vt.get("detected", 0) > 0:
            print(f"VirusTotal: ⚠️ {vt['detected']}/{vt['total']} engines detected malware")
        elif vt.get("status") == "not_found":
            print("VirusTotal: Not found in database")
        else:
            print(f"VirusTotal: ✓ 0/{vt.get('total', 0)} — No malware detected")
    if data.get("mismatch") and data.get("message"):
        print(f"\n{data['message']}")
    print()
