import os
import re
from collections import defaultdict
import argparse

def tokenize(line):
    """
    Convert a line of text into a list of lowercase words, stripping out non-alphanumeric characters.
    """
    cleaned = re.sub(r'[^a-z0-9 ]', ' ', line.lower())
    return cleaned.split()

def build_inverted_index(input_dir, max_mb):
    """
    Build an inverted index from text files in the input_dir, processing files until max_mb is reached.
    """
    index = defaultdict(lambda: defaultdict(int))

    max_bytes = max_mb * 1024 * 1024
    total_bytes = 0

    # Get (filename, size) pairs
    files_with_sizes = [
        (fname, os.path.getsize(os.path.join(input_dir, fname)))
        for fname in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, fname))
    ]

    # Sort files alphabetically (you can sort by size or modified time if needed)
    files_with_sizes.sort(key=lambda x: x[0])

    for filename, size in files_with_sizes:
        if total_bytes + size > max_bytes:
            break

        total_bytes += size
        filepath = os.path.join(input_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                words = tokenize(line)
                for word in words:
                    if word:
                        index[word][filename] += 1

    return index

def write_output(index, output_file):
    """
    Write the inverted index to a file in the format:
    word filename1:count1 filename2:count2 ...
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(index.keys()):
            postings = [f"{filename}:{count}" for filename, count in index[word].items()]
            line = word + " " + " ".join(postings) + "\n"
            f.write(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build an inverted index from text files")
    parser.add_argument("input_dir", help="Path to the folder containing input text files")
    parser.add_argument("output_path", help="Path to the output inverted index file")
    parser.add_argument("max_mb", type=int, help="Max total size (in MB) of files to process")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: input directory '{args.input_dir}' does not exist.")
        exit(1)

    inverted_index = build_inverted_index(args.input_dir, args.max_mb)
    write_output(inverted_index, args.output_path)
    print(f"Inverted index written to {args.output_path}")
