package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

const (
	RED   = "\033[31m"
	RESET = "\033[0m"
)

func main() {
	log.SetFlags(0) // remove timestamp in log
	if len(os.Args) < 2 {
		log.Fatal("Please specify root directory")
	}
	if len(os.Args) < 3 {
		log.Fatal("Please specify branch name")
	}

	root := os.Args[1]
	target := os.Args[2]
	entries, err := os.ReadDir(root)
	if err != nil {
		log.Fatalf("Failed to list entries under root directory, %v", err)
	}

	var results string
	for _, e := range entries {
		dir := root 
		if !strings.HasSuffix(dir, "/") {
			dir += "/"
		}
		dir += e.Name()
		listedBranches, err := listBranch(dir)
		if err != nil {
			// log.Printf("Failed to listBranch, dir: %v, %v", dir, err)
			continue
		}
		
		for _, v := range listedBranches {
			if strings.Contains(v, target) {
				results += fmt.Sprintf("%-70v %v%v%v\n", dir, RED, v, RESET)
				break
			}
		}
	}

	log.Print(results)
}

// list branches of repository
func listBranch(repo string) ([]string, error) {
	var cmdout []byte
	var err error
	cmd := exec.Command("git", "-C", repo, "branch")
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		return nil, fmt.Errorf(RED+"Not a git repository, %v"+RESET, err)
	}

	outstr := string(cmdout)
	branches := strings.Split(outstr, "\n")
	for i, v := range branches {
		branches[i] = strings.TrimSpace(strings.Replace(v, "*", "", 1))
	}
	return branches, nil
}
