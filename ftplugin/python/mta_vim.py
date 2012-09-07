import mta_core
import vim

def CurrentLineAndColumn():
  """Returns the 1-based current line and 1-based current column."""
  line, column = vim.current.window.cursor
  column += 1
  return line, column


def LocationOfEnclosingTagsInWindowView():
  # 1-based line numbers
  first_window_line = int( vim.eval( "line('w0')" ) )
  last_window_line = int( vim.eval( "line('w$')" ) )

  # -1 because vim.current.buffer is 0-based whereas vim lines are 1-based
  visible_text = '\n'.join(
    vim.current.buffer[ first_window_line -1 : last_window_line ] )

  cursor_line, cursor_column = CurrentLineAndColumn()
  adapted_cursor_line = cursor_line - first_window_line + 1

  ( opening_tag_line,
    opening_tag_column,
    closing_tag_line,
    closing_tag_column ) = mta_core.LocationsOfEnclosingTags(
      visible_text,
      adapted_cursor_line,
      cursor_column )

  return [ opening_tag_line + first_window_line - 1,
           opening_tag_column,
           closing_tag_line + first_window_line - 1,
           closing_tag_column ]

