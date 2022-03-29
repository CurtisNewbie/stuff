package com.curtisnewbie.generator.sql;

import com.sun.net.httpserver.*;
import org.junit.jupiter.api.*;

import java.util.*;

/**
 * @author yongj.zhuang
 */
public class SqlDmlGeneratorTest {

    @Test
    public void generate_insert_template_sql() {

        Map<String, String> defaultParams = new HashMap<>();
        defaultParams.put("sender_type", "0");
        defaultParams.put("title_en", "''");
        defaultParams.put("content", "''");
        defaultParams.put("content_en", "''");
        defaultParams.put("business_id", "'ALL'");
        defaultParams.put("name", "''");
        defaultParams.put("status", "1");
        defaultParams.put("created_at", "CURRENT_TIMESTAMP");
        defaultParams.put("created_by", "''");
        defaultParams.put("updated_by", "''");
        defaultParams.put("updated_at", "CURRENT_TIMESTAMP");
        defaultParams.put("trace_id", "''");
        defaultParams.put("del_flag", "'N'");
        final String insertIntoValues = "insert into message.t_msg_template(code,sender_type,title,title_en,content,content_en,business_id,name,description,status,created_by,created_at,updated_by,updated_at,trace_id,del_flag) values";
        final List<Map<String, String>> params = Arrays.asList(
                new ChainedMap(defaultParams).thenPut("code", "'SMS_237560619'").thenPut("title", "'VA 管理费收取成功提醒 (阿里云国内)'").thenPut("description", "'VA 管理费收取成功提醒 (阿里云国内)'").get(),
                new ChainedMap(defaultParams).thenPut("code", "'SMS_237590493'").thenPut("title", "'VA 管理费收取成功提醒 (阿里云国际)'").thenPut("description", "'VA 管理费收取成功提醒 (阿里云国际)'").get(),
                new ChainedMap(defaultParams).thenPut("code", "'SMS_237570578'").thenPut("title", "'VA 管理费收取失败提醒 (阿里云国内)'").thenPut("description", "'VA 管理费收取失败提醒 (阿里云国内)'").get(),
                new ChainedMap(defaultParams).thenPut("code", "'SMS_237590496'").thenPut("title", "'VA 管理费收取失败提醒 (阿里云国际)'").thenPut("description", "'VA 管理费收取失败提醒 (阿里云国际)'").get(),
                new ChainedMap(defaultParams).thenPut("code", "'50860'").thenPut("title", "'VA 管理费收取成功提醒 (祝通融)'").thenPut("description", "'VA 管理费收取成功提醒 (祝通融)'").get(),
                new ChainedMap(defaultParams).thenPut("code", "'50861'").thenPut("title", "'VA 管理费收取失败提醒 (祝通融)'").thenPut("description", "'VA 管理费收取失败提醒 (祝通融)'").get(),
                new ChainedMap(defaultParams).thenPut("sender_type", "3")
                        .thenPut("code", "'va_mng_fee_charge_success'")
                        .thenPut("title", "'VA 管理费收费成功'")
                        .thenPut("title_en", "'VA Management Fee Charge Success'")
                        .thenPut("content", "'尊敬的光子易会员${legalName}，您于${deductionTime}成功扣取账户管理费，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}，感谢您对PhotonPay支持！'")
                        .thenPut("content_en", "'Dear PhotonPay member ${legalName}, ${deductionTime} successfully deducted the account management fee, the global account number is ${accountNumber}, the deduction amount is ${deductionAmtAndCurrency}, thank you for your support to PhotonPay!'")
                        .thenPut("description", "'VA 管理费收费成功'").get(),

                new ChainedMap(defaultParams).thenPut("sender_type", "3")
                        .thenPut("code", "'va_mng_fee_charge_failure'")
                        .thenPut("title", "'VA 管理费收费失败'")
                        .thenPut("title_en", "'VA Management Fee Charge Failure'")
                        .thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}因账户余额不足，账户管理费扣款失败，全球账户是${accountNumber}，扣费金额为${deductionAmtAndCurrency}。该账户现进入待注销期（即日起至${lastDay}），超过日期仍没有扣费成功，则账户会被注销，如需帮助请联系我们。400-859-9576'")
                        .thenPut("content_en", "'Dear PhotonEase member ${legalName}, ${deductionTime} account management fee debit failed due to insufficient account balance, global account is ${accountNumber}, debit amount is ${deductionAmtAndCurrency}. The account is now in the pending cancellation period (from now until ${lastDay}), after the date there is still no successful deduction, the account will be cancelled, if you need help please contact us. 400-859-9576'")
                        .thenPut("description", "'VA 管理费收费失败'").get()
        );

        SqlDmlGenerator sqlDmlGenerator = new SqlDmlGenerator(insertIntoValues, params);
        sqlDmlGenerator.generateInsertSql();
    }

    @Test
    public void generate_insert_sender_template_sql() {

        Map<String, String> defaultParams = new HashMap<>();
        defaultParams.put("remark", "''");
        defaultParams.put("created_at", "CURRENT_TIMESTAMP");
        defaultParams.put("created_by", "''");
        defaultParams.put("updated_by", "''");
        defaultParams.put("updated_at", "CURRENT_TIMESTAMP");
        defaultParams.put("trace_id", "''");
        defaultParams.put("del_flag", "'N'");

        final String insertIntoValues = "INSERT INTO message_dev.t_msg_sender_template (template_code,sender_code,sender_template_code,content,remark,created_by,created_at,updated_by,updated_at,trace_id,del_flag) values";
        final List<Map<String, String>> params = Arrays.asList(
                new ChainedMap(defaultParams).thenPut("template_code", "'SMS_237560619'").thenPut("sender_code", "'aliSms'").thenPut("sender_template_code", "'SMS_237560619'").thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}成功扣取账户管理费，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}，扣费详情请登录光子易会员端！'").get(),
                new ChainedMap(defaultParams).thenPut("template_code", "'SMS_237590493'").thenPut("sender_code", "'aliSms'").thenPut("sender_template_code", "'SMS_237590493'").thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}成功扣取账户管理费，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}，扣费详情请登录光子易会员端！'").get(),
                new ChainedMap(defaultParams).thenPut("template_code", "'SMS_237570578'").thenPut("sender_code", "'aliSms'").thenPut("sender_template_code", "'SMS_237570578'").thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}因账户余额不足，账户管理费扣款失败，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}。该账户现进入待注销期（即日起至${lastDay}），超过日期仍没有扣费成功，则账户会被注销，如需帮助请联系我们。400-859-9576'").get(),
                new ChainedMap(defaultParams).thenPut("template_code", "'SMS_237590496'").thenPut("sender_code", "'aliSms'").thenPut("sender_template_code", "'SMS_237590496'").thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}因账户余额不足，账户管理费扣款失败，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}。该账户现进入待注销期（即日起至${lastDay}），超过日期仍没有扣费成功，则账户会被注销，如需帮助请联系我们。400-859-9576'").get(),
                new ChainedMap(defaultParams).thenPut("template_code", "'50860'").thenPut("sender_code", "'ztSms'").thenPut("sender_template_code", "'50860'").thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}成功扣取账户管理费，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}，扣费详情请登录光子易会员端！'").get(),
                new ChainedMap(defaultParams).thenPut("template_code", "'50861'").thenPut("sender_code", "'ztSms'").thenPut("sender_template_code", "'50861'").thenPut("content", "'尊敬的光子易会员${legalName}，${deductionTime}因账户余额不足，账户管理费扣款失败，全球账号是${accountNumber}，扣费金额为${deductionAmtAndCurrency}。该账户现进入待注销期（即日起至${lastDay}），超过日期仍没有扣费成功，则账户会被注销，如需帮助请联系我们。400-859-9576'").get()
        );

        SqlDmlGenerator sqlDmlGenerator = new SqlDmlGenerator(insertIntoValues, params);
        sqlDmlGenerator.generateInsertSql();
    }
}
