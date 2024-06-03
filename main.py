from time import sleep
import random
import zmq

min_port = 42000
max_port = 42016

ip = "localhost"

time = [0]
port = 0


# TODO: If this is used only once, remove this function
def send(socket, topic, msg):
    global time
    global port
    time[0] += 1
    send_msg = "%s %d %d %s" % (topic, time[0], port, msg)
    socket.send(send_msg.encode())


def read(msg):
    global time
    recv_time, recv_port, msg = msg.split(" ", maxsplit=2)
    recv_time = int(recv_time)
    recv_port = int(recv_port)
    time[0] = max(time[0], recv_time) + 1
    return recv_time, recv_port, msg


def recv_lamport(msg):
    recv_time, recv_port, msg = read(msg)
    print("Received '" + msg + "' at time", recv_time, "from", recv_port)


def recv_exclusion(msg, port):
    recv_time, recv_port, msg = read(msg)
    # TODO
    msg_split = msg.split(" ")
    if len(msg_split) == 1: # This is a request
        pass # TODO


def recv_leader(msg, port):
    recv_time, recv_port, msg = read(msg)
    # TODO


# ZeroMQ doesn't support bidirectional broadcasting, so we have to create a
# separate socket for the subscriber and the publisher
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
port = pub_socket.bind_to_random_port("tcp://*",
                                      min_port=min_port,
                                      max_port=max_port,
                                      max_tries=100)
has_resource = False
print("Bound to port", port)

sub_socket = context.socket(zmq.SUB)
# TODO: Create thread that tries to connect to other ports regularly
for i in range(min_port, max_port):
    if i == port:
        continue # Don't listen to yourself
    sub_socket.connect("tcp://%s:%s" % (ip, str(i)))
sub_socket.setsockopt(zmq.SUBSCRIBE, b"")


while True:
    #  Do some 'work' for a random amount of time, with average of 1 second
    sleep(random.expovariate(lambd=1))

    # There is a 1 in 10 chance of us wanting to access the resource
    wants_resource = (random.randint(0, 10) == 0)
    leader_is_dead = False # TODO
    if wants_resource and not has_resource:
        send(pub_socket, "resource", "request")
    if leader_is_dead:
        send(pub_socket, "leader")
    else:
        # TODO: Send in certain intervals
        send(pub_socket, "time", "Hello")

    string = sub_socket.recv().decode()
    topic, msg = string.split(" ", maxsplit=1)

    if topic == "time":
        recv_lamport(msg)
    if topic == "resource":
        recv_exclusion(msg, port)
    if topic == "leader":
        recv_leader(msg, port)
