from ast_parser import parse_file
from core import AstDoc, Code, BuildContext
from linker import link
from transformer import transform
from utils import get_name_prefix, relative_of


def parse_test_file(file_name: str) -> AstDoc:
    file_path = relative_of(__file__, "./sphinx-example/source/" + file_name)
    return parse_file(file_path)


def transform_test_file(file_name: str) -> Code:
    ast = parse_test_file(file_name)
    code = transform(ast)
    return code


def html_lines(title, body_lines):
    result = [
        "<html>",
        "<head>",
        f"<title>{title}</title>",
        "</head>",
        "<body>",
    ]
    result.extend(body_lines)
    result.extend(["</body>", "</html>"])
    return result


def pre_link(ctx: BuildContext, file_name):
    """run pre-link task before link"""
    ast = parse_test_file(file_name)
    code = transform(ast)
    code.write_cache(ctx.cache)


def link_test_file(file_name):
    base_dir = relative_of(__file__, "../../docs")
    ctx = BuildContext(base_dir, cache_name="test.cache")
    pre_link(ctx, "index.rst")
    pre_link(ctx, "install.rst")
    pre_link(ctx, "api.rst")
    pre_link(ctx, "tutorial.rst")
    ctx.cache.save()
    return list(link(ctx, get_name_prefix(file_name)))
