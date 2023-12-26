package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"regexp"
	"strings"
)

const (
	red   = "\033[1;31m"
	reset = "\033[1;0m"
	green = "\033[1;32m"
	cyan  = "\033[1;36m"
)

type Requirement struct {
	Name     string
	Docs     []string
	Repos    []string
	Branches []string
	Todos    []string

	InDoc      bool
	InRepos    bool
	InTodos    bool
	InBranches bool
}

func (r *Requirement) ResetFlags() {
	r.InRepos = false
	r.InDoc = false
	r.InBranches = false
	r.InTodos = false
}

func (r Requirement) String() string {
	s := ""
	s += fmt.Sprintf("%v%v%v\n", green, r.Name, reset)
	if len(r.Docs) > 0 {
		s += fmt.Sprintf(" Docs: \n    %+v\n", strings.Join(r.Docs, "\n    "))
	}
	if len(r.Repos) > 0 {
		s += fmt.Sprintf(" Repos: \n    %v%+v%v\n", cyan, strings.Join(r.Repos, "\n    "), reset)
	}
	if len(r.Branches) > 0 {
		s += fmt.Sprintf(" Branches: \n    %v%+v%v\n", cyan, strings.Join(r.Branches, "\n    "), reset)
	}
	if len(r.Todos) > 0 {
		s += fmt.Sprintf(" Todos: \n    %+v\n", strings.Join(r.Todos, "\n    "))
	}
	// s += fmt.Sprintf(" Flags: InDoc:%v, InRepos: %v, InTodos: %v, InBranches: %v\n", r.InDoc, r.InRepos, r.InTodos, r.InBranches)
	return s
}

func main() {

	cmd := exec.Command("git", "status")
	var cmdout []byte
	var err error
	if cmdout, err = cmd.CombinedOutput(); err != nil {
		fmt.Printf("%sNot a git repository, %v%s", red, err, reset)
		return
	}
	outstr := string(cmdout)

	lines := strings.Split(outstr, "\n")
	if len(lines) < 1 {
		fmt.Printf("%sNot a git repository%s", red, reset)
		return
	}

	l := strings.Index(lines[0], "On branch")
	branch := ""
	if l > -1 {
		branch = string([]rune(lines[0])[l+10:])
	}
	fmt.Printf("On Branch %v%v%v\n", red, branch, reset)

	cwd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	cwdr := []rune(cwd)
	for i := len(cwdr) - 1; i >= 0; i-- {
		if cwdr[i] == '/' {
			cwd = string(cwdr[i+1:])
			break
		}
	}
	fmt.Printf("Current Repo: %v%s%v\n\n", red, cwd, reset)

	reqFileName := os.Getenv("REQUIREMENTS_FILE")
	reqFile, err := os.Open(reqFileName)
	if err != nil {
		panic(err)
	}

	byt, err := io.ReadAll(reqFile)
	if err != nil {
		panic(err)
	}

	content := string(byt)

	splited := strings.Split(content, "\n")
	if len(splited) < 1 {
		fmt.Printf("%sRequirement not found%s", red, reset)
	}

	requirements := []Requirement{}

	titleRegex := regexp.MustCompile(`^- \[[\* Xx]*\] *(.*)`)
	docRegex := regexp.MustCompile(`^ {2}- (文档|需求):\s*`)
	reposRegex := regexp.MustCompile(`^ {2}- (服务|代码仓库|服务列表|服务):\s*`)
	branchRegex := regexp.MustCompile(`^ {2}- 分支:\s*`)
	todoRegex := regexp.MustCompile(`^ {2}- 待办:\s*`)
	bulletRegex := regexp.MustCompile(`^ {4}- *(.*)`)

	start := 0
	for i, l := range splited {
		if strings.TrimSpace(l) == "## Active Requirements" {
			start = i
			break
		}
	}

	for i := start; i < len(splited); i++ {
		l := splited[i]

		if strings.HasPrefix(l, "#") || strings.HasPrefix(l, "```") || strings.TrimSpace(l) == "" {
			continue
		}

		if matched := titleRegex.FindStringSubmatch(l); len(matched) > 0 {
			curr := Requirement{}
			curr.Docs = []string{}
			curr.Repos = []string{}
			curr.Branches = []string{}
			curr.Todos = []string{}
			curr.Name = matched[1]
			requirements = append(requirements, curr)
		} else {
			if len(requirements) < 1 {
				panic(fmt.Errorf("illegal format, line: %v", l))
			}
			curr := requirements[len(requirements)-1]

			if matched := docRegex.FindStringSubmatch(l); len(matched) > 0 {
				curr.ResetFlags()
				curr.InDoc = true
			} else if matched := reposRegex.FindStringSubmatch(l); len(matched) > 0 {
				curr.ResetFlags()
				curr.InRepos = true
			} else if matched := todoRegex.FindStringSubmatch(l); len(matched) > 0 {
				curr.ResetFlags()
				curr.InTodos = true
			} else if matched := branchRegex.FindStringSubmatch(l); len(matched) > 0 {
				curr.ResetFlags()
				curr.InBranches = true
			} else if matched := bulletRegex.FindStringSubmatch(l); len(matched) > 0 {
				if curr.InDoc {
					curr.Docs = append(curr.Docs, matched[1])
				} else if curr.InRepos {
					curr.Repos = append(curr.Repos, matched[1])
				} else if curr.InTodos {
					curr.Todos = append(curr.Todos, matched[1])
				} else if curr.InBranches {
					curr.Branches = append(curr.Branches, matched[1])
				}
			}
			requirements[len(requirements)-1] = curr
		}
	}

	mr := []Requirement{}

	for _, req := range requirements {
		matched := false
		for _, v := range req.Branches {
			if strings.Contains(v, branch) {
				mr = append(mr, req)
				matched = true
				break
			}
		}
		if matched {
			break
		}
		for _, v := range req.Repos {
			if strings.Contains(v, cwd) {
				mr = append(mr, req)
				matched = true
				break
			}
		}
	}

	for _, req := range mr {
		fmt.Printf("%v\n", req)
	}
}
