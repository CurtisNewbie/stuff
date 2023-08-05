-- search files, respects gitignore
vim.keymap.set('n', 'gs', ':lua require"telescope.builtin".find_files()<CR>', {})

-- ripgrep files, respects gitignore
vim.keymap.set('n', 'gf', ':lua require"telescope.builtin".live_grep()<CR>', {})
