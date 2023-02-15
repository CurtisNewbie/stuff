package main

import (
	"log"
	"os"
	"os/exec"
	"strings"
)

func main() {
	cmd := exec.Command("git", "status")
	var cmdout []byte
	var err error
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		log.Printf("Not a git repository, %v", err)
		return
	}
	outstr := string(cmdout)
	// log.Printf("\n%s", outstr)

	lines := strings.Split(outstr, "\n")
	if len(lines) < 1 {
		log.Print("Not a git repository")
		return
	}

	l := strings.Index(lines[0], "On branch")
	branch := ""
	if l > -1 {
		branch = string([]rune(lines[0])[l+10:])
	}

	reqfile := os.Getenv("REQUIREMENTS_FILE")
	cmd = exec.Command("grep", "--color", "-h", "-i", branch, reqfile)
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		log.Printf("Requirement not found, err: %v", err)
		return
	}
	log.Printf("\n%s", string(cmdout))
}
