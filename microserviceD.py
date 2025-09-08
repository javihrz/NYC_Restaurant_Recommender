import pandas as pd
import time
import os
from pathlib import Path


def clear_comm_path():
    with open(comm_path, "w"):
        pass


def get_comparison():
    saved_dataframe = pd.read_csv(saved_path)
    saved_dataframe.to_csv(comm_path, mode='a', index=False)


def save_new_comparison():
    new_dataframe = pd.read_csv(comm_path)
    clear_comm_path()
    new_dataframe.to_csv(saved_path, index=False)


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "project_data"
    comm_dir = base_dir / "comm"

    data_dir.mkdir(exist_ok=True)
    comm_dir.mkdir(exist_ok=True)

    saved_path = data_dir / "saved_comparison.csv"
    comm_path = comm_dir / "comm_pipe_d.csv"

    while True:
        time.sleep(3)
        comm_path_size = os.stat(comm_path).st_size

        if comm_path_size == 0:
            continue

        with open(comm_path, "r") as comm_csv_file:
            first_line = comm_csv_file.readline().strip()

        if comm_path_size == 3 and first_line == "d2":
            get_comparison()
            print("Retrieved dataframe comparison.")

        elif comm_path_size > 3 and first_line == "d2":
            print("Waiting to transfer...")

        elif first_line == "transfer complete":
            clear_comm_path()
            print("Transfer of dataframe is complete.")

        else:
            save_new_comparison()
            print("New comparison has been saved.")
