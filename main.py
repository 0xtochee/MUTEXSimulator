import threading
import time

class TokenRing:
    def __init__(self, num_processes, max_passes):
        self.num_processes = num_processes
        self.token_holder = 0
        self.lock = threading.Lock()
        self.processes = [threading.Thread(target=self.process, args=(i,)) for i in range(num_processes)]
        self.token_pass_count = 0
        self.max_passes = max_passes

    def process(self, pid):
        while self.token_pass_count < self.max_passes:
            with self.lock:
                if self.token_holder == pid:
                    print(f"Process {pid} has the token and is in the critical section.")
                    time.sleep(2)

                    # Pass the token
                    self.token_holder = (pid + 1) % self.num_processes
                    self.token_pass_count += 1
                    print(f"Process {pid} passes the token to Process {self.token_holder}.")

            time.sleep(1)

    def start(self):
        for p in self.processes:
            p.start()
        for p in self.processes:
            p.join()  # Ensures all threads complete

if __name__ == "__main__":
    num_processes = 5
    max_passes = 10  # Stop after 10 token passes
    token_ring = TokenRing(num_processes, max_passes)
    token_ring.start()
