package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"sync"
)

const (
	RED   = "\033[31m"
	RESET = "\033[0m"
)

type ListBranchRes struct {
	Repo     string
	Branches []string
	Err      error
}

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

	aggChan := make(chan ListBranchRes, len(entries))
	var wg sync.WaitGroup

	// list branches of each repositories in parallel
	for _, e := range entries {
		dir := root
		if !strings.HasSuffix(dir, "/") {
			dir += "/"
		}
		dir += e.Name()

		wg.Add(1)
		go func() {
			defer wg.Done()
			listBranch(dir, aggChan)
		}()
	}
	wg.Wait()
	close(aggChan)

	// aggregate results
	var results string
	for r := range aggChan {
		if r.Err != nil {
			continue
		}

		for _, v := range r.Branches {
			if strings.Contains(v, target) {
				results += fmt.Sprintf("%-70v %v%v%v\n", r.Repo, RED, v, RESET)
				break
			}
		}
	}
	log.Print(results)
}

// list branches of repository
func listBranch(repo string, receiver chan ListBranchRes) {
	var cmdout []byte
	var err error
	cmd := exec.Command("git", "-C", repo, "branch")
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		receiver <- ListBranchRes{
			Repo:     repo,
			Branches: nil,
			Err:      fmt.Errorf(RED+"Not a git repository, %v"+RESET, err),
		}
		return
	}

	outstr := string(cmdout)
	branches := strings.Split(outstr, "\n")
	for i, v := range branches {
		branches[i] = strings.TrimSpace(strings.Replace(v, "*", "", 1))
	}

	receiver <- ListBranchRes{
		Repo:     repo,
		Branches: branches,
		Err:      nil,
	}
}
