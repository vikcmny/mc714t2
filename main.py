from time import sleep
import random
from network import Host
from mutual_exclusion import ExclusionModule
from election import ElectionModule


def print_status(host, resource_module, leader_module):
    DGRAY = '\033[0;37m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'
    if resource_module.has_resource:
        print(f"{WHITE}Using resource!{NC} ", end="")
    elif resource_module.wants_resource:
        print(f"{DGRAY}Wants resource{NC}  ", end="")
    else:
        print("...             ", end="")

    if leader_module.leader is None:
        print("Who?    ", end="")
    elif leader_module.leader == host.host_id:
        print("Leader! ", end="")
    else:
        print(f"{leader_module.leader:>7}", end=" ")

    print("Time:", host.time)

    for i in range(len(resource_module.ok_tracker)):
        if i == host.host_id:
            print(".", end=" ")
        else:
            print(resource_module.ok_tracker[i], end=" ")


def reset_cursor():
    print("\033[F" * 1, end="")


host = Host()
resource_module = ExclusionModule(host)
leader_module = ElectionModule(host)

sleep(2) # Wait for all other processes to start

while True:
    print_status(host, resource_module, leader_module)

    # Do some 'work' for a random amount of time, with average of 0.1 second
    # But do not work if you are participating in an election
    if not leader_module.sent_request:
        sleep(random.expovariate(lambd=10))

    if resource_module.has_resource:
        if random.randint(0, 10) == 0:
            resource_module.release()
            resource_module.wants_resource = False
    else:
        if not resource_module.wants_resource:
            resource_module.wants_resource = (random.randint(0, 10) == 0)

    if random.randint(0, 50) == 0:
        # TODO Make hosts actually die
        leader_module.leader = None # Simulate not being able to communicate with the leader

    resource_module.broadcast_if_necessary()
    leader_module.broadcast_if_necessary()
    # TODO: Send in certain intervals

    for string in host.recv():
        string = string.decode()
        topic, msg = string.split(" ", maxsplit=1)

        if topic == "resource":
            resource_module.recv(msg)
        if topic == "leader":
            leader_module.recv(msg)

    reset_cursor()
