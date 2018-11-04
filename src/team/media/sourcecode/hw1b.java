package hw1b;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

public class hw1b {

    public static void main(String[] args){

        String fileName = args[0];
//        String fileName ="src/hw1b/example.txt"; // for test

        // read in file content
        File file = new File(fileName);
        List<String> list = new ArrayList<>();
        BufferedReader br;
        try{
            br = new BufferedReader(new FileReader(file));

            String s;
            while((s=br.readLine())!=null){
                list.add(s);
            }
        }catch (Exception e){
            System.out.println(e);
        }

        // print out reversely
        while(list.size()>0){
            System.out.println(list.get(list.size()-1));
            list.remove(list.size()-1);
        }


    }

}
