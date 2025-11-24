import os
import time
import random
import argparse
from scapy.all import ICMP, IP, sr1
import statistics


def ping(host, count=4, timeout=2, stop_on_reply=False):
    """Send ICMP echo requests to `host`.

    Args:
        host (str): destination host or IP
        count (int): number of echo requests to send
        timeout (float): timeout for each request in seconds
        stop_on_reply (bool): if True, stop after first successful reply

    Returns:
        tuple: (rtts list, sent count, received count)
    """
    rtts = []
    sent = 0
    received = 0

    print(f"Pinging {host} with {count} packets:")

    try:
        for i in range(count):
            sent += 1
            packet = IP(dst=host) / ICMP(seq=i)
            start_time = time.time()
            reply = sr1(packet, timeout=timeout, verbose=0)
            end_time = time.time()

            if reply:
                rtt = (end_time - start_time) * 1000  # in ms
                rtts.append(rtt)
                received += 1
                # Print in the format you asked for
                print(f"Reply from {reply.src}: seq={i} time={rtt:.2f} ms")
                if stop_on_reply:
                    break
            else:
                print(f"Request timed out for seq={i}")

            time.sleep(1)
    except KeyboardInterrupt:
        # Allow user to stop with Ctrl+C without a huge traceback
        print("\nUser interrupted (Ctrl+C). Stopping ping loop.")

    # Statistics
    if sent == 0:
        loss = 0
    else:
        loss = ((sent - received) / sent) * 100

    print("\n--- Ping Statistics ---")
    print(f"Packets: Sent = {sent}, Received = {received}, Lost = {sent - received} ({loss:.0f}% loss)")
    if rtts:
        print(f"RTT (ms): min={min(rtts):.2f}, max={max(rtts):.2f}, avg={statistics.mean(rtts):.2f}")

    return rtts, sent, received


def _main():
    parser = argparse.ArgumentParser(description="Simple ICMP ping using scapy")
    parser.add_argument("host", nargs="?", help="Host or IP to ping (e.g. google.com)")
    parser.add_argument("-c", "--count", type=int, default=4, help="Number of packets to send")
    parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout per packet (s)")
    parser.add_argument("--stop-on-reply", action="store_true", help="Stop after first successful reply")

    args = parser.parse_args()

    if args.host:
        host = args.host
    else:
        # fallback to interactive prompt if no host provided
        host = input("Enter host (e.g., google.com): ")

    ping(host, count=args.count, timeout=args.timeout, stop_on_reply=args.stop_on_reply)


if __name__ == "__main__":
    _main()
