from time import sleep
import random
from network import Host
from mutual_exclusion import ExclusionModule


def recv_lamport(host, msg):
    recv_time, recv_id, msg = host.read(msg)


def recv_leader(host, msg):
    recv_time, recv_id, msg = host.read(msg)
    # TODO


host = Host()
resource_module = ExclusionModule(host)
# leader_module = ElectionModule(host) # TODO

sleep(2)

while True:
    #  Do some 'work' for a random amount of time, with average of 1 second
    # sleep(random.expovariate(lambd=10))
    sleep(0.1)

    # There is a 1 in 10 chance of us wanting to access the resource
    resource_module.wants_resource = (random.randint(0, 10) == 0)
    leader_is_dead = False # TODO
    resource_module.broadcast_if_necessary()
    if leader_is_dead:
        host.broadcast("leader", "TODO")
    else:
        # TODO: Send in certain intervals
        host.broadcast("time", "Hello")

    string = host.recv()
    print("Received string: %s" % string)
    string = string.decode()
    topic, msg = string.split(" ", maxsplit=1)

    if topic == "time":
        recv_lamport(host, msg)
    if topic == "resource":
        resource_module.recv(msg)
    if topic == "leader":
        recv_leader(msg)
