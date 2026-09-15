# -- Imports ------------------------------------------------------------------

from os import getenv
from plistlib import loads
from subprocess import run

# -- Class --------------------------------------------------------------------


class Preferences(object):
    """Process the current preferences of the LaTeX bundle.

    This class reads the LaTeX preferences and provides a dictionary-like
    interface to process them.

    The values come from `defaults export`, which is the command line face of
    the same preferences database CFPreferences reads. It used to come from
    CFPreferences directly through PyObjC, which meant every LaTeX command in
    this bundle needed a Python with PyObjC installed into it, and the bundle
    told people to get one by running pip against Apple's Python, which macOS
    refuses. Nothing here needs a Python extension.

    """

    def __init__(self):
        """Create a new Preferences object from the current settings.

        Examples:

            >>> preferences = Preferences()
            >>> keys = ['latexViewer', 'latexEngine', 'latexUselatexmk',
            ...         'latexVerbose', 'latexDebug', 'latexAutoView',
            ...         'latexKeepLogWin', 'latexEngineOptions']
            >>> all([key in preferences.prefs for key in keys])
            True

        """
        tm_identifier = getenv('TM_APP_IDENTIFIER', 'com.macromates.textmate')

        self.default_values = {
            'latexAutoView': True,
            'latexEngine': "pdflatex",
            'latexEngineOptions': "",
            'latexVerbose': False,
            'latexUselatexmk': True,
            'latexViewer': "TextMate",
            'latexKeepLogWin': True,
            'latexDebug': False,
        }
        self.prefs = self.default_values.copy()

        for key, value in self.read_defaults(tm_identifier).items():
            if key not in self.prefs:
                continue
            # The database stores booleans as booleans, but a value a person
            # set with `defaults write -int` arrives as a number, so anything
            # standing in for a boolean is read as one.
            self.prefs[key] = (bool(value) if isinstance(self.default_values[key], bool)
                               else value)

    @staticmethod
    def read_defaults(domain):
        """Return the whole preferences domain as a dictionary.

        An empty dictionary when the domain does not exist yet, which is the
        normal case on a machine where nothing has been changed.

        """
        result = run(['defaults', 'export', domain, '-'],
                     capture_output=True, check=False)
        if result.returncode != 0 or not result.stdout:
            return {}
        try:
            return loads(result.stdout)
        except Exception:
            return {}

    def __getitem__(self, key):
        """Return a value stored inside Preferences.

        If the value is no defined then ``None`` will be returned.

        Arguments:

            key

                The key of the value that should be returned

        Examples:

            >>> preferences = Preferences()
            >>> preferences['latexEngine'].find('tex') >= 0
            True
            >>> isinstance(preferences['latexUselatexmk'], bool)
            True

        """
        return self.prefs.get(key, None)

    def defaults(self):
        """Return a string containing the default preference values.

        Returns: ``str``

        Examples:

            >>> preferences = Preferences()
            >>> print(preferences.defaults()) # doctest:+NORMALIZE_WHITESPACE
            { latexAutoView = 1;
              latexDebug = 0;
              latexEngine = pdflatex;
              latexEngineOptions = "";
              latexKeepLogWin = 1;
              latexUselatexmk = 1;
              latexVerbose = 0;
              latexViewer = TextMate; }

        """
        plist = {
            preference: int(value) if isinstance(value, bool) else value
            for preference, value in self.default_values.items()
        }
        preference_items = [
            '{} = {};'.format(
                preference,
                plist[preference] if str(plist[preference]) else '""')
            for preference in sorted(plist)
        ]
        return '{{ {} }}'.format(' '.join(preference_items))


if __name__ == '__main__':
    from doctest import testmod
    testmod()
