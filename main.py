from time import sleep
import random
from network import Host
from mutual_exclusion import ExclusionModule
from election import ElectionModule


def recv_lamport(host, msg):
    recv_time, recv_id, msg = host.read(msg)


host = Host()
resource_module = ExclusionModule(host)
leader_module = ElectionModule(host)

sleep(2) # Wait for all other processes to start

while True:
    # Print the current status
    if resource_module.has_resource:
        print("Using resource! ", end="")
    elif resource_module.wants_resource:
        print("Wants resource  ", end="")
    else:
        print("...             ", end="")

    if leader_module.leader is None:
        print("Who?    ", end="")
    elif leader_module.leader == host.host_id:
        print("Leader! ", end="")
    else:
        print(f"{leader_module.leader:>7}", end=" ")

    print("Time:", host.time)

    # Do some 'work' for a random amount of time, with average of 0.1 second
    # But do not work if you are participating in an election
    if not leader_module.sent_request:
        sleep(random.expovariate(lambd=10))

    if resource_module.has_resource:
        if random.randint(0, 100) == 0:
            resource_module.release()
            resource_module.wants_resource = False
    else:
        resource_module.wants_resource |= (random.randint(0, 10) == 0)

    if random.randint(0, 100) == 0:
        # TODO Make hosts actually die
        leader_module.leader = None # Simulate not being able to communicate with the leader

    # resource_module.broadcast_if_necessary()
    leader_module.broadcast_if_necessary()
    # TODO: Send in certain intervals

    for string in host.recv():
        string = string.decode()
        topic, msg = string.split(" ", maxsplit=1)

        if topic == "time":
            recv_lamport(host, msg)
        if topic == "resource":
            resource_module.recv(msg)
        if topic == "leader":
            leader_module.recv(msg)

    for i in range(1):
        print("\033[F", end="")
