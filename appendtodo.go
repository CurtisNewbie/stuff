package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"strings"
	"time"
)

const BASE = "/Users/photon/dev/notes/todo"

func main() {
	log.SetFlags(0) // remove timestamp in log
	args := os.Args
	if len(args) < 1 {
		log.Print("Nothing to append")
		return
	}

	appended := strings.Join(args[1:], " ")
	today := time.Now().Format("20060102")
	dirpath := fmt.Sprintf("%s/%s", BASE, today)

	_, err := os.Stat(dirpath)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			if err = os.Mkdir(dirpath, os.ModePerm); err != nil {
				log.Fatalf("Failed to create directory, %v", err)
			}
		} else {
			log.Fatalf("Failed to open directory, %v", err)
		}
	}

	fpath := fmt.Sprintf("%s/%s.md", dirpath, today)
	log.Printf("Opening file '%s'", fpath)
	_, err = os.Stat(fpath)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			f, err := os.Create(fpath)
			defer f.Close()

			if err != nil {
				log.Fatalf("Failed to create file, %v", err)
			}

			content := fmt.Sprintf("# TODO %s\n\n - %s", today, appended)
			log.Printf("Writing content: '%s'", content)
			_, err = f.WriteString(content)
			if err != nil {
				log.Fatalf("Failed to write content, %v", err)
			}
			return
		} else {
			log.Fatalf("Failed to open file, %v", err)
		}
	}

	f, err := os.OpenFile(fpath, os.O_APPEND|os.O_WRONLY, os.ModeAppend)
	defer f.Close()
	if err != nil {
		log.Fatalf("Failed to open file, %v", err)
	}
	content := fmt.Sprintf("- %s", appended)
	log.Printf("Writing content: '%s'", content)
	_, err = f.WriteString(content)
	if err != nil {
		log.Fatalf("Failed to write content, %v", err)
	}
}
