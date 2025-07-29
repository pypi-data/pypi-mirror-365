"""
AST模块：将字典转换为DML语句
支持复杂条件表达式，包括LIKE、OR、AND、=等关键字
"""

from typing import Dict, List, Any, Tuple, Union
import re


class ASTNode:
    """抽象语法树节点基类"""
    
    def __init__(self, node_type: str, value: Any = None):
        self.node_type = node_type
        self.value = value
        self.children = []
    
    def add_child(self, child: 'ASTNode'):
        """添加子节点"""
        self.children.append(child)
    
    def __repr__(self):
        return f"ASTNode({self.node_type}, {self.value})"


class ConditionParser:
    """条件表达式解析器"""
    
    def __init__(self):
        self.operators = {
            '=': 'EQ',
            '!=': 'NE',
            '>': 'GT',
            '>=': 'GE',
            '<': 'LT',
            '<=': 'LE',
            'LIKE': 'LIKE',
            'IN': 'IN',
            'NOT IN': 'NOT_IN',
            'IS NULL': 'IS_NULL',
            'IS NOT NULL': 'IS_NOT_NULL',
            '&': 'BIT_AND',
            '|': 'BIT_OR',
            '^': 'BIT_XOR',
            '<<': 'BIT_LSHIFT',
            '>>': 'BIT_RSHIFT'
        }
        self.logical_ops = {'AND', 'OR'}
    
    def parse_condition_dict(self, condition_dict: Dict[str, Any]) -> ASTNode:
        """解析条件字典为AST"""
        if not condition_dict:
            return None
        
        # 获取所有逻辑操作符键
        logical_keys = [key for key in condition_dict.keys() if key.upper() in self.logical_ops]
        
        # 如果有逻辑操作符键
        if logical_keys:
            # 如果只有一个逻辑操作符，直接返回对应的逻辑节点
            if len(logical_keys) == 1:
                key = logical_keys[0]
                return self._parse_logical_op(key.upper(), condition_dict[key])
            else:
                # 多个逻辑操作符并列（如AND和OR并列）
                # 创建一个复合结构，正确处理AND和OR的并列关系
                
                # 收集所有条件
                conditions = []
                
                # 处理AND条件
                if 'AND' in condition_dict:
                    and_conditions = condition_dict['AND']
                    if and_conditions:
                        and_node = self._parse_logical_op('AND', and_conditions)
                        if and_node and and_node.children:
                            conditions.append(and_node)
                
                # 处理OR条件
                if 'OR' in condition_dict:
                    or_conditions = condition_dict['OR']
                    if or_conditions:
                        or_node = self._parse_logical_op('OR', or_conditions)
                        if or_node and or_node.children:
                            conditions.append(or_node)
                
                # 根据条件数量决定结构
                if len(conditions) == 0:
                    return None
                elif len(conditions) == 1:
                    return conditions[0]
                else:
                    # 多个逻辑节点并列，正确处理AND和OR的混合关系
                    # 在这种情况下，应该保持原始的AND/OR结构
                    
                    # 检查是否只有OR条件
                    or_conditions = [c for c in conditions if c.node_type == 'OR']
                    and_conditions = [c for c in conditions if c.node_type == 'AND']
                    
                    if len(or_conditions) == 1 and len(and_conditions) == 1:
                        # AND和OR并列的情况，创建AND作为根节点，包含AND子句和OR子句
                        root = ASTNode('AND')
                        
                        # 添加AND子句的所有条件
                        if and_conditions[0].children:
                            for child in and_conditions[0].children:
                                root.add_child(child)
                        
                        # 添加OR子句作为一个整体
                        root.add_child(or_conditions[0])
                        
                        return root
                    else:
                        # 其他情况，使用AND作为默认连接
                        root = ASTNode('AND')
                        for condition in conditions:
                            root.add_child(condition)
                        return root
        
        # 纯字段条件
        return self._parse_field_conditions(condition_dict)
    
    def _parse_logical_op(self, op: str, conditions: List[Any]) -> ASTNode:
        """解析逻辑操作符"""
        node = ASTNode(op)
        for condition in conditions:
            if isinstance(condition, dict):
                child = self.parse_condition_dict(condition)
                if child:
                    node.add_child(child)
        return node
    
    def _parse_field_conditions(self, conditions: Dict[str, Any]) -> ASTNode:
        """解析字段条件"""
        root = ASTNode('AND')
        
        for field, value in conditions.items():
            if isinstance(value, dict):
                # 检查是否有位运算或算术运算
                special_op_found = False
                
                # 支持的运算符映射
                special_ops = {'&', '|', '^', '<<', '>>', '-', '+', '*', '/', '&~'}
                
                for op, op_value in value.items():
                    if op in special_ops:
                        special_op_found = True
                        expected_value = value.get('=', None)
                        
                        if op == '&~':
                            # 位清除操作 (field & ~value)
                            if expected_value is not None:
                                expr = f"({field} & ~?) = ?"
                                node = ASTNode('CUSTOM_EXPR')
                                node.add_child(ASTNode('FIELD', expr))
                                node.add_child(ASTNode('VALUE', [op_value, expected_value]))
                                root.add_child(node)
                            else:
                                raise ValueError(f"Bitwise clear operation '&~' requires explicit comparison value. Use '= 0' or '= 1' etc.")
                        elif expected_value is not None:
                            # (field op value) = expected_value
                            expr = f"({field} {op} ?) = ?"
                            node = ASTNode('CUSTOM_EXPR')
                            node.add_child(ASTNode('FIELD', expr))
                            node.add_child(ASTNode('VALUE', [op_value, expected_value]))
                            root.add_child(node)
                        else:
                            # 检查是否有!=操作符
                            not_equal_value = value.get('!=')
                            if not_equal_value is not None:
                                # (field op value) != not_equal_value
                                expr = f"({field} {op} ?) != ?"
                                node = ASTNode('CUSTOM_EXPR')
                                node.add_child(ASTNode('FIELD', expr))
                                node.add_child(ASTNode('VALUE', [op_value, not_equal_value]))
                                root.add_child(node)
                            else:
                                # 位运算与算术运算都必须提供明确的比较值
                                raise ValueError(f"Operation '{op}' requires explicit comparison value. Use '!= 0' or '= 1' etc.")
                        break  # 只处理一次特殊运算
                
                # 如果没有特殊运算，处理标准运算符
                if not special_op_found:
                    for op, op_value in value.items():
                        op_upper = op.upper()
                        if op_upper in self.operators:
                            node = ASTNode(self.operators[op_upper])
                            node.add_child(ASTNode('FIELD', field))
                            node.add_child(ASTNode('VALUE', op_value))
                            root.add_child(node)
            else:
                # 等值条件需要明确指定
                raise ValueError(f"Field '{field}' requires explicit condition. Use '= value' or other operators.")
        
        return root
    
    def parse_condition_string(self, condition_str: str) -> ASTNode:
        """解析条件字符串为AST（高级功能）"""
        # 这里可以实现更复杂的字符串解析
        # 暂时返回None，后续可以扩展
        return None


class DMLGenerator:
    """DML语句生成器"""
    
    def __init__(self):
        self.parser = ConditionParser()
    
    def dict_to_select(self, query_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """将字典转换为SELECT语句，支持联表查询"""
        table_name = query_dict.get('table')
        if not table_name:
            raise ValueError("Table name is required in query_dict")
            
        fields = query_dict.get('fields', ['*'])
        joins = query_dict.get('joins', [])
        where_ast = self.parser.parse_condition_dict(query_dict.get('where', {}))
        order_by = query_dict.get('order_by')
        limit = query_dict.get('limit')
        offset = query_dict.get('offset')
        group_by = query_dict.get('group_by')
        having_ast = self.parser.parse_condition_dict(query_dict.get('having', {}))
        
        fields_sql = ', '.join(fields) if fields != ['*'] else '*'
        
        sql_parts = [f"SELECT {fields_sql} FROM {table_name}"]
        params = []
        
        # 处理联表查询
        for join in joins:
            join_sql, join_params = self._generate_join_clause(join)
            sql_parts.append(join_sql)
            params.extend(join_params)
        
        if where_ast and where_ast.children:
            where_sql, where_params = self._generate_where_clause(where_ast)
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)
        
        if group_by:
            group_fields = ', '.join(group_by) if isinstance(group_by, list) else group_by
            sql_parts.append(f"GROUP BY {group_fields}")
            
            if having_ast and having_ast.children:
                having_sql, having_params = self._generate_where_clause(having_ast)
                sql_parts.append(f"HAVING {having_sql}")
                params.extend(having_params)
        
        if order_by:
            sql_parts.append(f"ORDER BY {order_by}")
        
        if limit is not None:
            limit_sql = f"LIMIT {limit}"
            if offset is not None:
                limit_sql += f" OFFSET {offset}"
            sql_parts.append(limit_sql)
        
        return " ".join(sql_parts), params
    
    def dict_to_insert(self, insert_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """将字典转换为INSERT语句"""
        table_name = insert_dict.get('table')
        if not table_name:
            raise ValueError("Table name is required in insert_dict")
            
        data = insert_dict.get('data', {})
        if not data:
            raise ValueError("Insert data is required")
        
        fields = list(data.keys())
        placeholders = ['?' for _ in fields]
        values = list(data.values())
        
        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        return sql, values
    
    def dict_to_update(self, update_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """将字典转换为UPDATE语句"""
        table_name = update_dict.get('table')
        if not table_name:
            raise ValueError("Table name is required in update_dict")
            
        updates = update_dict.get('set', {})
        where_ast = self.parser.parse_condition_dict(update_dict.get('where', {}))
        
        if not updates:
            raise ValueError("Update data is required")
        
        update_parts = []
        params = []
        
        for field, value in updates.items():
            if isinstance(value, dict):
                # 处理复杂表达式，如位运算
                update_expr, expr_params = self._generate_set_expression(field, value)
                update_parts.append(update_expr)
                params.extend(expr_params)
            else:
                # 处理简单值
                update_parts.append(f"{field} = ?")
                params.append(value)
        
        update_sql = ", ".join(update_parts)
        
        sql = f"UPDATE {table_name} SET {update_sql}"
        
        if where_ast and where_ast.children:
            where_sql, where_params = self._generate_where_clause(where_ast)
            sql += f" WHERE {where_sql}"
            params.extend(where_params)
        
        return sql, params
    
    def dict_to_delete(self, delete_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """将字典转换为DELETE语句"""
        table_name = delete_dict.get('table')
        if not table_name:
            raise ValueError("Table name is required in delete_dict")
            
        where_ast = self.parser.parse_condition_dict(delete_dict.get('where', {}))
        
        sql = f"DELETE FROM {table_name}"
        params = []
        
        if where_ast and where_ast.children:
            where_sql, where_params = self._generate_where_clause(where_ast)
            sql += f" WHERE {where_sql}"
            params.extend(where_params)
        
        return sql, params
    
    def dict_to_count(self, count_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """将字典转换为COUNT语句"""
        table_name = count_dict.get('table')
        if not table_name:
            raise ValueError("Table name is required in count_dict")
            
        where_ast = self.parser.parse_condition_dict(count_dict.get('where', {}))
        
        sql = f"SELECT COUNT(*) FROM {table_name}"
        params = []
        
        if where_ast and where_ast.children:
            where_sql, where_params = self._generate_where_clause(where_ast)
            sql += f" WHERE {where_sql}"
            params.extend(where_params)
        
        return sql, params
    
    def _generate_where_clause(self, ast: ASTNode) -> Tuple[str, List[Any]]:
        """生成WHERE子句"""
        if ast.node_type == 'AND':
            # 检查是否包含OR子节点
            or_children = [child for child in ast.children if child.node_type == 'OR']
            if or_children and len(ast.children) > 1:
                # 有OR子节点的特殊情况，使用OR连接
                parts = []
                params = []
                
                # 处理AND条件
                and_conditions = [child for child in ast.children if child.node_type != 'OR']
                if and_conditions:
                    and_parts = []
                    for child in and_conditions:
                        clause, child_params = self._generate_where_clause(child)
                        and_parts.append(f"({clause})")
                        params.extend(child_params)
                    if and_parts:
                        parts.append(" AND ".join(and_parts))
                
                # 处理OR条件
                for or_child in or_children:
                    clause, or_params = self._generate_where_clause(or_child)
                    parts.append(f"({clause})")
                    params.extend(or_params)
                
                return " OR ".join(parts), params
            else:
                return self._generate_logical_clause(ast, 'AND')
        elif ast.node_type == 'OR':
            return self._generate_logical_clause(ast, 'OR')
        else:
            return self._generate_condition_clause(ast)
    
    def _generate_logical_clause(self, ast: ASTNode, op: str) -> Tuple[str, List[Any]]:
        """生成逻辑操作符子句"""
        parts = []
        params = []
        
        for child in ast.children:
            clause, child_params = self._generate_where_clause(child)
            parts.append(f"({clause})")
            params.extend(child_params)
        
        return f" {op} ".join(parts), params
    
    def _generate_join_clause(self, join_config: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """生成JOIN子句"""
        join_type = join_config.get('type', 'INNER')
        table = join_config.get('table')
        on_conditions = join_config.get('on', {})
        
        if not table:
            raise ValueError("JOIN table name is required")
        
        # 标准化JOIN类型
        join_type = join_type.upper()
        if join_type not in {'INNER', 'LEFT', 'RIGHT', 'FULL'}:
            raise ValueError(f"Invalid JOIN type: {join_type}. Must be one of: INNER, LEFT, RIGHT, FULL")
        
        # 生成ON条件 - 直接处理字段引用，不参数化
        if on_conditions:
            parts = []
            params = []
            
            for left_field, condition in on_conditions.items():
                if isinstance(condition, dict):
                    for op, right_field in condition.items():
                        if op == '=':
                            parts.append(f"{left_field} = {right_field}")
                        else:
                            parts.append(f"{left_field} {op} {right_field}")
                else:
                    # 处理简单的等值条件
                    parts.append(f"{left_field} = {condition}")
            
            on_sql = " AND ".join(parts)
            return f"{join_type} JOIN {table} ON {on_sql}", params
        
        # 如果没有ON条件，返回基本的JOIN
        return f"{join_type} JOIN {table}", []

    def _generate_set_expression(self, field: str, expr_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """生成SET子句的复杂表达式"""
        params = []
        
        # 支持的操作符映射
        op_map = {
            '&': '&',
            '|': '|',
            '^': '^',
            '&~': '& ~',
            '<<': '<<',
            '>>': '>>',
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/'
        }
        
        for op, value in expr_dict.items():
            if op in op_map:
                sql_op = op_map[op]
                # 其他位运算和算术运算
                expression = f"{field} = {field} {sql_op} ?"
                params.append(value)
                return expression, params
        
        # 如果操作符不被支持，抛出异常
        supported_ops = ', '.join(op_map.keys())
        actual_ops = ', '.join(expr_dict.keys())
        raise ValueError(f"Unsupported SET expression operators: {actual_ops}. Supported operators: {supported_ops}")

    def _generate_condition_clause(self, ast: ASTNode) -> Tuple[str, List[Any]]:
        """生成条件子句"""
        if ast.node_type == 'CUSTOM_EXPR':
            # 处理自定义表达式，如位运算
            if len(ast.children) >= 2:
                field_node = ast.children[0]
                value_node = ast.children[1]
                
                field_expr = field_node.value
                values = value_node.value
                
                # 支持多个参数的情况
                if isinstance(values, list):
                    return field_expr, values
                else:
                    return field_expr, [values]
            return "", []
        
        if len(ast.children) < 2:
            return "", []
        
        field_node = ast.children[0]
        value_node = ast.children[1]
        
        field = field_node.value
        value = value_node.value
        
        op_map = {
            'EQ': '=',
            'NE': '!=',
            'GT': '>',
            'GE': '>=',
            'LT': '<',
            'LE': '<=',
            'LIKE': 'LIKE',
            'IN': 'IN',
            'NOT_IN': 'NOT IN',
            'IS_NULL': 'IS NULL',
            'IS_NOT_NULL': 'IS NOT NULL'
        }
        
        op = op_map.get(ast.node_type)
        if op is None:
            supported_ops = ', '.join(op_map.keys())
            raise ValueError(f"Unsupported condition operator: {ast.node_type}. Supported operators: {supported_ops}")
        
        if op == 'IN' or op == 'NOT_IN':
            placeholders = ', '.join(['?' for _ in value])
            return f"{field} {op} ({placeholders})", list(value)
        elif op == 'IS NULL' or op == 'IS NOT NULL':
            return f"{field} {op}", []
        else:
            return f"{field} {op} ?", [value]


class QueryBuilder:
    """查询构建器，提供链式调用接口"""
    
    def __init__(self, table_name: str = None):
        self.table_name = table_name
        self.query_dict = {}
    
    def select(self, *fields):
        """选择字段"""
        if fields:
            self.query_dict['fields'] = list(fields)
        return self
    
    def join(self, table: str, on: Dict[str, Any], join_type: str = 'INNER'):
        """添加JOIN联表查询"""
        if 'joins' not in self.query_dict:
            self.query_dict['joins'] = []
        
        join_config = {
            'type': join_type,
            'table': table,
            'on': on
        }
        self.query_dict['joins'].append(join_config)
        return self
    
    def inner_join(self, table: str, on: Dict[str, Any]):
        """添加INNER JOIN"""
        return self.join(table, on, 'INNER')
    
    def left_join(self, table: str, on: Dict[str, Any]):
        """添加LEFT JOIN"""
        return self.join(table, on, 'LEFT')
    
    def right_join(self, table: str, on: Dict[str, Any]):
        """添加RIGHT JOIN"""
        return self.join(table, on, 'RIGHT')
    
    def full_join(self, table: str, on: Dict[str, Any]):
        """添加FULL JOIN"""
        return self.join(table, on, 'FULL')
    
    def where(self, **conditions):
        """添加WHERE条件"""
        self.query_dict['where'] = conditions
        return self
    
    def where_or(self, *conditions):
        """添加OR条件"""
        if 'OR' not in self.query_dict:
            self.query_dict['OR'] = []
        self.query_dict['OR'].extend(conditions)
        return self
    
    def where_and(self, *conditions):
        """添加AND条件"""
        if 'AND' not in self.query_dict:
            self.query_dict['AND'] = []
        self.query_dict['AND'].extend(conditions)
        return self
    
    def order_by(self, field: str):
        """排序"""
        self.query_dict['order_by'] = field
        return self
    
    def group_by(self, *fields):
        """分组"""
        self.query_dict['group_by'] = list(fields)
        return self
    
    def having(self, **conditions):
        """添加HAVING条件"""
        self.query_dict['having'] = conditions
        return self
    
    def limit(self, limit: int, offset: int = None):
        """限制结果数量"""
        self.query_dict['limit'] = limit
        if offset is not None:
            self.query_dict['offset'] = offset
        return self
    
    def to_sql(self) -> Tuple[str, List[Any]]:
        """生成SQL"""
        if self.table_name:
            self.query_dict['table'] = self.table_name
        generator = DMLGenerator()
        return generator.dict_to_select(self.query_dict)
    
    def insert(self, **data):
        """插入数据"""
        if self.table_name:
            self.query_dict['table'] = self.table_name
        self.query_dict['data'] = data
        generator = DMLGenerator()
        return generator.dict_to_insert(self.query_dict)
    
    def update(self, **updates):
        """更新数据"""
        if self.table_name:
            self.query_dict['table'] = self.table_name
        self.query_dict['set'] = updates
        generator = DMLGenerator()
        return generator.dict_to_update(self.query_dict)
    
    def delete(self):
        """删除数据"""
        if self.table_name:
            self.query_dict['table'] = self.table_name
        generator = DMLGenerator()
        return generator.dict_to_delete(self.query_dict)


# 快捷函数
def select(**kwargs) -> Tuple[str, List[Any]]:
    """快速构建SELECT查询"""
    generator = DMLGenerator()
    return generator.dict_to_select(kwargs)


def insert(**data) -> Tuple[str, List[Any]]:
    """快速构建INSERT语句"""
    generator = DMLGenerator()
    return generator.dict_to_insert({'data': data, **data})


def update(**kwargs) -> Tuple[str, List[Any]]:
    """快速构建UPDATE语句"""
    generator = DMLGenerator()
    return generator.dict_to_update(kwargs)


def delete(**conditions) -> Tuple[str, List[Any]]:
    """快速构建DELETE语句"""
    generator = DMLGenerator()
    return generator.dict_to_delete({'where': conditions, **conditions})


def count(**conditions) -> Tuple[str, List[Any]]:
    """快速构建COUNT查询"""
    generator = DMLGenerator()
    return generator.dict_to_count({'where': conditions, **conditions})