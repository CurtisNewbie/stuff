package main

import (
	"log"
	"os"
	"os/exec"
	"strings"
)

var (
	red   = "\033[31m"
	reset = "\033[0m"
	green = "\033[31m"
	cyan  = "\033[36m"
)

func main() {
	log.SetFlags(0) // remove timestamp in log

	cmd := exec.Command("git", "status")
	var cmdout []byte
	var err error
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		log.Printf("%sNot a git repository, %v%s", red, err, reset)
		return
	}
	outstr := string(cmdout)
	// log.Printf("\n%s", outstr)

	lines := strings.Split(outstr, "\n")
	if len(lines) < 1 {
		log.Printf("%sNot a git repository%s", red, reset)
		return
	}

	l := strings.Index(lines[0], "On branch")
	branch := ""
	if l > -1 {
		branch = string([]rune(lines[0])[l+10:])
	}

	reqfile := os.Getenv("REQUIREMENTS_FILE")
	cmd = exec.Command("grep", "-h", "-i", branch, reqfile)
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		log.Printf("%sRequirement not found%s", red, reset)
		return
	}
	log.Print("\n" + string(cmdout) + "\n")
}
