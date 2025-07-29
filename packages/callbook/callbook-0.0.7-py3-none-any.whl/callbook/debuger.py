import linecache
import os
from pathlib import Path


class FunctionData:
    def __init__(self) -> None:
        self.functionName = ''     # 函数名
        self.fileName = ''         # 文件名
        self.startLineNumber = 0   # 函数开始行
        self.endLineNumber = 0     # 函数结束行
        self.annotations = {}      # 源代码行注释
        self.comment = ''          # 源代码全局注释
        self.source = ''           # 源代码
        self.comment_delete_flag = False
        self.annotations_delete_flag = False

    def content(self) -> str:
        # 确定函数名所在的行
        arr = self.functionName.split('!')
        if len(arr) < 2:
            raise ValueError("函数名不是module!function形式")  # Changed to raise an exception
        functionName = arr[1]  # 去掉!前的模块名称
        # 可能带namespace，而namespace很可能不包含在函数名所在的
        functionName = functionName.split('::')[-1] + '('

        if not self.fileName:
            raise FileNotFoundError("没有找到文件路径")  # Changed to raise an exception
        
        file_path = self.fileName
        if not Path(file_path).exists():
            file_path = self.adjust_filepath(file_path)
            if not file_path:
                raise FileNotFoundError(f"没有找到文件 {self.fileName}")  # Changed to raise an exception

        nCount = 20
        for i in range(self.startLineNumber, 0, -1):
            line = linecache.getline(file_path, i)
            nCount -= 1
            if functionName in line or nCount == 0:  # 最多往上搜索20行
                break

        lines = []
        for i in range(i, self.endLineNumber + 1):
            line = linecache.getline(file_path, i)
            lines.append(line)

        return ''.join(lines)
    
    def adjust_filepath(self, filename: str) -> str:
        setting_paths = self.get_nt_source_paths()
        if not setting_paths:
            return ''

        parts = filename.split('\\')
        count = len(parts)
        for index, part in enumerate(parts):
            for path in setting_paths:
                parts[index] = path
                fullpath = "\\".join(parts[index - count:])
                if Path(fullpath).exists():
                    return fullpath
        return ''
    
    def get_nt_source_paths(self) -> list:
        source_path = os.environ.get('_NT_SOURCE_PATH')
        paths = []
        if source_path:
            paths = source_path.split(';')
        return paths

    def assign(self, o: dict) -> None:
        self.__dict__ = o

    def __repr__(self):
        return f"<FunctionData: {self.functionName}: {self.fileName} ({self.startLineNumber} - {self.endLineNumber})>"


class BreakPointHit:
    def __init__(self) -> None:
        self.id = 0                # id号
        self.startOffset = 0       # 函数入口偏移量
        self.offset = 0            # Instruction Offset
        self.functionName = ''     # 函数名
        self.threadId = 0          # 线程Id
        self.lineNumber = 0        # callstack中当前行

    def __repr__(self):
        return f"<common.BreakPointHit startOffset:{self.startOffset}, functionName:{self.functionName}>"

    def assign(self, o: dict) -> None:
        """
        Assign the value by the dictionary
        """
        self.__dict__ = o
