import os           # For file and directory operations
import re           # For regular expressions (text cleaning)
from collections import defaultdict  # For nested dictionaries with default values
import argparse     # For command-line argument parsing


def tokenize(line):
    """
    Convert a line of text into a list of lowercase words, stripping out non-alphanumeric characters.

    Args:
    - line (str): A single line of text

    Returns:
    - List[str]: A list of cleaned, lowercase words
    """
    # Replace all characters NOT a-z, 0-9, or space with spaces
    cleaned = re.sub(r'[^a-z0-9 ]', ' ', line.lower())
    # Split the cleaned line by whitespace into words
    return cleaned.split()


def build_inverted_index(input_dir):
    """
    Build an inverted index from all text files in a directory.

    The inverted index maps each word to a dictionary of filenames and counts,
    representing how many times the word appeared in each file.

    Args:
    - input_dir (str): Path to the directory containing input text files

    Returns:
    - defaultdict: A nested dictionary of the form { word: { filename: count } }
    """
    # Create a nested dictionary: default value for missing words is another defaultdict(int)
    # This inner defaultdict(int) automatically initializes counts to 0 for new filenames
    index = defaultdict(lambda: defaultdict(int))

    # Iterate over every file in the input directory
    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)  # Full path to the file

        # Process only regular files (ignore directories, symlinks, etc.)
        if os.path.isfile(filepath):
            # Open file in read mode with UTF-8 encoding
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read the file line by line
                for line in f:
                    # Tokenize the line into words (lowercased, cleaned)
                    words = tokenize(line)

                    # For each non-empty word, increment the count for that word and file
                    for word in words:
                        if word:
                            index[word][filename] += 1

    # Return the fully built inverted index
    return index


def write_output(index, output_file):
    """
    Write the inverted index to a file in a Hadoop-like output format.

    Each line will have the format:
    word filename1:count1 filename2:count2 ...

    Args:
    - index (dict): The inverted index dictionary
    - output_file (str): Path where the output file will be saved
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Iterate over all words in alphabetical order
        for word in sorted(index.keys()):
            # Build a list of "filename:count" strings for each file the word appeared in
            postings = [f"{filename}:{count}" for filename, count in index[word].items()]
            # Create the output line by joining word and postings separated by spaces
            line = word + " " + " ".join(postings) + "\n"
            # Write the line to the output file
            f.write(line)


if __name__ == "__main__":
    # Set up command line argument parser with description
    parser = argparse.ArgumentParser(description="Build an inverted index from text files")
    # Positional argument for the input directory path
    parser.add_argument("input_dir", help="Path to the folder containing input text files")
    # Positional argument for the output file path
    parser.add_argument("output_path", help="Path to the output inverted index file")
    # Parse the command line arguments into `args`
    args = parser.parse_args()

    # Validate that the input directory exists before processing
    if not os.path.isdir(args.input_dir):
        print(f"Error: input directory '{args.input_dir}' does not exist.")
        exit(1)  # Exit with error code 1 if directory not found

    # Build the inverted index from the input directory
    inverted_index = build_inverted_index(args.input_dir)
    # Write the constructed inverted index to the specified output file
    write_output(inverted_index, args.output_path)
    # Print confirmation message on success
    print(f"Inverted index written to {args.output_path}")