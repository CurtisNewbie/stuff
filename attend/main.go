package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path"
	"regexp"
	"sort"
	"strings"
	"time"

	"github.com/curtisnewbie/miso/miso"
)

const (
	precision = 100000

	ANSIRed   = "\033[1;31m"
	ANSIGreen = "\033[1;32m"
	ANSICyan  = "\033[1;36m"
	ANSIReset = "\033[0m"
)

var (
	DirFlag   = flag.String("dir", "", "input file dir")
	AfterFlag = flag.String("after", "", "after date")
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

	now := time.Now()
	pool := miso.NewAsyncPool(500, 10)
	ocrFutures := miso.NewAwaitFutures[string](pool)
	for _, f := range files {
		inf, err := f.Info()
		if err != nil {
			panic(fmt.Errorf("failed to read file info: %v, %v", f.Name(), err))
		}

		if inf.ModTime().Before(now.Add(-time.Hour * 24 * 14)) { // 14 days ago
			continue
		}

		fpath := path.Join(*DirFlag, f.Name())
		ocrFutures.SubmitAsync(func() (string, error) {
			return Ocr(fpath)
		})
	}

	fileContent := make([]string, 0, len(files))
	futures := ocrFutures.Await()
	for _, fu := range futures {
		s, err := fu.Get()
		if err != nil {
			panic(err)
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
	dateMap := map[string][]time.Time{}
	pat := regexp.MustCompile(`.*打卡时间: *(\d{4}-\d{2}-\d{2} *\d{2}:?\d{2}:?\d{2}).*`)

	for _, s := range fileContent {
		lines := strings.Split(s, "\n")

		for _, l := range lines {
			l = strings.TrimSpace(l)
			if l == "" {
				continue
			}

			res := pat.FindStringSubmatch(l)
			if len(res) < 1 {
				if strings.Contains(l, "打卡时间") {
					fmt.Printf("line invalid: %s\n", l)
				}
				continue
			}

			ds := strings.TrimSpace(res[1])
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
		if len(v) < 2 {
			fmt.Printf("Date missing attendence record, skipped: %+v\n", v)
			continue
		}
		var st time.Time = v[0]
		var ed time.Time = v[1]
		if st.After(ed) {
			st, ed = ed, st
		}
		tr := NewTimeRange(k, st, ed)
		trs = append(trs, tr)
	}
	sort.Slice(trs, func(i, j int) bool { return trs[i].start.Before(trs[j].start) })
	fmt.Println()

	total := float64(0)
	for _, tr := range trs {
		h := float64(int(float64(tr.Dur())/float64(time.Hour)*precision)) / precision
		diff := float64(h*60) - float64(8*60)
		start := ANSIGreen
		if diff-0 <= 0.000001 {
			start = ANSIRed
		}
		fmt.Printf("%v - %v  %.2fh  %s%.2fm%s\n", FormatTime(tr.start), FormatTime(tr.end), h, start, diff, ANSIReset)
		total += h
	}

	remain := float64(len(trs)*8) - total
	if remain < 0 {
		remain = 0
	}

	fmt.Printf("\ntotal: %.2fh (for %d days), need: %.2fh (%.1fm)\n", total, len(trs), remain, remain*60)
	fmt.Println()
}
