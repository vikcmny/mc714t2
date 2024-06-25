import time

timeout = 1


class ElectionModule:
    def __init__(self, host):
        self.host = host
        self.leader = None
        self.waiting_for_coordinator = False
        self.sent_request = False
        self.request_time = None

    def send(self, send_id, msg):
        self.host.send(send_id, "leader", msg)

    def broadcast(self, msg):
        self.host.broadcast("leader", msg)

    def recv(self, msg):
        _, recv_id, msg = self.host.read(msg)
        if msg == "ELECTION":
            if self.host.host_id > recv_id:
                self.send(recv_id, "OK")
                self.begin_election()
        elif msg == "OK":
            assert self.host.host_id < recv_id
            self.waiting_for_coordinator = True
        elif msg == "COORDINATOR":
            self.leader = recv_id
            self.waiting_for_coordinator = False
            self.sent_request = False

    def begin_election(self):
        self.host.broadcast("leader", "ELECTION")
        self.request_time = time.time() # Local time is fine since this will only be used for timeout
        self.sent_request = True

    def broadcast_if_necessary(self):
        if not self.sent_request:
            if self.leader is None:
                self.begin_election()
        elif (not self.waiting_for_coordinator
              and time.time() > self.request_time + timeout):
            # If not waiting for a higher process to be a coordinator and
            # you didn't receive any OK, then announce to everyone you are the leader
            self.host.broadcast("leader", "COORDINATOR")
            self.sent_request = False
            self.detected_leader_is_dead = False
            self.leader = self.host.host_id
            self.request_time = None
