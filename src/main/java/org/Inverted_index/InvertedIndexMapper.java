package org.Inverted_index;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class InvertedIndexMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    // Variable to store the name of the file being processed
    private String filename;
    // Constant value to represent the count of each word occurrence
    private final IntWritable one = new IntWritable(1);
    // Text object to store the word and filename combination
    private final Text wordAtFile = new Text();

    @Override
    protected void setup(Context context) {
        // Retrieve the file split information and extract the filename
        FileSplit split = (FileSplit) context.getInputSplit();
        Path path = split.getPath();
        filename = path.getName();
    }

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // Convert the line to lowercase and remove non-alphanumeric characters
        String line = value.toString().toLowerCase().replaceAll("[^a-z0-9 ]", " ");
        // Tokenize the line into individual words
        StringTokenizer tokenizer = new StringTokenizer(line);

        while (tokenizer.hasMoreTokens()) {
            String word = tokenizer.nextToken();
            if (!word.isEmpty()) {
                // Set the word and filename combination as the key
                wordAtFile.set(word + "@" + filename);
                // Write the key-value pair to the context
                context.write(wordAtFile, one);
            }
        }
    }
}
