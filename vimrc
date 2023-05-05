:set paste 
:set hlsearch
:set incsearch
:set ignorecase
:set smartcase
:set expandtab
:set number
:syntax enable 

:set tabstop=2
:set shiftwidth=2

"filetype plugin indent on
nnoremap <C-n> :NERDTreeToggle<CR>

" quote word with double quotes
nnoremap qw veS"

" qoute word with **
noremap qs veS*bveS*

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


