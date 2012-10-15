import unittest
import os
import tempfile
import shutil


def dummy_validator(value):  # pragma: no cover
    pass


def dummy_action(value):  # pragma: no cover
    pass


def dummy_prompt(value):  # pragma: no cover
    pass


class resolve_dotted_pathTest(unittest.TestCase):

    def call_FUT(self, name):
        from ..configurator import resolve_dotted_path
        return resolve_dotted_path(name)

    def test_nomodule(self):
        self.assertRaises(ImportError, self.call_FUT, 'foobar.blabla:foo')

    def test_return_abs_path(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        abs_path = self.call_FUT('mrbob.tests:templates')
        self.assertEquals(abs_path, template_dir)


class resolve_dotted_funcTest(unittest.TestCase):

    def call_FUT(self, name):
        from ..configurator import resolve_dotted_func
        return resolve_dotted_func(name)

    def test_nomodule(self):
        self.assertRaises(ImportError, self.call_FUT, 'foobar.blabla:foo')

    def test_error_no_func(self):
        from ..configurator import ConfigurationError
        self.assertRaises(ConfigurationError, self.call_FUT, 'mrbob.rendering:foo')

    def test_return_func(self):
        from mrbob.rendering import jinja2_renderer
        func = self.call_FUT('mrbob.rendering:jinja2_renderer')
        self.assertEquals(func, jinja2_renderer)


class parse_templateTest(unittest.TestCase):

    def call_FUT(self, name):
        from ..configurator import parse_template
        return parse_template(name)

    def test_relative(self):
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        abs_path = self.call_FUT('templates')
        os.chdir(old_cwd)
        self.assertEqual(abs_path, template_dir)

    def test_absolute(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        abs_path = self.call_FUT(template_dir)
        self.assertEqual(abs_path, template_dir)

    def test_dotted(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        abs_path = self.call_FUT('mrbob.tests:templates')
        self.assertEqual(abs_path, template_dir)

    def test_not_a_dir(self):
        from ..configurator import ConfigurationError
        self.assertRaises(ConfigurationError, self.call_FUT, 'foo_bar')


class ConfiguratorTest(unittest.TestCase):

    def call_FUT(self, *args, **kw):
        from ..configurator import Configurator
        return Configurator(*args, **kw)

    def test_parse_questions_basic(self):
        target_dir = tempfile.mkdtemp()
        try:
            c = self.call_FUT('mrbob.tests:templates/questions1',
                              target_dir,
                              {})
            self.assertEqual(len(c.questions), 2)
            self.assertEqual(c.questions[0].name, 'foo.bar.car.dar')
            self.assertEqual(c.questions[0].question, 'Why?')
            self.assertEqual(c.questions[1].name, 'foo')
            self.assertEqual(c.questions[1].question, 'What?')
        finally:
            shutil.rmtree(target_dir)

    def test_parse_questions_no_questions(self):
        target_dir = tempfile.mkdtemp()
        try:
            c = self.call_FUT('mrbob.tests:templates/questions2',
                              target_dir,
                              {})
            self.assertEqual(len(c.questions), 0)
        finally:
            shutil.rmtree(target_dir)

    def test_parse_questions_extra_parameter(self):
        from ..configurator import TemplateConfigurationError
        target_dir = tempfile.mkdtemp()
        try:
            self.assertRaises(TemplateConfigurationError,
                              self.call_FUT,
                              'mrbob.tests:templates/questions3',
                              target_dir,
                              {})
        finally:
            shutil.rmtree(target_dir)

    def test_parse_questions_all(self):
        target_dir = tempfile.mkdtemp()
        try:
            c = self.call_FUT('mrbob.tests:templates/questions4',
                              target_dir,
                              {})
            self.assertEqual(len(c.questions), 1)
            self.assertEqual(c.questions[0].name, u'foo')
            self.assertEqual(c.questions[0].default, True)
            self.assertEqual(c.questions[0].required, True)
            self.assertEqual(c.questions[0].validator, dummy_validator)
            self.assertEqual(c.questions[0].help, u'Blabla blabal balasd a a sd')
            self.assertEqual(c.questions[0].action, dummy_action)
            self.assertEqual(c.questions[0].command_prompt, dummy_prompt)
        finally:
            shutil.rmtree(target_dir)


class QuestionTest(unittest.TestCase):

    def call_FUT(self, *args, **kw):
        from ..configurator import Question
        return Question(*args, **kw)

    def test_defaults(self):
        q = self.call_FUT('foo', 'Why?')
        self.assertEqual(q.name, 'foo')
        self.assertEqual(q.default, None)
        self.assertEqual(q.required, False)
        self.assertEqual(q.help, "")
        self.assertEqual(q.validator, None)
        self.assertEqual(q.command_prompt, raw_input)

    def test_repr(self):
        q = self.call_FUT('foo', 'Why?')
        self.assertEqual(repr(q), u"<Question name=foo question='Why?' default=None required=False>")

    def test_ask(self):

        def cmd(q):
            self.assertEqual(q, '--> Why?:')
            return 'foo'

        q = self.call_FUT('foo', 'Why?', command_prompt=cmd)
        answer = q.ask()
        self.assertEqual(answer, 'foo')

    def test_ask_default_empty(self):
        q = self.call_FUT('foo',
                          'Why?',
                          default="moo",
                          command_prompt=lambda x: '')
        answer = q.ask()
        self.assertEqual(answer, 'moo')

    def test_ask_default_not_empty(self):

        def cmd(q):
            self.assertEqual(q, '--> Why? [moo]:')
            return 'foo'

        q = self.call_FUT('foo',
                          'Why?',
                          default="moo",
                          command_prompt=cmd)
        answer = q.ask()
        self.assertEqual(answer, 'foo')

    def test_ask_no_default(self):

        def cmd(q, go=['foo', '']):
            return go.pop()

        q = self.call_FUT('foo',
                          'Why?',
                          command_prompt=cmd)
        answer = q.ask()
        self.assertEqual(answer, 'foo')

    def test_ask_no_help(self):

        def cmd(q, go=['foo', '?']):
            return go.pop()

        q = self.call_FUT('foo',
                          'Why?',
                          command_prompt=cmd)
        answer = q.ask()
        self.assertEqual(answer, 'assert output')

    def test_ask_help(self):

        def cmd(q, go=['foo', '?']):
            return go.pop()

        q = self.call_FUT('foo',
                          'Why?',
                          help="foobar_help",
                          command_prompt=cmd)
        answer = q.ask()
        self.assertEqual(answer, 'foobar_help')

    def test_validator_no_return(self):
        q = self.call_FUT('foo',
                          'Why?',
                          validator=dummy_validator,
                          command_prompt=lambda x: 'foo')
        answer = q.ask()
        self.assertEqual(answer, 'foo')

    def test_validator_return(self):
        q = self.call_FUT('foo',
                          'Why?',
                          validator=lambda x: 'moo',
                          command_prompt=lambda x: 'foo')
        answer = q.ask()
        self.assertEqual(answer, 'moo')

    def test_validator_error(self):
        from ..configurator import ValidationError

        def cmd(q, go=['foo', 'moo']):
            return go.pop()

        def validator(value):
            if value != 'foo':
                raise ValidationError

        q = self.call_FUT('foo',
                          'Why?',
                          validator=validator,
                          command_prompt=cmd)
        answer = q.ask()
        self.assertEqual(answer, 'foo')
