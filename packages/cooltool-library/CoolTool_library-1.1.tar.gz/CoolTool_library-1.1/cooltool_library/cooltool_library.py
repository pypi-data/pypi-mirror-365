"""
A simple library with function to help you with console ptoject
"""

import os
from typing import Literal, Union
import random

class CTl:
    """
    The principal Classes of this library with every function
    """

    letter_collection = ["a", "b", "c", "d", "e", "f", "g", "h", "i",
                                   "j", "k", "l", "m", "n", "o", "p", "q", "r",
                                     "s", "t", "u", "v", "w", "x", "y", "z"]
    @staticmethod
    def easy_input(
        possibilities_list: list = [],
        *,
        type: Literal["number", "letter"] = "number",
        upper_case: bool = False, separator_type: str = "-",
        edited_input: str = "Input: "
        ) -> Union[str, int, float, bool ,None]:
        """
        Display a list of options on screen and ask for user input to select one, handling errors automatically

        PARAMETERS

            - Every Parameter the function can accept:
            - type: The type of counter for selection, e.g. number = 1 option, 2 option2, 3 option3, etc.
            - upper_case: Whether to use uppercase or lowercase letters.
            - separator_type: The separator between the counter and the value, e.g. sep=", ": 1, option 2, option2, etc.
            - edited_input: What to print in the input prompt for the user.
            - possibilities_list: The list of possible choices for the input.

        RETURN

            - Returns the value chosen by the user in input.

        USE EXAMPLE
            from cooltool_library import *
            list = [a + 1 for a in range(0, 300)]
            var = CTl.easy_input(list, type="letter", upper_case=False, separator_type=" :) ", edited_input="Insert input: ")
            print("You choose:", var)
        """
        if type == "letter":
            while True:
                try:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    dict_final = {}
                    letter_collection = CTl.letter_collection
                    for i, value in enumerate(possibilities_list):
                        if i < 26:
                            key = letter_collection[i]
                        else:
                            first_letter = letter_collection[(i // 26) - 1]
                            second_letter = letter_collection[i % 26]
                            key = first_letter + second_letter
                        if upper_case:
                            key = key.upper()
                        print(f"{key}{separator_type}{value}")
                        dict_final[key] = value
                    user_input = input(edited_input)
                    if user_input in dict_final.keys():
                        return dict_final[user_input]
                    elif possibilities_list == []:
                        return None
                except:
                    if possibilities_list == []:
                        return None
                    continue
        
        elif type == "number":
            while True:
                try:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    for i, value in enumerate(possibilities_list, start=1):
                        print(f"{i}{separator_type}{value}")
                    user_input = int(input(edited_input))
                    if user_input >= 1 and user_input <= len(possibilities_list):
                        return possibilities_list[user_input - 1]
                    elif possibilities_list == []:
                        return None
                except:
                    if possibilities_list == []:
                        return None
                    continue

    @staticmethod
    def generate_password(
            ammissed_character_type: tuple[Literal["number", "letter", "special_char"]] = ("number", "letter", "special_char"),
            password_lenght: int = 8,
            *,
            not_ammissed_characters: tuple = ()
            ) -> str:
        """
        A simple password generator system with many parameters to edit the result
        """
        password = ""
        number = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
        special_char = ("@", "!", "?", "%", "$", "&", "^", "-", "_", ".", ",", "#", "|")

        available_chars = []
        if "number" in ammissed_character_type:
            available_chars.extend(number)
        if "letter" in ammissed_character_type:
            available_chars.extend(CTl.letter_collection)
        if "special_char" in ammissed_character_type:
            available_chars.extend(special_char)

        for i in range(password_lenght):
            not_find = True
            while not_find:
                character = random.choice(available_chars)
                if character in not_ammissed_characters:
                    continue
                else:
                    not_find = False
            password += character
        return password