package org.Inverted_index;

import java.io.IOException;
import java.util.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Reducer;

public class InvertedIndexReducer extends Reducer<Text, IntWritable, Text, Text> {

    private final Map<String, List<String>> invertedIndex = new HashMap<>();

    /**
     * The reduce method aggregates the counts of words across different files.
     * It constructs an inverted index where each word maps to a list of files
     * and their respective counts.
     *
     * @param key The word and filename combination (e.g., "word@filename").
     * @param values The counts of the word in the specified file.
     * @param context The context to write the output.
     */
    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {

        // Split the key into word and filename
        String[] parts = key.toString().split("@");
        String word = parts[0];
        String filename = parts[1];

        // Calculate the total count for the word in the specified file
        int sum = 0;
        for (IntWritable val : values)
            sum += val.get();

        // Concatenate the filename and count into a single string
        String entry = filename + ":" + sum;

        // If the word is not already in the inverted index, initialize it
        if (!invertedIndex.containsKey(word)) {
            invertedIndex.put(word, new ArrayList<>());
        }
        // Add the filename:sum entry to the list of files for the word
        invertedIndex.get(word).add(entry);
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        for (Map.Entry<String, List<String>> entry : invertedIndex.entrySet()) {
            // For each word, join the list of file entries into a single string
            String word = entry.getKey();
            String files = String.join(" ", entry.getValue());
            // Emit the word and its associated files with counts
            context.write(new Text(word), new Text(files));
        }
    }
}

