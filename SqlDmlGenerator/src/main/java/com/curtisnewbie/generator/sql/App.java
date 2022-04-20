package com.curtisnewbie.generator.sql;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;

/**
 * @author yongj.zhuang
 */
public class App {

    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.out.println("Please specify path to the json param file:");
            return;
        }

        final String path = args[0];
        File file = new File(path);
        if (!file.exists()) {
            System.out.printf("File: %s doesn't exist\n", path);
            return;
        }


        final JsonBasedCmd cmd = new ObjectMapper().readValue(file, JsonBasedCmd.class);
        final SqlInsertDmlGenerator generator = new SqlInsertDmlGenerator(cmd.getFields(), cmd.getDbName(), cmd.getTableName())
                .withJsonDefaultParam(cmd.getDefaultParams())
                .withTabDelimitedParams(cmd.getTabDelimitedParam(), true);

        System.out.println(generator.generateInsertSql());
        System.out.println();
    }
}
