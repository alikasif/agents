from .parser import parse_aql
from .transpiler import transpile_ast_to_code, compile_to_graph_spec
def compile_aql(aql_src_or_ast):
    if isinstance(aql_src_or_ast, str):
        ast = parse_aql(aql_src_or_ast)
    else:
        ast = aql_src_or_ast
    code = transpile_ast_to_code(ast, exec_args={})
    graph_spec = compile_to_graph_spec(ast)
    return { 'code': code, 'graph_spec': graph_spec }
