import sys
import os


class luamaker:
    """
    lua 处理器
    """
    @staticmethod
    def makeLuaTable(table):
        """
        table 转换为 lua table 字符串
        """
        _tableMask = {}
        _keyMask = {}

        def analysisTable(_table, _indent, _parent):
            if isinstance(_table, tuple):
                _table = list(_table)
            if isinstance(_table, list):
                _table = dict(zip(range(1, len(_table) + 1), _table))
            if isinstance(_table, dict):
                _tableMask[id(_table)] = _parent
                cell = []
                thisIndent = _indent + "    "
                for k in _table:
                    if sys.version_info[0] == 2:
                        if type(k) not in [int, float, bool, list, dict, tuple]:
                            k = k.encode()

                    if not (isinstance(k, str) or isinstance(k, int) or isinstance(k, float)):
                        return
                    key = isinstance(
                        k, int) and "[" + str(k) + "]" or "[\"" + str(k) + "\"]"
                    if _parent + key in _keyMask.keys():
                        return
                    _keyMask[_parent + key] = True
                    var = None
                    v = _table[k]
                    if sys.version_info[0] == 2:
                        if type(v) not in [int, float, bool, list, dict, tuple]:
                            v = v.encode()
                    if isinstance(v, str):
                         # print("lua", var)
                        v = v.replace("\\", "\\\\")
                        v = v.replace("\"", "\\\"")
                        var = "\"" + v + "\""

                    elif isinstance(v, bool):
                        var = v and "true" or "false"
                    elif isinstance(v, int) or isinstance(v, float):
                        var = str(v)
                    else:
                        var = analysisTable(v, thisIndent, _parent + key)

                    cell.append(thisIndent + key + " = " + str(var))
                lineJoin = ",\n"
                return "{\n" + lineJoin.join(cell) + "\n" + _indent + "}"
            else:
                pass
        return analysisTable(table, "", "root")
