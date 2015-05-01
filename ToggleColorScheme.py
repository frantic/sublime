import sublime, sublime_plugin

class ToggleColorSchemeCommand(sublime_plugin.TextCommand):
    light_scheme = "Packages/User/SublimeLinter/Soda (SL).tmTheme"
    light_theme = "Spacegray Light.sublime-theme"
    dark_scheme = "Packages/User/PlasticCodeWrap (3) (SL).tmTheme"
    dark_theme = "Spacegray.sublime-theme"

    def run(self, edit, **args):
        s = sublime.load_settings("Preferences.sublime-settings")
        current_scheme = s.get("color_scheme")

        if current_scheme == self.light_scheme:
            s.set("color_scheme", self.dark_scheme)
            s.set("theme", self.dark_theme)
        else:
            s.set("color_scheme", self.light_scheme)
            s.set("theme", self.light_theme)

        sublime.save_settings("Preferences.sublime-settings")
