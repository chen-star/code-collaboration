package netease;
//import java.util.Scanner;
//public class Main {
//
//    public static void main(String[] args){
//        Scanner in = new Scanner(System.in);
//        int n1 = Integer.parseInt(in.nextLine());
//        int[][] a=new int[n1][];
//        int[] num = new int[n1];
//            
//        for (int i=0;i<n1;i++){
//            String[] s=in.nextLine().split(" ");
//            num[i]=Integer.parseInt(s[0]);
//            a[i]=new int[num[i]];
//            for (int j=0;j<num[i];j++){
//                a[i][j]=Integer.parseInt(s[j+1]);
//            }
//                
//        }
//        int[] res = new int[n1];
//        for (int i=0;i<n1;i++){
//            int n = a[i][0];
//            res[i] = check(n,a[i],a[i][1]-a[i][0],1);
//        }
//        for (int i=0;i<n1;i++){
//            System.out.println(res[i]);
//        }
//        in.close();
//    }
//    
//    public static int check(int n,int[] a,int t,int s){
//        int cur=a[s];
//        if (n==2){return t;}
//        for (int i=s+1;i<n;i++){
//            if (a[i]>cur+t){
//                return check(n,a,a[s+1]-a[0],s+1);
//            }
//        }
//        return t;
//    }
//}

import java.util.Scanner;
public class Main {

    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int n1 = Integer.parseInt(in.nextLine());
        int[] a=new int[n1];
        int[] b=new int[n1];
        int[] c=new int[n1];
        for (int i=0;i<n1;i++){
            String[] s = in.nextLine().split(" ");
            a[i]=Integer.parseInt(s[0]);
            b[i]=Integer.parseInt(s[1]);
            c[i]=Integer.parseInt(s[2]);
        }
        int[] res = new int[n1];
        for (int i=0;i<n1;i++){
            if(c[i]==a[i]||c[i]==b[i]){
                res[i]=1;
                break;
            }
            if (c[i]>a[i]&&c[i]>b[i]){
                res[i]=0;
                break;
            }
            if (a[i]==b[i]){
                res[i]=0;
                break;
            }
            int t=0;
            if (a[i]>b[i]){
                t=a[i]-b[i];
            }else{
                int x=a[i];
                a[i]=b[i];
                b[i]=x;
                t=a[i]-b[i];
            }
            if(c[i]%t==0){
                res[i]=2*(c[i]/t);
            }else{
                for (int x=1;x<=a[i]/b[i];x++){
                    if ((a[i]-x*b[i])%c[i]==0){
                        res[i]=2+2*(x-1);
                        break;
                    }
                }
            }
        }
        for (int i=0;i<n1;i++){
            System.out.println(res[i]);
        }
    }
}