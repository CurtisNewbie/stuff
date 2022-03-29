package com.curtisnewbie.generator.sql;

import org.junit.jupiter.api.*;

import java.util.*;

/**
 * @author yongj.zhuang
 */
public class SqlDmlGeneratorTest {

    @Test
    public void generate_insert_sql() {
        final String insertIntoValues = "insert into db.table_name(code,title,content,status) values";

        final List<Map<String, String>> params = Arrays.asList(
                new ChainedMap(defaultParams()).thenPut("code", "'VAC1'").thenPut("title", "'VAC 1'").thenPut("content", "'Some random content'").get(),
                new ChainedMap(defaultParams()).thenPut("code", "'VAC1'").thenPut("title", "'VAC 1'").thenPut("content", "'Some random content'").get(),
                new ChainedMap(defaultParams()).thenPut("code", "'VAC1'").thenPut("title", "'VAC 1'").thenPut("content", "'Some random content'").get()
                );

        SqlDmlGenerator sqlDmlGenerator = new SqlDmlGenerator(insertIntoValues, params);
        sqlDmlGenerator.generateInsertSql();
    }

    private Map<String, String> defaultParams() {
        Map<String, String> param = new HashMap<>();
        param.put("code", "''");
        param.put("title", "''");
        param.put("content", "''");
        param.put("status", "1");
        return param;
    }
}
