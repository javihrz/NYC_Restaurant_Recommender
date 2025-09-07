import os
import time


def initialize():
    """creates all the .txt files incase they aren't already their locally"""
    if not os.path.exists("log.txt"):
        with open("log.txt", "w"):
            pass       # Creates an empty file

    if not os.path.exists("response.txt"):
        with open("response.txt", "w"):
            pass

    if not os.path.exists("request.txt"):
        with open("request.txt", "w"):
            pass


def write_log(entry):
    """this puts in another entry into log.txt"""
    entry = str(entry)
    with open("log.txt", "a") as log:
        log.write(entry.strip() + "\n")


def copy_log():
    """copy's the contents of log.txt and puts them in response.txt, which the developer can then extract/interact with, log.txt cannot
    be interacted with directly"""
    with open("log.txt", "r") as source:
        lines = source.readlines()

    with open("response.txt", "w") as destination:
        for line in lines:
            if line.strip():
                destination.write(line)


def delete_last_log():
    """deletes the last log, can be looped multiple times if more than one deletion is wanted"""
    with open("log.txt", "r") as log:
        lines = log.readlines()
    with open("log.txt", "w") as log:
        # slice off the last line/log
        log.writelines(lines[:-1])


def process_command(command):
    """decides which process the developer has chosen for the microservice to do"""
    command = str(command)

    if command[0:2] == "w ":
        data = command[2:].strip()
        write_log(data)

    elif command == "d":
        delete_last_log()

    elif command == "a2":
        copy_log()


def listen():
    """checks requests.txt every 0.2 seconds to see if a command has been input"""

    print("watching request.txt...")
    while True:
        if os.path.exists("request.txt"):
            with open("request.txt", "r") as request:
                content = request.read().strip()

            if content:
                process_command(content)

                # clear request file to show the message was received
                with open("request.txt", "w") as request:
                    request.write("")

        time.sleep(0.2)  # delay


if __name__ == "__main__":
    initialize()
    listen()
