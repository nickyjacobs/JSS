#!/usr/bin/env python3
"""
Demo script voor Caesar cipher decoder
"""

from caesar_decoder import CaesarDecoder, print_results


def main():
    decoder = CaesarDecoder()
    
    print("="*70)
    print("CAESAR CIPHER DECODER - DEMONSTRATIE")
    print("="*70)
    
    # Voorbeeld 1: Langere tekst (werkt het beste)
    print("\n" + "="*70)
    print("VOORBEELD 1: Langere tekst met shift 7")
    print("="*70)
    
    message1 = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. THIS IS A LONGER MESSAGE TO DEMONSTRATE FREQUENCY ANALYSIS. THE MORE TEXT WE HAVE THE BETTER THE RESULTS WILL BE."
    shift1 = 7
    encrypted1 = decoder.encrypt(message1, shift1)
    
    print(f"\nOrigineel bericht:\n{message1}")
    print(f"\nShift waarde: {shift1}")
    print(f"\nEncrypted bericht:\n{encrypted1}")
    
    print("\n🔍 Analyseren en kraken...")
    result1 = decoder.crack(encrypted1, show_all=False)
    print_results(result1)
    
    if result1['shift'] == shift1:
        print("\n✅ SUCCES! De shift is correct gedetecteerd!")
    else:
        print(f"\n⚠️  Shift niet perfect (verwacht: {shift1}, gevonden: {result1['shift']})")
    
    # Voorbeeld 2: Met alle pogingen
    print("\n\n" + "="*70)
    print("VOORBEELD 2: Kortere tekst met alle pogingen")
    print("="*70)
    
    message2 = "FREQUENCY ANALYSIS IS A POWERFUL CRYPTOGRAPHIC TECHNIQUE"
    shift2 = 13
    encrypted2 = decoder.encrypt(message2, shift2)
    
    print(f"\nOrigineel bericht:\n{message2}")
    print(f"\nShift waarde: {shift2}")
    print(f"\nEncrypted bericht:\n{encrypted2}")
    
    print("\n🔍 Analyseren met alle pogingen...")
    result2 = decoder.crack(encrypted2, show_all=True)
    print_results(result2)
    
    # Voorbeeld 3: Frequency analyse demonstratie
    print("\n\n" + "="*70)
    print("VOORBEELD 3: Letter frequentie analyse")
    print("="*70)
    
    sample_text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    frequencies = decoder.analyze_frequencies(sample_text)
    
    print(f"\nTekst: {sample_text}")
    print("\nTop 10 meest voorkomende letters:")
    print("-" * 40)
    for i, (letter, freq) in enumerate(list(frequencies.items())[:10], 1):
        expected = decoder.ENGLISH_FREQUENCIES.get(letter, 0)
        diff = freq - expected
        print(f"{i:2d}. {letter}: {freq:6.2f}% (verwacht: {expected:5.2f}%, verschil: {diff:+6.2f}%)")
    
    # Voorbeeld 4: Interactief
    print("\n\n" + "="*70)
    print("VOORBEELD 4: Probeer je eigen bericht!")
    print("="*70)
    
    user_message = input("\nVoer een bericht in om te encrypten: ")
    if user_message:
        user_shift = int(input("Voer een shift waarde in (0-25): "))
        user_encrypted = decoder.encrypt(user_message, user_shift)
        
        print(f"\nEncrypted: {user_encrypted}")
        print("\n🔍 Proberen te kraken...")
        
        user_result = decoder.crack(user_encrypted, show_all=True)
        print_results(user_result)
        
        if user_result['shift'] == user_shift:
            print("\n✅ Perfect! Automatisch gekraakt!")
        else:
            print(f"\n⚠️  Gevonden shift: {user_result['shift']} (verwacht: {user_shift})")
            print("Dit kan gebeuren bij zeer korte teksten of teksten met weinig letters.")


if __name__ == "__main__":
    main()
