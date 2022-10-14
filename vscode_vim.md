# vscode & vim

[Doc for key-remaping](https://github.com/VSCodeVim/Vim/#key-remapping)

In `settings.json`, to use `gs` for searching symbols, `gc` to go to implementation:

```json
  "vim.normalModeKeyBindings": [
    {
      "before": [
        "g",
        "s"
      ],
      "commands": [
        "workbench.action.gotoSymbol"
      ]
    },
    {
      "before": [
        "g",
        "c"
      ],
      "commands": [
        "editor.action.goToImplementation"
      ]
    }
  ],
```