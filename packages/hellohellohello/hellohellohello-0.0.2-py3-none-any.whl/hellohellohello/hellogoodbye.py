#!/usr/bin/env python3

# CLI app inspired by the Beatles' "Hello, Goodbye"

__version__ = '0.0.1'

def get_lyric_opposite(user_input):
    mapping = {
        'hello': 'goodbye',
        'goodbye': 'hello',
        'yes': 'no',
        'no': 'yes',
        'stop': 'go, go, go',
        'go': 'stop',
        'high': 'low',
        'low': 'high',
        'why': "I don't know",  # lyric reference
        'I don\'t know': 'why',
        'you say': 'I say',
        'I say': 'you say',
    }
    key = user_input.strip().lower()
    return mapping.get(key, "I can't respond to that, but you say yes, I say no!")

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ('--version', '-v'):
        print(__version__)
        return
    print("Welcome to hello-goodbye! (Inspired by the Beatles)")
    while True:
        user_input = input("Enter something (or 'exit' to quit): ")
        if user_input.strip().lower() == 'exit':
            print('Goodbye!')
            break
        print(get_lyric_opposite(user_input))

if __name__ == "__main__":
    main()
