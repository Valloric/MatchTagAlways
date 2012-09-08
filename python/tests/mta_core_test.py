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

from nose.tools import eq_
from .. import mta_core


def LineColumnOffsetConversions_Basic_test():
  text = "foo"
  eq_( 2, mta_core.OffsetForLineColumnInString( text, 1, 3 ) )
  eq_( (1, 3), mta_core.LineColumnForOffsetInString( text, 2 ) )


def LineColumnOffsetConversions_BasicMultiLine_test():
  text = "foo\nbar"
  eq_( 6, mta_core.OffsetForLineColumnInString( text, 2, 3 ) )
  eq_( (2, 3), mta_core.LineColumnForOffsetInString( text, 6 ) )


def LineColumnOffsetConversions_ComplexMultiLine_test():
  text = "foo\nbar\nqux the thoeu \n\n\n aa "
  eq_( 8, mta_core.OffsetForLineColumnInString( text, 3, 1 ) )
  eq_( 21, mta_core.OffsetForLineColumnInString( text, 3, 14 ) )
  eq_( 25, mta_core.OffsetForLineColumnInString( text, 6, 1 ) )

  eq_( (3, 1), mta_core.LineColumnForOffsetInString( text, 8 ) )
  eq_( (3, 14), mta_core.LineColumnForOffsetInString( text, 21 ) )
  eq_( (6, 1), mta_core.LineColumnForOffsetInString( text, 25 ) )


def LineColumnOffsetConversions_EmtpyLine_test():
  # Vim allows the user to stop on an empty line and declares that column 1
  # exists even when there are no characters on that line
  text = "foo\nbar\nqux the thoeu \n\n\n aa "
  eq_( 23, mta_core.OffsetForLineColumnInString( text, 5, 1 ) )


def LineColumnOffsetConversions_FailOnEmptyString_test():
  text = ""
  eq_( None, mta_core.OffsetForLineColumnInString( text, 1, 3 ) )
  eq_( (None, None), mta_core.LineColumnForOffsetInString( text, 2 ) )


def LineColumnOffsetConversions_FailLineOutOfRange_test():
  text = "foo\nbar\nqux the thoeu \n\n\n aa "
  eq_( None, mta_core.OffsetForLineColumnInString( text, 10, 3 ) )
  eq_( (None, None), mta_core.LineColumnForOffsetInString( text, 100 ) )


def LineColumnOffsetConversions_FailColumnOutOfRange_test():
  text = "foo\nbar\nqux the thoeu \n\n\n aa "
  # eq_( None, mta_core.OffsetForLineColumnInString( text, 2, 0 ) )
  eq_( None, mta_core.OffsetForLineColumnInString( text, 2, 5 ) )
  eq_( None, mta_core.OffsetForLineColumnInString( text, 2, 4 ) )

  eq_( (None, None), mta_core.LineColumnForOffsetInString( text, 3 ) )
  eq_( (None, None), mta_core.LineColumnForOffsetInString( text, 7 ) )
  eq_( (None, None), mta_core.LineColumnForOffsetInString( text, 22 ) )


def TAG_REGEX_Works_test():
  eq_(
    {
      'start_slash' : None,
      'tag_name' : 'div',
      'end_slash' : None,
    },
    mta_core.TAG_REGEX.match( "<div>" ).groupdict() )

  eq_(
    {
      'start_slash' : None,
      'tag_name' : 'p',
      'end_slash' : None,
    },
    mta_core.TAG_REGEX.match( "< p \n\n id='xx' \nclass='b'>" ).groupdict() )

  eq_(
    {
      'start_slash' : None,
      'tag_name' : 'foo:bar-goo',
      'end_slash' : None,
    },
    mta_core.TAG_REGEX.match( "<foo:bar-goo>" ).groupdict() )

  eq_(
    {
      'start_slash' : '/',
      'tag_name' : 'p',
      'end_slash' : None,
    },
    mta_core.TAG_REGEX.match( "</p>" ).groupdict() )

  eq_(
    {
      'start_slash' : '/',
      'tag_name' : 'p',
      'end_slash' : None,
    },
    mta_core.TAG_REGEX.match( "<\n/  p>" ).groupdict() )

  eq_(
    {
      'start_slash' : None,
      'tag_name' : 'br',
      'end_slash' : '/',
    },
    mta_core.TAG_REGEX.match( "< br \n\n id='xx' \nclass='b' />" ).groupdict() )


def PacifyHtmlComments_Works_test():
  eq_( 'foo xxxx xxxxx \txxx \n xxxxxx xxxxx xxx',
       mta_core.PacifyHtmlComments(
         'foo <!-- <div> \tfoo \n </div> <br/> -->' ) )


def GetPreviousUnmatchedOpeningTag_Simple_test():
  html = "<div> foo"
  eq_( 0, mta_core.GetPreviousUnmatchedOpeningTag( html, 6 ).start_offset )


def GetPreviousUnmatchedOpeningTag_Nested_test():
  html = "<div><div></div> foo "
  eq_( 0, mta_core.GetPreviousUnmatchedOpeningTag( html, 17 ).start_offset )

  html = "<div><div><p></p> foo "
  eq_( 5, mta_core.GetPreviousUnmatchedOpeningTag( html, 18 ).start_offset )


def GetPreviousUnmatchedOpeningTag_NestedMultiLine_test():
  html = "<div>\n<div\n></div> foo "
  eq_( 0, mta_core.GetPreviousUnmatchedOpeningTag( html, 20 ).start_offset )

  html = "<\ndiv>\n<div><br/><p>\n\n</p> foo "
  eq_( 7, mta_core.GetPreviousUnmatchedOpeningTag( html, 27 ).start_offset )


def GetPreviousUnmatchedOpeningTag_OnAngleBracket_test():
  html = "<div>x"
  eq_( 0, mta_core.GetPreviousUnmatchedOpeningTag( html, 5 ).start_offset )
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 4 ) )


def GetPreviousUnmatchedOpeningTag_OrphanOpeningTag_test():
  html = "<div><p><i><br></i></p>x"
  eq_( 0, mta_core.GetPreviousUnmatchedOpeningTag( html, 23 ).start_offset )


def GetNextUnmatchedClosingTag_NoOpeningTagFail_test():
  html = "foobar"
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 3 ) )

  html = "<!DOCTYPE>"
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 3 ) )

  html = "</div>"
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 3 ) )

  html = "</div> foo"
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 7 ) )

  html = "</div><br/></div> foo "
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 18 ) )

  html = "<\n/div>\n<div/><br/><p/>\n\n</p> foo "
  eq_( None, mta_core.GetPreviousUnmatchedOpeningTag( html, 30 ) )


def GetNextUnmatchedClosingTag_Simple_test():
  html = "foo </div>"
  eq_( 4, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )


def GetNextUnmatchedClosingTag_Nested_test():
  html = "foo <div></div></div>"
  eq_( 15, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )

  html = "foo <div><br/></div></div>"
  eq_( 20, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )

  html = "foo <\ndiv><\n\nbr/></div></div>"
  eq_( 23, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )


def GetNextUnmatchedClosingTag_NoClosingTagFail_test():
  html = "foobar"
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 0 ) )

  html = "<!DOCTYPE>"
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 0 ) )

  html = "<div>"
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 0 ) )

  html = "foo <div>"
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 0 ) )

  html = "foo <div><br/><div>"
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 0 ) )

  html = "foo <\ndiv>\n<div/><br/><p/>\n\n<p>"
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 0 ) )


def GetNextUnmatchedClosingTag_OnAngleBracket_test():
  html = "x</div>"
  eq_( 1, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )
  eq_( 1, mta_core.GetNextUnmatchedClosingTag( html, 1 ).start_offset )
  eq_( None, mta_core.GetNextUnmatchedClosingTag( html, 2 ) )


def GetNextUnmatchedClosingTag_OrphanOpeningTag_test():
  html = "x<p><i><br></i></p></div>"
  eq_( 19, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )

  html = "x<p><i><br></i></p><br></div>"
  eq_( 23, mta_core.GetNextUnmatchedClosingTag( html, 0 ).start_offset )


def LocationsOfEnclosingTags_Basic_test():
  html = "<div> foo </div>"
  eq_( ( 1, 1, 1, 11 ), mta_core.LocationsOfEnclosingTags( html, 1, 7 ) )


def LocationsOfEnclosingTags_Nested_test():
  html = "<div><p><br/></p> foo </div>"
  eq_( ( 1, 1, 1, 23 ), mta_core.LocationsOfEnclosingTags( html, 1, 19 ) )


def LocationsOfEnclosingTags_MultiLine_test():
  html = "<\ndiv><\n\np>\n<br/></p>\n foo </div>"
  eq_( ( 1, 1, 6, 6 ), mta_core.LocationsOfEnclosingTags( html, 6, 2 ) )

  html = "<\ndiv><\n\np>\n<br/></p>\n foo <\ta>\tbar\n<br/><\n/a> </div>"
  eq_( ( 1, 1, 8, 5 ), mta_core.LocationsOfEnclosingTags( html, 6, 2 ) )


def LocationsOfEnclosingTags_Comments_test():
  html = "<div><p><!-- <div> --><br/></p> foo </div>"
  eq_( ( 1, 1, 1, 37 ), mta_core.LocationsOfEnclosingTags( html, 1, 34 ) )


def LocationsOfEnclosingTags_CursorInTag_test():
  html = "<\ndiv\t \nid='foo' \n>baz <p>qux<br/></p></div>"
  eq_( ( 1, 1, 4, 21 ), mta_core.LocationsOfEnclosingTags( html, 3, 2 ) )


def LocationsOfEnclosingTags_CursorInTagFull_test():
  html = "<div></div>"
  def gen( column ):
    eq_( ( 1, 1, 1, 6 ), mta_core.LocationsOfEnclosingTags( html, 1, column ) )

  for i in xrange( 1, len( html ) + 1 ):
    yield gen, i


def LocationsOfEnclosingTags_UnbalancedOpeningTag_test():
  # this is the reason why we need to continue looking for a different opening
  # tag if the closing tag we found does not match
  html = "<ul><li>foo</ul>"
  eq_( ( 1, 1, 1, 12 ), mta_core.LocationsOfEnclosingTags( html, 1, 9 ) )

  html = "<ul><li></ul></ul>"
  eq_( ( 1, 1, 1, 9 ), mta_core.LocationsOfEnclosingTags( html, 1, 1 ) )

  # this is the reason why we need to be able to skip over orphan open tags
  html = "<ul><ul><li></ul>x<ul><li></ul>\n</ul>"
  eq_( ( 1, 1, 2, 1 ), mta_core.LocationsOfEnclosingTags( html, 1, 2 ) )
  eq_( ( 1, 1, 2, 1 ), mta_core.LocationsOfEnclosingTags( html, 1, 18 ) )


def LocationsOfEnclosingTags_UnbalancedOpeningTagFull_test():
  html = "<ul><li>foo</ul>"
  def gen( column ):
    eq_( ( 1, 1, 1, 12 ), mta_core.LocationsOfEnclosingTags( html, 1, column ) )

  for i in xrange( 1, len( html ) + 1 ):
    yield gen, i


def LocationsOfEnclosingTags_Fail_test():
  html = ""
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 2 ) )

  html = "foo bar baz qux"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 8 ) )

  html = "<div>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 2 ) )

  html = "</div>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 2 ) )

  html = "<div></div>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 10, 10 ) )
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 20 ) )

  html = "<div><div>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 5 ) )

  html = "<div><br/><div>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 8 ) )

  html = "</div><div/>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 5 ) )

  html = "</div></div>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 5 ) )

  html = "<div></foo>"
  eq_( ( 0, 0, 0, 0 ), mta_core.LocationsOfEnclosingTags( html, 1, 5 ) )
