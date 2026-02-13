#!/usr/bin/env python3
"""
Caesar Cipher Decoder met Frequency Analysis
Automatisch decrypten van Caesar cipher zonder kennis van de shift waarde
"""

import string
from collections import Counter
from typing import Tuple, Dict, List


class CaesarDecoder:
    """Caesar cipher decoder met frequency analysis"""
    
    # Engelse letter frequenties (percentage)
    ENGLISH_FREQUENCIES = {
        'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702,
        'F': 2.228, 'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153,
        'K': 0.772, 'L': 4.025, 'M': 2.406, 'N': 6.749, 'O': 7.507,
        'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056,
        'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150, 'Y': 1.974,
        'Z': 0.074
    }
    
    def __init__(self):
        self.alphabet = string.ascii_uppercase
        self.alphabet_lower = string.ascii_lowercase
    
    def encrypt(self, text: str, shift: int) -> str:
        """Encrypt een tekst met Caesar cipher"""
        result = []
        for char in text:
            if char.isupper():
                idx = (self.alphabet.index(char) + shift) % 26
                result.append(self.alphabet[idx])
            elif char.islower():
                idx = (self.alphabet_lower.index(char) + shift) % 26
                result.append(self.alphabet_lower[idx])
            else:
                result.append(char)
        return ''.join(result)
    
    def decrypt(self, text: str, shift: int) -> str:
        """Decrypt een tekst met Caesar cipher"""
        return self.encrypt(text, -shift)
    
    def calculate_frequencies(self, text: str) -> Dict[str, float]:
        """Bereken letter frequenties in een tekst"""
        # Filter alleen letters
        letters = [char.upper() for char in text if char.isalpha()]
        if not letters:
            return {}
        
        # Tel voorkomens
        counter = Counter(letters)
        total = len(letters)
        
        # Bereken percentages
        frequencies = {letter: (count / total) * 100 for letter, count in counter.items()}
        return frequencies
    
    def chi_squared(self, observed_freq: Dict[str, float]) -> float:
        """Bereken chi-squared statistiek tegen Engelse frequenties"""
        chi_squared = 0.0
        for letter in self.alphabet:
            observed = observed_freq.get(letter, 0.0)
            expected = self.ENGLISH_FREQUENCIES.get(letter, 0.0)
            if expected > 0:
                chi_squared += ((observed - expected) ** 2) / expected
        return chi_squared
    
    def find_best_shift(self, encrypted_text: str) -> Tuple[int, float, str]:
        """
        Vind de beste shift waarde met frequency analysis
        Retourneert: (shift, chi_squared_score, decrypted_text)
        """
        best_shift = 0
        best_score = float('inf')
        best_decrypted = ""
        
        # Test alle mogelijke shifts (0-25)
        for shift in range(26):
            decrypted = self.decrypt(encrypted_text, shift)
            frequencies = self.calculate_frequencies(decrypted)
            
            if frequencies:
                score = self.chi_squared(frequencies)
                
                # Lagere chi-squared = betere match met Engels
                if score < best_score:
                    best_score = score
                    best_shift = shift
                    best_decrypted = decrypted
        
        return best_shift, best_score, best_decrypted
    
    def crack(self, encrypted_text: str, show_all: bool = False) -> Dict:
        """
        Kraak een encrypted bericht automatisch
        Retourneert een dictionary met resultaten
        """
        shift, score, decrypted = self.find_best_shift(encrypted_text)
        
        result = {
            'encrypted': encrypted_text,
            'decrypted': decrypted,
            'shift': shift,
            'confidence_score': score,
            'all_attempts': []
        }
        
        if show_all:
            # Toon alle mogelijke decrypties met scores
            attempts = []
            for s in range(26):
                d = self.decrypt(encrypted_text, s)
                freq = self.calculate_frequencies(d)
                chi = self.chi_squared(freq) if freq else float('inf')
                attempts.append({
                    'shift': s,
                    'text': d,
                    'score': chi
                })
            # Sorteer op score (laagste eerst = beste)
            attempts.sort(key=lambda x: x['score'])
            result['all_attempts'] = attempts
        
        return result
    
    def analyze_frequencies(self, text: str) -> Dict[str, float]:
        """Analyseer en toon letter frequenties van een tekst"""
        frequencies = self.calculate_frequencies(text)
        
        # Sorteer op frequentie (hoogste eerst)
        sorted_freq = sorted(
            frequencies.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return dict(sorted_freq)


def print_results(result: Dict):
    """Print de resultaten op een mooie manier"""
    print("\n" + "="*60)
    print("CAESAR CIPHER DECODER RESULTATEN")
    print("="*60)
    print(f"\nEncrypted tekst: {result['encrypted']}")
    print(f"\nGevonden shift: {result['shift']}")
    print(f"Confidence score: {result['confidence_score']:.2f} (lager = beter)")
    print(f"\nDecrypted tekst: {result['decrypted']}")
    
    if result['all_attempts']:
        print("\n" + "-"*60)
        print("ALLE MOGELIJKE DECRYPTIES (gesorteerd op waarschijnlijkheid):")
        print("-"*60)
        for i, attempt in enumerate(result['all_attempts'][:5], 1):  # Top 5
            print(f"\n{i}. Shift {attempt['shift']:2d} (score: {attempt['score']:.2f}):")
            print(f"   {attempt['text']}")


def main():
    """Hoofdfunctie voor interactieve gebruik"""
    decoder = CaesarDecoder()
    
    print("="*60)
    print("CAESAR CIPHER DECODER MET FREQUENCY ANALYSIS")
    print("="*60)
    print("\nKies een optie:")
    print("1. Decrypt een bericht (automatisch shift detectie)")
    print("2. Encrypt een bericht")
    print("3. Analyseer letter frequenties")
    print("4. Test met voorbeeld")
    
    choice = input("\nKeuze (1-4): ").strip()
    
    if choice == "1":
        encrypted = input("\nVoer encrypted tekst in: ")
        show_all = input("Toon alle pogingen? (j/n): ").lower() == 'j'
        result = decoder.crack(encrypted, show_all=show_all)
        print_results(result)
        
    elif choice == "2":
        text = input("\nVoer tekst in om te encrypten: ")
        shift = int(input("Voer shift waarde in (0-25): "))
        encrypted = decoder.encrypt(text, shift)
        print(f"\nEncrypted tekst: {encrypted}")
        
    elif choice == "3":
        text = input("\nVoer tekst in om te analyseren: ")
        frequencies = decoder.analyze_frequencies(text)
        print("\nLetter frequenties:")
        print("-" * 40)
        for letter, freq in list(frequencies.items())[:10]:
            print(f"{letter}: {freq:.2f}%")
            
    elif choice == "4":
        # Test voorbeeld
        test_message = "HELLO WORLD THIS IS A TEST MESSAGE"
        test_shift = 3
        encrypted_test = decoder.encrypt(test_message, test_shift)
        
        print(f"\nTest bericht: {test_message}")
        print(f"Shift gebruikt: {test_shift}")
        print(f"Encrypted: {encrypted_test}")
        print("\nProberen te kraken...")
        
        result = decoder.crack(encrypted_test, show_all=True)
        print_results(result)
        
        if result['shift'] == test_shift:
            print("\n✓ SUCCES! Shift correct gedetecteerd!")
        else:
            print(f"\n✗ Shift niet correct (verwacht: {test_shift}, gevonden: {result['shift']})")
    
    else:
        print("Ongeldige keuze!")


if __name__ == "__main__":
    main()
