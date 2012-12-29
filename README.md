# Always highlight enclosing tags

The MatchTagAlways.vim (MTA) plug-in for the [Vim text editor][vim] always
highlights the XML/HTML tags that enclose your cursor location. It's probably
easiest to describe with a screenshot:

![MatchTagAlways screen shot](http://i.imgur.com/qAf0N.gif)

It even works with HTML templating languages like Jinja or HTML5 use-cases
like unclosed tags. It's pretty smart and should do the right thing in most
cases. If it doesn't, report the problem on the [issue tracker][tracker]!

## Installation

Use [Vundle][vundle] to install the plugin. You _are_ using Vundle to manage
your Vim plugins, right? [Pathogen][pathogen] works fine too (but I recommend
Vundle).

Note that the plugin requires that your copy of Vim is compiled with Python
support. You can check for this with `:echo has('python')` in Vim. If the output
is `1`, then you have Python support.

After installation you should be done. The plugin should be plug & play. It will
automatically turn itself on for HTML, XML and a few other HTML-like filetypes.
You can also explicitly turn it on for other filetypes too (more details in the
Options section).

## Options

All options have reasonable defaults so if the plug-in works after installation
you don't need to change any options. These options can be configured in your
[vimrc script] [vimrc] by including a line like this:

    let g:mta_use_matchparen_group = 1

Note that after changing an option in your [vimrc script] [vimrc] you have to
restart Vim for the changes to take effect.

### The `g:mta_filetypes` option

This option holds all the filetypes for which this plugin will try to find and
highlight enclosing tags. It's a Vim dictionary with keys being Vim filetypes.
The values set for those keys don't matter and are not checked, the only thing
that matters is that a key is present in the dictionary (VimL has no sets).

You can find out what the current file's filetype is in Vim with `:set ft?`.
Don't forget that question mark at the end!

Default: `{ 'html' : 1, 'xhtml' : 1, 'xml' : 1, 'jinja' : 1 }`

    let g:mta_filetypes = {
        \ 'html' : 1,
        \ 'xhtml' : 1,
        \ 'xml' : 1,
        \ 'jinja' : 1,
        \}

### The `g:mta_use_matchparen_group` option

When set to 1, forces the use of the [MatchParen][matchparen] syntax group. This
is the same group that Vim uses to highlight parens, braces etc. This option is
useful for people who want to use the same highlight color for both constructs.

When set to 0, MTA will use a custom `MatchTag` syntax group with a default
highlight color. See the `g:mta_set_default_matchtag_color` option for
instructions on how to change that color.

By default, this option is set to 1 because this makes it very unlikely that
your colorscheme will conflict with the default colors used for the `MatchTag`
group. It's the safe choice. Feel free to toggle this option to 0 (the author
uses it like this).

Default: `1`

    let g:mta_use_matchparen_group = 1

### The `g:mta_set_default_matchtag_color` option

This option only makes sense when `g:mta_use_matchparen_group` is set to 0. When
it is, `g:mta_set_default_matchtag_color` option can be used to prevent MTA from
overwriting any color you have set for the `MatchTag` group.

So, if you want to use a custom color for tag highlighting, have both
`g:mta_use_matchparen_group` and `g:mta_set_default_matchtag_color` set to 0 and
then set a custom color for `MatchTag` in your `vimrc`. For example, the
following command would set a light green text background and a black foreground
color ('foreground' is the text color):

    highlight MatchTag ctermfg=black ctermbg=lightgreen guifg=black guibg=lightgreen

See `:help highlight` for more details on text highlighting commands.

Default: `1`

    let g:mta_set_default_matchtag_color = 1

## FAQ

### I've noticed that sometimes no tags are highlighted. Why?

The plugin only scans the lines that are visible in your window. If an opening
tag is visible but the closing tag is not, no tag will be highlighted. This is
for performance reasons (ie. what happens if the user opens a 10k HTML file?).

It's also possible that the plugin's parser is just out of ideas on how to
extract the enclosing tags out of your text. This should be very rare though.

## Contact

If you have questions, bug reports, suggestions, etc. please use the [issue
tracker][tracker]. The latest
version is available at <http://valloric.github.com/MatchTagAlways/>.

The author's homepage is <http://val.markovic.io>.

## License

This software is licensed under the [GPL v3 license][gpl].
© 2012 Strahinja Val Markovic &lt;<val@markovic.io>&gt;.


[vimrc]: http://vimhelp.appspot.com/starting.txt.html#vimrc
[vim]: http://www.vim.org/
[gpl]: http://www.gnu.org/copyleft/gpl.html
[vundle]: https://github.com/gmarik/vundle#about
[pathogen]: https://github.com/tpope/vim-pathogen#pathogenvim
[matchparen]: http://vimhelp.appspot.com/pi_paren.txt.html
[tracker]: https://github.com/Valloric/MatchTagAlways/issues
