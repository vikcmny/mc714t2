from time import sleep
import zmq

min_port = 42000
max_port = 42016

ip = "localhost"


def recv_lamport(msg, time, port):
    recv_time, msg = msg.split(" ", maxsplit=1)
    recv_time = int(recv_time)
    print("%s: Received '%s' at time %d" % (port, msg, recv_time))
    time[0] = max(time[0], recv_time) + 1


# TODO: If this is used only once, remove this function
def send(socket, time, topic, msg):
    time[0] += 1
    socket.send((topic + " " + str(time[0]) + " " + msg).encode())


# ZeroMQ doesn't support bidirectional broadcasting, so we have to create a
# separate socket for the subscriber and the publisher
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
port = pub_socket.bind_to_random_port("tcp://*",
                                      min_port=min_port,
                                      max_port=max_port,
                                      max_tries=100)
print("Bound to port", port)

sub_socket = context.socket(zmq.SUB)
# TODO: Create thread that tries to connect to other ports regularly
for i in range(min_port, max_port):
    if i == port:
        continue # Don't listen to yourself
    sub_socket.connect("tcp://%s:%s" % (ip, str(i)))
sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

time = [0]

while True:
    #  Do some 'work'
    sleep(1)
    #  Send reply back to client
    send(pub_socket, time, "time", " Hello from " + str(port))
    string = sub_socket.recv().decode()
    topic, msg = string.split(" ", maxsplit=1)
    if topic == "time":
        recv_lamport(msg, time, port)
