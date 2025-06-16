package org.Inverted_index;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.StringTokenizer;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class InvertedIndexMapper_inMapperCombiner extends Mapper<LongWritable, Text, Text, IntWritable> {

    private String filename;
    private final Map<String, Integer> inMapperCounts = new HashMap<>(); // In-mapper combiner
    private final Text wordAtFile = new Text();

    @Override
    protected void setup(Context context) {
        FileSplit split = (FileSplit) context.getInputSplit();
        Path path = split.getPath();
        filename = path.getName();
    }

    @Override
    protected void map(LongWritable key, Text value, Context context) {
        String line = value.toString().toLowerCase().replaceAll("[^a-z0-9 ]", " ");
        StringTokenizer tokenizer = new StringTokenizer(line);

        while (tokenizer.hasMoreTokens()) {
            String word = tokenizer.nextToken();
            if (!word.isEmpty()) {
                String mapKey = word + "@" + filename;
                inMapperCounts.merge(mapKey, 1, Integer::sum);
            }
        }
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        for (Map.Entry<String, Integer> entry : inMapperCounts.entrySet()) {
            wordAtFile.set(entry.getKey());
            context.write(wordAtFile, new IntWritable(entry.getValue()));
        }
    }
}
