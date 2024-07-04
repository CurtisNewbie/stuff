package main

import (
	"fmt"
	"math"
	"strings"
	"time"

	"github.com/curtisnewbie/miso/util"
)

func ParseTime(s string) (time.Time, error) {
	s = strings.TrimSpace(s)
	t, err := util.FuzzParseTimeLoc([]string{
		"2006-01-0215:04:05",
		"2006-01-02 15:04:05",
		"2006-01-02 15:0405",
		"2006-01-02 1504:05",
		"2006-01-02 150405",
		"2006-01-0215:04:05",
		"2006-01-0215:0405",
		"2006-01-021504:05",
		"2006-01-02150405",
		"2006-01-02",
		"2006年01月02日 15:04:05",
	}, s, time.Local)
	if err == nil {
		return time.ParseInLocation("2006-01-02 15:04", t.Format("2006-01-02 15:04"), time.Local)
	}
	return t, err
}

func FormatTime(t time.Time) string {
	return t.Format("2006-01-02 15:04:05")
}

func FormatMoth(t time.Time) string {
	return t.Format("2006/01")
}

func FormatDate(t time.Time) string {
	return t.Format("2006-01-02")
}

func FormatWkDay(t time.Time) string {
	return t.Format("Mon")
}

func FormatHms(t time.Time) string {
	return t.Format("15:04:05")
}

type TimeRange struct {
	Leave   bool
	date    string
	start   time.Time
	end     time.Time
	guessed bool
}

func (t *TimeRange) Dur() time.Duration {
	nstart0, _ := ParseTime(t.date + " 12:00:00")
	nstart1, _ := ParseTime(t.date + " 13:30:00")
	lstart, _ := ParseTime(t.date + " 18:30:00")
	lend, _ := ParseTime(t.date + " 19:00:00")

	var d time.Duration
	if t.end.Before(nstart0) {
		d = t.end.Sub(t.start)
	} else if t.end.Before(nstart1) {
		d = nstart0.Sub(t.start)
	} else if !t.end.Before(lend) {
		d = lstart.Sub(t.start) + t.end.Sub(lend) - (90 * time.Minute)
	} else if t.end.Before(lend) {
		d = t.end.Sub(t.start) - (90 * time.Minute)
	} else {
		d = t.end.Sub(t.start) - (90 * time.Minute)
	}

	// util.Printlnf("start: %v, end: %v, d: %v", t.start, t.end, d)
	if t.Leave {
		d = d + (time.Hour * 4)
	}
	return d
}

func NewTimeRange(date string, start time.Time, end time.Time, guessed bool) TimeRange {
	tr := TimeRange{}
	tr.date = date
	tr.start = start
	tr.end = end
	tr.guessed = guessed
	return tr
}

func HourMin(h float64) string {
	sb := strings.Builder{}
	if h < 0 {
		sb.WriteRune('-')
	}
	h = math.Abs(h)
	hr := h - float64(int(h))
	hrf := float64(int(hr*precision)) / precision
	m := hrf * 60

	ih := int(h)
	if ih > 0 {
		sb.WriteString(fmt.Sprintf("%dh", ih))
	}
	if m > 0.1 {
		if sb.Len() > 1 {
			sb.WriteRune(' ')
		}
		sb.WriteString(fmt.Sprintf("%.1fm", m))
	}
	return sb.String()
}
