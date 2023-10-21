package main

import (
	"testing"

	"github.com/curtisnewbie/miso/miso"
)

func TestFetchRealImageHref(t *testing.T) {
	rail := miso.EmptyRail()
	realHref, err := FetchRealImageSrc(rail, "https://www.sex.com/pin/57364974-bj-1/")
	if err != nil {
		t.Log(err)
		t.FailNow()
	}
	rail.Infof("real: %v", realHref)
}
