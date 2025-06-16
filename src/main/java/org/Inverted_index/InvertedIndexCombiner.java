package org.Inverted_index;
import java.io.IOException;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Reducer;

public class InvertedIndexCombiner extends Reducer<Text, IntWritable, Text, IntWritable> {

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {
        // Initialize a variable to store the sum of values
        int sum = 0;
        // Iterate through all values associated with the key and calculate the sum
        for (IntWritable val : values)
            sum += val.get();
        // Write the key and the computed sum to the context
        context.write(key, new IntWritable(sum));
    }
}

