package main

import (
	"bytes"
	"fmt"
	"image"
	"image/draw"
	_ "image/jpeg" // registers the jpeg decoder for image.Decode/DecodeConfig
	"image/png"
	"io"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"sync"

	"github.com/curtisnewbie/miso/util/cli"
)

const (
	ocrLang = "chi_sim+eng"

	// Tesseract refuses images higher than INT16_MAX (32767) and OCR-ing a
	// huge screenshot is slow since the OCR pipeline is single-threaded, so
	// long screenshots are split into tiles which are OCR'd concurrently.
	ocrTileHeight = 3000
	// tesseract rejects images higher than INT16_MAX (32767)
	ocrMaxTileHeight = 16000
	ocrTileOverlap   = 200 // avoids cutting a text line in half
)

var (
	ocrConcurrency = max(1, runtime.NumCPU())

	// limits the concurrent tesseract processes
	ocrProcSem = make(chan struct{}, ocrConcurrency)
	// limits the concurrent in-memory decoding of long screenshots, a decoded
	// screenshot takes ~4 bytes per pixel, e.g. 184 MB for a 46 MP one
	ocrDecodeSem = make(chan struct{}, max(2, ocrConcurrency/4))
)

// Ocr extracts the text of an image. A long screenshot is split into tiles
// which are OCR'd concurrently, because tesseract is single-threaded per image
// and refuses images higher than INT16_MAX (32767) px.
func Ocr(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	cfg, _, err := image.DecodeConfig(f)
	f.Close()

	// unknown format or not that long, let tesseract handle the file directly
	if err != nil || cfg.Height <= ocrTileHeight {
		return ocrFile(path)
	}

	tiles := ocrTiles(cfg.Height)
	bufs, err := encodeTiles(path, tiles)
	if err != nil {
		return "", err
	}

	outs := make([]string, len(tiles))
	errs := make([]error, len(tiles))
	var wg sync.WaitGroup
	for i := range tiles {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			outs[i], errs[i] = ocrStdin(bufs[i])
		}(i)
	}
	wg.Wait()

	sb := strings.Builder{}
	var err0 error
	for i := range tiles {
		if errs[i] != nil {
			err0 = fmt.Errorf("ocr tile %d-%d of %v failed: %w", tiles[i][0], tiles[i][1], path, errs[i])
			continue
		}
		sb.WriteString(outs[i])
		sb.WriteString("\n")
	}
	return sb.String(), err0
}

// encodeTiles decodes the image once and encodes its tiles into PNG buffers.
// The decoded image, which is much bigger than the encoded tiles, is dropped
// right after, so decoding doesn't hold back the concurrent OCR-ing.
func encodeTiles(path string, tiles [][2]int) ([]*bytes.Buffer, error) {
	ocrDecodeSem <- struct{}{}
	defer func() { <-ocrDecodeSem }()

	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	img, _, err := image.Decode(f)
	if err != nil {
		return nil, err
	}

	bufs := make([]*bytes.Buffer, len(tiles))
	errs := make([]error, len(tiles))
	var wg sync.WaitGroup
	for i, t := range tiles {
		wg.Add(1)
		go func(i, top, bottom int) {
			defer wg.Done()
			bufs[i], errs[i] = encodeTile(img, top, bottom)
		}(i, t[0], t[1])
	}
	wg.Wait()

	for _, err := range errs {
		if err != nil {
			return nil, err
		}
	}
	return bufs, nil
}

func encodeTile(img image.Image, top, bottom int) (*bytes.Buffer, error) {
	b := img.Bounds()
	sub := image.NewRGBA(image.Rect(0, 0, b.Dx(), bottom-top))
	draw.Draw(sub, sub.Bounds(), img, image.Pt(b.Min.X, b.Min.Y+top), draw.Src)

	var buf bytes.Buffer
	// BestSpeed keeps the lossless re-encoding cheap, the size doesn't matter
	// since the tile is only fed to tesseract
	enc := png.Encoder{CompressionLevel: png.BestSpeed}
	if err := enc.Encode(&buf, sub); err != nil {
		return nil, err
	}
	return &buf, nil
}

func ocrTiles(height int) [][2]int {
	// OCR time is linear in pixels, so a very long screenshot is evenly split
	// into NumCPU tiles to keep all the cores busy without extra waves
	h := ocrTileHeight
	if n := ocrConcurrency; height > n*h {
		h = min((height+n-1)/n, ocrMaxTileHeight)
	}

	tiles := make([][2]int, 0, height/h+1)
	for top := 0; top < height; {
		bottom := min(top+h, height)
		tiles = append(tiles, [2]int{top, bottom})
		if bottom == height {
			break
		}
		top = bottom - ocrTileOverlap
	}
	return tiles
}

func ocrStdin(r io.Reader) (string, error) {
	return runOcr([]string{"stdin", "-"}, func(c *exec.Cmd) {
		c.Stdin = r
	})
}

func ocrFile(path string) (string, error) {
	return runOcr([]string{path, "-"}, nil)
}

func runOcr(args []string, opt func(*exec.Cmd)) (string, error) {
	ocrProcSem <- struct{}{}
	defer func() { <-ocrProcSem }()

	full := append(args, "-l", ocrLang, "--psm", "3")
	b, err := cli.Run(nil, "tesseract", full, func(c *exec.Cmd) {
		c.Env = append(c.Env, "OMP_THREAD_LIMIT=1")
		if opt != nil {
			opt(c)
		}
	})
	return string(b), err
}
