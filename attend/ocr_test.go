package main

import (
	"testing"
)

func TestOcrPhone(t *testing.T) {
	s, err := Ocr("testdata/out.png")
	if err != nil {
		t.Fatal(err)
	}
	t.Log(s)
}
