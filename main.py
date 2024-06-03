import threading
from time import sleep
import zmq

min_port = 42000
max_port = 42016


# TODO: If this is used only once, remove this function
def send(socket, topic, msg):
    with time_lock:
        time[0] += 1
        socket.send((topic + " " + msg).encode())


def run_server(time_lock, time, port_ref, port_lock):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    port_selected = socket.bind_to_random_port("tcp://*",
                                               min_port=min_port,
                                               max_port=max_port,
                                               max_tries=100)
    port_ref[0] = port_selected
    port_lock.release()
    print("Bound to port", port_ref[0])
    while True:
        #  Do some 'work'
        sleep(1)
        #  Send reply back to client
        with time_lock:
            send(socket, "time", time[0] + " Hello from " + str(port_selected))
        pass


def recv_lamport(msg, time_lock, time, port):
    recv_time, msg = msg.split(" ", maxsplit=1)
    recv_time = int(recv_time)
    print("%s: Received '%s' at time %d" % (port, msg, recv_time))
    with time_lock:
        time[0] = max(time[0], recv_time) + 1


def run_client(ip, time_lock, time, port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    # TODO: Create thread that tries to connect to other ports regularly
    for i in range(min_port, max_port):
        if i == port:
            continue # Don't listen to yourself
        socket.connect("tcp://%s:%s" % (ip, str(i)))
    socket.setsockopt(zmq.SUBSCRIBE, b"")

    while True:
        string = socket.recv().decode()
        topic, msg = string.split(" ", maxsplit=1)
        if topic == "time":
            recv_lamport(msg, time_lock, time, port)


# ZeroMQ doesn't support bidirectional broadcasting, so we have to create a
# separate thread for the client and the server, both with pub/sub architecture
time_lock = threading.Lock()
time = [0] # Storing as array so we can pass by reference
port_lock = threading.Lock()
port = [0] # Ditto. No need for
port_lock.acquire()
server_thread = threading.Thread(target=run_server,
                                 args=(time_lock, time, port, port_lock))
print("Starting server thread")
server_thread.start()

ip = "localhost" # TODO: Don't use localhost
sleep(1) # Wait for servers to open, also so that we don't have to use locks
         # for accessing port

port_lock.acquire()
client_thread = threading.Thread(target=run_client,
                                 args=(ip, time_lock, time, port[0]))

print("Starting client thread")
client_thread.start()
print("Waiting")
sleep(10)
server_thread.join()
client_thread.join()
print("Done")
port_lock.release()
