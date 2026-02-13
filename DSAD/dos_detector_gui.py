#!/usr/bin/env python3
"""
DoS Attack Detector GUI
Graphical user interface for the DoS attack detector.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from datetime import datetime
from dos_detector import DoSDetector
import sys
import os


class DoSDetectorGUI:
    """Graphical user interface for DoS attack detector."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DoS Attack Detector")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Detector instance
        self.detector = None
        self.detector_thread = None
        self.is_monitoring = False
        
        # Queue for thread-safe GUI updates
        self.stats_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        
        # Attack history
        self.attack_history = []
        
        # Setup UI
        self.setup_ui()
        
        # Start GUI update loop
        self.update_gui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DoS Attack Detector", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Interface selection
        ttk.Label(control_frame, text="Interface:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.interface_var = tk.StringVar(value="All")
        self.interface_combo = ttk.Combobox(control_frame, textvariable=self.interface_var, 
                                            width=20, state="readonly")
        self.interface_combo['values'] = self.get_interfaces()
        self.interface_combo.grid(row=0, column=1, padx=5)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Stopped", 
                                      foreground="red", font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=2, padx=20)
        
        # Start/Stop button
        self.start_stop_btn = ttk.Button(control_frame, text="Start Monitoring", 
                                          command=self.toggle_monitoring, width=20)
        self.start_stop_btn.grid(row=0, column=3, padx=10)
        
        # Configuration panel
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Thresholds
        thresholds = [
            ("SYN Flood:", "syn_threshold", 100),
            ("UDP Flood:", "udp_threshold", 200),
            ("ICMP Flood:", "icmp_threshold", 150),
            ("HTTP Flood:", "http_threshold", 300),
        ]
        
        self.threshold_vars = {}
        for i, (label, key, default) in enumerate(thresholds):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(config_frame, text=label).grid(row=row, column=col, padx=5, sticky=tk.W)
            var = tk.IntVar(value=default)
            self.threshold_vars[key] = var
            threshold_entry = ttk.Entry(config_frame, textvariable=var, width=10)
            threshold_entry.grid(row=row, column=col+1, padx=5)
            ttk.Label(config_frame, text="packets").grid(row=row, column=col+2, padx=5, sticky=tk.W)
        
        # Time window
        ttk.Label(config_frame, text="Time Window:").grid(row=2, column=0, padx=5, sticky=tk.W)
        self.time_window_var = tk.IntVar(value=10)
        time_window_entry = ttk.Entry(config_frame, textvariable=self.time_window_var, width=10)
        time_window_entry.grid(row=2, column=1, padx=5)
        ttk.Label(config_frame, text="seconds").grid(row=2, column=2, padx=5, sticky=tk.W)
        
        # Apply button
        apply_btn = ttk.Button(config_frame, text="Apply Settings", 
                               command=self.apply_settings, width=15)
        apply_btn.grid(row=2, column=3, padx=10)
        
        # Statistics panel
        stats_frame = ttk.LabelFrame(main_frame, text="Real-time Statistics", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create progress bars for each attack type
        self.progress_bars = {}
        self.progress_labels = {}
        
        attack_types = [
            ("SYN Flood", "syn"),
            ("UDP Flood", "udp"),
            ("ICMP Flood", "icmp"),
            ("HTTP Flood", "http"),
        ]
        
        for i, (name, key) in enumerate(attack_types):
            # Label
            label = ttk.Label(stats_frame, text=f"{name}:")
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            
            # Progress bar
            progress = ttk.Progressbar(stats_frame, length=300, mode='determinate', maximum=100)
            progress.grid(row=i, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
            self.progress_bars[key] = progress
            
            # Value label
            value_label = ttk.Label(stats_frame, text="0/0", font=("Arial", 9))
            value_label.grid(row=i, column=2, padx=5, pady=5, sticky=tk.W)
            self.progress_labels[key] = value_label
        
        stats_frame.columnconfigure(1, weight=1)
        
        # Alert panel
        alert_frame = ttk.LabelFrame(main_frame, text="Attack Alerts", padding="10")
        alert_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(4, weight=1)
        
        # Alert text area
        self.alert_text = scrolledtext.ScrolledText(alert_frame, height=10, width=80,
                                                     font=("Courier", 9), wrap=tk.WORD)
        self.alert_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.alert_text.config(state=tk.DISABLED)
        
        # Clear button
        clear_btn = ttk.Button(alert_frame, text="Clear Alerts", command=self.clear_alerts)
        clear_btn.grid(row=1, column=0, pady=(5, 0))
        
        alert_frame.columnconfigure(0, weight=1)
        alert_frame.rowconfigure(0, weight=1)
        
    def get_interfaces(self):
        """Get list of available network interfaces."""
        try:
            from scapy.all import get_if_list
            interfaces = ["All"] + list(get_if_list())
            return interfaces
        except:
            return ["All"]
    
    def apply_settings(self):
        """Apply configuration settings."""
        if self.is_monitoring:
            messagebox.showwarning("Warning", 
                                  "Stop monitoring before changing settings.")
            return
        
        # Validate thresholds
        for key, var in self.threshold_vars.items():
            if var.get() <= 0:
                messagebox.showerror("Error", f"{key} must be greater than 0.")
                return
        
        if self.time_window_var.get() <= 0:
            messagebox.showerror("Error", "Time window must be greater than 0.")
            return
        
        messagebox.showinfo("Success", "Settings applied. Start monitoring to use new settings.")
    
    def toggle_monitoring(self):
        """Start or stop monitoring."""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start the detector."""
        try:
            # Get settings
            interface = self.interface_var.get()
            if interface == "All":
                interface = None
            
            # Create detector with callbacks
            self.detector = DoSDetector(
                syn_threshold=self.threshold_vars["syn_threshold"].get(),
                udp_threshold=self.threshold_vars["udp_threshold"].get(),
                icmp_threshold=self.threshold_vars["icmp_threshold"].get(),
                http_threshold=self.threshold_vars["http_threshold"].get(),
                time_window=self.time_window_var.get(),
                interface=interface,
                stats_callback=self.stats_callback,
                alert_callback=self.alert_callback
            )
            
            # Start detector in separate thread
            self.detector_thread = threading.Thread(target=self.detector.start_monitoring, 
                                                    args=(True,), daemon=True)
            self.detector_thread.start()
            
            self.is_monitoring = True
            self.start_stop_btn.config(text="Stop Monitoring")
            self.status_label.config(text="Status: Monitoring", foreground="green")
            
            # Disable configuration
            for widget in self.root.winfo_children():
                self.disable_config(widget)
            
        except PermissionError as e:
            error_msg = (
                f"Permission denied: {str(e)}\n\n"
                "Packet capture requires elevated privileges.\n\n"
                "On macOS:\n"
                "1. Try running: python3 dos_detector_gui.py (without sudo)\n"
                "2. Or grant Terminal/IDE network access in System Preferences\n"
                "3. Or use: sudo python3 dos_detector_gui.py\n\n"
                "On Linux:\n"
                "Run with: sudo python3 dos_detector_gui.py"
            )
            messagebox.showerror("Permission Error", error_msg)
            self.is_monitoring = False
        except Exception as e:
            error_msg = (
                f"Failed to start monitoring:\n{str(e)}\n\n"
                "Possible solutions:\n"
                "- Ensure you have root/administrator privileges\n"
                "- Check that the network interface exists\n"
                "- Verify scapy is installed correctly"
            )
            messagebox.showerror("Error", error_msg)
            self.is_monitoring = False
    
    def disable_config(self, widget):
        """Recursively disable configuration widgets."""
        # Don't disable interface selector
        if isinstance(widget, (ttk.Entry,)):
            widget.config(state="disabled")
        elif isinstance(widget, ttk.Combobox):
            # Keep interface combo enabled, disable others
            if widget != self.interface_combo:
                widget.config(state="disabled")
        for child in widget.winfo_children():
            self.disable_config(child)
    
    def stop_monitoring(self):
        """Stop the detector."""
        if self.detector:
            self.detector.stop()
            self.detector = None
        
        self.is_monitoring = False
        self.start_stop_btn.config(text="Start Monitoring")
        self.status_label.config(text="Status: Stopped", foreground="red")
        
        # Reset progress bars
        for key in self.progress_bars:
            self.progress_bars[key]['value'] = 0
            self.progress_labels[key].config(text="0/0")
        
        # Re-enable configuration
        for widget in self.root.winfo_children():
            self.enable_config(widget)
    
    def enable_config(self, widget):
        """Recursively enable configuration widgets."""
        if isinstance(widget, (ttk.Combobox, ttk.Entry)):
            widget.config(state="normal")
        for child in widget.winfo_children():
            self.enable_config(child)
    
    def stats_callback(self, stats_dict):
        """Callback for statistics updates (called from detector thread)."""
        self.stats_queue.put(stats_dict)
    
    def alert_callback(self, attack_type, src_ip, count, threshold, rate, timestamp):
        """Callback for alerts (called from detector thread)."""
        alert_data = {
            'attack_type': attack_type,
            'src_ip': src_ip,
            'count': count,
            'threshold': threshold,
            'rate': rate,
            'timestamp': timestamp
        }
        self.alert_queue.put(alert_data)
    
    def update_gui(self):
        """Update GUI elements from queues."""
        # Process statistics updates
        try:
            while True:
                stats_dict = self.stats_queue.get_nowait()
                self.update_statistics(stats_dict)
        except queue.Empty:
            pass
        
        # Process alerts
        try:
            while True:
                alert_data = self.alert_queue.get_nowait()
                self.display_alert(alert_data)
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.update_gui)
    
    def update_statistics(self, stats_dict):
        """Update statistics display."""
        for key, data in stats_dict.items():
            current = data['current']
            threshold = data['threshold']
            
            # Update progress bar
            percentage = min(100, (current / threshold) * 100) if threshold > 0 else 0
            self.progress_bars[key]['value'] = percentage
            
            # Update label
            self.progress_labels[key].config(text=f"{current}/{threshold}")
            
            # Change color based on percentage
            if percentage >= 100:
                self.progress_bars[key].config(style="danger.Horizontal.TProgressbar")
            elif percentage >= 75:
                self.progress_bars[key].config(style="warning.Horizontal.TProgressbar")
            else:
                self.progress_bars[key].config(style="TProgressbar")
    
    def display_alert(self, alert_data):
        """Display alert in the alert panel."""
        attack_type = alert_data['attack_type']
        src_ip = alert_data['src_ip']
        count = alert_data['count']
        threshold = alert_data['threshold']
        rate = alert_data['rate']
        timestamp = alert_data['timestamp']
        
        # Add to history
        self.attack_history.append(alert_data)
        
        # Enable text widget for editing
        self.alert_text.config(state=tk.NORMAL)
        
        # Format alert message
        alert_msg = f"[{timestamp}] {attack_type.upper()} ATTACK DETECTED!\n"
        alert_msg += f"  Source IP: {src_ip}\n"
        alert_msg += f"  Packet Count: {count} (Threshold: {threshold})\n"
        alert_msg += f"  Attack Rate: {rate:.2f} packets/second\n"
        alert_msg += "-" * 70 + "\n\n"
        
        # Insert at beginning
        self.alert_text.insert("1.0", alert_msg)
        
        # Disable text widget
        self.alert_text.config(state=tk.DISABLED)
        
        # Show system notification
        self.root.bell()
        
        # Flash window (platform dependent)
        try:
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
        except:
            pass
    
    def clear_alerts(self):
        """Clear the alert panel."""
        self.alert_text.config(state=tk.NORMAL)
        self.alert_text.delete("1.0", tk.END)
        self.alert_text.config(state=tk.DISABLED)
        self.attack_history.clear()


def main():
    """Main entry point for GUI."""
    # On macOS, GUI apps shouldn't be run with sudo directly
    # Instead, we'll show a warning if privileges are needed
    if sys.platform == 'darwin':
        if os.geteuid() == 0:
            print("Warning: Running GUI with sudo on macOS may cause issues.")
            print("Try running without sudo first. Packet capture will prompt for privileges when needed.")
    
    root = tk.Tk()
    
    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create custom styles for progress bars
    style.configure("danger.Horizontal.TProgressbar", 
                   background='red', troughcolor='lightgray')
    style.configure("warning.Horizontal.TProgressbar", 
                   background='orange', troughcolor='lightgray')
    
    app = DoSDetectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
