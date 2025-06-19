package org.Inverted_index;

import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.StringTokenizer;
import java.util.Arrays;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class InvertedIndexMapper_inMapperCombiner extends Mapper<LongWritable, Text, Text, IntWritable> {

    // Variable to store the name of the file being processed
    private String filename;
    // In-memory map to store word counts for the current map task
    private final Map<String, Integer> inMapperCounts = new HashMap<>();
    // Text object to store the word and filename combination
    private final Text wordAtFile = new Text();

    // Define a set of common stopwords
    private static final Set<String> STOPWORDS = new HashSet<>(Arrays.asList(
            "the", "is", "and", "in", "to", "of", "a", "with", "on", "for", "an", "by", "at", "this", "that", "it", "be",
            "as", "from", "or", "are", "was", "were", "which", "has", "have", "had", "but", "not", "they", "their", "its"
    ));

    @Override
    protected void setup(Context context) {
        // Retrieve the file split information and extract the filename
        FileSplit split = (FileSplit) context.getInputSplit();
        Path path = split.getPath();
        filename = path.getName();
    }

    /**
     * The map method processes each line of the input file, tokenizes it into words,
     * and accumulates counts for each word in an in-memory map.
     *
     * @param key The line number (not used).
     * @param value The line of text from the input file.
     * @param context The context to write the output.
     */

    @Override
    protected void map(LongWritable key, Text value, Context context) {
        // Convert the line to lowercase and remove non-alphanumeric characters
        String line = value.toString().toLowerCase().replaceAll("[^a-z0-9 ]", " ");
        // Tokenize the line into individual words
        StringTokenizer tokenizer = new StringTokenizer(line);

        while (tokenizer.hasMoreTokens()) {
            String word = tokenizer.nextToken();
            // Skip empty or stopword terms
            if (!word.isEmpty() && !STOPWORDS.contains(word)) {
                // Construct the key as `word@filename`
                String mapKey = word + "@" + filename;
                // Increment the count for the key in the in-memory map
                inMapperCounts.merge(mapKey, 1, Integer::sum);
            }
        }
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        // Emit all accumulated word counts
        for (Map.Entry<String, Integer> entry : inMapperCounts.entrySet()) {
            wordAtFile.set(entry.getKey());
            context.write(wordAtFile, new IntWritable(entry.getValue()));
        }
    }
}