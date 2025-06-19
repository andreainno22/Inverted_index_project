import os
import random

ALLOWED_SIZES = [500 * 1024, 1 * 1024 * 1024, 5 * 1024 * 1024, 25 * 1024 * 1024, 50 * 1024 * 1024]

def generate_sizes(total_bytes, n=50):
    """
    Generate `n` sizes randomly chosen from ALLOWED_SIZES that sum up to <= total_bytes.
    Attempts to maximize the sum to reduce leftover space, preferring larger sizes.
    """
    best_sizes = []
    best_sum = 0

    # Sort allowed sizes in descending order to prefer larger sizes
    # This helps fill the space faster and maximize the sum.
    sorted_allowed_sizes = sorted(ALLOWED_SIZES, reverse=True)

    for attempt in range(10000):
        current_sizes = []
        current_sum = 0

        # Try to generate `n` sizes
        for _ in range(n):
            # Choose from a pool of allowed sizes, preferring larger ones that fit
            possible_choices = [s for s in sorted_allowed_sizes if current_sum + s <= total_bytes]

            if not possible_choices:
                break  # No more sizes can be added without exceeding the total

            # Randomly choose a size from the possible options (already sorted)
            chosen_size = random.choice(possible_choices)
            current_sizes.append(chosen_size)
            current_sum += chosen_size

        # If this combination is better (greater sum), save it
        if current_sum > best_sum:
            best_sum = current_sum
            best_sizes = current_sizes[:]

            # If we have completely filled the space, exit early
        if best_sum == total_bytes:
            break

    if not best_sizes and total_bytes > 0:
        # Fallback: if no valid combination is found, create a single file
        # with the maximum allowed size or the total file size.
        return [min(max(ALLOWED_SIZES), total_bytes)], min(max(ALLOWED_SIZES), total_bytes)
    elif not best_sizes and total_bytes == 0:
        return [], 0

    return best_sizes, best_sum


def split_file(input_path, output_dir="splitted_fixed_50"):
    total_size = os.path.getsize(input_path)

    # Calculate a reasonable number of files to generate.
    # At least 1 if the file is not empty, otherwise based on an estimate.
    num_files_to_generate = min(50, max(1, total_size // (500 * 1024) + 1))

    sizes, sum_sizes = generate_sizes(total_size, n=num_files_to_generate)

    # Sort the generated sizes in descending order before writing files
    # This is the key step to have larger files at the beginning.
    sizes.sort(reverse=True)

    os.makedirs(output_dir, exist_ok=True)

    written_bytes = 0
    file_count = 0

    with open(input_path, 'rb') as infile:
        for idx, sz in enumerate(sizes):
            chunk = infile.read(sz)
            if not chunk:
                print(f"Early end of file at part_{idx:02d}")
                break

            out_path = os.path.join(output_dir, f"part_{idx:02d}.txt")
            with open(out_path, 'wb') as out:
                out.write(chunk)
            written_bytes += len(chunk)
            file_count += 1
            print(f"{out_path} written - {len(chunk)} bytes")

        # Leftover: read everything remaining in the input file
        leftover = infile.read()
        leftover_size = len(leftover)

        # Write the leftover only if it is greater than 500KB
        if leftover_size > 500 * 1024:
            out_path = os.path.join(output_dir, f"part_{file_count:02d}.txt")
            with open(out_path, 'wb') as out:
                out.write(leftover)
            written_bytes += leftover_size
            file_count += 1
            print(f"{out_path} written - {leftover_size} bytes (leftover)")
        elif leftover_size > 0:
            print(f"Leftover {leftover_size} bytes (<500KB) ignored")

    print(f"\nSplit completed: {file_count} files written in '{output_dir}'. Total bytes written: {written_bytes}/{total_size}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python split_file.py <input_file>")
        sys.exit(1)
    split_file(sys.argv[1])