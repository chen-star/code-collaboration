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


public class OaklandCrimeStatsKML extends Configured implements Tool {
  final static double OAKLAND_X = 1354326.897;
  final static double OAKLAND_Y = 411447.7828;
  final static double RANGE = 200.0;
  final static double FEET_TO_METER = 0.3048;//foot*0.3048=meter
        public static class OaklandCrimeStatsKMLMap extends Mapper<LongWritable, Text, Text, Text>
        {
                private final static IntWritable one = new IntWritable(1);
                private Text word = new Text();
                private Text coor = new Text();

                @Override
                public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
                {
                        String line = value.toString();
                        String[] params = line.split("\t");
                        String crime = params[4];
                        if(crime.equals("AGGRAVATED ASSAULT") && isNearOakland(Double.parseDouble(params[0]),Double.parseDouble(params[1]))){
                          word.set("Oakland AGGRAVATED ASSAULT");
                          coor.set(params[8]+","+params[7]+",0.00");//last two colomns for KML GIS
                          context.write(word,coor);
                        }
                }
        }

        private static boolean isNearOakland(double x,double y){
          double distance = Math.sqrt(Math.pow(x-OAKLAND_X,2)+Math.pow(y-OAKLAND_Y,2))*FEET_TO_METER;//in meter
          return ((distance-RANGE)<0.001);
        }

        public static class OaklandCrimeStatsKMLReducer extends Reducer<Text, Text, Text, Text>
        {
                public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException
                {
                  String opening = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
                          + "<kml xmlns=\"http://earth.google.com/kml/2.2\">\n"
                          + "<Document>\n"
                          + "<Style id=\"style1\">\n"
                          + "<IconStyle>\n"
                          + "<Icon>\n"
                          + "<href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>\n"
                          + "</Icon>\n"
                          + "</IconStyle>\n"
                          + "</Style>"; // the first part of kml file
                  String closing = "</Document>\n"
                          + "</kml>"; // the last part of kml file
                  StringBuilder sb = new StringBuilder();
                  sb.append(opening);
                        for(Text coor: values)
                        {
                              String t = "<Placemark>\n"
                                      + "<name>aggravated assault</name>\n"
                                      + "<styleUrl>#style1</styleUrl>\n"
                                      + "<Point>\n"
                                      + "<coordinates>" + coor.toString() + "</coordinates>\n"
                                      + "</Point>\n"
                                      + "</Placemark>\n";
                              sb.append(t);
                        }
                        sb.append(closing);
                        context.write(new Text(sb.toString()),new Text());
                }

        }

        public int run(String[] args) throws Exception  {

                Job job = new Job(getConf());
                job.setJarByClass(OaklandCrimeStatsKML.class);
                job.setJobName("oaklandcrimestats");

                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(Text.class);

                job.setMapperClass(OaklandCrimeStatsKMLMap.class);
                job.setReducerClass(OaklandCrimeStatsKMLReducer.class);


                job.setInputFormatClass(TextInputFormat.class);
                job.setOutputFormatClass(TextOutputFormat.class);


                FileInputFormat.setInputPaths(job, new Path(args[0]));
                FileOutputFormat.setOutputPath(job, new Path(args[1]));

                boolean success = job.waitForCompletion(true);
                return success ? 0: 1;
        }


        public static void main(String[] args) throws Exception {

                int result = ToolRunner.run(new OaklandCrimeStatsKML(), args);
                System.exit(result);
        }

}
