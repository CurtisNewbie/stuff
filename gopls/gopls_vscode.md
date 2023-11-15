# gopls vscode

- https://github.com/golang/tools/blob/master/gopls/doc/settings.md
- https://landontclipp.github.io/blog/2023/07/15/analyzing-go-heap-escapes/#configuring-vscode-for-gc-heap-escape-highlighting

```json
"gopls": {
	"ui.codelenses": {
		"generate": true,
		"gc_details": true
	},
	"ui.diagnostic.annotations": {
		"escape": true
	},
	"ui.semanticTokens": true
}
```

command + p, then enter `> Go: Toggle gc details`.
