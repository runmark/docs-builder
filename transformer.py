from core import AstDoc, Code


def transform(doc: AstDoc) -> Code:
    code = Code()
    code.name = doc.data
    code.title = doc.title()
    transform_toctree(doc, code)
    CodeVisitor(code).visit(doc)
    return code


def transform_toctree(doc: AstDoc, code: Code):
    """convert toctree to nested <ul> tag"""
    headers = doc.headers()

    code.add_toctree("<ul>")
    for index, node in enumerate(headers):
        if node.name == "h1":
            transform_toc(index, node)
    code.add_toctree("</ul>")
