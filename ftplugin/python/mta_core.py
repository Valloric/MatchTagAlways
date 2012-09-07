#!/usr/bin/env python

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
  if match.end() <= from_position:
    return Tag( match )
  return None


def ForwardFindTag( text, from_position ):
  return Tag( TAG_REGEX.search( text, from_position ) )


def OffsetForLineColumnInString( text, line, column ):
  offset = -1
  current_line = 1
  current_column = 0
  for char in text:
    offset += 1
    current_column += 1
    if char == '\n':
      current_line += 1
      current_column = 0
      continue

    if current_line == line and current_column == column:
      return offset
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
  return None, None


def GetOpeningTag( html, cursor_offset ):
  tags_to_close = 0
  search_index = cursor_offset
  while True:
    prev_tag = ReverseFindTag( html, search_index )
    if not prev_tag:
      return None
    if prev_tag.kind == TagType.CLOSING:
      tags_to_close += 1
    elif prev_tag.kind == TagType.OPENING:
      if tags_to_close > 0:
        tags_to_close -= 1
      else:
        return prev_tag
    # self-closed tags ignored

    search_index = prev_tag.start_offset
  return None


def GetClosingTag( html, cursor_offset ):
  tags_to_close = 0
  search_index = cursor_offset
  while True:
    next_tag = ForwardFindTag( html, search_index )
    if not next_tag:
      return None
    if next_tag.kind == TagType.OPENING:
      tags_to_close += 1
    elif next_tag.kind == TagType.CLOSING:
      if tags_to_close > 0:
        tags_to_close -= 1
      else:
        return next_tag
    # self-closed tags ignored

    search_index = next_tag.end_offset
  return None


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
  sanitized_html = PacifyHtmlComments( input_html )
  cursor_offset = OffsetForLineColumnInString( sanitized_html,
                                               cursor_line,
                                               cursor_column )
  bad_result = ( 0, 0, 0, 0 )
  if cursor_offset == None:
    return bad_result

  adapted_cursor_offset = AdaptCursorOffsetIfNeeded( sanitized_html,
                                                     cursor_offset )
  opening_tag = GetOpeningTag( sanitized_html, adapted_cursor_offset )
  closing_tag = GetClosingTag( sanitized_html, adapted_cursor_offset )

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

