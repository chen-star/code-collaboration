/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package clickerServlet;

import java.util.HashMap;
import java.util.Map;

/**
 * The Question List Model
 * 
 * @author chenjiaxin
 */
public class QuestionListModel {
    // key is the answer
    // value if the count of each answer
    Map<String, Integer> map;
    
    // init the question list model class
    public QuestionListModel() {
        this.map = new HashMap<>();
    }
    
    /*
     * add an answer into list 
     * 
     * Arguments
     * @param ans the answer of the question
     * @return void
     */
    public void addAns(String ans) {
        if (map.containsKey(ans)) {
            map.put(ans, map.get(ans)+1);
        } else {
            map.put(ans, 1);
        }
    }
    
    /*
     * add an answer into list 
     * 
     * Arguments
     * @return this map of answer
     */
    public Map<String, Integer> getMap() {
        return this.map;
    }
    
    /*
     * remove all the records in map
     * 
     */
    public void clear() {
        this.map.clear();
    }
}
