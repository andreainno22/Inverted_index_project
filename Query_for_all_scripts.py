import os
import sys
import termios
import tty

# Define stopwords to filter out common words during search
STOPWORDS = {
    "the", "is", "and", "in", "to", "of", "a", "with", "on", "for", "an", "by", "at",
    "this", "that", "it", "be", "as", "from", "or", "are", "was", "were", "which",
    "has", "have", "had", "but", "not", "they", "their", "its"
}

def get_line_or_esc():
    """
    Reads user input for a search query, character by character.
    Allows exiting with the ESC key.
    """
    buffer = ""
    print("Search query (ESC to exit): ", end="", flush=True)
    while True:
        ch = sys.stdin.read(1)  # Read one character at a time
        if ch == '\x1b':  # ESC key pressed
            return None
        elif ch == '\n':  # ENTER key pressed
            return buffer.strip()  # Return the query
        else:
            buffer += ch  # Append character to the buffer
            print(ch, end="", flush=True)

def parse_index_line(line):
    """
    Parses a line from the inverted index file.
    Extracts the word and the set of associated filenames.
    """
    parts = line.strip().split()
    if not parts:  # Skip empty lines
        return None, set()
    word = parts[0].lower()  # First part is the word
    # Extract filenames from the remaining parts
    files = {entry.split(':')[0] for entry in parts[1:]}
    return word, files

def load_inverted_index(path):
    """
    Loads the inverted index from a file or directory.
    Returns a dictionary mapping words to sets of filenames.
    """
    index = {}
    if os.path.isdir(path):  # If the path is a directory
        for filename in os.listdir(path):
            if filename.startswith("part-"):  # Process files starting with "part-"
                with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                    for line in f:
                        word, files = parse_index_line(line)
                        if word:  # Add word and associated files to the index
                            index.setdefault(word, set()).update(files)
    else:  # If the path is a single file
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                word, files = parse_index_line(line)
                if word:  # Add word and associated files to the index
                    index.setdefault(word, set()).update(files)
    return index

def search(index, query):
    """
    Searches the inverted index for files containing the query terms.
    Filters out stopwords and returns the intersection of matching files.
    """
    terms = query.strip().lower().split()  # Split query into terms
    filtered_terms = [term for term in terms if term not in STOPWORDS]  # Remove stopwords

    if not filtered_terms:  # If no valid terms remain
        return set()  # Return an empty set

    result = None
    for term in filtered_terms:
        if term not in index:  # If term is not in the index
            return set()  # Return an empty set
        # Perform intersection of file sets for all terms
        result = index[term] if result is None else result & index[term]
    return result or set()

if __name__ == "__main__":
    # Prompt user for the path to the inverted index
    path = input("Enter path to inverted index (file or directory): ").strip()
    inverted_index = load_inverted_index(path)  # Load the index

    print("\nType your queries below. Press ESC to exit.\n")

    # Configure terminal settings for character-by-character input
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)  # Set terminal to cbreak mode
        while True:
            query = get_line_or_esc()  # Get user query
            if query is None:  # Exit if ESC is pressed
                print("\nExiting.")
                break

            results = search(inverted_index, query)  # Perform search
            if results:  # If matches are found
                print("\nMatching files:")
                for filename in sorted(results):  # Print matching filenames
                    print(filename)
            else:  # If no matches are found
                print("\nNo matches found.")
            print()
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)