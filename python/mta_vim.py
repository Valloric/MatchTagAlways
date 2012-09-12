#!/usr/bin/env python
#
# Copyright (C) 2012  Strahinja Val Markovic  <val@markovic.io>
#
# This file is part of MatchTagAlways.
#
# MatchTagAlways is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MatchTagAlways is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MatchTagAlways.  If not, see <http://www.gnu.org/licenses/>.

import mta_core
import vim

def CurrentLineAndColumn():
  """Returns the 1-based current line and 1-based current column."""
  line, column = vim.current.window.cursor
  column += 1
  return line, column


def CanAccessCursorColumn( cursor_column ):
  try:
    # The passed-in cursor_column is 1-based, vim.current.line is 0-based
    vim.current.line[ cursor_column - 1 ]
    return True
  except IndexError:
    return False


def LocationOfEnclosingTagsInWindowView():
  # 1-based line numbers
  first_window_line = int( vim.eval( "line('w0')" ) )
  last_window_line = int( vim.eval( "line('w$')" ) )

  # -1 because vim.current.buffer is 0-based whereas vim lines are 1-based
  visible_text = '\n'.join(
    vim.current.buffer[ first_window_line -1 : last_window_line ] )

  cursor_line, cursor_column = CurrentLineAndColumn()
  adapted_cursor_line = cursor_line - first_window_line + 1

  if not CanAccessCursorColumn( cursor_column ):
    # We need to do this because when the cursor is on the last column in insert
    # mode, that column *doesn't exist yet*. Not until the user actually types
    # something in and moves the cursor forward.
    cursor_column -= 1

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

