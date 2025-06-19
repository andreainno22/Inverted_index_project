from pyspark import SparkContext, SparkConf
import sys
import re
from collections import defaultdict

def get_files_with_limit(sc, input_dir, total_bytes_limit):
    """
    Selects and returns a list of file paths from a given HDFS directory (input_dir),
    such that the total size of the selected files does not exceed total_bytes_limit (in bytes).
    Useful for testing.

    Inputs:
        sc: the active Spark context
        input_dir: HDFS directory path to scan the files
        total_bytes_limit: maximum total size of selected files (in bytes)

    Output:
        List[str]: list of file paths (as strings) whose combined size ≤ total_bytes_limit
    """

    hadoop_conf = sc._jsc.hadoopConfiguration()
    fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(hadoop_conf)
    path = sc._jvm.org.apache.hadoop.fs.Path(input_dir)
    files = fs.listStatus(path)

    # sort files by ascending size
    sorted_files = sorted(files, key=lambda f: f.getLen())

    selected_files = []
    accumulated_size = 0
    for f in sorted_files:
        size = f.getLen()
        if accumulated_size + size <= total_bytes_limit:
            selected_files.append(f.getPath().toString())
            accumulated_size += size
        else:
            break

    return selected_files

def process_text(partition, stopwords):
    """
    Processes a partition of input files to count word occurrences.
    It normalizes the text and excludes the stopwords.

    Input:
        partition: an iterator of (file_path, content) tuples
        stopwords: o set of words to exclude from counting

    Output:
        tuple: each output is a (word@filename, count) pair representing
            how many times a given word appears in a specific file.
    """

    counts = defaultdict(int)
    for file_path, content in partition:
        file_name = file_path.split("/")[-1]
        cleaned_text = re.sub("[^a-z0-9 ]", " ", content.lower())
        words = cleaned_text.split()
        for word in words:
            if word not in stopwords:
                key = f"{word}@{file_name}"
                counts[key] += 1
    for key, count in counts.items():
        yield (key, count)

if _name_ == "_main_":

    # check the input
    if len(sys.argv) != 4:
        print("Usage: spark-submit inverted_index_optimized.py <input_dir> <output_dir> <totalMB>")
        sys.exit(-1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    total_mb = float(sys.argv[3])
    total_bytes_limit = total_mb * 1024 * 1024

    # define the spark context
    conf = SparkConf().setAppName("InvertedIndex_Spark")
    sc = SparkContext(conf=conf)

    # create list of stopwords
    stopwords_list = [
        "the", "is", "and", "in", "to", "of", "a", "with", "on", "for", "an", "by", "at", "this", "that", "it", "be",
        "as", "from", "or", "are", "was", "were", "which", "has", "have", "had", "but", "not", "they", "their", "its"
    ]

    # select file for testing
    selected_files = get_files_with_limit(sc, input_dir, total_bytes_limit)
    if not selected_files:
        print("No files selected. Total size is 0 bytes.")
        sc.stop()
        sys.exit(-1)

    # apply all the stages
    sc.wholeTextFiles(",".join(selected_files)) \
        .mapPartitions(lambda partition: process_text(partition, stopwords_list)) \
        .reduceByKey(lambda a, b: a + b) \
        .map(lambda kv: (kv[0].split("@")[0], f"{kv[0].split('@')[1]}:{kv[1]}")) \
        .aggregateByKey([], lambda acc, v: acc + [v], lambda acc1, acc2: acc1 + acc2) \
        .mapValues(lambda values: " ".join(values)) \
        .saveAsTextFile(output_dir)

    sc.stop()