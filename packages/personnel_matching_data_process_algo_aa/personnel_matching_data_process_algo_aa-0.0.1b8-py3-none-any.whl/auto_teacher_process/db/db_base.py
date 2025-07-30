import os
import time
from abc import ABC, abstractmethod

import aiomysql
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm

from auto_teacher_process.config import Config
from auto_teacher_process.logger import setup_logger


class BaseDBProcessor(ABC):
    def __init__(self, logger=None, system="llm_processor", stage="unkonw_task_name"):
        """
        基类初始化
        实例变量:
        - debug_mode 调试模式
        - args: argparse.Namespace 解析后的命令行参数
        - logger: logging.Logger 日志记录器
        - db_engine: sqlalchemy.engine.base.Engine 数据库引擎
        - config_path: 数据库配置文件路径
        """
        self.logger = logger if logger else setup_logger(system=system, stage=stage)
        self.db_engine = None
        self.async_db_engine = None
        self._setup_db_engine()

    def _setup_db_engine(self) -> None:
        """
        初始化数据库引擎
        输入: 无
        输出: 无 (初始化实例变量 db_engine)
        """
        # self.logger.debug("初始化数据库引擎")
        try:
            db_config = Config.DB.MYSQL.DB_URL
            self.db_engine = create_engine(db_config)
            # self.logger.debug("数据库连接成功")
        except Exception as e:
            # self.logger.error(f"数据库连接失败: {e}", exc_info=True)
            raise ConnectionError(f"数据库连接失败:{e}")

    async def set_up_async_db_engine(self) -> None:
        """
        初始化异步数据库引擎
        输入: 无
        输出: 无 (初始化实例变量 async_db_engine)
        手动启停，使用完需要手动关闭引擎
        """
        try:
            self.async_db_engine = await aiomysql.create_pool(
                host=Config.DB.MYSQL.HOST,
                port=Config.DB.MYSQL.PORT,
                user=Config.DB.MYSQL.USER,
                password=Config.DB.MYSQL.PASSWORD,
                db=Config.DB.MYSQL.DATABASE,
                autocommit=True,
                minsize=1,
                maxsize=1000,
            )
        except Exception as e:
            raise ConnectionError(f"异步数据库连接失败:{e}")

    async def close_async_db_engine(self) -> None:
        """
        关闭异步数据库引擎
        输入: 无
        输出: 无
        """
        if self.async_db_engine:
            try:
                self.async_db_engine.close()
                await self.async_db_engine.wait_closed()
                self.async_db_engine = None
            except Exception as e:
                raise ConnectionError(f"异步数据库关闭失败:{e}")

    async def async_db_execute_query(self, sql, params=None, fetch_type="all", execute_type="query"):
        """
        通用异步数据库执行函数，支持查询、插入、更新、删除操作

        参数:
            sql: SQL语句
            params: 参数化查询参数 (默认: None)
            fetch_type: 查询结果获取方式 'all' 或 'one' (仅在 execute_type 为 'query' 时生效)
            execute_type: 操作类型 'query' 或 'execute'，默认为 'query'
        返回:
            查询结果（pd.DataFrame 或 单行数据）或受影响行数（int）
        """
        if not self.async_db_engine:
            raise ConnectionError("请先初始化异步数据库引擎")

        async with self.async_db_engine.acquire() as conn:
            async with conn.cursor() as cursor:
                if params:
                    await cursor.execute(sql, params)
                else:
                    await cursor.execute(sql)

                if execute_type == "query":
                    columns = [desc[0] for desc in cursor.description]
                    if fetch_type == "all":
                        results = await cursor.fetchall()
                        return pd.DataFrame(results, columns=columns)
                    elif fetch_type == "one":
                        result = await cursor.fetchone()
                        if result is None:
                            return pd.DataFrame([], columns=columns)
                        return pd.DataFrame([result], columns=columns)
                    else:
                        raise ValueError(f"无效的fetch_type: {fetch_type}")
                elif execute_type == "execute":
                    return pd.DataFrame([[cursor.rowcount]], columns=["rowcount"])
                else:
                    raise ValueError(f"无效的execute_type: {execute_type}")

    def _get_all_folders(self, file_dir: str, find_rule_str: str) -> pd.DataFrame:
        """
        获取路径下所有文件夹, 读取后返回pd.df
        输入:
            path (str): 目标路径
            find_rule_str (str): 文件名匹配规则
        输出:
            pd.DataFrame: 合并后的pd.df
        """
        self.logger.info(f"递归查找路径下所有包含'{find_rule_str}'的CSV文件:{file_dir}")
        merged_df = pd.DataFrame()

        # 使用os.walk递归遍历目录
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.endswith(".csv") and find_rule_str in file:
                    file_path = os.path.join(root, file)
                    try:
                        df = pd.read_csv(file_path)
                        merged_df = pd.concat([merged_df, df], ignore_index=True)
                        self.logger.info(f"成功读取文件: {file_path}")
                    except Exception as e:
                        self.logger.warning(f"读取文件{file_path}失败: {e}，跳过此文件")

        self.logger.info(f"合并数据总量: {len(merged_df)}")
        return merged_df

    def get_df(self, file_dir: str | pd.DataFrame) -> pd.DataFrame:
        if isinstance(file_dir, pd.DataFrame):
            return file_dir
        if not isinstance(file_dir, str):
            raise TypeError(f"[get_df] 参数 file_dir 必须是 str 或 pd.DataFrame，但收到类型: {type(file_dir)}")

        if not os.path.exists(file_dir):
            raise FileNotFoundError(f"[get_df] 找不到文件: {file_dir}")
        _, ext = os.path.splitext(file_dir.lower())

        try:
            if ext == ".csv":
                return pd.read_csv(file_dir)
            if ext in [".xlsx", ".xls"]:
                return pd.read_excel(file_dir)
            if ext == ".parquet":
                return pd.read_parquet(file_dir)
        except Exception as e:
            raise RuntimeError(f"[get_df] 加载文件失败: {file_dir}，错误: {e}")

    def _process_in_batches(
        self, data: pd.DataFrame, batch_size: int, progress_file: str, process_batch_func: callable, *args, **kwargs
    ) -> None:
        """
        批处理通用逻辑
        """
        total_records = len(data)
        self.logger.debug(f"批量处理数据总量: {total_records}:\n{data}")
        if total_records == 0:
            self.logger.debug("空数据集，跳过处理")
            return

        start_batch = 0
        if os.path.exists(progress_file):
            with open(progress_file) as f:
                start_batch = int(f.read().strip())

        total_batches = (total_records + batch_size - 1) // batch_size

        try:
            with self.db_engine.begin() as conn:
                for batch_num, start in tqdm(enumerate(range(0, total_records, batch_size)), total=total_batches):
                    if batch_num < start_batch:
                        continue

                    batch_df = data.iloc[start : start + batch_size]
                    try:
                        start_time = time.perf_counter()
                        process_batch_func(conn, batch_df, *args, **kwargs)

                        # 更新进度
                        with open(progress_file, "w") as f:
                            f.write(str(batch_num + 1))

                        end_time = time.perf_counter()
                        duration_ms = (end_time - start_time) * 1000
                        self.logger.info(
                            f"Batch {batch_num + 1} 处理成功，已处理 {start + len(batch_df)}/{total_records} 条记录",
                            extra={"event": "running", "duration_ms": duration_ms},
                        )
                    except Exception as e:
                        self.logger.error(f"Batch {batch_num + 1} 处理失败: {e}", exc_info=True)
                        raise e

            # 所有批次成功处理完成
            if os.path.exists(progress_file):
                os.remove(progress_file)
                self.logger.debug("所有批次处理成功。进度文件已删除。")

        except Exception as e:
            self.logger.error(f"常规错误: {e}", exc_info=True)
            raise e
        finally:
            self.db_engine.dispose()
            self.logger.debug("处理过程已完成。")

    def insert_db(
        self,
        df: pd.DataFrame,
        table_name: str,
        batch_size: int = 1000,
        progress_file: str = "insert_progress.txt",
        single_operation: bool = False,
    ) -> None:
        # TODO: 返回第一条和最后一条的主键id
        """
        插入数据到数据库
        输入:
            df (pd.DataFrame): 要插入的数据
            table_name (str): 目标表名
            batch_size (int): 批处理大小
            progress_file (str): 进度记录文件
            single_operation (bool): 是否单次操作
        输出: 无
        """
        self.logger.info(f"执行数据库插入，目标表名:{table_name}", extra={"event": "db"})

        def process_batch(conn, batch_df):
            batch_df.to_sql(name=table_name, con=conn, if_exists="append", index=False)

        # 1. 获取当前最大 ID
        if single_operation:
            self.logger.debug("执行单次操作")
            try:
                with self.db_engine.begin() as conn:
                    process_batch(conn, df)
            except Exception as e:
                self.logger.error(f"单次操作失败: {e}", exc_info=True)
                raise RuntimeError("单次操作失败")
        else:
            self._process_in_batches(
                data=df, batch_size=batch_size, progress_file=progress_file, process_batch_func=process_batch
            )
        self.logger.info(f"数据插入完成，目标表名:{table_name}", extra={"event": "db"})

    def get_db(self, query: str) -> pd.DataFrame:
        """
        执行SQL查询返回DataFrame
        输入:
            query (str): SQL查询语句
        输出:
            pd.DataFrame: 查询结果
        """
        self.logger.debug(f"执行数据库查询，查询语句:{query[:100]}")
        try:
            with self.db_engine.connect() as conn:
                result = pd.read_sql(text(query), conn)
            return result
        except Exception as e:
            self.logger.error(f"数据库查询错误:{e}", exc_info=True)
            raise e

    def update_db(
        self,
        df: pd.DataFrame,
        update_sql: str,
        progress_file: str = "update_progress.txt",
        batch_size: int = 10000,
        single_operation: bool = False,
    ) -> None:
        """
        批量更新数据库
        输入:
            df (pd.DataFrame): 包含更新数据的DataFrame
            update_sql (str): 更新SQL模板
            progress_file (str): 进度记录文件
            batch_size (int): 批处理大小
            single_operation (bool): 是否单次操作
        输出: 无
        """
        self.logger.info(f"执行数据库更新，更新语句:{update_sql[:100]}", extra={"event": "db"})

        def process_batch(conn, batch_df, update_sql):
            params = batch_df.to_dict(orient="records")
            conn.execute(text(update_sql), params)

        if single_operation:
            self.logger.debug("执行单次操作")
            try:
                with self.db_engine.begin() as conn:
                    process_batch(conn, df, update_sql)
            except Exception as e:
                self.logger.error(f"单次操作失败: {e}", exc_info=True)
                raise RuntimeError("单次操作失败")
        else:
            self._process_in_batches(
                data=df,
                batch_size=batch_size,
                progress_file=progress_file,
                process_batch_func=process_batch,
                update_sql=update_sql,
            )
        self.logger.info(f"数据更新完成，更新语句:{update_sql[:100]}", extra={"event": "db"})

    def delete_db(
        self,
        df: pd.DataFrame,
        delete_sql: str,
        progress_file: str = "delete_progress.txt",
        batch_size: int = 10000,
        single_operation: bool = False,
    ) -> None:
        """
        批量删除数据
        输入:
            df (pd.DataFrame): 包含要删除记录标识的DataFrame
            delete_sql (str): 删除SQL模板
            progress_file (str): 进度记录文件
            batch_size (int): 批处理大小
            single_operation (bool): 是否单次操作
        输出: 无
        """
        self.logger.info(f"执行数据库删除，删除语句:{delete_sql[:100]}", extra={"event": "db"})

        def process_batch(conn, batch_df, delete_sql):
            params = batch_df.to_dict(orient="records")
            conn.execute(text(delete_sql), params)

        if single_operation:
            self.logger.debug("执行单次操作")
            try:
                with self.db_engine.begin() as conn:
                    process_batch(conn, df, delete_sql)
            except Exception as e:
                self.logger.error(f"单次操作失败: {e}", exc_info=True)
                raise RuntimeError("单次操作失败")
        else:
            self._process_in_batches(
                data=df,
                batch_size=batch_size,
                progress_file=progress_file,
                process_batch_func=process_batch,
                delete_sql=delete_sql,
            )
        self.logger.info(f"数据删除完成，删除语句:{delete_sql[:100]}", extra={"event": "db"})

    @abstractmethod
    def process(self, input_data: dict) -> None:
        """
        主处理流程 (抽象方法，子类必须实现)
        输入: 无
        输出: 无
        """

    def run(self, input_data: dict) -> None:
        """
        执行入口
        输入: input_data (dict): 输入数据
        输出: 无
        """
        try:
            self.logger.info(
                f"启动db.run处理流程{self.__class__.__name__}", extra={"event": "db"}
            )
            start_time = time.perf_counter()
            self.process(input_data)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            self.logger.info("db.run处理完成", extra={"event": "db", "duration_ms": duration_ms})
        except Exception as e:
            self.logger.error(f"处理失败: {e!s}", exc_info=True)
            raise e
