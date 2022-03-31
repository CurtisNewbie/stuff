package com.curtisnewbie.generator.sql;

import org.junit.jupiter.api.*;

import java.util.*;

/**
 * @author yongj.zhuang
 */
public class SqlDmlGeneratorTest {

    public static final String fields = "";
    public static final String dbName = "";
    public static final String tableName = "";
    public static final String jsonDefaultParam = "";
    public static final String jsonArrayParams = "";

    @Test
    public void generate_insert_template_sql() {
        final String insertSql = new SqlDmlGenerator(fields, dbName, tableName)
                .withMapDefaultParam(new ChainedMap()
                        .thenPut("created_at", "CURRENT_TIMESTAMP")
                        .thenPut("created_by", "''")
                        .thenPut("updated_by", "''")
                        .thenPut("updated_at", "CURRENT_TIMESTAMP")
                        .thenPut("trace_id", "''")
                        .thenPut("del_flag", "'N'")
                        .get())
                .withJsonDefaultParam(jsonDefaultParam)
                .withJsonArrayParams(jsonArrayParams)
                .generateInsertSql();

        System.out.println(insertSql);
    }

}
