class ExclusionModule:
    def __init__(self, host):
        self.host = host
        self.wants_resource = False
        self.has_resource = False
        self.last_host_request_time = None
        self.sent_request = False
        self.request_queue = []
        self.oks_received = 0

    def send(self, send_id, msg):
        print("Sending message: %s" % msg)
        self.host.send(send_id, "resource", msg)

    def broadcast(self, msg):
        self.host.broadcast("resource", msg)

    def queue_request(self, recv_id):
        self.request_queue.append(recv_id)

    def recv(self, msg):
        recv_time, recv_id, msg = self.host.read(msg)
        if msg == "request":
            if not self.wants_resource and not self.has_resource:
                self.host.connect_to_id(recv_id)
                self.send(recv_id, "OK")
            elif self.has_resource:
                self.queue_request(recv_id)
            else: # wants_resource == True
                if recv_time < self.last_host_request_time or \
                   recv_time == self.last_host_request_time and \
                   self.host.host_id < recv_id:
                    self.send(recv_id, "OK")
                else:
                    self.queue_request(recv_id)
        elif msg == "OK":
            if self.sent_request:
                self.oks_received += 1
                if self.oks_received >= 1: # TODO Use actual number of peers
                    self.has_resource = True
                    self.sent_request = False

    def broadcast_if_necessary(self):
        if not self.sent_request:
            # broadcast request and wait if you want to obtain the resource
            if self.wants_resource and not self.has_resource:
                self.host.broadcast("resource", "request")
                self.last_host_request_time = self.host.time
                self.sent_request = True

    def release(self):
        self.has_resource = False
        print("Released resource")
        for i in self.request_queue:
            print(i)
            self.send(i, "OK")
        self.oks_received = 0
