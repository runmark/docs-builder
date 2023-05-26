import os


class BuildContext:
    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, "src")
        self.cache_dir = os.path.join(base_dir, "cache")
        self.build_dir = os.path.join(base_dir, "build")
        self.compile_tasks = []
        self.link_tasks = []
        self.executed_tasks = []

    def add_compile_task(self, task):
        self.compile_tasks.append(task)

    def add_link_task(self, task):
        self.link_tasks.append(task)

    def execute_task(self, task_list: list, task):
        task.exec(self)
        if task_list:
            task_list.remove(task)
        self.executed_tasks.append(task)

    def execute_tasks(self, task_list):
        while task_list:
            for task in task_list[:]:
                self.execute_task(task_list, task)


class Task:
    def exec(self, ctx: BuildContext):
        self.ctx = ctx
        self.run()

    def run(self):
        raise NotImplementedError()


class Scan(Task):
    def __str__(self):
        return "scan"

    def run(self):
        for filename in os.listdir(self.ctx.src_dir):
            if filename.endswith(".rst"):
                self.ctx.add_compile_task(Parse(filename))
                self.ctx.add_link_task(Link(filename))


class Parse(Task):
    """rst file -> ast model"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"parse({self._filename})"

    def run(self):
        self.ctx.add_compile_task(Transform(self._filename))


class Transform(Task):
    """ast model -> code model"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"transform({self._filename})"

    def run(self):
        self.ctx.add_compile_task(WriteCache(self._filename))


class WriteCache(Task):
    """write code to cache"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"writecache({self._filename})"

    def run(self):
        pass


class Link(Task):
    """generate final output"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"link({self._filename})"

    def run(self):
        pass


class AstNode:
    def __init__(self, name, data=None):
        self._name = name
        self._data = data
        self._children = None

    def append_child(self, child):
        self._children = self._children or []
        self._children.append(child)

    def ast_string(self, depth: int):
        indent = " " * (depth * 2)
        result = f"{indent}{self._name}"
        if self._data:
            result += f"({self._data})"
        return result

    def iter(self, depth: int):
        yield depth, self
        for child in self._children or []:
            for descendant in child.iter(depth + 1):
                yield descendant
            # yield child.iter(depth + 1)


class AstDoc(AstNode):
    def __init__(self, data):
        super().__init__("doc", data)

    def dump_ast(self):
        return "\n".join([node.ast_string(depth) for depth, node in self.iter(depth=0)])


if __name__ == "__main__":
    root = AstDoc("install")
    root.append_child(AstNode("h1", "Installation"))

    print(root.dump_ast())
