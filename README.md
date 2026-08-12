# File Exchange

A lightweight LAN-based file transfer app. Discover devices on your local
network and send files directly between them — no internet, cloud, or
account required.

## Download

**[⬇ Get the latest release] 
https://github.com/ibrahimrzaiqat/File-Exchange/releases

## Quick Start

1. Run `FileExchange.exe` on each device (same WiFi/hotspot network)
2. Windows will warn it's unsigned — click **More info → Run anyway**, and
   **Allow** when Firewall asks
3. Wait a few seconds — devices appear automatically in the list
4. Click a device, drag & drop your file(s) onto the app, hit **Send**

Received files land straight in your **Downloads** folder.

## Features

- 🔍 Automatic device discovery — no manual IP entry
- 📂 Drag-and-drop, including multiple files at once
- 📊 Real-time progress tracking
- ⚠️ Auto-removes offline devices and cancels dead transfers cleanly
- 🖥️ Standalone `.exe` — no Python required to run it

---

<details>
<summary><strong>Running from source</strong></summary>

Requires Python 3.8+ and PyQt5.

```bash
git clone https://github.com/ibrahimrzaiqat/File-Exchange.git
cd File-Exchange
pip install PyQt5
python FileExchange.py
```

</details>

<details>
<summary><strong>How it works</strong></summary>

- **Discovery**: each instance periodically broadcasts a UDP message
  announcing itself; others on the same network hear it and add the sender
  to their device list
- **Staleness detection**: a device that stops broadcasting (closed, asleep,
  disconnected) is automatically removed from the list after a short timeout
- **Transfer**: once a device is selected, the app opens a direct TCP
  connection and streams the file(s) over, with a small JSON header per file
  describing its name and size

</details>

<details>
<summary><strong>Limitations</strong></summary>

- Local network only — not an internet file-sharing tool; devices must
  share the same network to see each other
- No encryption or authentication — intended for trusted home/family
  networks, not public ones
- Windows only (packaged `.exe`); running from source may work
  cross-platform but is untested
- Some mobile hotspots isolate connected devices from each other
  ("AP isolation"), which can block discovery even on the same hotspot —
  this is a phone/OS setting outside the app's control

</details>

## License

Personal project, shared for educational purposes.
