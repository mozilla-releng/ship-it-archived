import re
from os import path


class ValidVersionPattern(object):
    _compiled_regex = None

    @classmethod
    def get_compiled_regex(self):
        if self._compiled_regex is None:
            pattern_string = _convert_js_version_pattern()
            self._compiled_regex = re.compile(pattern_string)
        return self._compiled_regex


def _convert_js_version_pattern():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'static/version_pattern.js')) as f:
        js_lines = f.readlines()

    js_lines = _remove_js_comments(js_lines)
    js_lines = _remove_end_of_lines(js_lines)
    js_lines = _remove_whitespaces(js_lines)

    js_string = ''.join(js_lines)
    js_string = _remove_js_string_concatenation(js_string)
    js_string = _remove_js_var_definition(js_string)
    js_string = _remove_js_trailing_characters(js_string)

    return _replace_double_backslashes(js_string)


def _remove_js_comments(lines):
    return map(lambda line: re.sub(r'//.*$', '', line), lines)


def _remove_end_of_lines(lines):
    return map(lambda line: line.rstrip('\n'), lines)


def _remove_whitespaces(lines):
    return map(lambda line: line.strip(), lines)


def _remove_js_string_concatenation(string):
    return string.replace("' +'", '')


def _remove_js_var_definition(string):
    return re.sub(r"var\s+[A-Za-z0-9_]+\s+=\s+'", '', string)


def _remove_js_trailing_characters(string):
    return string.replace("';", '')


def _replace_double_backslashes(string):
    return string.replace('\\\\', '\\')
