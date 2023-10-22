package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/curtisnewbie/miso/miso"
	"golang.org/x/net/html"
)

const (
	TagDiv = "div"
	TagA   = "a"
	TagImg = "img"

	AttrHref    = "href"
	AttrSrc     = "src"
	AttrDataSrc = "data-src"
	AttrAlt     = "alt"
	AttrClass   = "class"

	ImageWrapperClass  = "image_wrapper"
	ImageClass         = "image"
	ActivityImageClass = "activity_image"
	ImageFrameClass    = "image_frame"

	BaseUrl = "https://www.sex.com"
)

var (
	Username = flag.String("username", "", "username")
	Dir      = flag.String("dir", "", "output directory")
	Start    = flag.Int("start", 1, "start page")
	End      = flag.Int("end", 1, "end page")
	client   *http.Client
)

func init() {
	client = &http.Client{Timeout: 60 * time.Second}
}

func main() {
	flag.Parse()
	rail := miso.EmptyRail()

	if Username == nil || *Username == "" {
		rail.Errorf("Require -username")
		return
	}
	if Dir == nil || *Dir == "" {
		rail.Errorf("Require -dir")
		return
	}

	if err := os.MkdirAll(*Dir, os.ModePerm); err != nil {
		panic(err)
	}

	// rail.SetLogLevel("debug")

	for i := *Start; i <= *End; i++ {
		rail.Infof("Start Page: %v", i)

		likes, err := FetchLikes(rail, i, *Username)
		if err != nil {
			panic(err)
		}

		for j := range likes.Images {
			img := likes.Images[j]

			file := img.OutputPath(*Dir)
			ok, err := miso.FileExists(file)
			if err != nil {
				panic(err)
			}
			if ok {
				rail.Infof("Already downloaded %v", file)
				continue
			}

			realHref, err := FetchRealImageSrc(rail, img.WrapperHref)
			if err != nil {
				panic(err)
			}
			img.RealHref = realHref

			rail.Debugf("Alt: %v, Name: %v, Src: %v, WrapperHref: %v, realHref: %v", img.Alt, img.Name, img.DataSrc, img.WrapperHref, realHref)
			rail.Infof("Page %v - [%v/%v] Name: %v, href: %v", i, j, len(likes.Images), img.Name, realHref)

			err = DownloadImage(rail, img, *Dir)
			if err != nil {
				panic(err)
			}
			time.Sleep(500 * time.Millisecond)
		}
		rail.Infof("End Page: %v", i)
	}
}

type Image struct {
	Name        string
	DataSrc     string
	Alt         string
	WrapperHref string
	RealHref    string
}

func (i Image) OutputPath(dir string) string {
	return dir + "/" + i.Name
}

type FetchLikesRes struct {
	Images []Image
	Next   bool
}

func FetchLikes(rail miso.Rail, page int, username string) (FetchLikesRes, error) {
	doc, err := miso.NewTClient(rail, fmt.Sprintf("%s/user/%s/likes", BaseUrl, username), client).
		AddHeader("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36").
		AddQueryParams("page", fmt.Sprintf("%v", page)).
		Get().
		Str()
	if err != nil {
		return FetchLikesRes{}, err
	}

	res := FetchLikesRes{
		Images: make([]Image, 0, 30),
		Next:   false,
	}

	wrapperHref := ""
	z := html.NewTokenizer(strings.NewReader(doc))
	for {
		ttype := z.Next()
		bname, isAttr := z.TagName()
		name := string(bname)

		textB := z.Text()
		text := string(textB)

		attr := map[string]string{}

		for {
			attrKeyB, attrValB, more := z.TagAttr()
			k := string(attrKeyB)
			v := string(attrValB)
			attr[k] = v
			if !more {
				break
			}
		}

		if name == TagImg || name == TagA {
			rail.Debugf("tokenType: %v, text: %v, name: %v, isAttr: %v, attr: %v", ttype, text, name, isAttr, attr)
		}

		curr := Image{}
		inCurr := false

		switch ttype {
		case html.ErrorToken:
			err := z.Err()
			if errors.Is(err, io.EOF) {
				err = nil
			}
			return res, err
		case html.TextToken:
		case html.StartTagToken, html.SelfClosingTagToken:
			if name == TagA && isAttr && IsImageWrapper(rail, attr) {
				if v, ok := attr[AttrHref]; ok {
					wrapperHref = v
				}
			} else if name == TagImg && isAttr && IsImage(rail, attr) {
				inCurr = true
				if v, ok := attr[AttrDataSrc]; ok {
					curr.DataSrc = v
					curr.Name = GuessName(v)
					curr.WrapperHref = ProcWrapperHref(wrapperHref)
				}
				if v, ok := attr[AttrAlt]; ok {
					curr.Alt = v
				}
				if ttype == html.SelfClosingTagToken {
					res.Images = append(res.Images, curr)
					curr = Image{}
					inCurr = false
				}
			}
		case html.EndTagToken:
			if name == TagImg && inCurr {
				res.Images = append(res.Images, curr)
				curr = Image{}
				inCurr = false
			}
		}
	}

}

func IsImageWrapper(rail miso.Rail, attr map[string]string) bool {
	if v, ok := attr[AttrClass]; ok {
		if strings.Contains(v, ImageWrapperClass) {
			return true
		}
	}
	return false
}

func IsImage(rail miso.Rail, attr map[string]string) bool {
	if v, ok := attr[AttrClass]; ok {
		if strings.Contains(v, ImageClass) && !strings.Contains(v, ActivityImageClass) {
			return true
		}
	}
	return false
}

func IsImageFrame(rail miso.Rail, attr map[string]string) bool {
	if v, ok := attr[AttrClass]; ok {
		if strings.Contains(v, ImageFrameClass) {
			return true
		}
	}
	return false
}

func GuessName(url string) string {
	i := strings.LastIndex(url, "/")
	if i < 0 {
		return url
	}
	ru := []rune(url)
	j := len(ru)

	if k := strings.LastIndex(url, "?"); k > -1 {
		j = k
	}

	return string(ru[i+1 : j])
}

func ProcWrapperHref(href string) string {
	return BaseUrl + href
}

func FetchRealImageSrc(rail miso.Rail, url string) (string, error) {
	doc, err := miso.NewTClient(rail, url, client).
		AddHeader("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36").
		Get().
		Str()
	if err != nil {
		return "", err
	}

	inImageFrame := false
	z := html.NewTokenizer(strings.NewReader(doc))
	for {
		ttype := z.Next()
		bname, isAttr := z.TagName()
		name := string(bname)

		textB := z.Text()
		text := string(textB)

		attr := map[string]string{}

		for {
			attrKeyB, attrValB, more := z.TagAttr()
			k := string(attrKeyB)
			v := string(attrValB)
			attr[k] = v
			if !more {
				break
			}
		}

		if name == TagImg || name == TagDiv {
			rail.Debugf("tokenType: %v, text: %v, name: %v, isAttr: %v, attr: %v", ttype, text, name, isAttr, attr)
		}

		imageSrc := ""

		switch ttype {
		case html.ErrorToken:
			err := z.Err()
			if errors.Is(err, io.EOF) {
				err = nil
			}
			return imageSrc, err
		case html.SelfClosingTagToken, html.StartTagToken:
			if name == TagDiv && isAttr && IsImageFrame(rail, attr) {
				inImageFrame = true
			} else if name == TagImg && isAttr && inImageFrame {
				if v, ok := attr[AttrSrc]; ok {
					imageSrc = v
					return imageSrc, nil
				}
			}
		}
	}

}

func DownloadImage(rail miso.Rail, image Image, dir string) error {
	file := image.OutputPath(dir)
	r := miso.NewTClient(rail, image.RealHref, client).
		AddHeader("Authority", "cdn.sex.com").
		AddHeader("Referer", "https://www.sex.com/").
		AddHeader("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36").
		Get()

	if r.Err != nil {
		return r.Err
	}

	f, err := os.Create(file)
	if err != nil {
		os.Remove(file)
		return err
	}

	_, err = io.Copy(f, r.Resp.Body)
	return err
}
