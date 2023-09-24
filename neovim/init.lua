if vim.g.vscode then
    -- https://github.com/sokhuong-uon/vscode-nvim/blob/main/init.lua
    local file = {
        formatDocument= function()
            vim.fn.VSCodeNotify("editor.action.formatDocument")
        end,
    }
    vim.keymap.set({'n'}, '==', file.formatDocument)
    vim.opt.clipboard='unnamedplus'
    vim.opt.ignorecase=true
    vim.opt.incsearch=true
else
    require('plugins')
    require('mason-config')
    require('lsp')
    require('code-completion')
    require('file-explorer')
    require('styling')
    require('file-finder')
    require('keymap')
    vim.wo.number = true
end



