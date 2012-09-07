#!/usr/bin/env python

from nose.tools import eq_
from .. import mta_core
import re


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
  eq_( None, mta_core.OffsetForLineColumnInString( text, 2, 0 ) )
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


def GetOpeningTag_Simple_test():
  html = "<div> foo"
  eq_( 0, mta_core.GetOpeningTag( html, 6 ).start_offset )


def GetOpeningTag_Nested_test():
  html = "<div><div></div> foo "
  eq_( 0, mta_core.GetOpeningTag( html, 17 ).start_offset )

  html = "<div><div><p></p> foo "
  eq_( 5, mta_core.GetOpeningTag( html, 18 ).start_offset )


def GetOpeningTag_NestedMultiLine_test():
  html = "<div>\n<div\n></div> foo "
  eq_( 0, mta_core.GetOpeningTag( html, 20 ).start_offset )

  html = "<\ndiv>\n<div><br/><p>\n\n</p> foo "
  eq_( 7, mta_core.GetOpeningTag( html, 27 ).start_offset )


def GetOpeningTag_OnAngleBracket_test():
  html = "<div>x"
  eq_( 0, mta_core.GetOpeningTag( html, 5 ).start_offset )
  eq_( None, mta_core.GetOpeningTag( html, 4 ) )


def GetClosingTag_NoOpeningTagFail_test():
  html = "</div> foo"
  eq_( None, mta_core.GetOpeningTag( html, 7 ) )

  html = "</div><br/></div> foo "
  eq_( None, mta_core.GetOpeningTag( html, 18 ) )

  html = "<\n/div>\n<div/><br/><p/>\n\n</p> foo "
  eq_( None, mta_core.GetOpeningTag( html, 30 ) )


def GetClosingTag_Simple_test():
  html = "foo </div>"
  eq_( 4, mta_core.GetClosingTag( html, 0 ).start_offset )


def GetClosingTag_Nested_test():
  html = "foo <div></div></div>"
  eq_( 15, mta_core.GetClosingTag( html, 0 ).start_offset )

  html = "foo <div><br/></div></div>"
  eq_( 20, mta_core.GetClosingTag( html, 0 ).start_offset )

  html = "foo <\ndiv><\n\nbr/></div></div>"
  eq_( 23, mta_core.GetClosingTag( html, 0 ).start_offset )


def GetClosingTag_NoClosingTagFail_test():
  html = "foo <div>"
  eq_( None, mta_core.GetClosingTag( html, 0 ) )

  html = "foo <div><br/><div>"
  eq_( None, mta_core.GetClosingTag( html, 0 ) )

  html = "foo <\ndiv>\n<div/><br/><p/>\n\n<p>"
  eq_( None, mta_core.GetClosingTag( html, 0 ) )


def GetClosingTag_OnAngleBracket_test():
  html = "x</div>"
  eq_( 1, mta_core.GetClosingTag( html, 0 ).start_offset )
  eq_( 1, mta_core.GetClosingTag( html, 1 ).start_offset )
  eq_( None, mta_core.GetClosingTag( html, 2 ) )


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
