# ICMP Ping Tool GUI

A simple GUI-based ping tool that allows users to ping a host and view real-time statistics, including round-trip time (RTT), TTL, and packet loss. This tool is useful for network diagnostics and helps users monitor connectivity with remote servers or devices.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation
Follow these steps to install and set up the Ping Tool GUI on your local machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nuha63 ping-tool-gui.git
   ```

2. **Install Python**:
   Make sure you have Python 3.x installed. You can download it from [python.org](https://www.python.org/downloads/).

3. **Install dependencies**:
   The project requires the `tkinter` and `socket` libraries. These are typically included in standard Python distributions, but you can install any missing libraries with:
   ```bash
   pip install tk
   ```

4. **Run the application**:
   To launch the Ping Tool GUI, run the Python script:
   ```bash
   python ICMP_Pinger_Gui.py
   ```

## Usage

1. Open the application, and you'll see a window with an input field for the host (IP or domain).
2. Enter a valid host (e.g., `google.com`) in the input field.
3. Click the "Start Ping" button to begin pinging the host. The results will appear in the text box below.
4. To stop the pinging, click the "Stop Ping" button. The statistics, including packet loss, RTT min/avg/max, and the number of packets sent/received, will be displayed in the result section.

Example usage:

- Enter `google.com` in the "Enter Host" field and press "Start Ping".
- View the ping results with RTT and TTL.
- Stop the pinging anytime and see statistics.

## Features

- **Real-time Ping Results**: View live ping responses with RTT and TTL for each packet sent.
- **Packet Loss**: See the percentage of packet loss while pinging the host.
- **Min/Avg/Max RTT**: The round-trip time (RTT) statistics are displayed, including minimum, average, and maximum values.
- **Error Handling**: Friendly error messages for DNS resolution failures or unreachable hosts.
- **Stop and Statistics**: You can stop the ping process and get detailed statistics like packets sent/received and RTT values.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Maintainer: [Sanjida Islam Nuha](https://github.com/nuha63)

Feel free to reach out for any questions or feedback regarding the Ping Tool GUI!