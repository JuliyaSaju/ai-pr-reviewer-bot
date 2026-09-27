def read_user_logs(filename):
    f = open(filename, "r")
    lines = f.readlines()
    return lines