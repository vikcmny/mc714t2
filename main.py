from time import sleep
import random
import zmq

min_port = 42000
max_port = 42016

time = [0]
host_id = -1


# TODO: If this is used only once, remove this function
def send(send_id, topic, msg):
    global time
    global host_id
    global peer_sockets
    time[0] += 1
    send_msg = "%s %d %d %s" % (topic, time[0], host_id, msg)
    peer_sockets[send_id].send(send_msg.encode())


def broadcast(topic, msg):
    global pub_socket
    global time
    global host_id
    time[0] += 1
    send_msg = "%s %d %d %s" % (topic, time[0], host_id, msg)
    pub_socket.send(send_msg.encode())


def recv(poller):
    global pub_socket
    global peer_sockets
    global peer_recv_socket
    polled_socks = dict(poller.poll())
    for i in [sub_socket, peer_recv_socket]:
        if polled_socks.get(i) == zmq.POLLIN:
            msg = i.recv()
            if len(msg.decode().split(" ")) == 1:
                msg = i.recv()
            return msg


def read(msg):
    recv_time, recv_id, msg = msg.split(" ", maxsplit=2)
    recv_time = int(recv_time)
    recv_id = int(recv_id)
    time[0] = max(time[0], recv_time) + 1
    return recv_time, recv_id, msg


def recv_lamport(msg):
    recv_time, recv_id, msg = read(msg)


def recv_exclusion(msg):
    global peer_sockets
    recv_time, recv_id, msg = read(msg)
    # TODO
    msg_split = msg.split(" ")
    if len(msg_split) == 1: # This is a request
        peer_sockets[recv_id].connect("tcp://127.0.0.%d:42068" %
                                      (recv_id + 10))
        print("Sending OK")
        send(recv_id, "resource", "OK")
        pass # TODO


def recv_leader(msg):
    recv_time, recv_id, msg = read(msg)
    # TODO


# ZeroMQ doesn't support bidirectional broadcasting, so we have to create a
# separate socket for the subscriber and the publisher
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
host_id = -1
for i in range(16):
    try:
        pub_socket.bind("tcp://127.0.0.%d:42069" % (i + 10))
    except zmq.error.ZMQError:
        continue
    host_id = i
    break
has_resource = False
print("Host id:", host_id)

sub_socket = context.socket(zmq.SUB)
# TODO: Create thread that tries to connect to other ports regularly
for i in range(0, 16):
    if i == host_id:
        continue # Don't listen to yourself
    sub_socket.connect("tcp://127.0.0.%d:42069" % (i + 10))
sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

# Besides broadcasting, we also need one-to-one messages
peer_sockets = []
peer_recv_socket = context.socket(zmq.ROUTER)
peer_recv_socket.bind("tcp://127.0.0.%d:42068" % (host_id + 10))
# Delay connecting until you receive something? Maybe?
for i in range(0, 16):
    if i == host_id:
        continue # Don't listen to yourself
    new_socket = context.socket(zmq.DEALER)
    new_socket.setsockopt(zmq.IDENTITY, str(host_id).encode())
    new_socket.connect("tcp://127.0.0.%d:42068" % (i + 10))
    peer_sockets.append(new_socket)

poller = zmq.Poller()
poller.register(sub_socket, zmq.POLLIN)
poller.register(peer_recv_socket, zmq.POLLIN)

has_resource = False
while True:
    #  Do some 'work' for a random amount of time, with average of 1 second
    # sleep(random.expovariate(lambd=10))
    sleep(0.1)

    # There is a 1 in 10 chance of us wanting to access the resource
    wants_resource = (random.randint(0, 10) == 0)
    leader_is_dead = False # TODO
    if wants_resource and not has_resource:
        broadcast("resource", "request")
    if leader_is_dead:
        broadcast("leader", "TODO")
    else:
        # TODO: Send in certain intervals
        broadcast("time", "Hello")

    string = recv(poller)
    print("Received string: %s" % string)
    string = string.decode()
    topic, msg = string.split(" ", maxsplit=1)

    if topic == "time":
        recv_lamport(msg)
    if topic == "resource":
        recv_exclusion(msg)
    if topic == "leader":
        recv_leader(msg)
