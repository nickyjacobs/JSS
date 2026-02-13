# DoS Attack Detector

Een netwerkverkeer monitor die patronen detecteert die wijzen op Denial of Service (DoS) aanvallen. Het gebruikt packet capture libraries om verkeerspatronen te analyseren, abnormale aanvraagsnelheden te identificeren en waarschuwingen te geven wanneer drempelwaarden worden overschreden.

## Features

- **Real-time monitoring**: Monitort netwerkverkeer in real-time voor DoS-aanvallen
- **Grafische gebruikersinterface**: Moderne GUI met real-time statistieken en waarschuwingen
- **Meerdere aanvalstypen**: Detecteert verschillende soorten DoS-aanvallen:
  - **SYN Flood**: Detecteert half-open TCP-verbindingen
  - **UDP Flood**: Detecteert UDP-packet overstromingen
  - **ICMP Flood**: Detecteert ping-flood aanvallen
  - **HTTP Flood**: Detecteert applicatielaag DoS-aanvallen
- **Drempelwaarde-gebaseerde waarschuwingen**: Configureerbare drempelwaarden per aanvalstype
- **Tijdvenster analyse**: Analyseert verkeerspatronen binnen een configureerbaar tijdvenster
- **IP-gebaseerde tracking**: Volgt verkeer per bron-IP voor nauwkeurige detectie

## Vereisten

- Python 3.7 of hoger
- Root/Administrator rechten (voor packet capture)
- Scapy library

## Installatie

1. Installeer de vereiste dependencies:

```bash
pip3 install -r requirements.txt
```

**Opmerking**: Op macOS gebruik je meestal `pip3` in plaats van `pip`.

Op Linux/macOS kan je ook system packages nodig hebben:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libpcap-dev

# macOS
brew install libpcap
```

## Gebruik

### Grafische Interface (Aanbevolen)

**Web-based GUI (Werkt op alle platforms, inclusief macOS):**

```bash
# Installeer extra dependencies voor web GUI
pip3 install flask flask-socketio

# Start de web GUI
python3 dos_detector_web_gui.py
```

De browser opent automatisch op http://localhost:5000. Als dit niet gebeurt, open deze URL handmatig in je browser.

**Desktop GUI (tkinter - kan problemen hebben op sommige macOS versies):**

**Op macOS:**
```bash
# Probeer eerst zonder sudo
python3 dos_detector_gui.py

# Of gebruik het launcher script
./start_gui.sh

# Als packet capture faalt, probeer dan met sudo
sudo python3 dos_detector_gui.py
```

**Op Linux:**
```bash
sudo python3 dos_detector_gui.py
```

De GUI biedt:
- **Control Panel**: Start/stop monitoring en selecteer netwerkinterface
- **Configuration Panel**: Configureer drempelwaarden en tijdvenster
- **Real-time Statistics**: Visuele progress bars voor elk aanvalstype
- **Attack Alerts**: Real-time waarschuwingen met details over gedetecteerde aanvallen

### Command-line Interface

Start de detector met standaard instellingen (vereist root/administrator rechten):

```bash
sudo python3 dos_detector.py
```

### Geavanceerd gebruik

Monitor een specifieke netwerkinterface:

```bash
sudo python3 dos_detector.py -i eth0
```

Pas drempelwaarden aan:

```bash
sudo python3 dos_detector.py --syn-threshold 50 --udp-threshold 100 --time-window 5
```

### Command-line opties

```
-i, --interface        Netwerkinterface om te monitoren (standaard: alle interfaces)
--syn-threshold       SYN flood drempelwaarde (standaard: 100 packets)
--udp-threshold       UDP flood drempelwaarde (standaard: 200 packets)
--icmp-threshold      ICMP flood drempelwaarde (standaard: 150 packets)
--http-threshold      HTTP flood drempelwaarde (standaard: 300 requests)
--time-window         Tijdvenster in seconden voor rate berekening (standaard: 10)
```

## Hoe het werkt

1. **Packet Capture**: De detector gebruikt Scapy om alle netwerkpakketten te capteren die door de geselecteerde interface(s) gaan.

2. **Pattern Analysis**: Elk pakket wordt geanalyseerd om het type te identificeren (TCP SYN, UDP, ICMP, HTTP).

3. **Rate Calculation**: Het aantal pakketten per bron-IP wordt geteld binnen een configureerbaar tijdvenster (standaard 10 seconden).

4. **Threshold Checking**: Wanneer het aantal pakketten van een specifiek type van een bron-IP de drempelwaarde overschrijdt, wordt een waarschuwing gegenereerd.

5. **Alerting**: Waarschuwingen worden weergegeven met details over:
   - Aanvalstype
   - Bron-IP
   - Aantal pakketten
   - Aanvalsnelheid (pakketten per seconde)

## Detectie Types

### SYN Flood
Detecteert wanneer een bron-IP een abnormaal aantal TCP SYN-pakketten verstuurt zonder de verbinding te voltooien. Dit is een indicatie van een SYN flood aanval die probeert server resources uit te putten.

### UDP Flood
Detecteert wanneer een bron-IP een groot aantal UDP-pakketten verstuurt. UDP-floods kunnen netwerkbandbreedte en server resources uitputten.

### ICMP Flood
Detecteert ping-flood aanvallen waarbij een groot aantal ICMP-echo-requests worden verstuurd om netwerkresources uit te putten.

### HTTP Flood
Detecteert applicatielaag DoS-aanvallen waarbij een groot aantal HTTP-requests worden verstuurd om webserver resources uit te putten.

## Output Voorbeeld

```
======================================================================
DoS Attack Detector - Starting Monitoring
======================================================================
Interface: All interfaces
Time Window: 10 seconds
Thresholds:
  - SYN Flood: 100 packets/10s
  - UDP Flood: 200 packets/10s
  - ICMP Flood: 150 packets/10s
  - HTTP Flood: 300 requests/10s
======================================================================
Monitoring... (Press Ctrl+C to stop)

[STATS] SYN: 45/100 | UDP: 12/200 | ICMP: 3/150 | HTTP: 23/300

======================================================================
[ALERT] 2026-02-12 14:30:15 - SYN FLOOD ATTACK DETECTED!
======================================================================
Source IP: 192.168.1.100
Packet Count: 150 (Threshold: 100)
Time Window: 10 seconds
Attack Rate: 15.00 packets/second
======================================================================
```

## Beperkingen

- Vereist root/administrator rechten voor packet capture
- Kan false positives genereren bij legitieme hoge verkeersvolumes
- Detecteert alleen bekende DoS-patronen; geavanceerde aanvallen kunnen worden gemist
- Werkt alleen op het lokale netwerksegment waar de detector draait

## Veiligheid

**BELANGRIJK**: Deze tool is uitsluitend bedoeld voor defensieve doeleinden - het detecteren en monitoren van DoS-aanvallen op je eigen netwerk. Gebruik deze tool niet om aanvallen uit te voeren of om netwerken te monitoren zonder toestemming.

## Licentie

Dit project is bedoeld voor educatieve en defensieve doeleinden.
