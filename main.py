import threading
import time
import random

class TokenRing:
    def __init__(self, num_processes, max_passes):
        self.num_processes = num_processes
        self.max_passes = max_passes
        self.token_pass_count = 0
        self.token_holder = 0  # Start with process 0 holding the token
        self.lock = threading.Lock()

        self.active_processes = {i: True for i in range(num_processes)}
        self.leader = max(self.active_processes.keys())  # Highest PID is leader initially

        self.processes = [
            threading.Thread(target=self.process, args=(i,)) for i in range(num_processes)
        ]

    def process(self, pid):
        while self.token_pass_count < self.max_passes:
            if not self.active_processes[pid]:
                time.sleep(1)
                continue

            if not self.lock.acquire(timeout=3):
                print(f"[Lock Timeout] Process {pid} could not acquire lock!")
                continue

            try:
                if self.token_holder == pid:
                    print(f"Process {pid} has the token and is in the critical section.")
                    time.sleep(2)

                    if random.random() < 0.1:
                        print(f"[Process Failed] Process {pid} has crashed!")
                        self.active_processes[pid] = False
                        self.trigger_leader_election()
                        continue  # Don't try to pass token from dead process

                    next_pid = self.get_next_active_process(pid)
                    if next_pid is None:
                        print("[System Halted] No active processes remaining.")
                        break

                    print(f"Process {pid} passes the token to Process {next_pid}.")
                    self.token_holder = next_pid
                    self.token_pass_count += 1
            finally:
                self.lock.release()

            time.sleep(1)

    def get_next_active_process(self, pid):
        """Safely returns the next active process after the given pid."""
        active_nodes = [p for p in range(self.num_processes) if self.active_processes.get(p, False)]

        if not active_nodes:
            return None  # System dead

        if pid not in active_nodes:
            # Current process has failed, just return first in list
            return active_nodes[0]

        index = active_nodes.index(pid)
        next_index = (index + 1) % len(active_nodes)
        return active_nodes[next_index]

    def trigger_leader_election(self):
        """Elect highest active process as new leader, regenerate token if needed."""
        active_nodes = [p for p in range(self.num_processes) if self.active_processes.get(p, False)]

        if not active_nodes:
            print("[System Halted] No active processes to elect a leader.")
            return

        self.leader = max(active_nodes)
        print(f"[New Leader Elected] Process {self.leader} is now the leader.")

        if self.token_holder not in active_nodes:
            self.token_holder = self.leader
            print(f"[Token Regenerated] New leader {self.leader} has the token.")

    def start(self):
        for p in self.processes:
            p.start()
        for p in self.processes:
            p.join()

if __name__ == "__main__":
    num_processes = 5
    max_passes = 5
    token_ring = TokenRing(num_processes, max_passes)
    token_ring.start()