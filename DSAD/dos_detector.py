#!/usr/bin/env python3
"""
DoS Attack Detector
Monitors network traffic for patterns indicating Denial of Service attacks.
Uses packet capture libraries to analyze traffic patterns, identify abnormal
request rates, and alert when thresholds are exceeded.
"""

import logging
import time
import signal
import sys
import warnings
from collections import defaultdict, deque
from datetime import datetime

# Onderdruk Scapy socket-close warning bij stop van sniff
logging.getLogger("scapy").setLevel(logging.ERROR)
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*Socket.*closed.*")
warnings.filterwarnings("ignore", message=".*unterminated subpattern.*")

from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw
from scapy.layers.http import HTTPRequest
import argparse
import threading
from typing import Dict, Deque


class DoSDetector:
    """Detects various types of DoS attacks by monitoring network traffic patterns."""
    
    def __init__(self, 
                 syn_threshold: int = 100,
                 udp_threshold: int = 200,
                 icmp_threshold: int = 150,
                 http_threshold: int = 300,
                 time_window: int = 10,
                 interface: str = None,
                 stats_callback=None,
                 alert_callback=None):
        """
        Initialize the DoS detector with configurable thresholds.
        
        Args:
            syn_threshold: Maximum SYN packets per time window before alert
            udp_threshold: Maximum UDP packets per time window before alert
            icmp_threshold: Maximum ICMP packets per time window before alert
            http_threshold: Maximum HTTP requests per time window before alert
            time_window: Time window in seconds for rate calculation
            interface: Network interface to monitor (None = all interfaces)
            stats_callback: Callback function for statistics updates (stats_dict)
            alert_callback: Callback function for alerts (attack_type, src_ip, count, threshold, rate)
        """
        self.syn_threshold = syn_threshold
        self.udp_threshold = udp_threshold
        self.icmp_threshold = icmp_threshold
        self.http_threshold = http_threshold
        self.time_window = time_window
        self.interface = interface
        self.stats_callback = stats_callback
        self.alert_callback = alert_callback
        
        # Packet counters per source IP
        self.syn_packets: Dict[str, Deque] = defaultdict(lambda: deque())
        self.udp_packets: Dict[str, Deque] = defaultdict(lambda: deque())
        self.icmp_packets: Dict[str, Deque] = defaultdict(lambda: deque())
        self.http_requests: Dict[str, Deque] = defaultdict(lambda: deque())
        
        # Overall packet counters for time window
        self.total_syn_count = 0
        self.total_udp_count = 0
        self.total_icmp_count = 0
        self.total_http_count = 0
        
        # Timestamps for time window management
        self.window_start_time = time.time()
        self.running = True
        
        # Alert history to prevent spam
        self.last_alert_time: Dict[str, float] = {}
        self.alert_cooldown = 5  # seconds between alerts for same attack type
        
    def cleanup_old_packets(self, packet_times: Deque, current_time: float):
        """Remove packets older than the time window."""
        while packet_times and (current_time - packet_times[0]) > self.time_window:
            packet_times.popleft()
    
    def check_syn_flood(self, src_ip: str, current_time: float):
        """Detect SYN flood attacks (half-open connections)."""
        if src_ip not in self.syn_packets:
            return False
            
        self.cleanup_old_packets(self.syn_packets[src_ip], current_time)
        syn_count = len(self.syn_packets[src_ip])
        
        if syn_count > self.syn_threshold:
            return True
        return False
    
    def check_udp_flood(self, src_ip: str, current_time: float):
        """Detect UDP flood attacks."""
        if src_ip not in self.udp_packets:
            return False
            
        self.cleanup_old_packets(self.udp_packets[src_ip], current_time)
        udp_count = len(self.udp_packets[src_ip])
        
        if udp_count > self.udp_threshold:
            return True
        return False
    
    def check_icmp_flood(self, src_ip: str, current_time: float):
        """Detect ICMP flood attacks (ping flood)."""
        if src_ip not in self.icmp_packets:
            return False
            
        self.cleanup_old_packets(self.icmp_packets[src_ip], current_time)
        icmp_count = len(self.icmp_packets[src_ip])
        
        if icmp_count > self.icmp_threshold:
            return True
        return False
    
    def check_http_flood(self, src_ip: str, current_time: float):
        """Detect HTTP flood attacks (application layer DoS)."""
        if src_ip not in self.http_requests:
            return False
            
        self.cleanup_old_packets(self.http_requests[src_ip], current_time)
        http_count = len(self.http_requests[src_ip])
        
        if http_count > self.http_threshold:
            return True
        return False
    
    def alert(self, attack_type: str, src_ip: str, count: int, threshold: int):
        """Generate alert for detected attack."""
        current_time = time.time()
        alert_key = f"{attack_type}_{src_ip}"
        
        # Prevent alert spam
        if alert_key in self.last_alert_time:
            if current_time - self.last_alert_time[alert_key] < self.alert_cooldown:
                return
        
        self.last_alert_time[alert_key] = current_time
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rate = count / self.time_window
        
        # Call GUI callback if available
        if self.alert_callback:
            self.alert_callback(attack_type, src_ip, count, threshold, rate, timestamp)
        
        # Also print to console if no GUI
        if not self.alert_callback:
            print(f"\n{'='*70}")
            print(f"[ALERT] {timestamp} - {attack_type.upper()} ATTACK DETECTED!")
            print(f"{'='*70}")
            print(f"Source IP: {src_ip}")
            print(f"Packet Count: {count} (Threshold: {threshold})")
            print(f"Time Window: {self.time_window} seconds")
            print(f"Attack Rate: {rate:.2f} packets/second")
            print(f"{'='*70}\n")
    
    def process_packet(self, packet):
        """Process captured packet and check for attack patterns."""
        if not self.running:
            return
        
        current_time = time.time()
        
        # Reset counters if time window has passed
        if current_time - self.window_start_time >= self.time_window:
            self.window_start_time = current_time
            self.total_syn_count = 0
            self.total_udp_count = 0
            self.total_icmp_count = 0
            self.total_http_count = 0
        
        # Process IP packets
        if IP in packet:
            src_ip = packet[IP].src
            
            # Check for TCP packets
            if TCP in packet:
                # Check for TCP SYN packets (SYN flood)
                if packet[TCP].flags == 2:  # SYN flag only (SYN packet)
                    self.syn_packets[src_ip].append(current_time)
                    self.total_syn_count += 1
                    
                    if self.check_syn_flood(src_ip, current_time):
                        count = len(self.syn_packets[src_ip])
                        self.alert("SYN Flood", src_ip, count, self.syn_threshold)
                
                # Check for HTTP requests (HTTP flood)
                # Check both HTTPRequest layer and raw payload for HTTP methods
                is_http = False
                if packet.haslayer(HTTPRequest):
                    is_http = True
                elif Raw in packet:
                    try:
                        payload = packet[Raw].load.decode('utf-8', errors='ignore')
                        # Check for common HTTP methods
                        if any(method in payload for method in ['GET ', 'POST ', 'PUT ', 'DELETE ', 'HEAD ', 'OPTIONS ']):
                            is_http = True
                    except:
                        pass
                
                if is_http:
                    self.http_requests[src_ip].append(current_time)
                    self.total_http_count += 1
                    
                    if self.check_http_flood(src_ip, current_time):
                        count = len(self.http_requests[src_ip])
                        self.alert("HTTP Flood", src_ip, count, self.http_threshold)
            
            # Check for UDP packets (UDP flood)
            elif UDP in packet:
                self.udp_packets[src_ip].append(current_time)
                self.total_udp_count += 1
                
                if self.check_udp_flood(src_ip, current_time):
                    count = len(self.udp_packets[src_ip])
                    self.alert("UDP Flood", src_ip, count, self.udp_threshold)
            
            # Check for ICMP packets (ICMP flood/ping flood)
            elif ICMP in packet:
                self.icmp_packets[src_ip].append(current_time)
                self.total_icmp_count += 1
                
                if self.check_icmp_flood(src_ip, current_time):
                    count = len(self.icmp_packets[src_ip])
                    self.alert("ICMP Flood", src_ip, count, self.icmp_threshold)
    
    def print_stats(self):
        """Print current statistics periodically."""
        while self.running:
            time.sleep(5)
            if not self.running:
                break
                
            current_time = time.time()
            
            # Clean up old packets for all IPs
            for ip in list(self.syn_packets.keys()):
                self.cleanup_old_packets(self.syn_packets[ip], current_time)
            for ip in list(self.udp_packets.keys()):
                self.cleanup_old_packets(self.udp_packets[ip], current_time)
            for ip in list(self.icmp_packets.keys()):
                self.cleanup_old_packets(self.icmp_packets[ip], current_time)
            for ip in list(self.http_requests.keys()):
                self.cleanup_old_packets(self.http_requests[ip], current_time)
            
            # Calculate current rates
            syn_rate = sum(len(packets) for packets in self.syn_packets.values())
            udp_rate = sum(len(packets) for packets in self.udp_packets.values())
            icmp_rate = sum(len(packets) for packets in self.icmp_packets.values())
            http_rate = sum(len(packets) for packets in self.http_requests.values())
            
            # Call GUI callback if available
            if self.stats_callback:
                stats_dict = {
                    'syn': {'current': syn_rate, 'threshold': self.syn_threshold},
                    'udp': {'current': udp_rate, 'threshold': self.udp_threshold},
                    'icmp': {'current': icmp_rate, 'threshold': self.icmp_threshold},
                    'http': {'current': http_rate, 'threshold': self.http_threshold}
                }
                self.stats_callback(stats_dict)
            
            # Also print to console if no GUI
            if not self.stats_callback:
                print(f"\r[STATS] SYN: {syn_rate}/{self.syn_threshold} | "
                      f"UDP: {udp_rate}/{self.udp_threshold} | "
                      f"ICMP: {icmp_rate}/{self.icmp_threshold} | "
                      f"HTTP: {http_rate}/{self.http_threshold}", end="", flush=True)
    
    def start_monitoring(self, gui_mode=False):
        """Start monitoring network traffic."""
        if not gui_mode:
            print("="*70)
            print("DoS Attack Detector - Starting Monitoring")
            print("="*70)
            print(f"Interface: {self.interface or 'All interfaces'}")
            print(f"Time Window: {self.time_window} seconds")
            print(f"Thresholds:")
            print(f"  - SYN Flood: {self.syn_threshold} packets/{self.time_window}s")
            print(f"  - UDP Flood: {self.udp_threshold} packets/{self.time_window}s")
            print(f"  - ICMP Flood: {self.icmp_threshold} packets/{self.time_window}s")
            print(f"  - HTTP Flood: {self.http_threshold} requests/{self.time_window}s")
            print("="*70)
            print("Monitoring... (Press Ctrl+C to stop)\n")
        
        # Start statistics thread
        stats_thread = threading.Thread(target=self.print_stats, daemon=True)
        stats_thread.start()
        
        # Start packet capture
        try:
            sniff(iface=self.interface, 
                  prn=self.process_packet, 
                  stop_filter=lambda x: not self.running,
                  store=False)
        except KeyboardInterrupt:
            if not gui_mode:
                print("\n\nStopping detector...")
            self.running = False
            # Re-raise KeyboardInterrupt so it can be caught by CLI
            raise
        except Exception as e:
            # Don't wrap KeyboardInterrupt in another exception
            if isinstance(e, KeyboardInterrupt):
                self.running = False
                raise
            if not gui_mode:
                print(f"\nError during packet capture: {e}")
                print("Note: You may need to run with sudo/administrator privileges")
            self.running = False
            raise
    
    def stop(self):
        """Stop the detector."""
        self.running = False


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nShutting down detector...")
    sys.exit(0)


def main():
    """Main entry point."""
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(
        description="DoS Attack Detector - Monitors network traffic for DoS attack patterns"
    )
    parser.add_argument(
        "-i", "--interface",
        type=str,
        default=None,
        help="Network interface to monitor (default: all interfaces)"
    )
    parser.add_argument(
        "--syn-threshold",
        type=int,
        default=100,
        help="SYN flood threshold (default: 100 packets)"
    )
    parser.add_argument(
        "--udp-threshold",
        type=int,
        default=200,
        help="UDP flood threshold (default: 200 packets)"
    )
    parser.add_argument(
        "--icmp-threshold",
        type=int,
        default=150,
        help="ICMP flood threshold (default: 150 packets)"
    )
    parser.add_argument(
        "--http-threshold",
        type=int,
        default=300,
        help="HTTP flood threshold (default: 300 requests)"
    )
    parser.add_argument(
        "--time-window",
        type=int,
        default=10,
        help="Time window in seconds for rate calculation (default: 10)"
    )
    
    args = parser.parse_args()
    
    detector = DoSDetector(
        syn_threshold=args.syn_threshold,
        udp_threshold=args.udp_threshold,
        icmp_threshold=args.icmp_threshold,
        http_threshold=args.http_threshold,
        time_window=args.time_window,
        interface=args.interface
    )
    
    detector.start_monitoring()


if __name__ == "__main__":
    main()
