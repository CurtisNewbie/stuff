package com.curtisnewbie.generator.sql;

import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;

import java.io.*;
import java.util.*;

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

        final ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

        final JsonBasedCmd cmd = objectMapper.readValue(file, JsonBasedCmd.class);
        final Set<String> excludedCsvFields = new HashSet<>();
        if (cmd.getExcludedCsvFields() != null) {
            for (String s : cmd.getExcludedCsvFields().split(",")) {
                final String trimmed = s.trim();
                if (!trimmed.isEmpty())
                    excludedCsvFields.add(trimmed);
            }
        }
        try (BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(cmd.getCsvFilePath()), "UTF-8"))) {
            final SqlInsertDmlGenerator generator = new SqlInsertDmlGenerator(cmd.getFields(), cmd.getDbName(), cmd.getTableName())
                    .withMapDefaultParam(cmd.getDefaultParams())
                    .withCsvParam(br, true, excludedCsvFields);

            System.out.println(generator.generateInsertSql());
            System.out.println();
        }
    }
}
