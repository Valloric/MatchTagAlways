" Only do this when not done yet for this buffer
" TODO: explain b:did_ftplugin
if exists( "b:loaded_match_tag_always" )
  finish
endif
let b:loaded_match_tag_always = 1

runtime ftplugin/MatchTagAlways.vim
