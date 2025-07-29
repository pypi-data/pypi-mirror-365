from menu import menu

def func_a():
    return "A"

def func_b():
    return "B"


if __name__ == '__main__':
    return_value = menu(a=func_a, b=func_b)
    print(f'Result is {return_value}')