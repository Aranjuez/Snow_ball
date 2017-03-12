from math import pi, atan, acos, degrees
import socket
import sys
import time


LOOP_SIZE = 3
USER = "a"
PASSWORD = "a"


def is_equal(x, y):
    return (x - y) < 0.1


def run(command):
    data = command + "\n"
    sock.sendall(bytes(data, "utf-8"))
    sfile = sock.makefile()
    rline = sfile.readline()
    result = rline.split()
    return result

#TODO pub bomb in front of plane
def put_bomb_now():
    status = run("STATUS")
    bomb_x, bomb_y = status[0][1], status[0][2]
    run("BOMB {0} {1}".format(bomb_x, bomb_y))


def scan_neighbourhood():
    status = run("STATUS")
    if status[6] != '0':
        bomb_x = float(status[8])
        bomb_y = float(status[9])
        print("Found bomb at x={0}, y={1}".format(bomb_x, bomb_y))
        return (True, (bomb_x, bomb_y))
    return (False, None)


def random_walk():
    i = 0
    mines = scan_map()
    print("-------mines found {0}".format(mines))
    run("BRAKE")
    time.sleep(5)
    status = run("STATUS")
    status[1] = float(status[1])
    status[2] = float(status[2])
    first_angle = get_radian(mines[LOOP_SIZE-1][0] - status[1], status[2] - mines[LOOP_SIZE-1][1])
    run("ACCELERATE {0} 1".format(first_angle))
    time.sleep(3)
    
    run("BRAKE")
    time.sleep(8)
    
    status = run("STATUS")
    status[1] = float(status[1])
    status[2] = float(status[2])
    second_angle = get_radian(mines[0][0] - status[1], status[2] - mines[0][1])
    run("ACCELERATE {0} 1".format(second_angle))
    time.sleep(2.5)
    
    next_i = 0
    try:
        while True:
            status = run("STATUS")
            x = float(status[1])
            y = float(status[2])
            if is_nearby(mines[next_i], (float(status[1]), float(status[2]))):
                run("BRAKE")
                time.sleep(2)
            if is_zero(float(status[3])) and is_zero(float(status[4])):
                next_i = next_i + 1
                if next_i == LOOP_SIZE:
                    next_angle = get_radian(mines[0][0]-x, y-mines[0][1])
                    next_i = 0
                else:
                    next_angle = get_radian(mines[next_i][0]-x, y-mines[next_i][1])
                run("ACCELERATE {0} 1".format(next_angle))
                time.sleep(1)
            
    except KeyboardInterrupt:
        print('interrupted!')


def get_radian(dx, dy):
    angle = atan(dy/dx)
    if dx > 0:
        if dy < 0:
            angle += (2 * pi)
    else:
        angle += pi
    return 2*pi - angle


def walk_towards_mine(mine):
    mine_x = float(mine[0])
    mine_y = float(mine[1])
    #Wait until v=0
    print("Walking towards mine")
    while True:
        status = run("STATUS")
        print("Vx={0}   Vy={1}".format(float(status[3]), float(status[4])))
        if abs(float(status[3])) < pow(10, -2) and abs(float(status[4])) < pow(10, -2):
            break
        time.sleep(2)
    x = float(status[1])
    y = float(status[2])
    print("Plane position------({0},{1})".format(x, y))
    print("Mine position------({0},{1})".format(mine_x, mine_y))
    angle_plane_mine = get_radian(mine_x - x, y - mine_y)
    
    run("ACCELERATE {0} 1".format(angle_plane_mine))


def add_new_mine(mines, newMine):
    for mine in mines:
        if is_equal(mine[0], newMine[0]) and is_equal(mine[1], newMine[1]):
            return
    print("------------Added new mine!")
    mines.append(newMine)


def scan_map():
    print("Start scanning map")
    mines = []
    numOfMines = 0
    configurations = run("CONFIGURATIONS")
    print(configurations)
    mapHeight = float(configurations[4])
    scanRadius = float(configurations[8])
    accAngle = acos(2*scanRadius/mapHeight)
    print("Scan angle {0}".format(accAngle))
    run("ACCELERATE {0} 1".format(accAngle))
    while True:
        put_bomb_now()
        nearbyInfo = scan_neighbourhood()
        if nearbyInfo[0]:
            add_new_mine(mines, nearbyInfo[1])
            if len(mines) == LOOP_SIZE:
                print("Finished scanning!")
                return mines


HOST, PORT = "localhost", 17429
data = USER + " " + PASSWORD + "\n"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.sendall(bytes(data, "utf-8"))
print("Connected")
scan_map()