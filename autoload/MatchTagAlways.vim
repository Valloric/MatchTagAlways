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


let s:script_folder_path = escape( expand( '<sfile>:p:h' ), '\' )
py import sys
py import vim
exe 'python sys.path = sys.path + ["' . s:script_folder_path . '/../python"]'
py import mta_vim


if g:mta_use_matchparen_group
  let s:match_group = 'MatchParen'
else
  let s:match_group = 'MatchTag'
endif


function! MatchTagAlways#Setup()
  " When vim is in diff mode, don't run
  if &diff
    return
  endif

  " If this is not an allowed filetype, don't do anything
  if !get( g:mta_filetypes, &filetype, 0 )
    return
  endif

  augroup matchtagalways
    autocmd! CursorMoved,CursorMovedI,WinEnter <buffer>
          \ call s:HighlightEnclosingTagsIfPossible()
  augroup END

  if !g:mta_use_matchparen_group && g:mta_set_default_matchtag_color
    hi MatchTag ctermfg=black ctermbg=lightblue guifg=black guibg=lightblue
  endif
endfunction


function! s:HighlightEnclosingTagsIfPossible()
  " Remove any previous highlighting.
  if get( w:, 'tags_highlighted', 0 )
      let w:tags_highlighted = 0
      2match none
  endif

  " Don't remove the pop-up menu and don't run when there are no colors at all.
  if pumvisible() || ( &t_Co < 8 && !has( "gui_running" ) )
      return
  endif

  call s:HighlightEnclosingTags()
endfunction


function! s:GetEnclosingTagLocations()
  " Sadly, pyeval does not exist before Vim 7.3.584
  if v:version >= 703 && has( 'patch584' )
    return pyeval( 'mta_vim.LocationOfEnclosingTagsInWindowView()' )
  else
    py vim.command( 'return ' + str( mta_vim.LocationOfEnclosingTagsInWindowView() ) )
  endif
endfunction


function! s:HighlightEnclosingTags()
  let [ opening_tag_line, opening_tag_column, closing_tag_line, closing_tag_column ] =
        \ s:GetEnclosingTagLocations()
  let first_window_line = line( 'w0' )

  if opening_tag_line < first_window_line
    return
  endif

  exe '2match ' . s:match_group . ' /' .
        \ '\(\%' . opening_tag_line . 'l\%' . opening_tag_column . 'c<\/\?\_s*\zs.\{-}\ze[ >\/]\)\|' .
        \ '\(\%' . closing_tag_line . 'l\%' . closing_tag_column . 'c<\/\?\_s*\zs.\{-}\ze[ >\/]\)' .
        \ '/'
  let w:tags_highlighted = 1
endfunction
