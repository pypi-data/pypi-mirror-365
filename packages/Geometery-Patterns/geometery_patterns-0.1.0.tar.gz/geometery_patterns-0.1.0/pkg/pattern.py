def pyramid(rows):
    for i in range(1,rows+1):
        print(" " * (rows-i) + "* " * i)

def right_angle(rows):
    for i in range(1,rows+1):
        print("*" * i)


def left_angle(rows):
    for i in range(1,rows+1):
        print(" " * (rows-i) + "*" * i)