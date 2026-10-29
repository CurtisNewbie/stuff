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

func TestOcrTiles(t *testing.T) {
	for _, h := range []int{1, 3000, 3001, 5914, 17662, 33598, 200000} {
		tiles := ocrTiles(h)
		if tiles[0][0] != 0 {
			t.Fatalf("height %v: first tile starts at %v", h, tiles[0][0])
		}
		if last := tiles[len(tiles)-1]; last[1] != h {
			t.Fatalf("height %v: last tile ends at %v", h, last[1])
		}
		for i, tile := range tiles {
			if top, bottom := tile[0], tile[1]; bottom <= top || bottom-top > ocrMaxTileHeight {
				t.Fatalf("height %v: invalid tile %v-%v", h, top, bottom)
			}
			if i > 0 {
				prev := tiles[i-1]
				if tile[0] > prev[1] {
					t.Fatalf("height %v: gap between %v and %v", h, prev, tile)
				}
				if overlap := prev[1] - tile[0]; overlap != ocrTileOverlap {
					t.Fatalf("height %v: unexpected overlap %v between %v and %v", h, overlap, prev, tile)
				}
			}
		}
		t.Logf("height %v: %v tiles", h, len(tiles))
	}
}
