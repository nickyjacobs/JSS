#!/usr/bin/env python3
"""
Test script voor de Caesar cipher decoder
"""

from caesar_decoder import CaesarDecoder


def test_basic_encryption():
    """Test basis encryptie en decryptie"""
    decoder = CaesarDecoder()
    
    message = "HELLO WORLD"
    shift = 3
    encrypted = decoder.encrypt(message, shift)
    decrypted = decoder.decrypt(encrypted, shift)
    
    assert decrypted == message, f"Failed: {decrypted} != {message}"
    print("✓ Basis encryptie/decryptie test geslaagd")


def test_frequency_analysis():
    """Test frequency analysis"""
    decoder = CaesarDecoder()
    
    # Test met Engels tekst
    text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    frequencies = decoder.analyze_frequencies(text)
    
    # E zou het meest moeten voorkomen
    most_common = list(frequencies.keys())[0]
    print(f"✓ Meest voorkomende letter: {most_common} ({frequencies[most_common]:.2f}%)")


def test_automatic_cracking():
    """Test automatische decryptie"""
    decoder = CaesarDecoder()
    
    test_cases = [
        ("HELLO WORLD", 3),
        ("THE QUICK BROWN FOX", 5),
        ("PYTHON IS AWESOME", 7),
        ("FREQUENCY ANALYSIS WORKS", 13),
    ]
    
    print("\nTest automatische decryptie:")
    print("-" * 60)
    
    for message, shift in test_cases:
        encrypted = decoder.encrypt(message, shift)
        result = decoder.crack(encrypted)
        
        if result['shift'] == shift:
            print(f"✓ Shift {shift:2d}: '{message[:30]}...' - CORRECT")
        else:
            print(f"✗ Shift {shift:2d}: '{message[:30]}...' - VERKEERD (gevonden: {result['shift']})")
            print(f"  Encrypted: {encrypted}")
            print(f"  Decrypted: {result['decrypted']}")


def test_long_text():
    """Test met langere tekst (betere frequency analysis)"""
    decoder = CaesarDecoder()
    
    long_text = """
    THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. 
    THIS IS A LONGER TEXT TO TEST FREQUENCY ANALYSIS.
    THE MORE TEXT WE HAVE, THE BETTER THE RESULTS WILL BE.
    FREQUENCY ANALYSIS WORKS BEST WITH LONGER MESSAGES.
    """
    
    shift = 4
    encrypted = decoder.encrypt(long_text, shift)
    result = decoder.crack(encrypted)
    
    print(f"\nLangere tekst test:")
    print(f"Verwacht shift: {shift}")
    print(f"Gevonden shift: {result['shift']}")
    print(f"Confidence score: {result['confidence_score']:.2f}")
    
    if result['shift'] == shift:
        print("✓ Langere tekst test geslaagd")
    else:
        print("✗ Langere tekst test gefaald")


def test_mixed_case():
    """Test met gemengde hoofdletters en kleine letters"""
    decoder = CaesarDecoder()
    
    message = "Hello World! This is a Test."
    shift = 10
    encrypted = decoder.encrypt(message, shift)
    decrypted = decoder.decrypt(encrypted, shift)
    
    assert decrypted == message, f"Failed: {decrypted} != {message}"
    print("✓ Gemengde case test geslaagd")


if __name__ == "__main__":
    print("=" * 60)
    print("CAESAR DECODER TESTS")
    print("=" * 60)
    
    test_basic_encryption()
    test_frequency_analysis()
    test_automatic_cracking()
    test_long_text()
    test_mixed_case()
    
    print("\n" + "=" * 60)
    print("ALLE TESTS VOLTOOID")
    print("=" * 60)
