import os
import sys
import termios
import tty

def get_line_or_esc():
    """
    Read input from the user, exit if ESC is pressed.
    """
    buffer = ""
    print("Search query (ESC to exit): ", end="", flush=True)

    while True:
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # ESC
            return None
        elif ch == '\n':  # ENTER
            return buffer.strip()
        else:
            buffer += ch
            print(ch, end="", flush=True)

def parse_index_line(line):
    parts = line.strip().split()
    if not parts:
        return None, set()
    word = parts[0].lower()
    files = {entry.split(':')[0] for entry in parts[1:]}
    return word, files

def load_inverted_index(path):
    index = {}
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.startswith("part-"):
                with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                    for line in f:
                        word, files = parse_index_line(line)
                        if word:
                            index.setdefault(word, set()).update(files)
    else:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                word, files = parse_index_line(line)
                if word:
                    index.setdefault(word, set()).update(files)
    return index

def search(index, query):
    terms = query.strip().lower().split()
    result = None
    for term in terms:
        if term not in index:
            return set()
        result = index[term] if result is None else result & index[term]
    return result or set()

if __name__ == "__main__":
    path = input("Enter path to inverted index (file or directory): ").strip()
    inverted_index = load_inverted_index(path)

    print("\nType your queries below. Press ESC to exit.\n")

    # Enable raw input mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            query = get_line_or_esc()
            if query is None:
                print("\nExiting.")
                break

            results = search(inverted_index, query)
            if results:
                print("\nMatching files:")
                for filename in sorted(results):
                    print(filename)
            else:
                print("\nNo matches found.")
            print()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
