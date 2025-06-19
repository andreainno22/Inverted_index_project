package org.Inverted_index;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.*;
import org.apache.hadoop.mapreduce.lib.output.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator; // Import per il Comparator
import java.util.List;

public class InvertedIndexDriver {
    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("Usage: InvertedIndexDriver <input path> <output path> <num reducers> <totalMB> <use inMapperCombiner>");
            System.exit(-1);
        }

        Configuration conf = new Configuration();

        Job job = Job.getInstance(conf, "Inverted Index");
        job.setJarByClass(InvertedIndexDriver.class);

        // Configure Mapper and Combiner based on argument
        if (!Boolean.parseBoolean(args[4])) { // If inMapperCombiner is false, use Combiner
            job.setMapperClass(InvertedIndexMapperOpt.class);
            job.setCombinerClass(InvertedIndexCombiner.class);
        } else { // Else, use in-mapper combiner
            job.setMapperClass(InvertedIndexMapper_inMapperCombiner.class);
        }

        job.setReducerClass(InvertedIndexReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        // Desired total data size in MB
        long desiredTotalMB = Long.parseLong(args[3]);
        // Convert MB to bytes for comparison
        long desiredTotalBytes = desiredTotalMB * 1024 * 1024;

        FileSystem fs = FileSystem.get(conf);
        Path inputDirPath = new Path(args[0]);

        // List all files in the input directory
        FileStatus[] allFilesStatus = fs.listStatus(inputDirPath);
        if (allFilesStatus == null || allFilesStatus.length == 0) {
            System.err.println("No files found in the input directory: " + inputDirPath);
            System.exit(-1);
        }

        List<FileStatus> availableFiles = new ArrayList<>();
        for (FileStatus fileStatus : allFilesStatus) {
            // Only consider actual files, not directories
            if (fileStatus.isFile()) {
                availableFiles.add(fileStatus);
            }
        }

        // Sort the list of available files by size (ascending)
        Collections.sort(availableFiles, Comparator.comparingLong(FileStatus::getLen));

        long currentTotalBytes = 0;
        int filesAdded = 0;

        // Iterate through sorted files and add them until desiredTotalBytes is reached
        for (FileStatus fileStatus : availableFiles) {
            if (currentTotalBytes >= desiredTotalBytes) {
                break; // Stop if we've reached or exceeded the desired total size
            }
            try {
                long fileSize = fileStatus.getLen(); // Get file size in bytes
                TextInputFormat.addInputPath(job, fileStatus.getPath());
                currentTotalBytes += fileSize;
                filesAdded++;
            } catch (IOException e) {
                System.err.println("Could not add file " + fileStatus.getPath().getName() + " to job input: " + e.getMessage());
            }
        }

        if (filesAdded == 0) {
            System.err.println("No files were added to the job input. Check if files exist and are accessible.");
            System.exit(-1);
        }

        System.out.println("Total files added: " + filesAdded);
        System.out.println("Total data size selected: " + (currentTotalBytes / (1024.0 * 1024.0)) + " MB");

        TextOutputFormat.setOutputPath(job, new Path(args[1]));

        // Set number of reducers
        int numReducers = Integer.parseInt(args[2]);
        job.setNumReduceTasks(numReducers);

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}