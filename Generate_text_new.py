import os
import glob
import random

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

def generate_file(path, size_gb, words):
    target = int(size_gb * (1024**3))
    total_written = 0
    with open(path, 'w', encoding='utf-8') as f:
        while total_written < target:
            line = generate_line(words)
            f.write(line)
            total_written += len(line.encode('utf-8'))
    print(f"Created: {path} – {size_gb} GB")

def generate_line(words, min_w=5, max_w=15):
    n = random.randint(min_w, max_w)
    s = random.choices(words, k=n)
    return s[0].capitalize() + ' ' + ' '.join(s[1:]) + '.\n'

def split_file_by_lines(input_path, output_dir, max_size_mb=10):
    max_bytes = max_size_mb * 1024 * 1024
    os.makedirs(output_dir, exist_ok=True)

    file_count = 0
    current_size = 0
    current_lines = []
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            line_size = len(line.encode('utf-8'))
            if current_size + line_size > max_bytes and current_lines:
                # scrivi file corrente
                out_path = os.path.join(output_dir, f"split_{file_count:05d}.txt")
                with open(out_path, 'w', encoding='utf-8') as outfile:
                    outfile.writelines(current_lines)
                print(f"Written {out_path} ({current_size/1024:.2f} KB)")
                file_count += 1
                current_lines = []
                current_size = 0

            current_lines.append(line)
            current_size += line_size

        # scrivi l'ultimo file se ci sono righe residue
        if current_lines:
            out_path = os.path.join(output_dir, f"split_{file_count:05d}.txt")
            with open(out_path, 'w', encoding='utf-8') as outfile:
                outfile.writelines(current_lines)
            print(f"Written {out_path} ({current_size/1024:.2f} KB)")

# Esempio di uso:
if __name__ == "__main__":
    words = load_words_from_txt('src/main/resources/texts')  # la tua funzione per caricare parole
    bigfile_path = "output_texts/bigfile.txt"
    generate_file(bigfile_path, 1, words)  # genera file da 1 GB

    split_dir = "splitted_texts/split"
    split_file_by_lines(bigfile_path, split_dir, max_size_mb=10)  # splitta in file da ~1MB
