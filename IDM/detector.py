"""
Intrusion Detection Monitor - log-based detection (failed logins, suspicious activity).
"""
import re
import time
import threading
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

# Default config; can be overridden by config.py
try:
    from config import AUTH_LOG, FAILED_LOGIN_THRESHOLD, TIME_WINDOW_SECONDS, ALERT_COOLDOWN_SECONDS
except ImportError:
    AUTH_LOG = "/var/log/auth.log"
    FAILED_LOGIN_THRESHOLD = 5
    TIME_WINDOW_SECONDS = 300
    ALERT_COOLDOWN_SECONDS = 60

# Pattern for "Failed password" with IP (sshd)
# e.g. "Failed password for invalid user admin from 192.168.1.1 port 22 ssh2"
# e.g. "Failed password for root from 10.0.0.5 port 22 ssh2"
FAILED_PASSWORD_RE = re.compile(
    r"Failed password .*? from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
    re.IGNORECASE
)
# "Invalid user" attempts (no password yet but probe)
INVALID_USER_RE = re.compile(
    r"Invalid user .*? from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
    re.IGNORECASE
)


class IntrusionDetector:
    """Monitor auth log for failed logins and alert on possible brute force."""

    def __init__(
        self,
        log_path=None,
        failed_threshold=5,
        time_window=300,
        alert_cooldown=60,
        alert_callback=None,
    ):
        self.log_path = Path(log_path or AUTH_LOG)
        self.failed_threshold = failed_threshold
        self.time_window = time_window
        self.alert_cooldown = alert_cooldown
        self.alert_callback = alert_callback
        self.failed_by_ip = defaultdict(lambda: deque())
        self.last_alert_time = {}
        self.running = False
        self._thread = None

    def _clean_old(self, ip):
        now = time.time()
        q = self.failed_by_ip[ip]
        while q and (now - q[0]) > self.time_window:
            q.popleft()

    def _check_alert(self, ip):
        self._clean_old(ip)
        count = len(self.failed_by_ip[ip])
        if count < self.failed_threshold:
            return
        key = f"failed_login_{ip}"
        now = time.time()
        if key in self.last_alert_time and (now - self.last_alert_time[key]) < self.alert_cooldown:
            return
        self.last_alert_time[key] = now
        rate = count / (self.time_window / 60.0) if self.time_window else 0
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.alert_callback:
            self.alert_callback("Failed login (brute force)", ip, count, self.failed_threshold, rate, ts)

    def _process_line(self, line):
        for pattern in (FAILED_PASSWORD_RE, INVALID_USER_RE):
            m = pattern.search(line)
            if m:
                ip = m.group(1)
                self.failed_by_ip[ip].append(time.time())
                self._check_alert(ip)
                return

    def _run(self):
        if not self.log_path.exists():
            return
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, 2)
                while self.running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    self._process_line(line)
        except PermissionError:
            pass
        except Exception:
            if self.running:
                raise

    def start(self):
        """Start monitoring in background thread."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
