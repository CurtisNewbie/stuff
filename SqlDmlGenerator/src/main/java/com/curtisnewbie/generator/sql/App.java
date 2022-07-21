package com.curtisnewbie.generator.sql;

import com.fasterxml.jackson.databind.*;

import java.io.*;
import java.io.InputStreamReader;
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
            if (file.createNewFile()) {
                try (BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(file)))) {
                    bw.write("{\n");
                    bw.write("\t\"fields\": \"\",\n");
                    bw.write("\t\"dbName\": \"\",\n");
                    bw.write("\t\"tableName\": \"\",\n");
                    bw.write("\t\"defaultParams\": {\n");
                    bw.write("\t\t\"created_at\": \"CURRENT_TIMESTAMP\",\n");
                    bw.write("\t\t\"created_by\": \"''\",\n");
                    bw.write("\t\t\"updated_at\": \"CURRENT_TIMESTAMP\",\n");
                    bw.write("\t\t\"updated_by\": \"''\",\n");
                    bw.write("\t\t\"trace_id\": \"''\",\n");
                    bw.write("\t\t\"del_flag\": \"'N'\",\n");
                    bw.write("\t\t\"enable\": \"Y\"\n");
                    bw.write("\t},\n");
                    bw.write("\t\"excludedCsvFields\": \"created_at,created_by,updated_by,updated_at,trace_id,del_flag\",\n");
                    bw.write("\t\"csvFilePath\": \"\"\n");
                    bw.write("}\n");
                }
                System.out.printf("File: %s doesn't exist, generated new one with default config\n", path);
                return;
            }

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
