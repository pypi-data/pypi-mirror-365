from dataclasses import dataclass
from typing import List, Callable, Optional
from pathlib import Path
import os
import chardet


@dataclass
class FunctionData:
    """
    存储函数调用相关的数据

    属性:
        name: 函数名称，格式为 "module!function"
        filename: 源文件路径
        offset: 函数在程序中的偏移量
        start_offset: 函数开始位置的偏移量
        end_offset: 函数结束位置的偏移量
        start_line_number: 函数定义开始的行号
        end_line_number: 函数定义结束的行号
        source: 源代码内容
        comment: 函数注释
        annotations: 函数注解
    """
    name: str = ""
    filename: str = ""
    start_offset: int = 0
    end_offset: int = 0
    start_line_number: int = 0
    end_line_number: int = 0
    source: str = ""
    comment: str = ""
    annotations: dict = None

    def content(self) -> str:
        """获取函数的源代码内容"""
        # 确定函数名所在的行
        arr = self.name.split('!')
        if len(arr) < 2:
            # Changed to raise an exception
            raise ValueError("函数名不是module!function形式")
        name = arr[1]  # 去掉!前的模块名称
        # 可能带namespace，而namespace很可能不包含在函数名所在的
        name = name.split('::')[-1] + '('

        if not self.filename:
            # Changed to raise an exception
            raise FileNotFoundError("没有找到文件路径")

        file_path = self.filename
        if not Path(file_path).exists():
            file_path = self._adjust_filepath(file_path)
            if not file_path:
                # Changed to raise an exception
                raise FileNotFoundError(f"没有找到文件 {self.filename}")
            
        charset = self.get_file_encoding(file_path)
        print(f"文件编码格式: {charset}")

        # 使用检测到的字符编码读取文件内容
        try:
            with open(file_path, 'r', encoding=charset or 'utf-8') as f:
                all_lines = f.readlines()
        except (UnicodeDecodeError, UnicodeError):
            # 如果编码检测失败，尝试使用UTF-8
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()

        # 确定函数名所在的行
        max_search_lines = 20  # 表示最大搜索行数
        start_search_line = max(0, self.start_line_number - 1)  # 转换为0索引
        
        # 向上搜索函数定义
        function_start_line = start_search_line
        for i in range(start_search_line, max(-1, start_search_line - max_search_lines), -1):
            if i < len(all_lines) and name in all_lines[i]:
                function_start_line = i
                break
            elif i == max(0, start_search_line - max_search_lines + 1):
                function_start_line = i

        # 提取函数内容
        end_line = min(self.end_line_number, len(all_lines))  # 转换为0索引并确保不超出范围
        lines = all_lines[function_start_line:end_line]

        return ''.join(lines)
    
    # --- 检测函数 ---
    def get_file_encoding(self, file_path):
        """
        检测文件编码格式。
        注意：必须以二进制模式('rb')打开文件，否则会出错。
        """
        try:
            with open(file_path, 'rb') as f:
                # 读取文件的前N个字节进行检测，对于大文件可以提高效率
                # 如果文件很小，可以直接 f.read()
                raw_data = f.read(1024) 
                result = chardet.detect(raw_data)
                
                encoding = result['encoding']
                confidence = result['confidence']
                
                print(f"文件 '{file_path}' 的检测结果:")
                print(f"  - 编码: {encoding}")
                print(f"  - 置信度: {confidence:.2f}")
                
                if confidence < 0.9:
                    print("  - 警告: 置信度较低，结果可能不准确。")
                    
                return encoding
                
        except FileNotFoundError:
            print(f"错误：文件 '{file_path}' 未找到。")
            return None

    def _adjust_filepath(self, filename: str) -> str:
        setting_paths = self._get_nt_source_paths()
        if not setting_paths:
            return ''

        parts = filename.split('\\')
        count = len(parts)
        for index, _ in enumerate(parts):
            for path in setting_paths:
                parts[index] = path
                fullpath = "\\".join(parts[index - count:])
                if Path(fullpath).exists():
                    return fullpath
        return ''

    def _get_nt_source_paths(self) -> list:
        source_path = os.environ.get('_NT_SOURCE_PATH')
        paths = []
        if source_path:
            paths = source_path.split(';')
        return paths


@dataclass
class CallData:
    id: int = -1
    func: FunctionData = None
    offset: int = 0
    line_number: int = 0
    thread_id: int = 0


class Call:
    """
    表示一个函数调用节点，可以构建调用树结构

    属性:
        m_id: 调用节点的唯一标识符
        m_is_header: 是否为头节点（根节点）
        m_call_data: 函数相关数据
        m_subcalls: 子调用列表
    """

    def __init__(self, call_data: CallData):
        self.m_id: int = -1
        self.m_is_header: bool = False
        self.m_call_data: CallData = call_data
        self.m_subcalls: List['Call'] = []

    @classmethod
    def create_header(cls) -> 'Call':
        """创建一个头节点（根节点）"""
        call = cls(CallData())
        call.m_is_header = True
        return call

    @classmethod
    def create(cls, data: CallData) -> 'Call':
        """使用函数数据创建一个调用节点"""
        return cls(data)

    def set_id(self, n_id: int) -> None:
        """设置节点ID"""
        self.m_id = n_id

    def get_id(self) -> int:
        """获取节点ID"""
        return self.m_id

    def is_leaf(self) -> bool:
        """判断是否为叶子节点（没有子调用）"""
        return len(self.m_subcalls) == 0

    def is_header(self) -> bool:
        """判断是否为头节点"""
        return self.m_is_header

    def add_subcall(self, subcall: 'Call') -> None:
        """添加一个子调用"""
        self.m_subcalls.append(subcall)

    def first_subcall(self) -> Optional['Call']:
        """获取第一个子调用"""
        if self.is_leaf():
            return None
        return self.m_subcalls[0]

    def get_number_subcalls(self) -> int:
        """获取子调用的数量"""
        return len(self.m_subcalls)

    def get_subcall(self, index: int) -> Optional['Call']:
        """获取指定索引的子调用"""
        if index < 0 or index >= len(self.m_subcalls):
            return None
        return self.m_subcalls[index]

    def append_list(self, call: 'Call') -> None:
        """将另一个调用树合并到当前调用树中"""
        if self != call:
            return

        if call.get_number_subcalls() > 1:
            raise RuntimeError("The call has one more sub calls")

        next_call = call.first_subcall()

        for sub_call in self.m_subcalls:
            if sub_call == next_call:
                sub_call.append_list(next_call)
                return

        if next_call is not None:
            self.m_subcalls.append(next_call)

    def create_tree(self) -> str:
        """生成调用树的字符串表示"""
        tree = []
        level = -1 if self.is_header() else 0
        self._create_tree(tree, level)
        return ''.join(tree)

    def _create_tree(self, tree: List[str], level: int) -> None:
        if not self.is_header():
            tree.append('\t' * level +
                        f"{self.m_id} {self.m_call_data.func.name}\n")

        for subcall in self.m_subcalls:
            subcall._create_tree(tree, level + 1)

    def display(self, level: int = 0) -> None:
        """以树形结构显示调用关系"""
        if not self.is_header():
            print(' ' * (level - 2) + '└ ' + self.m_call_data.func.name)

        for subcall in self.m_subcalls:
            subcall.display(level + 2)

    def traverse(self, visit: Callable[['Call'], None]) -> None:
        """遍历调用树，对每个节点执行访问函数"""
        if not self.is_header():
            visit(self)

        for subcall in self.m_subcalls:
            subcall.traverse(visit)

    def count(self) -> int:
        """计算调用树中的节点总数"""
        count = 0

        def increment_count(_: 'Call') -> None:
            nonlocal count
            count += 1
        self.traverse(increment_count)
        return count

    @property
    def data(self) -> CallData:
        """获取函数数据"""
        return self.m_call_data
    
    @property
    def function(self) -> FunctionData:
        """获取函数数据"""
        return self.m_call_data.func

    @property
    def subcalls(self) -> List['Call']:
        """获取子调用列表"""
        return self.m_subcalls
