:set paste 
:set hlsearch
:set incsearch
:set smartcase
:set expandtab
:set number
:syntax enable 

filetype plugin indent on
nnoremap <C-n> :NERDTreeToggle<CR>

:command W w

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
