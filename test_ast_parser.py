import os
from unittest import TestCase


class ParserTest(TestCase):
    def test_parse_install(self):
        base_dir = os.path.dirname(__file__)
        install_filepath = os.path.normpath(
            os.path.join(base_dir, "./sphinx-example/source/install.rst")
        )
        ast = parse_file(install_filepath)

        self.assertEqual(
            ast.dump_ast(),
            """
doc(install)
  h1(Installation)
        """.strip(),
        )
