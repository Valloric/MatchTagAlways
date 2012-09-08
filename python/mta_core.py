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

import re


TAG_REGEX = re.compile(
  r"""<\s*                    # the opening bracket + whitespace
      (?P<start_slash>/)?     # captures the slash if closing bracket
      \s*                     # more whitespace
      (?P<tag_name>[\w:-]+)   # the tag name, captured
      .*?                     # anything else in the tag
      (?P<end_slash>/)?       # ending slash, for self-closed tags
      >""",
  re.VERBOSE | re.DOTALL )

COMMENT_REGEX = re.compile( '<!--.*?-->', re.DOTALL )


class TagType( object ):
  OPENING = 1
  CLOSING = 2
  SELF_CLOSED = 3


class Tag( object ):
  def __init__( self, match_object ):
    if not match_object:
      self.valid = False
      return
    self.valid = True
    self.name = match_object.group( 'tag_name' )

    if match_object.group( 'start_slash' ):
      self.kind = TagType.CLOSING
    elif match_object.group( 'end_slash' ):
      self.kind = TagType.SELF_CLOSED
    else:
      self.kind = TagType.OPENING

    self.start_offset = match_object.start()
    self.end_offset = match_object.end()


  def __nonzero__( self ):
    return self.valid


  def __eq__( self, other ):
    if type( other ) is type( self ):
        return
    return False


def PacifyHtmlComments( text ):
  """Replaces the contents (including delimiters) of all HTML comments in the
  passed-in text with 'x'. For instance, 'foo <!-- bar -->' becomes
  'foo xxxx xxx xxx'. We can't just remove the comments because that would screw
  with the mapping of string offset to Vim line/column."""

  def replacement( match ):
    return re.sub( '\S', 'x', match.group() )
  return COMMENT_REGEX.sub( replacement, text )


def ReverseFindTag( text, from_position ):
  try:
    bracket_index = text.rindex( '<', 0, from_position )
  except ValueError:
    return None
  match = TAG_REGEX.match( text, bracket_index )
  if not match:
    return None
  if match.end() <= from_position:
    return Tag( match )
  return None


def ForwardFindTag( text, from_position ):
  return Tag( TAG_REGEX.search( text, from_position ) )


def OffsetForLineColumnInString( text, line, column ):
  offset = -1
  current_line = 1
  current_column = 0
  previous_char = ''
  for char in text:
    offset += 1
    current_column += 1
    if char == '\n':
      current_line += 1
      current_column = 0

    if current_line == line and current_column == column:
      return offset
    if current_line > line:
      # Vim allows the user to stop on an empty line and declares that column 1
      # exists even when there are no characters on that line
      if current_column == 0 and previous_char == '\n':
        return offset -1
      break
    previous_char = char
  return None


def LineColumnForOffsetInString( text, offset ):
  current_offset = -1
  current_line = 1
  current_column = 0
  for char in text:
    current_offset += 1
    current_column += 1
    if char == '\n':
      current_line += 1
      current_column = 0
      continue

    if current_offset == offset:
      return current_line, current_column
    if current_offset > offset:
      break
  return None, None


def TagWithSameNameExistsInSequence( tag, sequence ):
  for current_tag in sequence:
    if current_tag.name == tag.name:
      return True
  return False


def GetPreviousUnmatchedOpeningTag( html, cursor_offset ):
  search_index = cursor_offset
  tags_to_close = []
  while True:
    prev_tag = ReverseFindTag( html, search_index )
    if not prev_tag:
      break
    search_index = prev_tag.start_offset

    if prev_tag.kind == TagType.CLOSING:
      tags_to_close.append( prev_tag )
    elif prev_tag.kind == TagType.OPENING:
      if tags_to_close:
        if tags_to_close[ -1 ].name == prev_tag.name:
          tags_to_close.pop()
        else:
          continue
      else:
        return prev_tag
    # self-closed tags ignored
  return None


def GetNextUnmatchedClosingTag( html, cursor_offset ):
  def RemoveClosedOpenTags( tags_to_close, new_tag ):
    i = 1
    for tag in reversed( tags_to_close ):
      if tag.name == new_tag.name:
        break
      else:
        i += 1
    assert i <= len( tags_to_close )
    del tags_to_close[ -i: ]
    return tags_to_close

  search_index = cursor_offset
  tags_to_close = []
  while True:
    next_tag = ForwardFindTag( html, search_index )
    if not next_tag:
      break
    search_index = next_tag.end_offset

    if next_tag.kind == TagType.OPENING:
      tags_to_close.append( next_tag )
    elif next_tag.kind == TagType.CLOSING:
      if not tags_to_close or not TagWithSameNameExistsInSequence(
        next_tag, tags_to_close ):
        return next_tag
      tags_to_close = RemoveClosedOpenTags( tags_to_close, next_tag )
    # self-closed tags ignored
  return None


def GetOpeningAndClosingTags( html, cursor_offset ):
  current_offset = cursor_offset

  closing_tag = GetNextUnmatchedClosingTag( html, current_offset )
  while True:
    opening_tag = GetPreviousUnmatchedOpeningTag( html, current_offset )

    if not opening_tag or not closing_tag:
      return None, None

    if opening_tag.name == closing_tag.name:
      return opening_tag, closing_tag
    current_offset = opening_tag.start_offset


def AdaptCursorOffsetIfNeeded( sanitized_html, cursor_offset ):
  """The cursor offset needs to be adapted if it is inside a tag.
  If the cursor is inside an opening tag, it will be moved to the index of the
  character just past the '>'. If it's inside the closing tag, it will be moved
  to the index of the '<'. This will ensure that both the opening and the
  closing tags are correctly found.
  If the cursor is inside a self-closed tag, then it doesn't really matter what
  we do with it, the surrounding tags will be correctly found (the self-closed
  tag is ignored, as it should be)."""

  preceding_angle_bracket_index = cursor_offset
  while True:
    if preceding_angle_bracket_index < 0:
      return cursor_offset
    char = sanitized_html[ preceding_angle_bracket_index ]
    if preceding_angle_bracket_index != cursor_offset and char == '>':
      # Not inside a tag, no need for adaptation
      return cursor_offset

    if char == '<':
      break
    preceding_angle_bracket_index -= 1

  tag = Tag( TAG_REGEX.match( sanitized_html,
                              preceding_angle_bracket_index ) )
  if not tag:
    return cursor_offset

  if tag.kind == TagType.OPENING:
    return tag.end_offset
  return tag.start_offset


def LocationsOfEnclosingTags( input_html, cursor_line, cursor_column ):
  bad_result = ( 0, 0, 0, 0 )
  try:
    sanitized_html = PacifyHtmlComments( input_html )
    cursor_offset = OffsetForLineColumnInString( sanitized_html,
                                                 cursor_line,
                                                 cursor_column )
    if cursor_offset == None:
      return bad_result

    adapted_cursor_offset = AdaptCursorOffsetIfNeeded( sanitized_html,
                                                       cursor_offset )
    opening_tag, closing_tag = GetOpeningAndClosingTags( sanitized_html,
                                                         adapted_cursor_offset )

    if not opening_tag or not closing_tag:
      return bad_result

    opening_tag_line, opening_tag_column = LineColumnForOffsetInString(
      sanitized_html,
      opening_tag.start_offset )

    closing_tag_line, closing_tag_column = LineColumnForOffsetInString(
      sanitized_html,
      closing_tag.start_offset )

    return ( opening_tag_line,
             opening_tag_column,
             closing_tag_line,
             closing_tag_column )
  except Exception:
    return bad_result

