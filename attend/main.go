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

	"github.com/curtisnewbie/miso/encoding"
	"github.com/curtisnewbie/miso/util"
)

const (
	precision = 1000000000

	ANSIRed    = "\033[1;31m"
	ANSIGreen  = "\033[1;32m"
	ANSICyan   = "\033[1;36m"
	ANSIYellow = "\033[1;93m"
	ANSIReset  = util.ANSIReset
)

var (
	ExtraDates = util.FlagStrSlice("extra", "extra date time records")
	DebugFlag  = flag.Bool("debug", false, "input file dir")
	DirFlag    = flag.String("dir", "", "input file dir")
	AfterFlag  = flag.String("after", "", "after date")
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
	flag.Parse()

	if *DirFlag == "" {
		flag.PrintDefaults()
		return
	}
	fmt.Println()

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
				encoding.ParseJson(buf, &cache)
			}
			if cache == nil {
				cache = map[string]string{}
			}
		}
	}

	now := time.Now()
	pool := util.NewAsyncPool(500, 10)
	ocrFutures := util.NewAwaitFutures[string](pool)

	var aft *time.Time = nil
	if *AfterFlag != "" {
		v, err := ParseTime(*AfterFlag)
		if err != nil {
			panic(err)
		}
		aft = &v
	}

	for _, f := range files {
		if strings.HasPrefix(f.Name(), ".") {
			continue
		}
		inf, err := f.Info()
		if err != nil {
			panic(fmt.Errorf("failed to read file info: %v, %v", f.Name(), err))
		}

		if aft != nil {
			if inf.ModTime().Before(*aft) {
				continue
			}
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
				fmt.Printf("ocr failed %v, %v\n", fpath, err)
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

	for _, s := range fileContent {
		sp := strings.Split(s, "\n")
		lines = append(lines, sp...)
	}
	if ExtraDates != nil {
		if *DebugFlag {
			fmt.Printf("ExtraDates: %v\n", *ExtraDates)
		}
		for _, ed := range *ExtraDates {
			lines = append(lines, "打卡时间: "+ed)
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
		var ds string
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

			if s1 == "结束" {
				if s3 == "上午" {
					ds = fmt.Sprintf("%s 12:00:00", s2)
				} else {
					ds = fmt.Sprintf("%s 18:30:00", s2)
				}
			} else {
				if s3 == "上午" {
					ds = fmt.Sprintf("%s 09:00:00", s2)
				} else {
					continue
				}
			}
			leave = true
		} else {
			ds = strings.TrimSpace(res[1])
		}

		parsedTime, err := ParseTime(ds)
		if err != nil {
			fmt.Printf("error - failed to parse time: %v, %v, l: '%s'\n", ds, err, l)
			continue
		}

		if aft != nil && parsedTime.Before(*aft) {
			continue
		}

		date := FormatDate(parsedTime)
		if prev, ok := dateMap[date]; ok {
			if leave {
				prev.Leave = true
				dateMap[date] = prev
			} else {
				duplicate := false
				for _, v := range prev.Times {
					if v.Equal(parsedTime) {
						duplicate = true
						break
					}
				}
				if !duplicate {
					prev.Times = append(prev.Times, parsedTime)
					dateMap[date] = prev
				}
			}
		} else {
			if leave {
				dateMap[date] = DateTime{Leave: true}
			} else {
				dateMap[date] = DateTime{Times: []time.Time{parsedTime}}
			}
		}
	}

	// fmt.Printf("dataMap: %+v\n", dateMap)
	trs := make([]TimeRange, 0, len(dateMap)/2)
	for k, dt := range dateMap {
		v := dt.Times
		var st time.Time
		var ed time.Time
		var estimated bool = false
		if len(v) < 2 {
			st = v[0]
			if FormatDate(st) != FormatDate(now) {
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

	currMonth := ""
	currMonthCnt := 0

	for _, tr := range trs {
		month := FormatMoth(tr.start)
		if currMonth == "" {
			currMonth = month
		} else if currMonth != month {
			diff := subtotal - float64(currMonthCnt*8)
			start := ANSIGreen + "+"
			if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
				start = ANSIRed
			}
			fmt.Printf("\n%s subtotal: %s = %.2fh (for %d days, %d hours), diff: %s%s (%.6fh) [avg: %.6fh]%s\n", currMonth, HourMin(subtotal), subtotal, currMonthCnt, currMonthCnt*8,
				start, HourMin(diff), diff, float64(subtotal)/float64(currMonthCnt), ANSIReset)
			fmt.Println()
			currMonth = month
			currMonthCnt = 0
			subtotal = 0
		}

		h := float64(tr.Dur()) / float64(time.Hour)
		diffh := h - 8
		diff := float64(h*60) - float64(8*60)
		start := ANSIGreen + "+"
		if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
			start = ANSIRed
		}

		var extraTag string
		var endHmsColorStart string
		if tr.guessed {
			extraTag = fmt.Sprintf("     ---     %vEstimated\x1b[0m", ANSICyan)
			endHmsColorStart = ANSICyan
		} else if tr.Leave {
			extraTag = fmt.Sprintf("     ---     %vLeave\x1b[0m", ANSIYellow)
			endHmsColorStart = ANSIYellow
		}
		dhms := util.PadSpace(-10, HourMin(diffh))
		util.NamedPrintlnf("${startDate} (${startWkDay})  ${startHms} - ${endHmsColorStart}${endHms}\x1b[0m  ${hHourMin} | ${h} ${colorStart}${diffhHourMin}${colorReset}${extraTag}",
			map[string]any{
				"startDate":        FormatDate(tr.start),
				"startWkDay":       FormatWkDay(tr.start),
				"startHms":         FormatHms(tr.start),
				"endHms":           FormatHms(tr.end),
				"hHourMin":         util.PadSpace(-10, HourMin(h)),
				"h":                util.FmtFloat(h, -10, 6),
				"colorStart":       start,
				"diffhHourMin":     dhms,
				"colorReset":       ANSIReset,
				"extraTag":         extraTag,
				"endHmsColorStart": endHmsColorStart,
			})
		total += h
		currMonthCnt += 1
		subtotal += h
	}

	// subtotal for last month
	{
		diff := subtotal - float64(currMonthCnt*8)
		start := ANSIGreen + "+"
		if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
			start = ANSIRed
		}

		fmt.Printf("\n%s subtotal: %s = %.2fh (for %d days, %d hours), diff: %s%s (%.6fh) [avg: %.6fh]%s\n", currMonth, HourMin(subtotal), subtotal, currMonthCnt, currMonthCnt*8,
			start, HourMin(diff), diff, float64(subtotal)/float64(currMonthCnt), ANSIReset)
	}
	println("")

	cf, err := util.ReadWriteFile(cacheFile)
	if err == nil {
		defer cf.Close()
		buf, err := encoding.WriteJson(cache)
		if err == nil {
			_, err = cf.Write(buf)
			if err != nil {
				fmt.Printf("failed to flush cache, %v\n", err)
			}
		}
	}
}
