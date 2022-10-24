# vscode & vim

[Doc for key-remaping](https://github.com/VSCodeVim/Vim/#key-remapping)

In `settings.json`, to use `gs` for searching symbols, `gc` to go to implementation, and `gu` to go to super class/interface (for java only):

```json
    "vim.normalModeKeyBindingsNonRecursive": [
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
        },
        {
            "before": [
                "g",
                "u"
            ],
            "commands": [
                {
                    "command": "java.action.navigateToSuperImplementation"
                }
            ]
        }
    ],
```
