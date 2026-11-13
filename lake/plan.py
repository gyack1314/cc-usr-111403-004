"""公共表达式描述的冻结身份。"""
from .storage import digest

def node_id(node):
    if node['op'] not in ('scan','filter','project'):raise ValueError('未知表达式')
    required=('snapshot','schema','collation','visibility_scope','determinism')
    if any(k not in node for k in required):raise ValueError('语义描述不完整')
    return digest(node)

def shareable(node):
    node_id(node)
    return node['determinism']=='deterministic' and ('input' not in node or shareable(node['input']))
