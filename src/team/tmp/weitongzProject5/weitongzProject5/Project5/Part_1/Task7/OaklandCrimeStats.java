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


public class OaklandCrimeStats extends Configured implements Tool {
  // the const for calculating the distance and if is within range of 200m
  final static double OAKLAND_X = 1354326.897;
  final static double OAKLAND_Y = 411447.7828;
  final static double RANGE = 200.0;//in meter
  final static double FEET_TO_METER = 0.3048;//foot*0.3048=meter
        public static class OaklandCrimeStatsMap extends Mapper<LongWritable, Text, Text, IntWritable>
        {
                private final static IntWritable one = new IntWritable(1);
                private Text word = new Text();
                

                @Override
                public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
                {
                        String line = value.toString();
         		// split the line by tab
	                String[] params = line.split("\t");
                        // the crime name is fifth, get params[4]
			String crime = params[4];
         		// we only want the Agg assault
         		// and then check if is within range of 200m, passing x and y
	                if(crime.equals("AGGRAVATED ASSAULT") && isNearOakland(Double.parseDouble(params[0]),Double.parseDouble(params[1]))){
                 	// if it is what we want, write to mapper output, with the same key
		          word.set("Oakland AGGRAVATED ASSAULT");
                          context.write(word,one);
                        }
                }
        }
	
	// helper function
	// takes in the x and y of crime location
	// returns true or false, whether is within range of 200m
        private static boolean isNearOakland(double x,double y){
	// calculate the distance from the given coors, and convert feet to meters
          double distance = Math.sqrt(Math.pow(x-OAKLAND_X,2)+Math.pow(y-OAKLAND_Y,2))*FEET_TO_METER;//in meter
          return ((distance-RANGE)<0.001);// special returns for comparison of non-int values
        }


        public static class OaklandCrimeStatsReducer extends Reducer<Text, IntWritable, Text, IntWritable>
        {
                public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException
                {
         		// now we only have 1 key and just sum up to get the count
	                int sum=0;
                        for(IntWritable value: values)
                        {
                                sum += value.get();
                        }

                        context.write(key,new IntWritable(sum));
                }

        }

        public int run(String[] args) throws Exception  {

                Job job = new Job(getConf());
                job.setJarByClass(OaklandCrimeStats.class);
                job.setJobName("oaklandcrimestats");

                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(IntWritable.class);

                job.setMapperClass(OaklandCrimeStatsMap.class);
                job.setReducerClass(OaklandCrimeStatsReducer.class);


                job.setInputFormatClass(TextInputFormat.class);
                job.setOutputFormatClass(TextOutputFormat.class);


                FileInputFormat.setInputPaths(job, new Path(args[0]));
                FileOutputFormat.setOutputPath(job, new Path(args[1]));

                boolean success = job.waitForCompletion(true);
                return success ? 0: 1;
        }


        public static void main(String[] args) throws Exception {

                int result = ToolRunner.run(new OaklandCrimeStats(), args);
                System.exit(result);
        }

}
