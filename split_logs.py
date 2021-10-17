def write_log(num, name, data):
    f = open(name, 'w')
    for i in range(num - 1):
        f.write(data[i] + "\n")
    f.write(data[-1])


with open("logs/monthlogs.log") as file:
    data = file.read()
    logs = data.split("\n")
    print(len(logs))
    write_log(1000, "logs/logs_1000.log", logs)
    write_log(10000, "logs/logs_10000.log", logs)
    write_log(100000, "logs/logs_100000.log", logs)
    write_log(1000000, "logs/logs_1000000.log", logs)
