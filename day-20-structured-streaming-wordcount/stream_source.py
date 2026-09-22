"""
Acts as the 'nc -lk 9999' equivalent for this exercise: a plain TCP
server that waits for Spark's socket source to connect, then streams out
a batch of sentences with a short delay between each - genuinely
arriving over time rather than all at once, which is the actual point
of testing a streaming word count.
"""
import socket
import time

HOST = "localhost"
PORT = 9999

lines = [
    "the quick brown fox jumps over the lazy dog",
    "the dog barks at the fox",
    "spark streaming reads words from a socket",
    "word count is the hello world of streaming",
    "the quick fox runs fast",
    "streaming data arrives continuously over time",
    "spark processes each micro batch as it arrives",
    "the lazy dog sleeps all day",
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
print(f"Listening on {HOST}:{PORT}, waiting for Spark to connect...", flush=True)

conn, addr = server.accept()
print(f"Connected by {addr}", flush=True)

with conn:
    for line in lines:
        print(f"Sending: {line}", flush=True)
        conn.sendall((line + "\n").encode("utf-8"))
        time.sleep(2)

print("All lines sent. Closing connection.", flush=True)
