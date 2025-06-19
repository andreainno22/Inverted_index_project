package org.Inverted_index;

import java.io.IOException;
import java.util.StringTokenizer;
import java.util.Set;
import java.util.HashSet;
import java.util.Arrays;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class InvertedIndexMapperOpt extends Mapper<LongWritable, Text, Text, IntWritable> {

    private String filename;
    private final IntWritable one = new IntWritable(1);
    private final Text wordAtFile = new Text();

    // Define a set of common stopwords
    private static final Set<String> STOPWORDS = new HashSet<>(Arrays.asList(
            "the", "is", "and", "in", "to", "of", "a", "with", "on", "for", "an", "by", "at", "this", "that", "it", "be",
            "as", "from", "or", "are", "was", "were", "which", "has", "have", "had", "but", "not", "they", "their", "its"
    ));

    // Setup method to initialize the filename from the input split
    @Override
    protected void setup(Context context) {
        FileSplit split = (FileSplit) context.getInputSplit();
        Path path = split.getPath();
        filename = path.getName();
    }

    /**
     * The map method processes each line of the input file, tokenizes it into words,
     * and emits each word along with the filename it was found in, excluding stopwords.
     *
     * @param key The line number (not used).
     * @param value The line of text from the input file.
     * @param context The context to write the output.
     */
    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // Clean line and tokenize
        String line = value.toString().toLowerCase().replaceAll("[^a-z0-9 ]", " ");
        StringTokenizer tokenizer = new StringTokenizer(line);

        while (tokenizer.hasMoreTokens()) {
            String word = tokenizer.nextToken();
            // Skip empty or stopword terms
            if (!word.isEmpty() && !STOPWORDS.contains(word)) {
                wordAtFile.set(word + "@" + filename);
                // Emit the word and filename combination with a count of 1
                context.write(wordAtFile, one);
            }
        }
    }
}

