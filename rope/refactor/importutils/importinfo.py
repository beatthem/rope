class ImportStatement(object):
    """Represent an import in a module

    `readonly` attribute controls whether this import can be changed
    by import actions or not.

    """

    def __init__(self, import_info, start_line, end_line,
                 main_statement=None, blank_lines=0):
        self.start_line = start_line
        self.end_line = end_line
        self.readonly = False
        self.main_statement = main_statement
        self._import_info = None
        self.import_info = import_info
        self._is_changed = False
        self.new_start = None
        self.blank_lines = blank_lines

    def _get_import_info(self):
        return self._import_info

    def _set_import_info(self, new_import):
        if not self.readonly and \
           new_import is not None and not new_import == self._import_info:
            self._is_changed = True
            self._import_info = new_import

    import_info = property(_get_import_info, _set_import_info)

    def get_import_statement(self):
        if True or self._is_changed or self.main_statement is None:
            return self.import_info.get_import_statement()
        else:
            return self.main_statement

    def empty_import(self):
        self.import_info = ImportInfo.get_empty_import()

    def move(self, lineno, blank_lines=0):
        self.new_start = lineno
        self.blank_lines = blank_lines

    def get_old_location(self):
        return self.start_line, self.end_line

    def get_new_start(self):
        return self.new_start

    def is_changed(self):
        return self._is_changed or (self.new_start is not None or
                                    self.new_start != self.start_line)

    def accept(self, visitor):
        return visitor.dispatch(self)


class ImportInfo(object):

    def get_imported_primaries(self, context):
        pass

    def get_imported_names(self, context):
        return [primary.split('.')[0]
                for primary in self.get_imported_primaries(context)]

    def get_import_statement(self):
        pass

    def is_empty(self):
        pass

    def __hash__(self):
        return hash(self.get_import_statement())

    def _are_name_and_alias_lists_equal(self, list1, list2):
        if len(list1) != len(list2):
            return False
        for pair1, pair2 in zip(list1, list2):
            if pair1 != pair2:
                return False
        return True

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.get_import_statement() == obj.get_import_statement()

    def __ne__(self, obj):
        return not self.__eq__(obj)

    @staticmethod
    def get_empty_import():
        return EmptyImport()


class NormalImport(ImportInfo):

    def __init__(self, names_and_aliases):
        self.names_and_aliases = names_and_aliases

    def get_imported_primaries(self, context):
        result = []
        for name, alias in self.names_and_aliases:
            if alias:
                result.append(alias)
            else:
                result.append(name)
        return result

    def get_import_statement(self):
        result = 'import '
        for name, alias in self.names_and_aliases:
            result += name
            if alias:
                result += ' as ' + alias
            result += ', '
        return result[:-2]

    def is_empty(self):
        return len(self.names_and_aliases) == 0


class FromImport(ImportInfo):

    def __init__(self, module_name, level, names_and_aliases):
        self.module_name = module_name
        self.level = level
        self.names_and_aliases = names_and_aliases

    def get_imported_primaries(self, context):
        if self.names_and_aliases[0][0] == '*':
            module = self.get_imported_module(context)
            return [name for name in module
                    if not name.startswith('_')]
        result = []
        for name, alias in self.names_and_aliases:
            if alias:
                result.append(alias)
            else:
                result.append(name)
        return result

    def get_imported_resource(self, context):
        """Get the imported resource

        Returns `None` if module was not found.
        """
        if self.level == 0:
            return context.pycore.find_module(
                self.module_name, folder=context.folder)
        else:
            return context.pycore.find_relative_module(
                self.module_name, context.folder, self.level)

    def get_imported_module(self, context):
        """Get the imported `PyModule`

        Raises `rope.base.exceptions.ModuleNotFoundError` if module
        could not be found.
        """
        if self.level == 0:
            return context.pycore.get_module(
                self.module_name, context.folder)
        else:
            return context.pycore.get_relative_module(
                self.module_name, context.folder, self.level)

    def get_import_statement(self):
        res_list = ['from ', '.' * self.level, self.module_name, ' import ']
        indent = int(len(self.names_and_aliases) > 1)
        if indent:
            res_list.append('(')
        # result = 'from ' + '.' * self.level + self.module_name + ' import '
        last_line_char_num = 0
        if not indent:
            # Only one import - but we need to be ensured that
            # it doesn't breaks 79 characters limit
            prefix = ''.join(res_list)
            res_list0 = []
            for name, alias in self.names_and_aliases:
                res_list0.append(name)
                if alias:
                    res_list0.extend([' as ', alias])
                postfix = ''.join(res_list0)
                if len(prefix) + len(postfix) > 79:
                    prefix += '(\n'
                    postfix = 4 * ' ' + postfix + ')'
                return prefix + postfix

        for name, alias in self.names_and_aliases:
            print name, alias
            res_list1 = []
            if (
                indent and
                (
                    not last_line_char_num or
                    (last_line_char_num + len(name)) > 79
                )
            ):
                # if res_list[-1] != '\n':
                if res_list[-1] == ' ':
                    res_list = res_list[:-1]
                res_list1.append('\n')
                res_list1.append(4 * ' ')
                last_line_char_num = 5
                print last_line_char_num, '179'
            res_list1.append(name)
            last_line_char_num += len(name)
            print last_line_char_num, '185'
            if alias:
                res_list1.extend([' as ', alias])
                last_line_char_num += (4 + len(alias))
            res_list1.append(',')
            last_line_char_num += 1
            print last_line_char_num, 191
            if last_line_char_num >= 79:
                # res_list1.insert(0, '\n')
                last_line_char_num = 0
                print 0, 195
            else:
                res_list1.append(' ')
                last_line_char_num += 1
                print last_line_char_num, 199
            res_list.extend(res_list1)
            # ('\n' if indent else ' ')
        result = ''.join(res_list[:-2]) + indent * ')'
        return result

    def is_empty(self):
        return len(self.names_and_aliases) == 0

    def is_star_import(self):
        return len(self.names_and_aliases) > 0 and \
               self.names_and_aliases[0][0] == '*'


class EmptyImport(ImportInfo):

    names_and_aliases = []

    def is_empty(self):
        return True

    def get_imported_primaries(self, context):
        return []


class ImportContext(object):

    def __init__(self, pycore, folder):
        self.pycore = pycore
        self.folder = folder
