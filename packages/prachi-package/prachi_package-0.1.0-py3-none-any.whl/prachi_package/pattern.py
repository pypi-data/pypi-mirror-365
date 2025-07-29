def pyramid(rows):
    pattern = ""
    for i in range(1, rows + 1):
        pattern += " " * (rows - i) + "* " * i + "\n"
    return pattern


def right_angle(rows):
    pattern = ""
    for i in range(1,rows+1):
        pattern += "*" * i + "\n"
    return pattern


def left_angle(rows):
    pattern=""
    for i in range(1,rows+1):
        pattern += " " * (rows-i) + "*" * i + "\n"
    return pattern

