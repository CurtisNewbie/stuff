package com.curtisnewbie.generator.sql;

import org.junit.jupiter.api.*;

/**
 * @author yongj.zhuang
 */
public class SqlInsertDmlGeneratorTest {

    public static final String fields = "";
    public static final String dbName = "";
    public static final String tableName = "";
    public static final String jsonDefaultParam = "";
    public static final String tabDelimitedParams = "";

    @Test
    public void generate_insert_template_sql() {
        final String insertSql = new SqlInsertDmlGenerator(fields, dbName, tableName)
                .withMapDefaultParam(new ChainedMap()
                        .thenPut("created_at", "CURRENT_TIMESTAMP")
                        .thenPut("created_by", "''")
                        .thenPut("updated_by", "''")
                        .thenPut("updated_at", "CURRENT_TIMESTAMP")
                        .thenPut("trace_id", "''")
                        .thenPut("del_flag", "'N'")
                        .get())
                .withJsonDefaultParam(jsonDefaultParam)
                .withTabDelimitedParams(tabDelimitedParams, true)
                .generateInsertSql();

        System.out.println(insertSql);
    }

}
