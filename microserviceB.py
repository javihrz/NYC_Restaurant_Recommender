import pandas as pd
import time
import os


def clear_comm_path():
    with open(comm_path, "w"):
        pass


def get_saved_favorites():
    saved_dataframe = pd.read_csv(favorite_path)
    saved_dataframe.to_csv(comm_path, mode='a', index=False)


def save_new_favorite():
    new_dataframe = pd.read_csv(comm_path)
    clear_comm_path()
    new_dataframe.to_csv(favorite_path, mode='a', header=False, index=False)


if __name__ == '__main__':
    comm_path = "comm_pipe_b.csv"
    favorite_path = "favorite_dataset.csv"

    while True:
        time.sleep(3)
        comm_path_size = os.stat(comm_path).st_size

        if comm_path_size == 0:
            continue

        with open(comm_path, "r") as comm_csv_file:
            first_line = comm_csv_file.readline().strip()

        if comm_path_size == 3 and first_line == "b2":
            get_saved_favorites()
            print("Retrieved favorites dataframe.")

        elif comm_path_size > 3 and first_line == "b2":
            print("Waiting to transfer...")

        elif first_line == "transfer complete":
            clear_comm_path()
            print("Transfer of dataframe is complete.")

        else:
            save_new_favorite()
            print("New favorite has been added.")
