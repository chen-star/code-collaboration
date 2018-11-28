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


public class RapesPlusRobberies extends Configured implements Tool {

        public static class RapesPlusRobberiesMap extends Mapper<LongWritable, Text, Text, IntWritable>
        {
        	// the output of mapper
	        private final static IntWritable one = new IntWritable(1);
                private Text word = new Text();

                @Override
                public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
                {
                        String line = value.toString();
                	// split the string by tab  
		       String[] params = line.split("\t");
			// the crime name is fifth, so get params[4]
                        StringTokenizer tokenizer = new StringTokenizer(params[4]);
                        while(tokenizer.hasMoreTokens())
                        {
                                word.set(tokenizer.nextToken());
                        	// get the crime name 
			       	String s = word.toString();
				// and check if it is robbery or rape
                                
				if(s.equals("ROBBERY") || s.equals("RAPE")){
				  word.set("Robbery plus Rape");
                                  context.write(word, one);
                                }

                        }
                }
        }
	
	// the signature is changed to <...Text, Text> for desired output format
        public static class RapesPlusRobberiesReducer extends Reducer<Text, IntWritable, Text, IntWritable>
        {
                public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException
                {
         		// set the counter for total(rape and robbery)
	                int total = 0;
                       
			// only 2 keys as mentioned above
                        for(IntWritable value: values)
                        {	
				// add 1 to total
                                total += value.get();
         
	               }
			// build the desired output format (rape_count + robbery_count)              
              	// output would be "Robbery plus Rape" with the total number
			context.write(key, new IntWritable(total));
                }

        }

        public int run(String[] args) throws Exception  {

                Job job = new Job(getConf());
                job.setJarByClass(RapesPlusRobberies.class);
                job.setJobName("rapesplusrobberies");

                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(IntWritable.class);

                job.setMapperClass(RapesPlusRobberiesMap.class);
                job.setReducerClass(RapesPlusRobberiesReducer.class);


                job.setInputFormatClass(TextInputFormat.class);
                job.setOutputFormatClass(TextOutputFormat.class);


                FileInputFormat.setInputPaths(job, new Path(args[0]));
                FileOutputFormat.setOutputPath(job, new Path(args[1]));

                boolean success = job.waitForCompletion(true);
                return success ? 0: 1;
        }


        public static void main(String[] args) throws Exception {

                int result = ToolRunner.run(new RapesPlusRobberies(), args);
                System.exit(result);
        }

}

