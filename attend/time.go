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
	t, err := util.FuzzParseTime([]string{
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
	}, s)
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
	date    string
	start   time.Time
	end     time.Time
	guessed bool
}

func (t *TimeRange) Dur() time.Duration {
	lstart, _ := ParseTime(t.date + " 18:30:00")
	lend, _ := ParseTime(t.date + " 19:00:00")

	if !t.end.Before(lend) {
		return lstart.Sub(t.start) + t.end.Sub(lend) - (90 * time.Minute)
	}

	if t.end.Before(lend) {
		return t.end.Sub(t.start) - (90 * time.Minute)
	}

	return t.end.Sub(t.start) - (90 * time.Minute)
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
