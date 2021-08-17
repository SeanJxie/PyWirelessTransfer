from typing import List

def choice_input(query: str, choices: List[str]):
    ret = input(f"{query} ({choices[0]}/{choices[1]}): ").lower()
    if ret not in choices:
        print("Invalid input. Please try again.")
        ret = input(f"{query} ({choices[0]}/{choices[1]}").lower()

    return ret


def indent_print(indent_size: int, s: str):
    print(' ' * indent_size + s)