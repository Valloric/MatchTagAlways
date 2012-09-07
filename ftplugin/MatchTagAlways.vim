if !has( 'python' )
  echohl WarningMsg |
        \ echomsg "MatchTagAlways unavailable: requires python 2.x" |
        \ echohl None
  finish
endif

let s:script_folder_path = escape( expand( '<sfile>:p:h' ), '\' )
py import vim
exe 'python sys.path = sys.path + ["' . s:script_folder_path . '/python"]'
py import mta_vim

augroup matchhtmlparen
  autocmd! CursorMoved,CursorMovedI,WinEnter <buffer> call s:HighlightEnclosingTagsIfPossible()
augroup END

function! s:HighlightEnclosingTagsIfPossible()
  " Remove any previous match.
  if exists('w:tag_hl_on') && w:tag_hl_on
      2match none
      let w:tag_hl_on = 0
  endif

  " Avoid that we remove the popup menu.
  " Return when there are no colors (looks like the cursor jumps).
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

  exe '2match MatchParen /' .
        \ '\(\%' . opening_tag_line . 'l\%' . opening_tag_column . 'c<\/\?\_s*\zs.\{-}\ze[ >\/]\)\|' .
        \ '\(\%' . closing_tag_line . 'l\%' . closing_tag_column . 'c<\/\?\_s*\zs.\{-}\ze[ >\/]\)' .
        \ '/'
  let w:tag_hl_on = 1
endfunction
