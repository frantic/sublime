import sublime, sublime_plugin
import re
import string

RE = re.compile(r'^var \w+ = require.+;$')

def sort_requires(text):
    output = []
    requires = set()
    for line in text.split('\n'):
        if RE.match(line):
            requires.add(line)
        else:
            output.extend(sorted(requires))
            output.append(line)
            requires = set()

    return '\n'.join(output)

def add_require(var, text):
    output = []
    added = False
    for line in text.split('\n'):
        if RE.match(line) and not added:
            output.append('var %s = require(\'%s\');' % (var, var));
            added = True
        output.append(line)

    return sort_requires('\n'.join(output))

def get_var(view):
    sel = view.substr(view.sel()[0])
    if len(sel):
        return sel
    else:
        a = b = view.sel()[0].a
        word_chars = string.ascii_letters + string.digits
        while view.substr(a - 1) in word_chars:
            a -= 1
        while view.substr(b) in word_chars:
            b += 1
        reg = sublime.Region(a, b)
        return view.substr(reg)

def pipe(view, edit, fn):
    everything = sublime.Region(0, view.size())
    content = view.substr(everything)
    replacement = fn(content)
    if content != replacement:
        view.replace(edit, everything, replacement)


class SortRequiresCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pipe(self.view, edit, lambda text: sort_requires(text))


class AddRequireCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        var = get_var(self.view)
        if var:
            pipe(self.view, edit, lambda text: add_require(var, text))
