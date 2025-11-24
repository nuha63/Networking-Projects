import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import statistics
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ICMPPingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICMP Pinger Lab")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Styling
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 11))
        
        # --- Input section ---
        ttk.Label(root, text="Enter Host or IP:").pack(pady=10)
        self.host_entry = ttk.Entry(root, width=40)
        self.host_entry.pack(pady=5)
        
        self.start_button = ttk.Button(root, text="Start Ping", command=self.start_ping)
        self.start_button.pack(pady=5)
        
        self.stop_button = ttk.Button(root, text="Stop Ping", command=self.stop_ping, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Simulation toggle
        self.simulate_var = tk.BooleanVar(value=False)
        self.sim_check = ttk.Checkbutton(root, text="Simulation only (no network)", variable=self.simulate_var)
        self.sim_check.pack(pady=2)

        # --- Output text box ---
        self.output_box = tk.Text(root, height=10, width=90, font=("Consolas", 10))
        self.output_box.pack(pady=10)
        
        # --- Network animation canvas ---
        self.net_canvas = tk.Canvas(root, width=760, height=80, bg='white', highlightthickness=1, highlightbackground='#ccc')
        self.net_canvas.pack(pady=5)
        # Positions for local and remote nodes
        self._node_y = 40
        self._left_x = 80
        self._right_x = 680
        # Draw nodes
        node_radius = 18
        self.net_canvas.create_oval(self._left_x-node_radius, self._node_y-node_radius, self._left_x+node_radius, self._node_y+node_radius, fill='#4CAF50', outline='')
        self.net_canvas.create_text(self._left_x, self._node_y+30, text='You')
        self.net_canvas.create_oval(self._right_x-node_radius, self._node_y-node_radius, self._right_x+node_radius, self._node_y+node_radius, fill='#2196F3', outline='')
        self.net_canvas.create_text(self._right_x, self._node_y+30, text='Host')
        # Packet item will be created when animating
        self._packet_item = None
        self._packet_label = None
        
        # --- Graph Area ---
        fig, self.ax = plt.subplots(figsize=(7, 3))
        self.ax.set_title("RTT vs Sequence")
        self.ax.set_xlabel("Sequence Number")
        self.ax.set_ylabel("RTT (ms)")
        self.line, = self.ax.plot([], [], marker='o')
        
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)
        
        # Data
        self.rtts = []
        self.seqs = []
        self.stop_flag = False

    def log(self, message):
        self.output_box.insert(tk.END, message + "\n")
        self.output_box.see(tk.END)

    def update_graph(self):
        self.line.set_data(self.seqs, self.rtts)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def animate_packet(self, to_host=True, duration=600):
        """Animate a small circle from local node to host (to_host=True) or back.

        This method runs in the GUI thread and uses `after` for smooth animation.
        """
        steps = 20
        delay = max(1, int(duration / steps))

        start_x = self._left_x if to_host else self._right_x
        end_x = self._right_x if to_host else self._left_x
        y = self._node_y

        # create packet item if not exists
        if self._packet_item is None:
            self._packet_item = self.net_canvas.create_oval(start_x-6, y-6, start_x+6, y+6, fill='orange', outline='')
        else:
            # move to start pos
            coords = self.net_canvas.coords(self._packet_item)
            cur_x = (coords[0] + coords[2]) / 2
            self.net_canvas.move(self._packet_item, start_x - cur_x, 0)
        # create or move label
        if self._packet_label is None:
            self._packet_label = self.net_canvas.create_text(start_x, y-14, text="", font=("Arial", 9))
        else:
            lbl_coords = self.net_canvas.coords(self._packet_label)
            cur_x_lbl = lbl_coords[0]
            self.net_canvas.move(self._packet_label, start_x - cur_x_lbl, 0)

        dx = (end_x - start_x) / steps

        def step(i):
            if i >= steps:
                # final position; small highlight to indicate arrival
                self.net_canvas.itemconfig(self._packet_item, fill='lime' if to_host else 'orange')
                # schedule restore color
                self.root.after(150, lambda: self.net_canvas.itemconfig(self._packet_item, fill='orange'))
                # hide label after arrival
                if self._packet_label is not None:
                    self.root.after(300, lambda: self.net_canvas.itemconfig(self._packet_label, text=""))
                return
            self.net_canvas.move(self._packet_item, dx, 0)
            if self._packet_label is not None:
                self.net_canvas.move(self._packet_label, dx, 0)
            self.root.after(delay, lambda: step(i+1))

        # start animation
        step(0)

    def set_packet_label(self, seq):
        """Set the label text shown above the moving packet (seq number)."""
        if self._packet_label is None:
            return
        self.net_canvas.itemconfig(self._packet_label, text=f"seq={seq}")

    def ping_host(self, host):
        # Import scapy here to avoid raising at module import time when GUI can't start
        simulate = bool(self.simulate_var.get())
        if not simulate:
            try:
                from scapy.all import IP, ICMP, sr1
            except Exception as e:
                self.log(f"scapy import failed: {e}")
                self.log("Install scapy in this Python environment to send ICMP packets or enable Simulation mode.")
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                return

        seq = 0
        sent = 0
        received = 0
        self.rtts.clear()
        self.seqs.clear()

        self.log(f"Pinging {host} with ICMP Echo Requests...\n")
        while not self.stop_flag and seq < 10:  # 10 packets
            sent += 1
            # animate packet going out (scheduled on GUI thread)
            try:
                # set label for this seq
                self.root.after(0, lambda s=seq: self.set_packet_label(s))
                self.root.after(0, lambda: self.animate_packet(to_host=True, duration=600))
            except Exception:
                pass

            if simulate:
                # simulate network RTT (ms)
                fake_rtt = random.uniform(10, 120)
                time.sleep((fake_rtt + random.uniform(5, 30)) / 1000.0)
                end_time = time.time()
                rtt = fake_rtt
                self.rtts.append(rtt)
                seq += 1
                received += 1
                self.seqs.append(seq)
                # animate return
                try:
                    self.root.after(0, lambda: self.animate_packet(to_host=False, duration=500))
                except Exception:
                    pass
                self.log(f"Reply from {host}: seq={seq} time={rtt:.2f} ms (simulated)")
            else:
                packet = IP(dst=host)/ICMP(seq=seq)
                start_time = time.time()
                reply = sr1(packet, timeout=2, verbose=0)
                end_time = time.time()
                seq += 1

                if reply:
                    rtt = (end_time - start_time) * 1000
                    self.rtts.append(rtt)
                    self.seqs.append(seq)
                    received += 1
                    # animate packet returning
                    try:
                        self.root.after(0, lambda: self.animate_packet(to_host=False, duration=500))
                    except Exception:
                        pass
                    self.log(f"Reply from {reply.src}: seq={seq} time={rtt:.2f} ms")
                else:
                    self.log(f"Request timed out for seq={seq}")

            self.update_graph()
            time.sleep(1)

        # Show summary
        loss = ((sent - received) / sent) * 100
        self.log("\n--- Ping Statistics ---")
        self.log(f"Packets: Sent = {sent}, Received = {received}, Lost = {sent - received} ({loss:.0f}% loss)")
        if self.rtts:
            self.log(f"RTT (ms): min={min(self.rtts):.2f}, max={max(self.rtts):.2f}, avg={statistics.mean(self.rtts):.2f}")
        else:
            self.log("No replies received.")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def start_ping(self):
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter a host or IP address.")
            return
        self.output_box.delete(1.0, tk.END)
        self.stop_flag = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.ping_host, args=(host,), daemon=True).start()

    def stop_ping(self):
        self.stop_flag = True
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("\nPing stopped by user.")

def headless_ping(host, count=10, timeout=2):
    """Fallback console ping when Tcl/Tk is unavailable."""
    seq = 0
    sent = 0
    received = 0
    rtts = []

    print(f"Headless: pinging {host} with {count} packets...")
    # Import scapy locally so module import doesn't fail when scapy isn't available
    try:
        from scapy.all import IP, ICMP, sr1
    except Exception as e:
        print("scapy import failed:", e)
        print("Install scapy in this Python environment to send ICMP packets.")
        return
    while seq < count:
        sent += 1
        packet = IP(dst=host) / ICMP(seq=seq)
        start_time = time.time()
        try:
            reply = sr1(packet, timeout=timeout, verbose=0)
        except PermissionError as e:
            print("Permission error: sending ICMP may require administrator privileges on Windows.")
            raise
        end_time = time.time()

        if reply:
            rtt = (end_time - start_time) * 1000
            rtts.append(rtt)
            received += 1
            print(f"Reply from {reply.src}: seq={seq} time={rtt:.2f} ms")
        else:
            print(f"Request timed out for seq={seq}")

        seq += 1
        time.sleep(1)

    loss = ((sent - received) / sent) * 100 if sent else 0
    print("\n--- Ping Statistics ---")
    print(f"Packets: Sent = {sent}, Received = {received}, Lost = {sent - received} ({loss:.0f}% loss)")
    if rtts:
        print(f"RTT (ms): min={min(rtts):.2f}, max={max(rtts):.2f}, avg={statistics.mean(rtts):.2f}")


def main():
    parser = argparse.ArgumentParser(description="ICMP pinger GUI or headless fallback")
    parser.add_argument("host", nargs="?", help="Host or IP to ping (if provided in headless mode)")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of packets (headless default 10)")
    parser.add_argument("--headless", action="store_true", help="Run in headless console mode (no GUI)")
    parser.add_argument("--simulate", action="store_true", help="Run GUI in simulation mode (no network)")
    args = parser.parse_args()

    if args.headless:
        if not args.host:
            print("Headless mode requires a host argument. Example: python icmp_pinger_gui.py 8.8.8.8 --headless")
            return
        headless_ping(args.host, count=args.count)
        return

    # Try to start GUI, but handle Tcl/Tk initialization errors and fall back
    try:
        root = tk.Tk()
    except Exception as e:
        print("Failed to initialize Tkinter/Tcl. GUI cannot start.")
        print("Error:", e)
        print("Common fixes: install the official Python from python.org with Tcl/Tk support, or set TCL_LIBRARY/TK_LIBRARY to your Tcl directory.")
        if args.host:
            print("\nFalling back to headless mode using provided host:")
            headless_ping(args.host, count=args.count)
        else:
            print("Run with --headless <host> to use console fallback, or fix your Tcl/Tk installation to enable the GUI.")
        return

    app = ICMPPingerApp(root)
    # If host provided as arg, pre-fill the entry
    if args.host:
        app.host_entry.insert(0, args.host)
    # set simulation mode from CLI
    if args.simulate:
        app.simulate_var.set(True)
    # auto-start ping when host provided from CLI
    if args.host:
        app.start_ping()
    root.mainloop()


if __name__ == "__main__":
    main()
