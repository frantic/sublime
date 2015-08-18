import sublime, sublime_plugin, subprocess, json
from threading import Timer

UNDERLINE = sublime.DRAW_SOLID_UNDERLINE | sublime.HIDE_ON_MINIMAP | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE;


# https://gist.github.com/walkermatt/2871026
def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator

class FlowTypeAtPosCommand(sublime_plugin.EventListener):

    @debounce(0.5)
    def get_flow_type_at_pos(self, view):
        file_name = view.file_name()
        if not file_name or not file_name.endswith('.js') or view.is_dirty():
            return

        body = view.substr(sublime.Region(0, view.size()))
        if not '@flow' in body:
            return

        point = view.sel()[0].a
        (line, col) = view.rowcol(point)

        # If the cursor is at the end of the word, we still want
        # to get the type of the word
        if view.classify(point) & sublime.CLASS_WORD_END:
            col = col - 1

        view.set_status("flow", "-")
        view.erase_regions("flow")

        proc = subprocess.Popen(
            ["/usr/local/bin/flow", "type-at-pos", "--json", file_name, str(line + 1), str(col + 1)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        (stdout, stderr) = (stdout.decode("utf8"), stderr.decode("utf8"))

        if proc.returncode == 0 and not stderr:
            resp = json.loads(stdout)
            t = resp.get("type", "E")
            view.set_status("flow", t)
            # view.show_popup(t)

            start = view.text_point(line, resp.get("start") - 1)
            end = view.text_point(line, resp.get("end"))
            region = sublime.Region(start, end)
            view.add_regions("flow", [region], "string", "", UNDERLINE)
        else:
            view.set_status("flow", "E " + stderr)

    def on_selection_modified_async(self, view):
        self.get_flow_type_at_pos(view)

    def on_modified_async(self, view):
        view.set_status("flow", "")
        view.erase_regions("flow")

    def on_post_save_async(self, view):
        self.get_flow_type_at_pos(view)

    def on_query_completions(self, view, prefix, location):
        file_name = view.file_name()
        if not file_name or not file_name.endswith('.js'):
            return

        body = view.substr(sublime.Region(0, view.size()))
        if not '@flow' in body:
            return

        point = view.sel()[0].a
        (line, col) = view.rowcol(point)
        content = view.substr(sublime.Region(0, view.size()))

        proc = subprocess.Popen(
            ["flow", "autocomplete", "--json", file_name, str(line + 1), str(col + 1)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate(bytes(content, "utf8"))
        (stdout, stderr) = (stdout.decode("utf8"), stderr.decode("utf8"))

        if proc.returncode == 0 and not stderr:
            resp = json.loads(stdout)

            result = []
            for suggestion in resp:
                name = suggestion.get("name", "?")
                type = suggestion.get("type", "?")
                result.append(("%s\t%s" % (name, type), name))

            return (result, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        else:
            print(stderr)
            return [];
