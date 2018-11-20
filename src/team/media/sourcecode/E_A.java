package E_A;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.*;


public class E_A {
    public static void main(String[] args) {
        // read in line by line
        Class currentClass = new Object() {
        }.getClass().getEnclosingClass();
        String fileNum = "A";
//        String fileType = "test-case";
//        String fileType = fileNum +"-small-practice";
      String fileType = fileNum +"-large";
//        String fileType = "A-small-attempt0";
//        String fileName = "src\\" + currentClass.getPackage().getName() + "\\" + fileType + ".in";
        String fileName = "src/" + currentClass.getPackage().getName() + "/" + fileType + ".in";


        PrintWriter writer;

        try {
            writer = new PrintWriter("src/" + currentClass.getPackage().getName() + "/" + fileType + ".out", "UTF-8");
            BufferedReader br = new BufferedReader(new FileReader(fileName));
// t rounds
            int t = Integer.parseInt(br.readLine());
            for (int i = 1; i < t + 1; i++) {
// do sth
                String[] str = br.readLine().split(" ");
                int n = Integer.parseInt(str[0]);
                int k = Integer.parseInt(str[1]);
                str = br.readLine().split(" ");
                int res = 0;
                long maxDay =0l;
                NavigableMap<Long,Integer> expire = new TreeMap<>();
                for(int j=0;j<n;j++){
                    long d = Long.parseLong(str[j]);
                    if(d>maxDay) maxDay=d;
                    expire.put(d,expire.getOrDefault(d,0)+1);
                }
                long day = 1l;
                long key = 0l;
                int value = 0;
                int canEat =k;
                for (Map.Entry<Long,Integer> entry : expire.entrySet()) {
                    key = entry.getKey();
                    value = entry.getValue();
                    while(day<=key && value>0){
                        if(canEat<=value){
                            res+=canEat;
                            value = value - canEat;
                            // next day
                            day++;
                            canEat=k;
                        }else{
                            res+=value;
                            canEat= canEat-value;
                            if(key<maxDay){
                                entry = expire.higherEntry(key);
                                key = entry.getKey();
                                value = entry.getValue();
                            }else{
                                break;
                            }

                        }
                    }



                }





// output, careful about blank space here
                writer.print("Case #" + i + ": " + res);
// print sth
                writer.println();
            }


            br.close();
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

