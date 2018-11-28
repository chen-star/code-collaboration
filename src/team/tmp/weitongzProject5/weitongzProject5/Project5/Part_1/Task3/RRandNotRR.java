package org.myorg;
import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.*;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.util.*;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


public class RRandNotRR extends Configured implements Tool {

        public static class RRandNotRRMap extends Mapper<LongWritable, Text, Text, IntWritable>
        {
               // output of mapper
		private final static IntWritable one = new IntWritable(1);
                private Text word = new Text();

                @Override
                public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
                {
                        String line = value.toString();
                        StringTokenizer tokenizer = new StringTokenizer(line);
                        while(tokenizer.hasMoreTokens())
                        {
                          // get the next token (word)
                          word.set(tokenizer.nextToken());
                          //check the contents by convert from text to the string
                          String s = word.toString();
                          if(s.contains("rr")){
                            //if it contains "rr", make a new record "Contains_rr, one"
                            word.set("Contains_rr");
                            context.write(word, one);
                          }else{
                            //if it does not contain "rr", make a new record "Not_rr, one"
                            word.set("Not_rr");
                            context.write(word, one);
                          }     
                        }
                }
        }

        public static class RRandNotRRReducer extends Reducer<Text, IntWritable, Text, IntWritable>
        {
                public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException
                {
			// start from zero
                        int sum = 0;
			// by now, the key is contains rr and each has value of 1
                        for(IntWritable value: values)
                        {
				// will count for how many words contain rr
                                sum += value.get();
                        }
			// reducer output
                        context.write(key, new IntWritable(sum));
                }

        }

        public int run(String[] args) throws Exception  {

                Job job = new Job(getConf());
                job.setJarByClass(RRandNotRR.class);
                job.setJobName("rrandnotrr");

                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(IntWritable.class);

                job.setMapperClass(RRandNotRRMap.class);
                job.setReducerClass(RRandNotRRReducer.class);


                job.setInputFormatClass(TextInputFormat.class);
                job.setOutputFormatClass(TextOutputFormat.class);


                FileInputFormat.setInputPaths(job, new Path(args[0]));
                FileOutputFormat.setOutputPath(job, new Path(args[1]));

                boolean success = job.waitForCompletion(true);
                return success ? 0: 1;
        }


        public static void main(String[] args) throws Exception {

                int result = ToolRunner.run(new RRandNotRR(), args);
                System.exit(result);
        }

}
