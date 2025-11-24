from scapy.all import ICMP, IP, send, AsyncSniffer
import random
import time


def handle_packet(packet):
    if packet.haslayer(ICMP) and packet[ICMP].type == 8:  # Echo Request
        delay = random.uniform(0, 0.5)  # Optional random delay
        time.sleep(delay)
        reply = IP(dst=packet[IP].src, src=packet[IP].dst) / ICMP(type=0, id=packet[ICMP].id, seq=packet[ICMP].seq)
        send(reply, verbose=0)
        print(f"Echo Reply sent to {packet[IP].src} after {delay:.2f}s delay")


def start_server():
    """Start an ICMP responder using AsyncSniffer so it can be stopped cleanly with Ctrl+C.

    The sniffing runs in a background thread; we block the main thread and wait.
    On KeyboardInterrupt we stop the sniffer and exit gracefully.
    """
    print("ICMP Server running... Press Ctrl+C to stop.")
    sniffer = AsyncSniffer(filter="icmp", prn=handle_packet, store=False)
    sniffer.start()
    try:
        # Keep main thread alive while sniffer runs in background
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping ICMP server...")
        sniffer.stop()
        sniffer.join()
        print("ICMP server stopped.")


if __name__ == "__main__":
    start_server()
