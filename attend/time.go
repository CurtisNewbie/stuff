package main

import (
	"strings"
	"time"

	"github.com/curtisnewbie/miso/miso"
)

func ParseTime(s string) (time.Time, error) {
	s = strings.TrimSpace(s)
	return miso.FuzzParseTime([]string{
		"2006-01-02 15:04:05",
		"2006-01-02 150405",
	}, s)
}

func FormatTime(t time.Time) string {
	return t.Format("2006-01-02 15:04:05")
}

func FormatDate(t time.Time) string {
	return t.Format("2006-01-02")
}

type TimeRange struct {
	date  string
	start time.Time
	end   time.Time
}

func (t *TimeRange) Dur() time.Duration {
	lstart, _ := ParseTime(t.date + " 18:30:00")
	lend, _ := ParseTime(t.date + " 19:00:00")

	if t.end.After(lend) {
		return lstart.Sub(t.start) + t.end.Sub(lend) - (90 * time.Minute)
	}

	if t.end.Before(lend) {
		return lstart.Sub(t.start) - (90 * time.Minute)

	}

	return t.end.Sub(t.start) - (90 * time.Minute)
}

func NewTimeRange(date string, start time.Time, end time.Time) TimeRange {
	tr := TimeRange{}
	tr.date = date
	tr.start = start
	tr.end = end
	return tr
}
