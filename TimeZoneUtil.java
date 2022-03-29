import java.util.*;
import java.time.*;

public class TimeZoneUtil {

    public static void main(String[] args) {

        // now is CST
        final LocalDateTime now = LocalDateTime.now();

        System.out.println();

        String[] tz;
        if (args.length > 0 && (tz = args[0].split(":")).length > 0) {
            String hhstr = tz[0];
            String mmstr = tz.length > 1 ? tz[1] : null;
            String ssstr = tz.length > 2 ? tz[2] : null;

            int hh, mm, ss;
            hh = Integer.parseInt(hhstr);
            mm = mmstr != null ? Integer.parseInt(mmstr) : 0;
            ss = ssstr != null ? Integer.parseInt(ssstr) : 0;

            LocalDateTime cst2utc = now.withHour(hh)
                    .withMinute(mm)
                    .withSecond(ss)
                    .withNano(0)
                    .minusHours(8);

            System.out.printf("CST %s:%s:%s -> UTC:\n\n", padZero(hh), padZero(mm), padZero(ss));
            System.out.printf("\tUTC: %s\n\n", cst2utc);
            printLine(30);

            LocalDateTime utc2cst = now.withHour(hh)
                    .withMinute(mm)
                    .withSecond(ss)
                    .withNano(0)
                    .plusHours(8);

            System.out.printf("UTC %s:%s:%s -> CST:\n\n", padZero(hh), padZero(mm), padZero(ss));
            System.out.printf("\tCST: %s\n\n", utc2cst);
            printLine(30);
        }

        System.out.println("Now:");
        System.out.println("\tCST: " + now);
        System.out.println("\tUTC: " + now.minusHours(8));
        System.out.println();
    }

    public static String padZero(int n) {
        if (n < 10) {
            return "0" + n;
        }
        return n + "";
    }

    public static void printLine(int n) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append("-");
        }
        System.out.println(sb.toString());
    }
}

