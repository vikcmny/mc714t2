import zmq


class Host:
    def __init__(self):
        self.time = 0
        self.host_id = -1

        # ZeroMQ doesn't support bidirectional broadcasting, so we have to
        # create a separate socket for the subscriber and the publisher
        context = zmq.Context()
        self.pub_socket = context.socket(zmq.PUB)
        for i in range(16):
            try:
                self.pub_socket.bind("tcp://127.0.0.%d:42069" % (i + 10))
            except zmq.error.ZMQError:
                continue
            self.host_id = i
            break
        print("Host id:", self.host_id)

        self.sub_socket = context.socket(zmq.SUB)
        # TODO: Create thread that tries to connect to other ports regularly
        for i in range(0, 16):
            if i == self.host_id:
                continue # Don't listen to yourself
            self.sub_socket.connect("tcp://127.0.0.%d:42069" % (i + 10))
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

        # Besides broadcasting, we also need one-to-one messages
        self.peer_sockets = []
        self.peer_recv_socket = context.socket(zmq.ROUTER)
        self.peer_recv_socket.bind("tcp://127.0.0.%d:42068" %
                                   (self.host_id + 10))
        # Delay connecting until you receive something? Maybe?
        for i in range(0, 16):
            if i == self.host_id:
                self.peer_sockets.append(None) # Don't listen to yourself
                continue
            new_socket = context.socket(zmq.DEALER)
            new_socket.setsockopt(zmq.IDENTITY, str(self.host_id).encode())
            self.peer_sockets.append(new_socket)
            self.connect_to_id(i)

        self.poller = zmq.Poller()
        self.poller.register(self.sub_socket, zmq.POLLIN)
        self.poller.register(self.peer_recv_socket, zmq.POLLIN)

    def connect_to_id(self, connect_id):
        if connect_id == self.host_id:
            return
        addr = "tcp://127.0.0.%d:42068" % (connect_id + 10)
        self.peer_sockets[connect_id].connect(addr)

    # TODO: If this is used only once, remove this function
    def send(self, send_id, topic, msg):
        self.time += 1
        send_msg = "%s %d %d %s" % (topic, self.time, self.host_id, msg)
        self.peer_sockets[send_id].send(send_msg.encode())

    def broadcast(self, topic, msg):
        self.time += 1
        send_msg = "%s %d %d %s" % (topic, self.time, self.host_id, msg)
        self.pub_socket.send(send_msg.encode())

    def recv(self):
        polled_socks = dict(self.poller.poll(1000))
        for i in [self.sub_socket, self.peer_recv_socket]:
            if polled_socks.get(i) == zmq.POLLIN:
                msg = i.recv()
                if len(msg.decode().split(" ")) == 1:
                    msg = i.recv()
                yield msg

    def read(self, msg):
        recv_time, recv_id, msg = msg.split(" ", maxsplit=2)
        recv_time = int(recv_time)
        recv_id = int(recv_id)
        self.time = max(self.time, recv_time) + 1
        return recv_time, recv_id, msg
