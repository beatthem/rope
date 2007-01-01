import compiler
import rope.base.pyobjects
import rope.base.pynames
import rope.base.exceptions


class StatementEvaluator(object):

    def __init__(self, scope):
        self.scope = scope
        self.result = None

    def visitName(self, node):
        self.result = self.scope.lookup(node.name)
    
    def visitGetattr(self, node):
        pyname = StatementEvaluator.get_statement_result(self.scope, node.expr)
        if pyname is not None:
            try:
                self.result = pyname.get_object().get_attribute(node.attrname)
            except rope.base.exceptions.AttributeNotFoundException:
                self.result = None

    def visitCallFunc(self, node):
        pyobject = self._get_object_for_node(node.node)
        if pyobject is None:
            return
        if pyobject.get_type() == rope.base.pyobjects.PyObject.get_base_type('Type'):
            self.result = rope.base.pynames.AssignedName(
                pyobject=rope.base.pyobjects.PyObject(type_=pyobject))
        elif pyobject.get_type() == rope.base.pyobjects.PyObject.get_base_type('Function'):
            self.result = rope.base.pynames.AssignedName(
                pyobject=pyobject._get_returned_object())
        elif '__call__' in pyobject.get_attributes():
            call_function = pyobject.get_attribute('__call__')
            self.result = rope.base.pynames.AssignedName(
                pyobject=call_function.get_object()._get_returned_object())
    
    def visitConst(self, node):
        if isinstance(node.value, (str, unicode)):
            self.result = rope.base.pynames.AssignedName(
                pyobject=rope.base.builtins.get_str())
            
    def visitAdd(self, node):
        pass
    
    def visitAnd(self, node):
        pass

    def visitBackquote(self, node):
        pass

    def visitBitand(self, node):
        pass

    def visitBitor(self, node):
        pass

    def visitXor(self, node):
        pass

    def visitCompare(self, node):
        pass
    
    def visitDict(self, node):
        keys = None
        values = None
        if node.items:
            item = node.items[0]
            keys = self._get_object_for_node(item[0])
            values = self._get_object_for_node(item[1])
        self.result = rope.base.pynames.AssignedName(
            pyobject=rope.base.builtins.get_dict(keys, values))
    
    def visitFloorDiv(self, node):
        pass
    
    def visitList(self, node):
        holding = None
        if node.nodes:
            holding = self._get_object_for_node(node.nodes[0])
        self.result = rope.base.pynames.AssignedName(
            pyobject=rope.base.builtins.get_list(holding))
    
    def visitListComp(self, node):
        pass

    def visitMul(self, node):
        pass
    
    def visitNot(self, node):
        pass
    
    def visitOr(self, node):
        pass
    
    def visitPower(self, node):
        pass
    
    def visitRightShift(self, node):
        pass
    
    def visitLeftShift(self, node):
        pass
    
    def visitSlice(self, node):
        self._call_function(node.expr, '__getslice__')
    
    def visitSliceobj(self, node):
        pass
    
    def visitTuple(self, node):
        objects = []
        if len(node.nodes) < 4:
            for stmt in node.nodes:
                pyobject = self._get_object_for_node(stmt)
                objects.append(pyobject)
        else:
            objects.append(self._get_object_for_node(node.nodes[0]))
        self.result = rope.base.pynames.AssignedName(
            pyobject=rope.base.builtins.get_tuple(*objects))

    def _get_object_for_node(self, stmt):
        pyname = StatementEvaluator.get_statement_result(self.scope, stmt)
        pyobject = None
        if pyname is not None:
            pyobject = pyname.get_object()
        return pyobject
    
    def visitSubscript(self, node):
        self._call_function(node.expr, '__getitem__')

    def _call_function(self, node, function_name):
        pyobject = self._get_object_for_node(node)
        if pyobject is None:
            return
        if function_name in pyobject.get_attributes():
            call_function = pyobject.get_attribute(function_name)
            self.result = rope.base.pynames.AssignedName(
                pyobject=call_function.get_object()._get_returned_object())

    @staticmethod
    def get_statement_result(scope, node):
        evaluator = StatementEvaluator(scope)
        compiler.walk(node, evaluator)
        return evaluator.result
    
    @staticmethod
    def get_string_result(scope, string):
        evaluator = StatementEvaluator(scope)
        node = compiler.parse(string)
        compiler.walk(node, evaluator)
        return evaluator.result
