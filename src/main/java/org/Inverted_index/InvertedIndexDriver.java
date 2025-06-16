package org.Inverted_index;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.*;
import org.apache.hadoop.mapreduce.lib.output.*;

import java.util.Arrays;
import java.util.Comparator;

public class InvertedIndexDriver {
    private static final long chunkSizeMB = 10; // Dimensione del chunk in MB
    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("Usage: InvertedIndexDriver <input path> <output path> <num reducers> <totalMB> <use inMapperCombiner>");
            System.exit(-1);
        }

        Configuration conf = new Configuration();

        Job job = Job.getInstance(conf, "Inverted Index");
        job.setJarByClass(InvertedIndexDriver.class);

        // to use the in-mapper combiner if specified
        if (!Boolean.parseBoolean(args[4])) {
            job.setMapperClass(InvertedIndexMapper.class);
            job.setCombinerClass(InvertedIndexCombiner.class);
        }   else {
            job.setMapperClass(InvertedIndexMapper_inMapperCombiner.class);
        }

        job.setReducerClass(InvertedIndexReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        long totalMB = Long.parseLong(args[3]);
        int maxFiles = (int)(totalMB / chunkSizeMB);

        // Select only the first N files from the directory.
        FileSystem fs = FileSystem.get(conf);
        FileStatus[] files = fs.listStatus(new Path(args[0]));

        // Sort by name to take file_00, file_01, ...
        Arrays.sort(files, Comparator.comparing(f -> f.getPath().getName()));

        for (int i = 0; i < Math.min(maxFiles, files.length); i++) {
            TextInputFormat.addInputPath(job, files[i].getPath());
        }

        TextOutputFormat.setOutputPath(job, new Path(args[1]));

        // Set number of reducers dynamically
        int numReducers = Integer.parseInt(args[2]);
        job.setNumReduceTasks(numReducers);

        job.waitForCompletion(true);
    }
}


