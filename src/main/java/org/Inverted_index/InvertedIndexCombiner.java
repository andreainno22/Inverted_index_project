package org.Inverted_index;
import java.io.IOException;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Reducer;

public class InvertedIndexCombiner extends Reducer<Text, IntWritable, Text, IntWritable> {

    /**
     * The reduce method aggregates the counts of words across different files.
     * It computes the sum of counts for each word and emits the result.
     *
     * @param key The word and filename combination (e.g., "word@filename").
     * @param values The counts of the word in the specified file.
     * @param context The context to write the output.
     */
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

