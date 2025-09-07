import pandas as pd
import random
import time
import os
from colorama import Fore, Style


class RestaurantFile:
    def __init__(self):
        self.data_frame = pd.read_csv("ny_restaurants.csv")
        self.saved_list = None
        self.unfiltered_list = None
        self.num_saved_list = 0
        self.saved_list_random = False
        self.latest_input_options = 1
        self.input_combo = None
        self.num_rows = self.data_frame.shape[0]

        pd.set_option('display.max_rows', None)

    def set_self_values(self, dataframe, user_command, random_status, display_option):
        """
        Sets self values depending on arguments from different methods.
        """
        self.set_saved_list(dataframe)
        self.set_input_combo(user_command)
        self.set_random_status(random_status)
        self.display_input_options(display_option)

    def display_info_screen(self):
        """
        Displays information screen, which contains more detailed info for each function.
        """
        print(screen_messages("functions_info"))
        self.display_input_options(self.latest_input_options)

    def display_input_options(self, option_num):
        """
        Displays the available keyboard options per window.
        """
        if option_num == 5:  # Special case for microservice displays.
            print(screen_messages("input_5"))
            return

        print(screen_messages(f"input_{option_num}"))

        self.set_latest_input_options(option_num)

    def display_entire_dataframe(self, user_command):
        """
        Displays all restaurants from the main csv file.
        """
        print(Fore.MAGENTA + "\n--- Full list of restaurants being viewed ---\n" + Style.RESET_ALL)

        whole_list = self.get_entire_list()
        print(whole_list)

        self.set_self_values(whole_list, user_command, False, 2)

    def display_random_dataframe(self, user_command):
        """
        Displays a random restaurant from the main csv file.
        """
        print(Fore.MAGENTA + "\n--- Random restaurant selected ---\n" + Style.RESET_ALL)

        random_restaurant = (self.get_random_row())
        print(random_restaurant)

        self.set_self_values(random_restaurant, user_command, True, 1)

    def display_selected_dataframe(self, user_command):
        """
        Displays all restaurants from the main csv file with a single cuisine type.
        """
        print(Fore.MAGENTA + "\n--- Search selected ---\n" + Style.RESET_ALL)
        print(screen_messages("search_1"))

        self.set_input_combo(user_command)

        searched_restaurants = self.search_type()
        print(searched_restaurants)

        self.set_self_values(searched_restaurants, self.get_input_combo(),
                             False, 1 if self.num_saved_list == 1 else 3)

    def display_filtered_dataframe(self, user_command):
        """
        Filters down from all restaurants that contain a wanted price point.
        """
        print(Fore.MAGENTA + "\n--- Filtration selected ---\n" + Style.RESET_ALL)
        print(screen_messages("filter_1"))

        self.set_input_combo(user_command)

        if user_command == "f":
            self.unfiltered_list = self.saved_list

        filtered_restaurants = self.filter_type(user_command)

        print("No restaurants to show" if len(filtered_restaurants) == 0 else filtered_restaurants)

        self.set_self_values(filtered_restaurants, self.get_input_combo(), False, 4)

    def get_entire_list(self):
        """
        Returns the entire csv file as a dataframe.
        """
        return self.data_frame

    def get_random_row(self):
        """
        Returns a random series as a dataframe.
        """
        row_num = random.randint(0, self.num_rows - 1)
        random_restaurant = self.data_frame.iloc[[row_num]]

        return random_restaurant

    def get_saved_list(self):
        """
        Sets the current dataframe view as a variable.
        """
        return self.saved_list

    def get_input_combo(self):
        """
        Returns the list of user inputs
        """
        return self.input_combo

    def set_latest_input_options(self, option_num):
        """
        Sets the most recent input option into a variable. Used for 'Info' window.
        """
        self.latest_input_options = option_num

    def set_input_combo(self, input_combination):
        """
        Tracks the user's inputs that are valid.
        """
        self.input_combo = input_combination

    def set_saved_list(self, current_list):
        """
        Sets the current dataframe view as a variable.
        """
        self.saved_list = current_list
        self.num_saved_list = current_list.shape[0]

    def set_random_status(self, bool_value):
        """
        Determines if most recent dataframe view was from the random input or not.
        """
        self.saved_list_random = bool_value

    def save_favorite_to_csv(self):
        """
        Sends currently displayed dataset to a csv file (microservice B) using a communication pipeline.
        """
        print(Fore.MAGENTA + "\n--- Type the number to favorite a new restaurant ---\n" + Style.RESET_ALL)

        whole_list = self.get_entire_list()
        print(whole_list)
        self.display_input_options(5)

        valid_inputs = {str(index_value) for index_value in range(self.num_rows)}

        while True:
            my_input = input("Your input: ")

            if my_input == "q":
                quit()

            elif my_input == "i":
                print(screen_messages("functions_info"))
                self.display_input_options(5)
                continue

            elif my_input == "x":
                print(Fore.MAGENTA + "\n--- Adding to favorites cancelled ---\n" + Style.RESET_ALL)
                self.display_input_options(self.latest_input_options)
                return

            elif my_input in valid_inputs:
                break

            invalid_message()

        new_fav_to_add = whole_list.iloc[[int(my_input)]]  # Writes to pipeline for Microservice B.
        new_fav_to_add.to_csv(comm_path_b, index=False)

        print(Fore.MAGENTA + "\n--- Following restaurant added to favorites ---\n" + Style.RESET_ALL)
        print(new_fav_to_add)

        self.set_input_combo(f"b1,{my_input}")
        self.display_input_options(self.latest_input_options)

    def save_dataframe_to_csv(self):
        """
        Sends currently displayed dataset to a csv file (microservice C) using a communication pipeline.
        """
        saved_list = self.get_saved_list()

        if saved_list is None or saved_list.shape[0] == 0:  # Number of rows in dataframe is 0.
            invalid_message()
            return

        saved_list.to_csv(comm_path_c, index=False)
        print(Fore.MAGENTA + "\n--- Current displayed list saved for future use. ---\n" + Style.RESET_ALL)
        self.set_input_combo("c1")
        self.display_input_options(self.latest_input_options)

    def save_comparison_to_csv(self):
        """
        Sends currently displayed dataset to a csv file (microservice D) using a communication pipeline.
        """
        print(Fore.MAGENTA + "\n--- Select 2 restaurants to save comparison ---\n" + Style.RESET_ALL)

        whole_list = self.get_entire_list()
        print(whole_list)
        self.display_input_options(5)

        valid_inputs = {str(index_value) for index_value in range(self.num_rows)}
        first_input, restaurant_num = None, 1

        while True:
            my_input = input(f"Restaurant {restaurant_num}: ")

            if my_input == "q":
                quit()

            elif my_input == str(first_input):
                print("Please select a different restaurant for comparison.")

            elif my_input == "i":
                print(screen_messages("functions_info"))
                self.display_input_options(5)

            elif my_input == "x":
                print(Fore.MAGENTA + "\n--- Comparison cancelled ---\n" + Style.RESET_ALL)
                self.display_input_options(self.latest_input_options)
                return

            elif my_input in valid_inputs and first_input is None:
                self.set_input_combo(my_input)
                first_input, restaurant_num = int(my_input), 2

            elif my_input in valid_inputs:
                second_input = int(my_input)
                break

            else:
                invalid_message()

        first_pick, second_pick = whole_list.iloc[[first_input]], whole_list.iloc[[second_input]]

        two_picks = pd.concat([first_pick, second_pick])  # Writes to pipeline for Microservice D.
        two_picks.to_csv(comm_path_d, index=False)

        print(Fore.MAGENTA + "\n--- Following restaurant added to comparison ---\n" + Style.RESET_ALL)
        print(two_picks)

        self.set_input_combo(f"d1,{self.get_input_combo()},{my_input}")
        self.display_input_options(self.latest_input_options)
        self.get_input_combo()

    def load_from_csv_files(self, key_phrase, comm_path):
        """
        Displays the saved dataframe from a csv file by using a communication pipeline.
        """
        with open(comm_path, "w") as comm_pipe:
            comm_pipe.write(f"{key_phrase}\n")

        header_message = None

        match key_phrase:
            case "b2":
                header_message = "Loading list of favorite restaurants"
            case "c2":
                header_message = "Loading last saved dataframe"
            case "d2":
                header_message = "Loading saved comparison"

        print(Fore.MAGENTA + f"\n--- {header_message}... ---" + Style.RESET_ALL)

        while True:
            time.sleep(2)
            comm_path_size = os.stat(comm_path).st_size

            with open(comm_path, "r") as comm_csv_file:
                first_line = comm_csv_file.readline().strip()

            if comm_path_size > 3 and first_line == key_phrase:
                break

            print(Fore.MAGENTA + f"--- {header_message}... ---" + Style.RESET_ALL)

        print(f"\n{pd.read_csv(comm_path, skiprows=1)}")  # Contents from communication pipeline file.

        with open(comm_path, "w") as comm_pipe:
            comm_pipe.write("transfer complete")

        self.set_input_combo(key_phrase)
        self.display_input_options(self.latest_input_options)

    def search_type(self):
        """
        Determines what value will be searched by the user.
        """
        while True:
            second_input = get_input()

            if second_input == "q":
                quit()

            elif second_input == "c":
                print(Fore.MAGENTA + "\n--- Cuisine type search selected ---\n" + Style.RESET_ALL)
                print(screen_messages("search_2"))

                current_combo = self.get_input_combo()
                self.set_input_combo(f"{current_combo},{second_input}")

                return self.cuisine_search()

            else:
                invalid_message()

    def cuisine_search(self):
        """
        Returns a dataframe that matches the user's key input in relation to searching.
        """
        cuisine_map = {
            "1": "Dessert",
            "2": "Italian",
            "3": "Thai",
            "4": "Mexican",
            "5": "Chinese",
            "6": "Japanese",
            "7": "American",
            "8": "Other",
        }

        main_cuisines = ("Dessert", "Italian", "Thai", "Japanese", "Chinese", "Mexican", "American")

        while True:
            cuisine_input = get_input()

            if cuisine_input == "q":
                quit()

            key_term = cuisine_map.get(cuisine_input)

            if key_term is None:
                invalid_message()
                continue

            break

        print(Fore.MAGENTA + f"\n--- Cuisine type ({key_term}) selected ---\n" + Style.RESET_ALL)

        current_combo = self.get_input_combo()
        self.set_input_combo(f"{current_combo},{cuisine_input}")

        cuisine_type = self.data_frame

        if key_term == "Other":
            return cuisine_type.loc[~cuisine_type["Cuisine"].isin(main_cuisines)]

        return cuisine_type.loc[cuisine_type["Cuisine"] == key_term]  # Searched rows.

    def filter_type(self, f_or_w):
        """
        Returns a dataframe that matches the user's key input in relation to filtering.
        """
        while True:
            second_input = get_input()
            valid_inputs = ["1", "2", "3"]
            filtered_set = set()

            if second_input == "q":
                quit()

            elif len(second_input) >= 1:

                for element in second_input:
                    if element in valid_inputs:
                        filtered_set.add(element)

                check_common = set(valid_inputs) & set(filtered_set)
                if check_common:
                    sorted_list = sorted(filtered_set)
                    current_combo = self.get_input_combo()
                    self.set_input_combo(f"{current_combo},{sorted_list}")

                    num_to_price = {
                        "1": "$",
                        "2": "$$",
                        "3": "$$$"
                    }

                    sorted_list = [num_to_price.get(item, item) for item in sorted_list]

                    df = self.saved_list
                    if f_or_w == "w":
                        df = self.unfiltered_list

                    filtered_restaurants = df[df["Price"].isin(sorted_list)]
                    print(Fore.MAGENTA + "\n--- Low cost ($) filtration applied ---\n" + Style.RESET_ALL)

                    return filtered_restaurants

                else:
                    invalid_message()

    def load_log(self):
        with open(request_file, "w") as comm_file:
            comm_file.write("a2")

        time.sleep(2)

        with open(comm_path_a, "r") as comm_file:
            file_content = comm_file.read()

        print(Fore.MAGENTA + f"\n--- Current input log ---\n" + Style.RESET_ALL)
        print(file_content)
        self.display_input_options(self.latest_input_options)

    def display_results(self, user_command):
        """
        Returns a dataframe that matches the user's key input.
        Considered the base method for the class.
        """
        if user_command == "q":
            quit()

        elif user_command == "a2":
            self.load_log()

        elif user_command == "b1":  # Microservice B - Favorites
            self.save_favorite_to_csv()

        elif user_command == "b2":
            self.load_from_csv_files("b2", comm_path_b)

        elif user_command == "c1":  # Microservice C - Saved selection
            self.save_dataframe_to_csv()

        elif user_command == "c2":
            self.load_from_csv_files("c2", comm_path_c)

        elif user_command == "d1":  # Microservice D - Comparison
            self.save_comparison_to_csv()

        elif user_command == "d2":
            self.load_from_csv_files("d2", comm_path_d)

        elif user_command == "i":
            self.display_info_screen()

        elif user_command == "e":
            self.display_entire_dataframe(user_command)

        elif user_command == "r":
            self.display_random_dataframe(user_command)

        elif user_command == "s":
            self.display_selected_dataframe(user_command)

        elif (user_command == "f" or user_command == "w") and self.saved_list_random is False:
            self.display_filtered_dataframe(user_command)

        else:
            invalid_message()


def get_input():
    """
    Records the user's input.
    """
    return input("Your input: ").lower()


def invalid_message():
    """
    Red 'invalid' text displayed to the user.
    """
    print(Fore.RED + "invalid input" + Style.RESET_ALL)


def screen_messages(keyword):
    """
    Message displays for the program.
    Created under a function to help condense the long messages.
    """
    # input_options_1
    if keyword == "input_1":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 1 ---\n\n"
                "Show full list of restaurants:  " + Fore.CYAN + "'e' \n" + Style.RESET_ALL +
                "Generate a random restaurant:   " + Fore.CYAN + "'r' \n" + Style.RESET_ALL +
                "Search new list of restaurants: " + Fore.CYAN + "'s' \n\n" + Style.RESET_ALL +
                "Add a restaurant to favorites:  " + Fore.CYAN + "'b1' \n" + Style.RESET_ALL +
                "View favorite restaurants:      " + Fore.CYAN + "'b2' \n" + Style.RESET_ALL +
                "Save current displayed list:    " + Fore.CYAN + "'c1' \n" + Style.RESET_ALL +
                "Load last saved list:           " + Fore.CYAN + "'c2' \n" + Style.RESET_ALL +
                "Save new comparison:            " + Fore.CYAN + "'d1' \n" + Style.RESET_ALL +
                "Load last saved comparison:     " + Fore.CYAN + "'d2' \n\n" + Style.RESET_ALL +
                "Get functions information:      " + Fore.CYAN + "'i' \n" + Style.RESET_ALL +
                "Quit program:                   " + Fore.CYAN + "'q' \n"
                "---------------------------------------" + Style.RESET_ALL)

    # input_options_2
    elif keyword == "input_2":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 1 ---\n\n"
                "Generate a random restaurant:   " + Fore.CYAN + "'r' \n" + Style.RESET_ALL +
                "Search new list of restaurants: " + Fore.CYAN + "'s' \n" + Style.RESET_ALL +
                "Filter current list down:       " + Fore.CYAN + "'f' \n\n" + Style.RESET_ALL +
                "Add a restaurant to favorites:  " + Fore.CYAN + "'b1' \n" + Style.RESET_ALL +
                "View favorite restaurants:      " + Fore.CYAN + "'b2' \n" + Style.RESET_ALL +
                "Save current displayed list:    " + Fore.CYAN + "'c1' \n" + Style.RESET_ALL +
                "Load last saved list:           " + Fore.CYAN + "'c2' \n" + Style.RESET_ALL +
                "Save new comparison:            " + Fore.CYAN + "'d1' \n" + Style.RESET_ALL +
                "Load last saved comparison:     " + Fore.CYAN + "'d2' \n\n" + Style.RESET_ALL +
                "Get functions information:      " + Fore.CYAN + "'i' \n" + Style.RESET_ALL +
                "Quit program:                   " + Fore.CYAN + "'q' \n"
                "---------------------------------------" + Style.RESET_ALL)

    # input_options_3
    elif keyword == "input_3":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 1 ---\n\n"
                "Reset full list of restaurants: " + Fore.CYAN + "'e'\n" + Style.RESET_ALL +
                "Generate a random restaurant:   " + Fore.CYAN + "'r' \n" + Style.RESET_ALL +
                "Search new list of restaurants: " + Fore.CYAN + "'s' \n" + Style.RESET_ALL +
                "Filter current list down:       " + Fore.CYAN + "'f' \n\n" + Style.RESET_ALL +
                "Add a restaurant to favorites:  " + Fore.CYAN + "'b1' \n" + Style.RESET_ALL +
                "View favorite restaurants:      " + Fore.CYAN + "'b2' \n" + Style.RESET_ALL +
                "Save current displayed list:    " + Fore.CYAN + "'c1' \n" + Style.RESET_ALL +
                "Load last saved list:           " + Fore.CYAN + "'c2' \n" + Style.RESET_ALL +
                "Save new comparison:            " + Fore.CYAN + "'d1' \n" + Style.RESET_ALL +
                "Load last saved comparison:     " + Fore.CYAN + "'d2' \n\n" + Style.RESET_ALL +
                "Get functions information:      " + Fore.CYAN + "'i' \n" + Style.RESET_ALL +
                "Quit program:                   " + Fore.CYAN + "'q' \n"
                "---------------------------------------" + Style.RESET_ALL)

    # input_options_4
    elif keyword == "input_4":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 1 ---\n\n"
                "Reset full list of restaurants:  " + Fore.CYAN + "'e'\n" + Style.RESET_ALL +
                "Generate a random restaurant:    " + Fore.CYAN + "'r' \n" + Style.RESET_ALL +
                "Search new list of restaurants:  " + Fore.CYAN + "'s' \n" + Style.RESET_ALL +
                "Edit current filtration options: " + Fore.CYAN + "'w' \n\n" + Style.RESET_ALL +
                "Add a restaurant to favorites:  " + Fore.CYAN + "'b1' \n" + Style.RESET_ALL +
                "View favorite restaurants:      " + Fore.CYAN + "'b2' \n" + Style.RESET_ALL +
                "Save current displayed list:    " + Fore.CYAN + "'c1' \n" + Style.RESET_ALL +
                "Load last saved list:           " + Fore.CYAN + "'c2' \n" + Style.RESET_ALL +
                "Save new comparison:            " + Fore.CYAN + "'d1' \n" + Style.RESET_ALL +
                "Load last saved comparison:     " + Fore.CYAN + "'d2' \n\n" + Style.RESET_ALL +
                "Get functions information:       " + Fore.CYAN + "'i' \n" + Style.RESET_ALL +
                "Quit program:                    " + Fore.CYAN + "'q' \n"
                "---------------------------------------" + Style.RESET_ALL)

    # input_options_5
    elif keyword == "input_5":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 1 ---\n\n"
                "Cancel microservice:       " + Fore.CYAN + "'x'\n" + Style.RESET_ALL +
                "Select a restaurant:       " + Fore.CYAN + "index number \n" + Style.RESET_ALL +
                "Get functions information: " + Fore.CYAN + "'i' \n" + Style.RESET_ALL +
                "Quit program:              " + Fore.CYAN + "'q' \n"
                "---------------------------------------" + Style.RESET_ALL)

    # search_options_1
    elif keyword == "search_1":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 2 ---\n\n"
                "Cuisine type: " + Fore.CYAN + "'c' \n\n" + Style.RESET_ALL +
                "Quit program: " + Fore.CYAN + "'q' \n\n"
                "---------------------------------------" + Style.RESET_ALL)

    # search_options_2
    elif keyword == "search_2":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 3 ---\n\n"
                "Note: Applying a new search will clear the current\n"
                "selection, and generate a new list.\n\n"
                "Dessert:      " + Fore.CYAN + "'1' \n" + Style.RESET_ALL +
                "Italian:      " + Fore.CYAN + "'2' \n" + Style.RESET_ALL +
                "Thai:         " + Fore.CYAN + "'3' \n" + Style.RESET_ALL +
                "Mexican:      " + Fore.CYAN + "'4' \n" + Style.RESET_ALL +
                "Chinese:      " + Fore.CYAN + "'5' \n" + Style.RESET_ALL +
                "Japanese:     " + Fore.CYAN + "'6' \n" + Style.RESET_ALL +
                "American:     " + Fore.CYAN + "'7' \n" + Style.RESET_ALL +
                "Other:        " + Fore.CYAN + "'8' \n\n" + Style.RESET_ALL +
                "Quit program: " + Fore.CYAN + "'q' \n\n"
                "---------------------------------------" + Style.RESET_ALL)

# filter_options_1
    elif keyword == "filter_1":
        return (Fore.CYAN + "---------------------------------------\n" + Style.RESET_ALL +
                "--- Keyboard input options 2 ---\n\n"
                "Note: More than one filtration option can be\n"
                "applied by using commas (Ex: '1,2').\n\n"
                "Low cost ($):      " + Fore.CYAN + "'1' \n" + Style.RESET_ALL +
                "Average cost ($$): " + Fore.CYAN + "'2' \n" + Style.RESET_ALL +
                "High cost ($$$):   " + Fore.CYAN + "'3' \n\n" + Style.RESET_ALL +
                "Quit program:      " + Fore.CYAN + "'q' \n\n"
                "---------------------------------------" + Style.RESET_ALL)

    # functions_info
    elif keyword == "functions_info":
        return (Fore.CYAN + "\nShow full list of restaurants /"
                            "Reset full list of restaurants\n" + Style.RESET_ALL +
                "    Press 'e' and enter. The current list is cleared, and\n"
                "    a new list that contains all restaurants from the\n"
                "    source file is loaded.\n\n"

                + Fore.CYAN + "Filter current list of restaurants\n" + Style.RESET_ALL +
                "    Press 'f' and enter. The current list is narrowed down\n"
                "    to match the user's preference.\n\n"

                + Fore.CYAN + "Generate a random restaurant\n" + Style.RESET_ALL +
                "    Press 'r' and enter. The current list is cleared, and \n"
                "    a single restaurant (picked at random) is displayed.\n\n"

                + Fore.CYAN + "Search new list of restaurants\n" + Style.RESET_ALL +
                "    Press 's' and enter. The current list is cleared, and\n"
                "    the program finds restaurants that match the user's\n"
                "    search criteria to generate a new list.\n\n"

                + Fore.CYAN + "Edit current filtration options\n" + Style.RESET_ALL +
                "    Press 'w' and enter. The current list is cleared, and\n"
                "    the pre-filtered list is re-filtered with the new\n"
                "    criteria and displayed to the user.\n\n"

                + Fore.CYAN + "Quit and close the program\n" + Style.RESET_ALL +
                "    Press 'q' and enter. The program will terminate the\n"
                "    current script. If one wishes to use the program again,\n"
                "    The Python file will have to be ran again.\n")


if __name__ == '__main__':
    my_file = RestaurantFile()

    request_file = "request.txt"
    comm_path_a = "response.txt"

    comm_path_c = "comm_pipe_c.csv"
    comm_path_b = "comm_pipe_b.csv"
    comm_path_d = "comm_pipe_d.csv"

    header = ("\n-- New York Restaurant Recommender --\n\n"
              "Hello! This service is to help you decide which restaurant \n"
              "to try from a list of restaurants in New York. \n"
              "The following section shows the current options available. \n"
              "Please type and submit a letter to get your desired results. Thank you! \n")
    print(header)
    my_file.display_input_options(1)

    while True:  # Loops until the user presses the 'Q' key.
        user_input = get_input()
        my_file.display_results(user_input)

        if user_input == "a2":
            continue

        my_combo = my_file.get_input_combo()
        with open(request_file, "w") as request:
            request.write(f"w {my_combo}")

        my_file.set_input_combo("")
