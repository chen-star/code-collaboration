public class Tester {
    public static void main(String[] args) {
        MyArray arr = new MyArray(0);
        arr.add("a");
        arr.add("b");
        arr.add("the");
        arr.add("children");
        arr.add("the");
        arr.add("the");
        arr.add("from");
        arr.add("the");
        arr.add("from");
        arr.display();
//        System.out.println("arr.getCapacity() = " + arr.getCapacity());
//        System.out.println("arr.size() = " + arr.size());
        arr.removeDups();
        arr.display();
    }
}
