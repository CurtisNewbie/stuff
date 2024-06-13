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

	"github.com/curtisnewbie/miso/util"
)

const (
	precision = 100000

	ANSIRed   = "\033[1;31m"
	ANSIGreen = "\033[1;32m"
	ANSICyan  = "\033[1;36m"
	ANSIReset = util.ANSIReset
)

var (
	DirFlag   = flag.String("dir", "", "input file dir")
	AfterFlag = flag.String("after", "", "after date")
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
				util.ParseJson(buf, &cache)
			}
			if cache == nil {
				cache = map[string]string{}
			}
		}
	}

	now := time.Now()
	pool := util.NewAsyncPool(500, 10)
	ocrFutures := util.NewAwaitFutures[string](pool)

	for _, f := range files {
		if strings.HasPrefix(f.Name(), ".") {
			continue
		}
		inf, err := f.Info()
		if err != nil {
			panic(fmt.Errorf("failed to read file info: %v, %v", f.Name(), err))
		}

		if inf.ModTime().Before(now.Add(-time.Hour * 24 * 14)) { // 14 days ago
			continue
		}

		fpath := path.Join(*DirFlag, f.Name())
		cacheKey := fpath + "_" + inf.ModTime().String()

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

	var aft *time.Time = nil
	if *AfterFlag != "" {
		v, err := ParseTime(*AfterFlag)
		if err != nil {
			panic(err)
		}
		aft = &v
	}

	// 打卡时间: 2024-06-06 09:11:46
	// 开始时间: 2024年06月12日 下午
	dateMap := map[string][]time.Time{}
	attPat := regexp.MustCompile(`.*打卡时间: *(\d{4}-\d{2}-\d{2} *\d{2}:?\d{2}:?\d{2}).*`)
	leavePat := regexp.MustCompile(`.*(开始|结束)时间: *(\d{4}年\d{2}月\d{2}日) *(上午|下午).*`)

	for _, s := range fileContent {
		lines := strings.Split(s, "\n")

		for _, l := range lines {
			l = strings.TrimSpace(l)
			if l == "" {
				continue
			}

			// leave from work
			var ds string
			res := attPat.FindStringSubmatch(l)
			if len(res) < 1 {
				if strings.Contains(l, "打卡时间") {
					fmt.Printf("line invalid: %s\n", l)
				}

				res = leavePat.FindStringSubmatch(l)
				if len(res) < 4 {
					if strings.Contains(l, "开始时间") || strings.Contains(l, "结束时间") {
						fmt.Printf("line invalid: %s\n", l)
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
				duplicate := false
				for _, v := range prev {
					if v.Equal(parsedTime) {
						duplicate = true
						break
					}
				}
				if !duplicate {
					dateMap[date] = append(prev, parsedTime)
				}
			} else {
				dateMap[date] = []time.Time{parsedTime}
			}
		}
	}
	// fmt.Printf("dataMap: %+v\n", dateMap)
	trs := make([]TimeRange, 0, len(dateMap)/2)
	for k, v := range dateMap {
		var st time.Time
		var ed time.Time
		var estimated bool = false
		if len(v) < 2 {
			st = v[0]
			if FormatDate(st) != FormatDate(now) {
				fmt.Printf("Date missing attendence record, skipped: %+v\n", v)
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
			fmt.Printf("\n%s subtotal: %s (for %d days, %d hours), diff: %s%s%s\n", currMonth, HourMin(subtotal), currMonthCnt, currMonthCnt*8,
				start, HourMin(diff), ANSIReset)
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

		if tr.guessed {
			fmt.Printf("%v (%v)  %v - \033[1;36m%v\x1b[0m  %-10s %s%s%s     ---     \033[1;36mEstimated\x1b[0m\n", FormatDate(tr.start),
				FormatWkDay(tr.start), FormatHms(tr.start), FormatHms(tr.end), HourMin(h), start, HourMin(diffh), ANSIReset)
		} else {
			fmt.Printf("%v (%v)  %v - %v  %-10s %s%s%s\n", FormatDate(tr.start), FormatWkDay(tr.start), FormatHms(tr.start), FormatHms(tr.end),
				HourMin(h), start, HourMin(diffh), ANSIReset)
		}

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
		util.Printlnf("\n%s subtotal: %s (for %d days, %d hours), diff: %s%s%s", currMonth, HourMin(subtotal), currMonthCnt, currMonthCnt*8, start, HourMin(diff), ANSIReset)
	}

	// total
	{
		diff := total - float64(len(trs)*8)
		start := ANSIGreen + "+"
		if diff < 0 && diff <= -1/precision { // e.g., -0.00001, is still 0
			start = ANSIRed
		}
		util.Printlnf("\ntotal: %.2fh (for %d days, %d hours), diff: %s%s%s", total, len(trs), len(trs)*8, start, HourMin(diff), ANSIReset)
		fmt.Println()
	}

	cf, err := util.ReadWriteFile(cacheFile)
	if err == nil {
		defer cf.Close()
		buf, err := util.WriteJson(cache)
		if err == nil {
			_, err = cf.Write(buf)
			if err != nil {
				fmt.Printf("failed to flush cache, %v\n", err)
			}
		}
	}
}
