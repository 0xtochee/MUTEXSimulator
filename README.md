#SIMULATION OF MUTUAL EXCLUISION USING THE TOKEN RING ALGORITHM

This simulation models mutual exclusion using a token ring protocol, with threads representing distributed processes. It ensures only one process enters the critical section via a token. If a process crashes, we elect a new leader using a Bully-style highest-PID rule, and regenerate the token if it’s lost. The code handles failure recovery, synchronization, and safe token-passing all in one system.
