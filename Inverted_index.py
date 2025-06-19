import os
import re
from collections import defaultdict
import argparse
import time
import psutil


def tokenize(line):
    """
    Tokenizes a line of text by converting it to lowercase and removing non-alphanumeric characters.
    Returns a list of words.
    """
    cleaned = re.sub(r'[^a-z0-9 ]', ' ', line.lower())
    return cleaned.split()


def build_inverted_index(input_dir, max_mb):
    """
    Builds an inverted index from text files in the specified directory.
    Processes files in ascending order of size until the total size reaches the max_mb limit.
    Returns the inverted index and the total size of processed files.
    """
    index = defaultdict(lambda: defaultdict(int))  # Dictionary to store the inverted index
    max_bytes = max_mb * 1024 * 1024  # Convert max_mb to bytes
    total_bytes = 0  # Track the total size of processed files

    # Collect filenames and their sizes from the input directory
    files_with_sizes = []
    for fname in os.listdir(input_dir):
        filepath = os.path.join(input_dir, fname)
        if os.path.isfile(filepath):
            try:
                files_with_sizes.append((fname, os.path.getsize(filepath)))
            except OSError as e:
                print(f"Warning: Could not get size for file '{fname}': {e}")

    # Sort files by size in ascending order
    files_with_sizes.sort(key=lambda x: x[1])
    print("Sorting files by size (ascending).")

    files_processed_count = 0  # Count the number of processed files
    for filename, size in files_with_sizes:
        # Stop processing if adding the current file exceeds the max_bytes limit
        if total_bytes + size > max_bytes and files_processed_count > 0:
            print(
                f"Stopping processing. Adding '{filename}' (size: {size / (1024 * 1024):.2f} MB) would exceed {max_mb} MB.")
            break
        elif total_bytes + size > max_bytes and files_processed_count == 0:
            # Skip the file if it alone exceeds the max_mb limit
            print(
                f"Skipping '{filename}' (size: {size / (1024 * 1024):.2f} MB) as it alone exceeds the {max_mb} MB limit.")
            continue

        total_bytes += size  # Update the total size
        files_processed_count += 1  # Increment the file count
        filepath = os.path.join(input_dir, filename)

        print(f"Processing file: {filename} (Current total: {total_bytes / (1024 * 1024):.2f} MB)")

        # Read the file and update the inverted index
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                words = tokenize(line)
                for word in words:
                    if word:
                        index[word][filename] += 1

    if files_processed_count == 0:
        print("No files were processed. Check input directory, file sizes, and max_mb limit.")
    else:
        print(
            f"Finished processing. Total files processed: {files_processed_count}. Total size processed: {total_bytes / (1024 * 1024):.2f} MB.")

    return index, total_bytes  # Return the inverted index and total size


def write_output(index, output_file):
    """
    Writes the inverted index to a file in the format:
    word filename1:count1 filename2:count2 ...
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(index.keys()):
            postings = [f"{filename}:{count}" for filename, count in index[word].items()]
            line = word + " " + " ".join(postings) + "\n"
            f.write(line)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Build an inverted index from text files, selecting files by size.")
    parser.add_argument("input_dir", help="Path to the folder containing input text files")
    parser.add_argument("output_path", help="Path to the output inverted index file")
    parser.add_argument("max_mb", type=int, help="Max total size (in MB) of files to process")

    args = parser.parse_args()

    # Validate the input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: input directory '{args.input_dir}' does not exist.")
        exit(1)

    start_time = time.time()  # Record the start time
    process = psutil.Process(os.getpid())  # Get the current process
    mem_before = process.memory_info().rss / (1024 * 1024)  # Memory usage before execution

    process.cpu_percent(interval=None)  # Initialize CPU usage tracking

    print(
        f"Building inverted index from '{args.input_dir}' with max {args.max_mb} MB, selecting files by size (ascending).")

    # Build the inverted index and write it to the output file
    inverted_index, processed_input_bytes = build_inverted_index(args.input_dir, args.max_mb)
    write_output(inverted_index, args.output_path)
    print(f"Inverted index successfully written to {args.output_path}. Total unique words: {len(inverted_index)}")

    end_time = time.time()  # Record the end time
    mem_after = process.memory_info().rss / (1024 * 1024)  # Memory usage after execution
    cpu_usage = process.cpu_percent(interval=None)  # Average CPU usage during execution

    execution_time = end_time - start_time  # Calculate execution time
    memory_used = mem_after - mem_before  # Calculate memory usage increase
    processed_input_mb = processed_input_bytes / (1024 * 1024)  # Convert processed bytes to MB

    # Print execution statistics
    print("\n--- Execution Statistics ---")
    print(f"Total execution time: {execution_time:.2f} seconds")
    print(f"Memory used (increase): {memory_used:.2f} MB")
    print(f"Process CPU usage (average during execution): {cpu_usage:.2f}%")
    print(f"Processed input size: {processed_input_mb:.2f} MB")
