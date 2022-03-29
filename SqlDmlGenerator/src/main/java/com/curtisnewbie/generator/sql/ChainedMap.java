package com.curtisnewbie.generator.sql;

import java.util.*;

/**
 * @author yongj.zhuang
 */
public class ChainedMap {

    private Map<String, String> param;

    public ChainedMap(Map<String, String> param) {
        this.param = new HashMap<>(param);
    }

    public ChainedMap() {
        this.param = new HashMap<>();
    }

    public ChainedMap thenPut(String k, String v) {
        param.put(k, v);
        return this;
    }

    public Map<String, String> get() {
        return param;
    }
}
