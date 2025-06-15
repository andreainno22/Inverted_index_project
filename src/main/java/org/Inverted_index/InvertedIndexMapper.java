package org.Inverted_index;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class InvertedIndexMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private String filename;
    private final IntWritable one = new IntWritable(1);
    private final Text wordAtFile = new Text();

    @Override
    protected void setup(Context context) {
        FileSplit split = (FileSplit) context.getInputSplit();
        Path path = split.getPath();
        filename = path.getName();
    }

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString().toLowerCase().replaceAll("[^a-z0-9 ]", " ");
        StringTokenizer tokenizer = new StringTokenizer(line);

        while (tokenizer.hasMoreTokens()) {
            String word = tokenizer.nextToken();
            if (!word.isEmpty()) {
                wordAtFile.set(word + "@" + filename);
                context.write(wordAtFile, one);
            }
        }
    }
}
