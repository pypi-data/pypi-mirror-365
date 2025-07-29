import sqlite3
from .call import Call, CallData, FunctionData


class Database:
    def __init__(self, db_name: str):
        """初始化数据库连接"""
        try:
            self.db = sqlite3.connect(db_name)
            self._execute_query("pragma synchronous = off")
            self._execute_query("pragma foreign_keys = off")
            self._execute_query("pragma journal_mode = WAL")
            self._execute_query("pragma temp_store = MEMORY")
        except sqlite3.Error as e:
            raise RuntimeError(f"无法打开数据库: {e}")

    def __del__(self):
        """关闭数据库连接"""
        self.db.close()

    def begin_transaction(self):
        """开始事务"""
        self._execute_query("BEGIN TRANSACTION")

    def commit_transaction(self):
        """提交事务"""
        self._execute_query("COMMIT")

    def rollback_transaction(self):
        """回滚事务"""
        self._execute_query("ROLLBACK")

    def _execute_query(self, query: str):
        """执行SQL查询"""
        try:
            cursor = self.db.cursor()
            cursor.execute(query)
            self.db.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"SQL错误: {e}")

    def create_table(self):
        """创建数据表"""
        sql_functions = """
            CREATE TABLE IF NOT EXISTS functions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT NOT NULL,
                file_name TEXT NOT NULL, 
                start_line_number INTEGER NOT NULL,
                end_line_number INTEGER NOT NULL,
                start_offset INTEGER NOT NULL UNIQUE,
                end_offset INTEGER NOT NULL,
                source TEXT,
                comment TEXT
            )
        """

        sql_calls = """
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                offset INTEGER NOT NULL,
                line_number INTEGER NOT NULL,
                thread_id INTEGER NOT NULL,
                parent_id INTEGER,
                function_id INTEGER,
                FOREIGN KEY(parent_id) REFERENCES calls(id),
                FOREIGN KEY(function_id) REFERENCES functions(id)
            )
        """

        sql_annotations = """
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_number INTEGER NOT NULL,
                annotation TEXT,
                function_id INTEGER NOT NULL,
                FOREIGN KEY(function_id) REFERENCES functions(id)
            )
        """

        self._execute_query(sql_functions)
        self._execute_query(sql_calls)
        self._execute_query(sql_annotations)

    def save_call(self, call: Call):
        """保存函数调用"""
        try:
            self.begin_transaction()
            self._execute_query("DELETE FROM calls")
            self._execute_query("DELETE FROM functions")
            self._save_call_imp(call)
            self.commit_transaction()
        except Exception as e:
            self.rollback_transaction()
            raise RuntimeError(f"保存函数调用时出错: {e}")

    def _save_call_imp(self, call: Call, parent_id: int = -1):
        """递归保存函数调用及其子调用"""
        call_id = -1
        if not call.is_header():
            call_id = self._insert_call(call, parent_id)

        for subcall in call.subcalls:
            self._save_call_imp(subcall, call_id)

    def _insert_call(self, call: Call, parent_id: int = -1) -> int:
        """插入函数调用到数据库"""
        data: CallData = call.data

        # 读取源代码
        if call.function.source is None:
            try:
                source = call.function.content()
                if source:
                    call.function.source = source
            except Exception as e:
                print(f"无法读取源代码: {e}")

        # 插入function记录
        sql_function = f"""
            INSERT OR IGNORE INTO functions 
            (function_name, file_name, start_line_number, end_line_number,
             start_offset, end_offset, source, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor = self.db.cursor()
        cursor.execute(sql_function, (
            data.func.name, data.func.filename,
            data.func.start_line_number, data.func.end_line_number,
            data.func.start_offset, data.func.end_offset,
            data.func.source, data.func.comment
        ))

        # 获取function_id
        cursor.execute(
            "SELECT id FROM functions WHERE start_offset = ?",
            (data.func.start_offset,)
        )
        function_id = cursor.fetchone()[0]

        # 插入annotation记录
        sql_annotation = """
            INSERT INTO annotations 
            (line_number, annotation, function_id)
            VALUES (?, ?, ?)
        """
        for line_number, annotation in data.func.annotations.items():
            cursor.execute(sql_annotation, (
                line_number, annotation, function_id
            ))

        # 插入call记录
        sql_call = """
            INSERT INTO calls 
            (offset, line_number, thread_id, parent_id, function_id)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(sql_call, (
            data.offset, data.line_number, data.thread_id,
            parent_id, function_id
        ))

        return cursor.lastrowid

    def get_call_count(self) -> int:
        """获取调用次数"""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM calls")
        return cursor.fetchone()[0]

    def load_call(self) -> Call:
        """从数据库加载函数调用信息"""
        # 获取所有annotations
        sql_annotations = """
            SELECT function_id, line_number, annotation
            FROM annotations
        """
        cursor = self.db.cursor()
        cursor.execute(sql_annotations)
        annotations_map = {}
        for func_id, line_number, annotation in cursor.fetchall():
            if func_id not in annotations_map:
                annotations_map[func_id] = {}
            annotations_map[func_id][line_number] = annotation

        # 修改主查询，添加function_id
        sql = """
            SELECT c.id, f.id as function_id, f.function_name, f.file_name, c.offset,
                   f.start_line_number, f.end_line_number,
                   f.start_offset, f.end_offset, f.source, f.comment,
                   c.line_number, c.thread_id, c.parent_id
            FROM calls c
            JOIN functions f ON c.function_id = f.id
        """

        cursor.execute(sql)
        header_node = Call.create_header()
        call_map = {}
        func_map = {}

        for row in cursor.fetchall():
            (id, function_id, func_name, file_name, offset, start_line, end_line,
             start_offset, end_offset, source, comment, line_number, thread_id, parent_id) = row
            
            if start_offset not in func_map:
                # 获取该函数的annotations
                annotations = annotations_map.get(function_id, {})
                
                func_map[start_offset] = FunctionData(
                    name=func_name,
                    filename=file_name,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    start_line_number=start_line,
                    end_line_number=end_line,
                    source=source,
                    comment=comment,
                    annotations=annotations
                )
            
            data = CallData(
                func=func_map[start_offset],
                offset=offset,
                line_number=line_number,
                thread_id=thread_id
            )

            call = Call.create(data)
            call.set_id(id)
            call_map[id] = call

            if parent_id in (-1, 0):
                header_node.add_subcall(call)
            elif parent_id in call_map:
                call_map[parent_id].add_subcall(call)

        return header_node
