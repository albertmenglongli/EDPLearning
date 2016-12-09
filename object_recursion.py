from enum import Enum


class Tag(Enum):
    html = 'html'
    header = 'header'
    h1 = 'h1'
    h2 = 'h2'
    h3 = 'h3'
    body = 'body'
    p = 'p'
    a = 'a'


def tag_start(tag):
    return '<' + tag.value + '>'


def tag_end(tag):
    return '</' + tag.value + '>'


class Letter(object):
    def __init__(self, content=''):
        self.lines = content.split('\n')
        self._current_line_no = 0

    @property
    def content(self):
        return str(self)

    @content.setter
    def content(self, value):
        self.lines = value.split('\n')

    def __len__(self):
        return len(self.lines)

    def __str__(self):
        return '\n'.join(self.lines)

    def __iter__(self):
        self._current_line_no = 0
        return self

    def next(self):
        if self._current_line_no >= len(self):
            raise StopIteration
        else:
            self._current_line_no += 1
            return self.lines[self._current_line_no - 1]

    def append(self, value):
        self.lines[-1] = self.lines[-1] + value

    def prepend(self, value):
        if self.lines:
            self.lines[0] = value + self.lines[0]
        else:
            self.lines.append(value)

    def append_line(self, line):
        self.lines.append(line)

    def append_lines(self, lines):
        self.lines.extend(lines)

    def prepend_line(self, line):
        self.lines.insert(0, line)

    def prepend_lines(self, lines):
        tmp_lines = lines
        tmp_lines.extend(self.lines)
        self.lines = tmp_lines


class BaseHandler(object):
    def __init__(self, successor=None):
        self._successor = successor

    @property
    def successor(self):
        return self._successor

    @successor.setter
    def successor(self, value):
        self._successor = value

    def handle(self, value):
        self.pre_handle(value)
        if self.successor:
            self.successor.handle(value)
        self.post_handle(value)

    def pre_handle(self, value):
        pass

    def post_handle(self, value):
        pass


class BodyWrapperHandler(BaseHandler):
    def __init__(self):
        super(BodyWrapperHandler, self).__init__()

    def pre_handle(self, value):
        pass


class IndentHandler(BaseHandler):
    def __init__(self, indent_content='    ', successor=None):
        super(IndentHandler, self).__init__(successor=successor)
        self.indent_content = indent_content

    def post_handle(self, letter_ref):
        _lines = []
        for line in letter_ref:
            _lines.append(self.indent_content + line)
        letter_ref.content = '\n'.join(_lines)


class TabIndentHandler(IndentHandler):
    def __init__(self, indent_content='\t', successor=None):
        super(TabIndentHandler, self).__init__(successor=successor)
        self.indent_content = indent_content


class HtmlTagHandler(BaseHandler):
    def __init__(self, tag, need_indent=True, successor=None):
        if need_indent:
            _successor = IndentHandler(successor=successor)
        else:
            _successor = successor
        super(HtmlTagHandler, self).__init__(successor=_successor)
        self.tag = tag

    def post_handle(self, letter_ref):
        letter_ref.prepend_line(tag_start(self.tag))
        letter_ref.append_line(tag_end(self.tag))


class UpperHandler(BaseHandler):
    def __init__(self, successor=None):
        super(UpperHandler, self).__init__(successor=successor)

    def pre_handle(self, letter_ref):
        letter_ref.lines = [line.upper() for line in letter_ref.lines]


class LowerHandler(BaseHandler):
    def __init__(self, successor=None):
        super(LowerHandler, self).__init__(successor=successor)

    def pre_handle(self, letter_ref):
        letter_ref.lines = [line.lower() for line in letter_ref.lines]


class BrHandler(BaseHandler):
    def __init__(self, successor=None):
        super(BrHandler, self).__init__(successor=successor)

    def pre_handle(self, letter_ref):
        letter_ref.lines = [line + '<br/>' for line in letter_ref.lines]

if __name__ == "__main__":
    content = '''Object Recursion
    This is a concept came up in 1998'''

    letter = Letter(content)
    handler = UpperHandler(successor=BrHandler(successor=HtmlTagHandler(Tag.html, successor=HtmlTagHandler(Tag.body))))
    handler.handle(letter)
    print letter
    # <html>
    #     <body>
    #         OBJECT RECURSION<br/>
    #         THIS IS A CONCEPT CAME UP IN 1998<br/>
    #     </body>
    # </html>
