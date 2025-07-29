from sys import stderr

def menu(**options):
    str_keys = ' / '.join(options.keys())
    str_prompt = '\n'.join(
        (
            'Enter one of the following values:',
            str_keys,
            'Choice: ',
        )
    )

    while True:
        choice = input(str_prompt)

        if choice in options:
            return options[choice]()
        
        print(f"\n{40 * '*'}\nInvalid choice; try again.\n{40 * '*'}\n", file=stderr)