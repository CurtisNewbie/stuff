package main

import (
	"os/exec"
)

func OcrPhone(path string) (string, error) {
	c := exec.Command("tesseract", path, "-", "-l", "chi_sim+eng", "--psm", "3", "quiet")
	b, err := c.CombinedOutput()
	if err != nil {
		return "", err
	}
	return string(b), nil
}
