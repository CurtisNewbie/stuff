package main

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/curtisnewbie/miso/util"
)

var (
	repos = []string{}
)

const (
	color = "\033[1;32m"
	reset = "\033[0m"
)

func main() {
	root, ok := os.LookupEnv("GIT_PATH")
	if !ok {
		util.Printlnf("missing GIT_PATH environment")
		return
	}

	envRepos, ok := os.LookupEnv("SYNC_REPOS")
	if ok {
		repos = append(repos, strings.Split(envRepos, ",")...)
	}
	util.Printlnf("Syncing repos: %+v", repos)

	pool := util.NewAsyncPool(len(repos), len(repos))
	aw := util.NewAwaitFutures[string](pool)

	for i := range repos {
		r := repos[i]
		aw.SubmitAsync(func() (string, error) { return SyncRepo(root, r, 0), nil })
	}
	fut := aw.Await()

	for _, f := range fut {
		s, _ := f.Get()
		util.Printlnf("\n" + s)
	}
}

func SyncRepo(root string, repo string, retry int) string {
	start := time.Now()
	main := "main"
	if repo == "stuff" {
		main = "master"
	}
	cmd := fmt.Sprintf("cd %s/%s && git switch %s && git fetch && git merge", root, repo, main)
	out, err := util.CliRun("bash", "-c", cmd)
	took := time.Since(start)
	outs := util.UnsafeByt2Str(out)
	var result string
	if err != nil {
		if retry < 3 {
			return SyncRepo(root, repo, retry+1)
		}
		if outs != "" {
			result = fmt.Sprintf("Sync %s%s%s failed, took %s, %v, %v, retry: %v", color, repo, reset, took, outs, err, retry)
		} else {
			result = fmt.Sprintf("Sync %s%s%s failed, took %s, %v: retry: %v", color, repo, reset, took, err, retry)
		}
	} else {
		if outs != "" {
			result = fmt.Sprintf("Sync %s%s%s succeeded, took %s, %v", color, repo, reset, took, outs)
		} else {
			result = fmt.Sprintf("Sync %s%s%s succeeded, took %s", color, repo, reset, took)
		}
	}
	return result
}
