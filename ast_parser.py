import os
import re

from core import AstDoc, AstNode


def parse_file(file_path) -> AstDoc:
    name = os.path.splitext(os.path.basename(file_path))[0]

    with open(file_path, "r") as fd:
        lines = [x.rstrip() for x in fd.readlines() if x.strip()]
        doc = parse(name, lines)
    return doc


def parse(name, lines) -> AstDoc:
    doc = AstDoc(name)

    items = list(parse_headers(lines))
    items = list(parse_toctree(items))
    items = list(parse_paragraphs(items))

    for item in items:
        doc.append_child(item)

    return doc


def parse_headers(lines):
    index = len(lines) - 1
    nodes = []
    while index >= 0:
        line = lines[index].rstrip()
        if set(line) == set("=") and index > 0:
            nodes.insert(0, AstNode("h1", lines[index - 1].strip()))
            index -= 2
        elif set(line) == set("-") and index > 0:
            nodes.insert(0, AstNode("h2", lines[index - 1].strip()))
            index -= 2
        else:
            nodes.insert(0, line)
            index -= 1
    return nodes


def parse_toctree(items):
    def find_index(items, predicate):
        return next((index for index, x in enumerate(items) if predicate(x)), -1)

    def is_toctree_start(x):
        return isinstance(x, str) and x.strip() == ".. toctree::"

    def is_toctree_end(x):
        return isinstance(x, AstNode) or (
            isinstance(x, str) and re.search("^([ \t]+)", x) is None
        )

    start = find_index(items, is_toctree_start)
    if start < 0:
        for item in items:
            yield item
        # yield items  # TODO different from above two lines
        # return items # TODO why cannot use return
    else:
        end = find_index(items[start + 1 :], is_toctree_end)
        end = start + end + 1 if end >= 0 else len(items)

        for i in range(start):
            yield items[i]

        toctree = AstNode("toctree")
        for i in range(start + 1, end):
            if isinstance(items[i], str) and items[i].strip():
                toctree.append_child(AstNode("toc", items[i].strip()))
        yield toctree

        for i in range(end, len(items)):
            yield items[i]


def parse_paragraphs(items):
    for item in items:
        if isinstance(item, AstNode):
            yield item
        elif isinstance(item, str) and item.strip():
            p = AstNode("p")

            for part in re.split(
                r"(:doc:`.+`)", item.strip()
            ):  # TODO re.split != str.split and parentheses's function
                m = re.match(r":doc:`(.+)`", part)
                if m:
                    p.append_child(AstNode("a", m.group(1)))
                else:
                    p.append_child(AstNode("text", part))
            yield p
