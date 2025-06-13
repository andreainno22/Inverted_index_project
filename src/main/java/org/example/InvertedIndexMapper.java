package org.example;
import java.io.IOException;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class InvertedIndexMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private String filename;

    @Override
    protected void setup(Context context) {
        FileSplit split = (FileSplit) context.getInputSplit();
        Path path = split.getPath();
        filename = path.getName();
    }

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString().toLowerCase().replaceAll("[^a-z0-9 ]", " ");
        String[] words = line.split("\\s+");

        for (String word : words) {
            if (!word.isEmpty()) {
                context.write(new Text(word + "@" + filename), new IntWritable(1));
            }
        }
    }
}

