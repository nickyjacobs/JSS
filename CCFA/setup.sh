#!/bin/bash
# Setup script voor Caesar Cipher Decoder

echo "=========================================="
echo "Caesar Cipher Decoder - Setup"
echo "=========================================="
echo ""

# Check Python versie
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 is niet geïnstalleerd!"
    exit 1
fi

echo ""
echo "✓ Python gevonden"
echo ""

# Check of alle bestanden aanwezig zijn
echo "Checking bestanden..."
files=("caesar_decoder.py" "caesar_web_gui.py" "test_decoder.py" "README.md")
missing_files=()

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "ERROR: Ontbrekende bestanden:"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo "✓ Alle bestanden aanwezig"
echo ""

# Test imports
echo "Testing imports..."
python3 -c "from caesar_decoder import CaesarDecoder; print('✓ Imports succesvol')" 2>&1

if [ $? -ne 0 ]; then
    echo "ERROR: Imports gefaald!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup voltooid!"
echo "=========================================="
echo ""
echo "Gebruik:"
echo "  Web GUI:    python3 caesar_web_gui.py"
echo "  CLI:        python3 caesar_decoder.py"
echo "  Tests:      python3 test_decoder.py"
echo ""
