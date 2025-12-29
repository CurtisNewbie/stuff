package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/curtisnewbie/miso/encoding/json"
	"github.com/curtisnewbie/miso/util"
	"github.com/curtisnewbie/miso/util/cli"
	"github.com/curtisnewbie/miso/util/flags"
	"github.com/curtisnewbie/miso/util/slutil"
	"github.com/curtisnewbie/miso/util/strutil"
)

const (
	precision = 1000000000

	ANSIRed    = "\033[1;31m"
	ANSIGreen  = "\033[1;32m"
	ANSICyan   = "\033[1;36m"
	ANSIYellow = "\033[1;93m"
	ANSIGray   = "\033[1;90m"
	ANSIReset  = cli.ANSIReset
)

var (
	ExtraDates = flags.StrSlice("extra", "extra date time records", false)
	DebugFlag  = flags.Bool("debug", false, "debug", false)
	DirFlag    = flags.String("dir", "", "input file dir", false)
	AfterFlag  = flags.String("after", "", "after date", false)
	LinesFlag  = flags.StrSlice("lines", "extra lines", false)
)

type CachedTimeRange struct {
	Start string
	End   string
}

var (
	cache   map[string]string
	cacheMu sync.Mutex
)

func main() {
	flags.Parse()

	if *DirFlag == "" {
		if es, ok := os.LookupEnv("ATTENDGO_DIR"); ok {
			*DirFlag = es
		}
	}
	if *DirFlag == "" {
		fmt.Printf("Arg '%v' is required \n\n", "dir")
		flag.Usage()
		os.Exit(2)
	}

	files, err := os.ReadDir(*DirFlag)
	if err != nil {
		log.Fatal(err)
	}

	const cacheFile = "/tmp/attend_cache.json"
	{
		cf, err := util.ReadWriteFile(cacheFile)
		if err == nil {
			buf, err := io.ReadAll(cf)
			cf.Close()

			if err == nil {
				_ = json.ParseJson(buf, &cache)
			}
			if cache == nil {
				cache = map[string]string{}
			}
		}
	}

	now := time.Now()
	today := FormatDate(now)
	pool := util.NewAntsAsyncPool(20)
	ocrFutures := util.NewAwaitFutures[string](pool)

	var aft time.Time = util.Now().StartOfMonth().Unwrap()

	if *AfterFlag != "" {
		v, err := ParseTime(*AfterFlag)
		if err != nil {
			panic(err)
		}
		aft = v
	}

	for _, f := range files {
		if strings.HasPrefix(f.Name(), ".") {
			continue
		}
		inf, err := f.Info()
		if err != nil {
			panic(fmt.Errorf("failed to read file info: %v, %v", f.Name(), err))
		}

		if inf.ModTime().Before(aft) {
			continue
		}

		fpath := path.Join(*DirFlag, f.Name())
		cacheKey := fpath + "_" + inf.ModTime().String()

		if *DebugFlag {
			fmt.Printf("cache_key: %v\n", cacheKey)
		}

		ocrFutures.SubmitAsync(func() (string, error) {

			cacheMu.Lock()
			if v, ok := cache[cacheKey]; ok {
				cacheMu.Unlock()
				return v, nil
			}
			cacheMu.Unlock()

			s, err := Ocr(fpath)
			if err == nil {
				cacheMu.Lock()
				cache[cacheKey] = s
				cacheMu.Unlock()
			} else {
				fmt.Printf("ocr failed %v, out: %v, %v\n", fpath, s, err)
			}
			return s, err
		})
	}

	fileContent := make([]string, 0, len(files))
	futures := ocrFutures.Await()
	for _, fu := range futures {
		s, err := fu.Get()
		if err != nil {
			fmt.Printf("OCR failed, %v", err)
			continue
		}
		fileContent = append(fileContent, s)
	}

	// 打卡时间: 2024-06-06 09:11:46
	// 开始时间: 2024年06月12日 下午

	type DateTime struct {
		Times []time.Time
		Leave bool
	}

	dateMap := map[string]DateTime{}
	attPat := regexp.MustCompile(`.*打卡时间: *(\d{4}-\d{2}-\d{2} *\d{2}:?\d{2}:?\d{2}).*`)
	leavePat := regexp.MustCompile(`.*(开始|结束)时间: *(\d{4}年\d{2}月\d{2}日) *(上午|下午).*`)

	lines := make([]string, 0, 100)
	if LinesFlag != nil {
		lines = append(lines, *LinesFlag...)
	}

	for _, s := range fileContent {
		sp := strings.Split(s, "\n")
		lines = append(lines, sp...)
	}

	parseExtra := func(ed string) {
		if t, err := ParseTime(ed); err == nil {
			lines = append(lines, "打卡时间: "+util.WrapTime(t).FormatStd())
		}
		if t, err := ParseTime(today + " " + ed); err == nil {
			lines = append(lines, "打卡时间: "+util.WrapTime(t).FormatStd())
		}
	}
	if ExtraDates != nil {
		fmt.Printf("ExtraDatesFlag: %+v\n", *ExtraDates)
		for _, ed := range *ExtraDates {
			parseExtra(ed)
		}
	}

	if es, ok := os.LookupEnv("ATTENDGO_EXTRA"); ok {
		sp := strutil.SplitStr(es, ",")
		fmt.Printf("ExtraDatesEnv: %+v\n", sp)
		for _, ed := range sp {
			parseExtra(ed)
		}
	}

	for _, l := range lines {
		l = strings.TrimSpace(l)
		if l == "" {
			continue
		}
		if *DebugFlag {
			fmt.Printf("l: %v\n", l)
		}

		// leave from work
		var leave bool = false
		var dsl []string
		res := attPat.FindStringSubmatch(l)
		if len(res) < 1 {
			if strings.Contains(l, "打卡时间:") {
				if *DebugFlag {
					fmt.Printf("line invalid: %s\n", l)
				}
			}

			res = leavePat.FindStringSubmatch(l)
			if len(res) < 4 {
				if *DebugFlag {
					if strings.Contains(l, "开始时间") || strings.Contains(l, "结束时间") {
						fmt.Printf("line invalid: %s\n", l)
					}
				}
				continue
			}

			s1 := res[1]
			s2 := res[2]
			s3 := res[3]

			s2 = strings.ReplaceAll(s2, "年", "-")
			s2 = strings.ReplaceAll(s2, "月", "-")
			s2 = strings.ReplaceAll(s2, "日", "")

			if *DebugFlag {
				fmt.Printf("s1: %v, s2: %v, s3: %v\n", s1, s2, s3)
			}

			if s1 == "结束" {
				if s3 == "上午" {
					dsl = append(dsl, fmt.Sprintf("%s 09:00:00", s2))
					dsl = append(dsl, fmt.Sprintf("%s 12:00:00", s2))
				} else {
					dsl = append(dsl, fmt.Sprintf("%s 18:30:00", s2))
				}
			} else {
				if s3 == "上午" {
					dsl = append(dsl, fmt.Sprintf("%s 09:00:00", s2))
				} else {
					dsl = append(dsl, fmt.Sprintf("%s 12:00:00", s2))
				}
			}
			leave = true
		} else {
			dsl = append(dsl, strings.TrimSpace(res[1]))
		}

		for _, ds := range dsl {
			parsedTime, err := ParseTime(ds)
			if err != nil {
				fmt.Printf("error - failed to parse time: %v, %v, l: '%s'\n", ds, err, l)
				continue
			}
			if *DebugFlag {
				fmt.Printf("parsed time: %v, l: '%s', leave: %v\n", ds, l, leave)
			}

			if parsedTime.Before(aft) {
				continue
			}

			date := FormatDate(parsedTime)
			if *DebugFlag {
				fmt.Printf("format date: %v, l: '%s'\n", date, l)
			}
			if prev, ok := dateMap[date]; ok {
				duplicate := false
				if leave {
					prev.Leave = true
				}
				for _, v := range prev.Times {
					if v.Equal(parsedTime) {
						if *DebugFlag {
							fmt.Printf("duplicate: %v\n", parsedTime)
						}
						duplicate = true
						break
					}
				}
				if !duplicate {
					prev.Times = append(prev.Times, parsedTime)
					dateMap[date] = prev
				}
			} else {
				dt := DateTime{Times: []time.Time{parsedTime}}
				if leave {
					dt.Leave = true
				}
				dateMap[date] = dt
			}
		}
	}

	// fmt.Printf("dataMap: %+v\n", dateMap)
	trs := make([]TimeRange, 0, len(dateMap)/2)
	for k, dt := range dateMap {
		// fmt.Printf("dt: %v\n", dt)
		v := dt.Times
		var st time.Time
		var ed time.Time
		var estimated bool = false
		if len(v) < 2 {
			st = v[0]
			if FormatDate(st) != today {
				if *DebugFlag {
					fmt.Printf("Date missing attendence record, skipped: %+v\n", v)
				}
				continue
			}
			ed = time.Date(now.Year(), now.Month(), now.Day(), 18, 30, 0, 0, time.Local)
			if now.After(ed) {
				ed = now
			}
			estimated = true

		} else if len(v) == 4 {
			fmt.Printf("half day leave: %+v\n", v)

			leave09, _ := ParseTime(k + " 09:00:00")
			leave12, _ := ParseTime(k + " 12:00:00")
			leave18, _ := ParseTime(k + " 18:30:00")

			// half day leave, so there should be 4 times
			// find the times for leave and drop them
			// they are either 09-12 or 12-18:30
			rmi, rmj := -1, -1
			for i := range len(v) {
				vi := v[i]
				if vi.Equal(leave09) {
					rmi = i
				} else if vi.Equal(leave12) {
					rmj = i
				}
			}
			if rmi > -1 && rmj > -1 {
				// leave 09:00 - 12:00
				v = slutil.SliceRemove(v, rmi, rmj)
			} else {
				rmi, rmj = -1, -1
				for i := range len(v) {
					vi := v[i]
					if vi.Equal(leave12) {
						rmi = i
					} else if vi.Equal(leave18) {
						rmj = i
					}
				}
				// leave 12:00 - 18:30
				v = slutil.SliceRemove(v, rmi, rmj)
			}

			st = v[0]
			ed = v[1]
			if st.After(ed) {
				st, ed = ed, st
			}
		} else {
			st = v[0]
			ed = v[1]
		}

		if st.After(ed) {
			st, ed = ed, st
		}
		tr := NewTimeRange(k, st, ed, estimated)
		if dt.Leave {
			tr.Leave = true
		}
		trs = append(trs, tr)
	}
	sort.Slice(trs, func(i, j int) bool { return trs[i].start.Before(trs[j].start) })
	fmt.Println()

	total := float64(0)
	subtotal := float64(0)

	statCurrMonth := ""
	statCurrMonthCnt := 0

	var hasPrevPrintedDate bool = false
	var prevPrintedDate util.Time

	for _, tr := range trs {
		month := FormatMoth(tr.start)
		if statCurrMonth == "" {
			statCurrMonth = month
		} else if statCurrMonth != month {
			diff := subtotal - float64(statCurrMonthCnt*8)
			start := ANSIGreen + "+"
			if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
				start = ANSIRed
			}
			fmt.Printf("\n%s subtotal: %s = %.2fh (for %d days, %d hours), diff: %s%s (%.6fh) [avg: %.6fh]%s\n", statCurrMonth, HourMin(subtotal), subtotal, statCurrMonthCnt, statCurrMonthCnt*8,
				start, HourMin(diff), diff, float64(subtotal)/float64(statCurrMonthCnt), ANSIReset)
			fmt.Println()
			statCurrMonth = month
			statCurrMonthCnt = 0
			subtotal = 0
		}

		trs := util.WrapTime(tr.start)
		if !hasPrevPrintedDate {
			prevPrintedDate = trs
			hasPrevPrintedDate = true
		} else {
			if prevPrintedDate.FormatDate() != trs.AddDate(0, 0, -1).FormatDate() {
				for prevPrintedDate.FormatDate() != trs.FormatDate() {
					prevPrintedDate = prevPrintedDate.AddDate(0, 0, 1)
					if prevPrintedDate.FormatDate() == trs.FormatDate() {
						break
					}
					missingFlag := ""
					startColor := ANSIGray
					switch prevPrintedDate.Weekday() {
					case time.Saturday, time.Sunday:
						startColor = ANSIGray
					default:
						missingFlag = strings.Repeat(" ", 62) + ANSIReset + "---     " + ANSIRed + "Missing"
					}

					println(strutil.NamedSprintf("${colorStart}${startDate} (${startWkDay})${missingFlag}${colorReset}",
						map[string]any{
							"startDate":   FormatDate(prevPrintedDate.Unwrap()),
							"startWkDay":  FormatWkDay(prevPrintedDate.Unwrap()),
							"colorStart":  startColor,
							"colorReset":  ANSIReset,
							"missingFlag": missingFlag,
						}))
				}
			} else {
				prevPrintedDate = trs
			}
		}

		h := float64(tr.Dur()) / float64(time.Hour)
		diffh := h - 8
		diff := float64(h*60) - float64(8*60)
		start := ANSIGreen
		positive := true
		if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
			start = ANSIRed
			positive = false
		}

		var extraTag string
		var endHmsColorStart string
		var startHmsColorStart string
		if tr.guessed {
			extraTag = fmt.Sprintf("     ---     %vEstimated\x1b[0m", ANSICyan)
			endHmsColorStart = ANSICyan
		} else if tr.Leave {
			extraTag = fmt.Sprintf("     ---     %vLeave\x1b[0m", ANSIYellow)
			startHmsColorStart = ANSIYellow
		}
		diffhs := strings.TrimSpace(HourMin(diffh))
		if positive {
			diffhs = "+" + diffhs
		}
		dhms := strutil.PadSpace(-10, diffhs)
		println(strutil.NamedSprintf("${startDate} (${startWkDay})  ${startHmsColorStart}${startHms} - ${endHmsColorStart}${endHms}\x1b[0m  ${hHourMin} | ${h} ${colorStart}${diffhHourMin}${colorReset}${extraTag}",
			map[string]any{
				"startDate":          FormatDate(tr.start),
				"startWkDay":         FormatWkDay(tr.start),
				"startHms":           FormatHms(tr.start),
				"endHms":             FormatHms(tr.end),
				"hHourMin":           strutil.PadSpace(-10, HourMin(h)),
				"h":                  strutil.FmtFloat(h, -10, 6),
				"colorStart":         start,
				"diffhHourMin":       dhms,
				"colorReset":         ANSIReset,
				"extraTag":           extraTag,
				"startHmsColorStart": startHmsColorStart,
				"endHmsColorStart":   endHmsColorStart,
			}))
		total += h
		statCurrMonthCnt += 1
		subtotal += h
	}

	// subtotal for last month
	{
		diff := subtotal - float64(statCurrMonthCnt*8)
		start := ANSIGreen + "+"
		if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
			start = ANSIRed
		}

		fmt.Printf("\n%s subtotal: %s = %.2fh (for %d days, %d hours), diff: %s%s (%.6fh) [avg: %.6fh]%s\n", statCurrMonth, HourMin(subtotal), subtotal, statCurrMonthCnt, statCurrMonthCnt*8,
			start, HourMin(diff), diff, float64(subtotal)/float64(statCurrMonthCnt), ANSIReset)
	}
	println("")

	cf, err := util.ReadWriteFile(cacheFile)
	if err == nil {
		defer cf.Close()
		buf, err := json.WriteJson(cache)
		if err == nil {
			_, err = cf.Write(buf)
			if err != nil {
				fmt.Printf("failed to flush cache, %v\n", err)
			}
		}
	}
}
