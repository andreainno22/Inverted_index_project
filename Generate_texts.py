#!/usr/bin/env python3
import os
import argparse
import random
import glob

def load_words_from_txt(word_dir):
    words = []
    pattern = os.path.join(word_dir, '*.txt')
    for path in glob.glob(pattern):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                for word in line.strip().split():
                    clean = ''.join(ch for ch in word if ch.isalpha())
                    if clean:
                        words.append(clean.lower())
    words = list(set(words))
    if not words:
        raise RuntimeError(f"No words found in {word_dir}")
    return words

def generate_line(words, min_w=5, max_w=15):
    n = random.randint(min_w, max_w)
    s = random.choices(words, k=n)
    return s[0].capitalize() + ' ' + ' '.join(s[1:]) + '.\n'

def generate_file(path, size_gb, words):
    target = int(size_gb * (1024**3))
    total_written = 0
    with open(path, 'w', encoding='utf-8') as f:
        while total_written < target:
            line = generate_line(words)
            f.write(line)
            total_written += len(line.encode('utf-8'))
    print(f"Created: {path} – {size_gb} GB")

def main():
    parser = argparse.ArgumentParser(description="Generate text files using words from your .txt files")
    parser.add_argument('sizes', type=float, nargs='+',
                        help="Sizes in GB of the files to generate (e.g. 1.5 2)")
    parser.add_argument('-p', '--prefix', default='text', help="Prefix for output file names")
    parser.add_argument('-d', '--dir', default='.', help="Output directory")
    parser.add_argument('-w', '--words', required=True,
                        help="Directory containing .txt files with words")
    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)
    words = load_words_from_txt(args.words)
    print(f"→ Loaded {len(words)} words from directory {args.words}")

    for i, size in enumerate(args.sizes, 1):
        filename = f"{args.prefix}_{i}_{size:.2f}GB.txt"
        filepath = os.path.join(args.dir, filename)
        generate_file(filepath, size, words)

if __name__ == "__main__":
    main()
