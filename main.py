import tkinter as tk
import threading
import time
import random
import math

class TokenRingGUI:
    def __init__(self, root, num_processes=5):
        self.root = root
        self.num_processes = num_processes
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack()

        self.process_radius = 30
        self.center_x, self.center_y = 300, 300
        self.ring_radius = 200
        self.processes = {}
        self.token_markers = {}
        self.token_holder = 0
        self.active_processes = {i: True for i in range(num_processes)}
        self.leader = max(self.active_processes.keys())
        self.token_pass_count = 0
        self.max_passes = 6

        self.log_text = tk.Text(root, height=10)
        self.log_text.pack()

        self.draw_ring()

        # Add a Start button
        self.start_button = tk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Add a Restart button
        self.restart_button = tk.Button(root, text="Restart Simulation", command=self.restart_simulation)
        self.restart_button.pack(side=tk.LEFT)

    def draw_ring(self):
        angle_step = 360 / self.num_processes
        for i in range(self.num_processes):
            angle = angle_step * i
            rad = angle * math.pi / 180
            x = self.center_x + self.ring_radius * math.cos(rad)
            y = self.center_y + self.ring_radius * math.sin(rad)
            color = "green" if self.active_processes[i] else "red"
            rectangle = self.canvas.create_rectangle(
                x - self.process_radius, y - self.process_radius,
                x + self.process_radius, y + self.process_radius,
                fill=color
            )
            label = self.canvas.create_text(x, y, text=str(i), font=("Arial", 12, "bold"))

            # Token marker (a small yellow circle)
            token_marker = self.canvas.create_oval(
                x - 5, y - self.process_radius - 15,
                x + 5, y - self.process_radius - 5,
                fill="gold", state="hidden"
            )

            self.processes[i] = (rectangle, label)
            self.token_markers[i] = token_marker


    def update_process_visual(self, pid):
        rectangle, label = self.processes[pid]
        
        label_text = f"{pid}"
        if pid == self.leader:
            label_text += " (L)"  # Show leader
        
        if not self.active_processes[pid]:
            # If it's a crashed process, show red unless it currently has the token
            color = "sky blue" if pid == self.token_holder else "red"
        else:
            color = "sky blue" if pid == self.token_holder else "green"

        self.canvas.itemconfig(rectangle, fill=color)
        self.canvas.itemconfig(label, text=label_text)
        self.update_token_marker()

    def update_token_marker(self):
        for pid, marker in self.token_markers.items():
            if pid == self.token_holder:
                self.canvas.itemconfig(marker, state="normal")
            else:
                self.canvas.itemconfig(marker, state="hidden")

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def simulation_loop(self):
        while self.token_pass_count < self.max_passes:
            pid = self.token_holder

            self.log(f"Process {pid} has the token and is in the critical section.")
            self.update_process_visual(pid)
            time.sleep(1.5)

            if self.active_processes[pid] and random.random() < 0.1:
                self.active_processes[pid] = False
                self.log(f"[Process Failed] Process {pid} has crashed!")
                self.update_process_visual(pid)
                self.trigger_leader_election()
                self.token_holder = self.leader
                self.log(f"[Token Regenerated] Leader {self.leader} has the token.")

            self.token_holder = (self.token_holder + 1) % self.num_processes
            self.token_pass_count += 1
            self.log(f"Token passed to Process {self.token_holder}.")
            self.update_process_visual(self.token_holder)
            time.sleep(0.5)

        self.log("Simulation complete.")

    def trigger_leader_election(self):
        active_nodes = [p for p in range(self.num_processes) if self.active_processes.get(p, False)]
        if not active_nodes:
            self.log("[System Halted] No active processes to elect a leader.")
            return
        self.leader = max(active_nodes)
        self.log(f"[New Leader Elected] Process {self.leader} is now the leader.")
        self.draw_ring()

    def start_simulation(self):
        threading.Thread(target=self.simulation_loop, daemon=True).start()

    def restart_simulation(self):
        self.token_pass_count = 0
        self.active_processes = {i: True for i in range(self.num_processes)}
        self.token_holder = 0
        self.leader = max(self.active_processes.keys())
        self.draw_ring()
        self.log("Simulation restarted.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Token Ring Mutual Exclusion Simulation")
    app = TokenRingGUI(root)
    root.mainloop()
