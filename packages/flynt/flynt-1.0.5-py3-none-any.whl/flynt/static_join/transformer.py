import ast
from typing import List, Tuple

from flynt.static_join.utils import get_static_join_bits
from flynt.utils.format import QuoteTypes
from flynt.utils.utils import (
    ast_formatted_value,
    ast_string_node,
    fixup_transformed,
    get_str_value,
    is_str_constant,
)


class JoinTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def visit_Call(self, node: ast.Call):
        """
        Transforms a static string join to an f-string.
        """
        res = get_static_join_bits(node)
        if not res:
            return self.generic_visit(node)
        joiner, args = res
        self.counter += 1
        args_with_interleaved_joiner: List[ast.AST] = []
        for arg in args:
            if is_str_constant(arg):
                args_with_interleaved_joiner.append(arg)
            else:
                args_with_interleaved_joiner.append(ast_formatted_value(arg))
            args_with_interleaved_joiner.append(ast_string_node(joiner))
        args_with_interleaved_joiner.pop()  # remove the last joiner
        if all(is_str_constant(arg) for arg in args_with_interleaved_joiner):
            return ast.Constant(
                value="".join(
                    get_str_value(arg) for arg in args_with_interleaved_joiner
                )
            )
        return ast.JoinedStr(args_with_interleaved_joiner)


def transform_join(tree: ast.AST, *args, **kwargs) -> Tuple[str, bool]:
    jt = JoinTransformer()
    new_tree = jt.visit(tree)
    changed = jt.counter > 0
    if changed:
        new_code = fixup_transformed(new_tree, quote_type=QuoteTypes.double)
    else:
        new_code = ""
    return new_code, changed
