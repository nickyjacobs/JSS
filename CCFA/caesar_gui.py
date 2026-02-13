#!/usr/bin/env python3
"""
GUI voor Caesar Cipher Decoder met Frequency Analysis
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from caesar_decoder import CaesarDecoder, print_results


class CaesarDecoderGUI:
    """GUI applicatie voor Caesar cipher decoder"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Caesar Cipher Decoder - Frequency Analysis")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.decoder = CaesarDecoder()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup de gebruikersinterface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🔐 Caesar Cipher Decoder",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Met Frequency Analysis",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input sectie
        input_frame = tk.LabelFrame(
            main_container,
            text="Input",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Mode selectie
        mode_frame = tk.Frame(input_frame, bg='#f0f0f0')
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="decrypt")
        
        tk.Radiobutton(
            mode_frame,
            text="🔓 Decrypt (automatisch)",
            variable=self.mode_var,
            value="decrypt",
            font=('Arial', 10),
            bg='#f0f0f0',
            activebackground='#e8f4f8',
            command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            mode_frame,
            text="🔒 Encrypt",
            variable=self.mode_var,
            value="encrypt",
            font=('Arial', 10),
            bg='#f0f0f0',
            activebackground='#e8f4f8',
            command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=10)
        
        # Shift input (alleen voor encrypt)
        self.shift_frame = tk.Frame(input_frame, bg='#f0f0f0')
        self.shift_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            self.shift_frame,
            text="Shift waarde (0-25):",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=5)
        
        self.shift_var = tk.StringVar(value="3")
        shift_entry = tk.Entry(
            self.shift_frame,
            textvariable=self.shift_var,
            width=5,
            font=('Arial', 10)
        )
        shift_entry.pack(side=tk.LEFT, padx=5)
        
        # Text input
        tk.Label(
            input_frame,
            text="Tekst:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            font=('Courier', 11),
            wrap=tk.WORD,
            bg='white',
            fg='#2c3e50'
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.process_button = tk.Button(
            button_frame,
            text="🚀 Verwerk",
            command=self.process_text,
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            relief=tk.RAISED,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑️ Wissen",
            command=self.clear_all,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            activebackground='#7f8c8d',
            activeforeground='white',
            relief=tk.RAISED,
            padx=20,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Output sectie
        output_frame = tk.LabelFrame(
            main_container,
            text="Resultaat",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Result info
        self.info_label = tk.Label(
            output_frame,
            text="Voer tekst in en klik op 'Verwerk'",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#7f8c8d',
            anchor='w'
        )
        self.info_label.pack(fill=tk.X, pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            font=('Courier', 11),
            wrap=tk.WORD,
            bg='#ecf0f1',
            fg='#2c3e50',
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Klaar",
            font=('Arial', 9),
            bg='#34495e',
            fg='white',
            anchor='w',
            padx=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial state
        self.on_mode_change()
    
    def on_mode_change(self):
        """Update UI wanneer mode verandert"""
        if self.mode_var.get() == "encrypt":
            self.shift_frame.pack(fill=tk.X, pady=(0, 10))
            self.process_button.config(text="🔒 Encrypt")
        else:
            self.shift_frame.pack_forget()
            self.process_button.config(text="🔓 Decrypt")
    
    def process_text(self):
        """Verwerk de input tekst"""
        text = self.input_text.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Waarschuwing", "Voer eerst tekst in!")
            return
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        try:
            if self.mode_var.get() == "encrypt":
                shift = int(self.shift_var.get())
                if not (0 <= shift <= 25):
                    raise ValueError("Shift moet tussen 0 en 25 zijn")
                
                encrypted = self.decoder.encrypt(text, shift)
                self.output_text.insert("1.0", encrypted)
                self.info_label.config(
                    text=f"✓ Geëncrypteerd met shift {shift}",
                    fg='#27ae60'
                )
                self.status_bar.config(text=f"Geëncrypteerd met shift {shift}")
            
            else:  # decrypt
                self.status_bar.config(text="Analyseren...")
                self.root.update()
                
                result = self.decoder.crack(text, show_all=True)
                
                # Toon resultaat
                output = f"🔍 Gevonden shift: {result['shift']}\n"
                output += f"📊 Confidence score: {result['confidence_score']:.2f} (lager = beter)\n"
                output += f"\n{'='*60}\n"
                output += f"DECRYPTED TEKST:\n"
                output += f"{'='*60}\n\n"
                output += result['decrypted']
                
                output += f"\n\n{'='*60}\n"
                output += f"TOP 5 MEEST WAARSCHIJNLIJKE DECRYPTIES:\n"
                output += f"{'='*60}\n\n"
                
                for i, attempt in enumerate(result['all_attempts'][:5], 1):
                    output += f"{i}. Shift {attempt['shift']:2d} (score: {attempt['score']:7.2f}):\n"
                    output += f"   {attempt['text']}\n\n"
                
                self.output_text.insert("1.0", output)
                
                if result['shift'] >= 0:
                    self.info_label.config(
                        text=f"✓ Automatisch gedecrypteerd! Shift: {result['shift']}",
                        fg='#27ae60'
                    )
                    self.status_bar.config(
                        text=f"Gedecrypteerd met shift {result['shift']} (score: {result['confidence_score']:.2f})"
                    )
                else:
                    self.info_label.config(
                        text="⚠️ Geen goede match gevonden",
                        fg='#e74c3c'
                    )
        
        except ValueError as e:
            messagebox.showerror("Fout", str(e))
            self.status_bar.config(text="Fout opgetreden")
        except Exception as e:
            messagebox.showerror("Fout", f"Onverwachte fout: {str(e)}")
            self.status_bar.config(text="Fout opgetreden")
        
        self.output_text.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Wis alle velden"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.info_label.config(
            text="Voer tekst in en klik op 'Verwerk'",
            fg='#7f8c8d'
        )
        self.status_bar.config(text="Gewist")


def main():
    """Start de GUI applicatie"""
    root = tk.Tk()
    app = CaesarDecoderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
