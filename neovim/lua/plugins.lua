return require('packer').startup(function(use)
  -- Configurations will go here soon
 use 'wbthomason/packer.nvim'
 use 'williamboman/mason.nvim'   
 use 'williamboman/mason-lspconfig.nvim'
 use 'neovim/nvim-lspconfig'  
 -- Hrsh7th Code Completion Suite
 use 'hrsh7th/nvim-cmp' 
 use 'hrsh7th/cmp-nvim-lsp'
 use 'hrsh7th/cmp-nvim-lua'
 use 'hrsh7th/cmp-nvim-lsp-signature-help'
 use 'hrsh7th/cmp-vsnip'                             
 use 'hrsh7th/cmp-path'                              
 use 'hrsh7th/cmp-buffer'                            
 use 'hrsh7th/vim-vsnip'
 use 'nvim-tree/nvim-tree.lua'
 use 'Mofiqul/dracula.nvim'
 use { 
  'nvim-telescope/telescope.nvim', tag = '0.1.2',
  requires = { {'nvim-lua/plenary.nvim'} }
 }
 use 'nvim-tree/nvim-web-devicons' 
 use 'mfussenegger/nvim-jdtls'
 use {
  -- recommended packer way of installing it is to run this function, copied from documentation
         'nvim-treesitter/nvim-treesitter',
      run = function()
              local ts_update = require('nvim-treesitter.install').update({ with_sync = true })
              ts_update()
         end,

 }
end)
