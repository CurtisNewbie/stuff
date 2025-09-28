package main

import (
	"os/exec"

	"github.com/curtisnewbie/miso/util/cli"
)

func Ocr(path string) (string, error) {
	b, err := cli.Run(nil, "tesseract", []string{path, "-", "-l", "chi_sim+eng", "--psm", "3", "quiet"}, func(c *exec.Cmd) {
		c.Env = append(c.Env, "OMP_THREAD_LIMIT=1")
	})
	return string(b), err
}
