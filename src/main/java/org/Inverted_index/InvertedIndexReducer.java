package org.Inverted_index;

import java.io.IOException;
import java.util.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Reducer;

public class InvertedIndexReducer extends Reducer<Text, IntWritable, Text, Text> {

    private final Map<String, List<String>> invertedIndex = new HashMap<>();

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {

        String[] parts = key.toString().split("@");
        String word = parts[0];
        String filename = parts[1];

        int sum = 0;
        for (IntWritable val : values)
            sum += val.get();

        String entry = filename + ":" + sum;

        if (!invertedIndex.containsKey(word)) {
            invertedIndex.put(word, new ArrayList<>());
        }
        invertedIndex.get(word).add(entry);
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        for (Map.Entry<String, List<String>> entry : invertedIndex.entrySet()) {
            String word = entry.getKey();
            String files = String.join(" ", entry.getValue());
            context.write(new Text(word), new Text(files));
        }
    }
}

