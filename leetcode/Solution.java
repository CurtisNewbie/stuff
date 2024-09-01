import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

class Solution {

    public static void main(String[] args) {
        System.out.println(arrToStr(arr("[1,2,3]")));
        System.out.println(arrToStr(multiArr("[[1,2,3],[4,5,6]]")));
    }

    // -------------------------------------------------------------

    private static Pattern arrPat = Pattern.compile("\\[([^\\]]*)\\]");

    public static int[] arr(String s) {
        Matcher m = arrPat.matcher(s);
        if (m.find()) {
            s = m.group(1);
        }
        String[] tok = s.split(",");
        int[] v = new int[tok.length];
        for (int i = 0; i < tok.length; i++) {
            v[i] = Integer.parseInt(tok[i]);
        }
        return v;
    }

    public static int[][] multiArr(String s) {
        s = s.trim().substring(1, s.length() - 1);
        Matcher m = arrPat.matcher(s);
        int n = 0;
        while (m.find()) {
            n += 1;
        }

        m = arrPat.matcher(s);
        int i = 0;
        int[][] r = new int[n][];
        while (m.find()) {
            r[i++] = arr(m.group(1));
        }
        return r;
    }

    public static String arrToStr(int[] arr) {
        return Arrays.toString(arr);
    }

    public static String arrToStr(int[][] arr) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < arr.length; i++) {
            int[] ar = arr[i];
            sb.append(arrToStr(ar));
            if (i < arr.length - 1) {
                sb.append("\n");
            }
        }
        return sb.toString();
    }

}