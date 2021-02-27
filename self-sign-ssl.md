# Self-signed SSL Certificate

src:

```
https://www.baeldung.com/spring-boot-https-self-signed-certificate
https://howtodoinjava.com/spring-boot/spring-boot-ssl-https-example/
```

## 1 Use `key-store` CLI tool that comes with JDK8

e.g.,

```
keytool -genkeypair -alias certAlias -keyalg RSA -keysize 2048 -storetype PKCS12 -keystore serverCert.p12 -validity 3650
```

## 2. Add spring-boot security

```
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

## 3. Setup spring-boot application.properties file

```
server.ssl.key-store-type=PKCS12
server.ssl.key-store=classpath:keystore/serverCert.p12
server.ssl.key-store-password=strongPassword
server.ssl.key-alias=certAlias
server.ssl.enabled=true
```

## 4. (Optionally) Set up spring security, for some of the paths

```
/**
 * @author yongjie.zhuang
 */
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // disable csrf for post (with caution)
        http.csrf().disable()
                .authorizeRequests()
                .antMatchers("/**")
                .permitAll();
    }
}
```
