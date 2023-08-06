# Neovim

- https://programmingpercy.tech/blog/learn-how-to-use-neovim-as-ide/
- https://github.com/neovim/nvim-lspconfig#keybindings-and-completion
- https://docs.rockylinux.org/books/nvchad/nvchad_ui/nvimtree/
- https://javadev.org/devtools/ide/neovim/lsp/
- https://github.com/neovim/nvim-lspconfig
- https://github.com/eruizc-dev/jdtls-launcher
- https://github.com/mfussenegger/nvim-jdtls
- https://download.eclipse.org/jdtls/milestones/?d

```
~/.config/nvim/

├── init.lua
├── lua
│   ├── code-completion.lua
│   ├── file-explorer.lua
│   ├── file-finder.lua
│   ├── lsp.lua
│   ├── mason-config.lua
│   ├── plugins.lua
│   └── styling.lua
└── plugin
    └── ... 
```

Install the font using terminal settings (E.g., setting for bash), select the font that you want to use, if absent, the setting for bash may show you a way to install the font.

To reload lua files:

```
luafile %
```

To sync packer stuff:

```
:PackerSync
```

Then install packer modules:

```
:PackerInstall
```


