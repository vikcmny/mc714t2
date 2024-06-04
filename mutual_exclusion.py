class ExclusionModule:
    def __init__(self, host):
        self.wants_resource = False
        self.has_resource = False
        self.last_host_request_time = None
        self.host = host

    def queue_request(self, recv_id):
        pass # TODO

    def recv(self, msg):
        recv_time, recv_id, msg = self.host.read(msg)
        # TODO
        msg_split = msg.split(" ")
        if len(msg_split) == 1: # This is a request
            if not self.wants_resource and not self.has_resource:
                self.host.connect_to_id(recv_id)
                self.host.send(recv_id, "resource", "OK")
            elif self.has_resource:
                self.queue_request(recv_id)
            else: # wants_resource == True
                if recv_time < self.last_host_request_time:
                    self.host.send(recv_id, "resource", "OK")
                else:
                    self.queue_request(recv_id)

    def broadcast_if_necessary(self):
        # TODO: Store timestamp of when you sent the broadcast
        # TODO: Don't broadcast more than once
        if (not self.sent_request) and \
           self.wants_resource and not self.has_resource:
            self.last_host_request_time = self.host.time
            self.host.broadcast("resource", "request")
            self.sent_request = True
