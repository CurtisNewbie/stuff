:set hlsearch
:set incsearch
:set ignorecase
:set smartcase
:set expandtab
:set number
:set relativenumber
:syntax enable

" :set autoindent

:set tabstop=2
:set shiftwidth=2

:highlight ExtraWhitespace ctermbg=red guibg=red
:match ExtraWhitespace /\s\+$/

"filetype plugin indent on
nnoremap <C-n> :NERDTreeToggle<CR>

" quote word with double quotes
nnoremap qw veS"b

" quote [curr:line_end] with double quotes
nnoremap ql v$S"0

" qoute word with **
nnoremap qs i**<ESC>ea**<ESC>

" qoute word with `
nnoremap qd veS`b

:command W w
:command Wq wq

set visualbell
set t_vb=

set splitright

set laststatus=2
if !has('gui_running')
  set t_Co=256
endif

" Specify a directory for plugins
" - For Neovim: stdpath('data') . '/plugged'
" - Avoid using standard Vim directory names like 'plugin'
call plug#begin('~/.vim/plugged')

Plug 'junegunn/fzf'
Plug 'junegunn/fzf.vim'
Plug 'preservim/nerdtree'
Plug 'itchyny/lightline.vim'
Plug 'sheerun/vim-polyglot'

" Initialize plugin system
call plug#end()

nnoremap -- :vsp<CR> <c-w>h :q<Enter>