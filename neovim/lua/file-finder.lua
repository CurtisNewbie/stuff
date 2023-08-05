-- search files, respects gitignore
vim.keymap.set('n', '<leader>ff', ':lua require"telescope.builtin".find_files({no_ignore=true, hidden=false})<CR>', {})
-- ripgrep files, respects gitignore
vim.keymap.set('n', '<leader>gs', ':lua require"telescope.builtin".live_grep()<CR>', {})
