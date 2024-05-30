package main

import (
	"flag"
	"fmt"
	"os"
	"strings"
	"time"
)

const (
	precision = 100000
)

var (
	FileFlag = flag.String("file", "", "input file path")
)

type TimeRange struct {
	date   string
	start  time.Time
	starts string
	end    time.Time
	ends   string
}

func (t *TimeRange) _withEnd(s string) error {
	tt, err := t._parseTime(s)
	if err != nil {
		return err
	}
	t.end = tt
	t.ends = s
	return nil
}

func (t *TimeRange) _withStart(s string) error {
	tt, err := t._parseTime(s)
	if err != nil {
		return err
	}
	t.start = tt
	t.starts = s
	return nil
}

func (t *TimeRange) _parseTime(s string) (time.Time, error) {
	return time.Parse("2006-01-02 15:04", fmt.Sprintf("%s %s", t.date, s))
}

func (t *TimeRange) Dur() time.Duration {
	lstart, _ := t._parseTime("18:30")
	lend, _ := t._parseTime("19:00")

	if t.end.After(lend) {
		return lstart.Sub(t.start) + t.end.Sub(lend) - (90 * time.Minute)
	}

	if t.end.Before(lend) {
		return lstart.Sub(t.start) - (90 * time.Minute)

	}

	return t.end.Sub(t.start) - (90 * time.Minute)

}

func NewTimeRange(date string, start string, end string) (TimeRange, error) {
	tr := TimeRange{}
	tr.date = date
	if err := tr._withStart(start); err != nil {
		return tr, err
	}
	if err := tr._withEnd(end); err != nil {
		return tr, err
	}
	return tr, nil
}

func main() {
	flag.Parse()

	if *FileFlag == "" {
		flag.PrintDefaults()
		return
	}

	fmt.Println()
	buf, err := os.ReadFile(*FileFlag)
	if err != nil {
		panic(err)
	}

	s := string(buf)
	lines := strings.Split(s, "\n")

	date := "2024-01-01" // doesn't matter

	// 00:00 - 00:00
	trs := make([]TimeRange, 0, 5)
	for _, l := range lines {
		l = strings.TrimSpace(l)
		if l == "" {
			continue
		}
		tkn := strings.Split(l, " ")
		if len(tkn) < 3 {
			fmt.Printf("Error - Illegal format: %s\n", l)
			continue
		}
		tr, err := NewTimeRange(date, tkn[0], tkn[2])
		if err != nil {
			panic(err)
		}
		trs = append(trs, tr)
	}

	total := float64(0)
	for _, tr := range trs {
		h := float64(int(float64(tr.Dur())/float64(time.Hour)*precision)) / precision
		fmt.Printf("%v - %v: %.2fh (diff %.2fm)\n", tr.starts, tr.ends, h, float64(h*60)-float64(8*60))
		total += h
	}

	remain := 40 - total
	if remain < 0 {
		remain = 0
	}

	if len(trs) < 5 {
		wdh := float64((5 - len(trs)) * 8)
		extPerDay := remain - wdh
		if extPerDay < 0 {
			extPerDay = 0
		}
		fmt.Printf("\ntotal: %.2fh, need: %.2fh (%.1fm) (extra %.2fh per day)\n", total, remain, remain*60, extPerDay)
	} else {
		fmt.Printf("\ntotal: %.2fh, need: %.2fh (%.1fm)\n", total, remain, remain*60)
	}
	fmt.Println()
}
