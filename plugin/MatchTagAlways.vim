" Copyright (C) 2012  Strahinja Val Markovic  <val@markovic.io>
"
" This file is part of MatchTagAlways.
"
" MatchTagAlways is free software: you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
"
" MatchTagAlways is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
"
" You should have received a copy of the GNU General Public License
" along with MatchTagAlways.  If not, see <http://www.gnu.org/licenses/>.

if exists( "g:loaded_matchtagalways" )
  finish
endif
let g:loaded_matchtagalways = 1

if !has( 'python' )
  echohl WarningMsg |
        \ echomsg "MatchTagAlways unavailable: requires python 2.x" |
        \ echohl None
  finish
endif

let g:mta_filetypes =
      \ get( g:, 'mta_filetypes', {
      \ 'html' : 1,
      \ 'xhtml' : 1,
      \ 'xml' : 1,
      \ 'jinja' : 1,
      \} )

let g:mta_use_matchparen_group =
      \ get( g:, 'mta_use_matchparen_group', 1 )
let g:mta_set_default_matchtag_color =
      \ get( g:, 'mta_set_default_matchtag_color', 1 )

augroup matchtagalways
  autocmd! FileType * call MatchTagAlways#Setup()
augroup END

