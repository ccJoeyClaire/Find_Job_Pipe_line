
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError, as_completed
from typing import Callable, List, Any, Optional, Tuple, Dict, Iterable, Union
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TaskResult:
    """任务结果数据类"""
    index: int
    input_data: Any
    output: Any = None
    error: Optional[Exception] = None
    status: TaskStatus = TaskStatus.PENDING
    execution_time: float = 0.0


class BatchRun:
    """
    并发式批处理模型
    
    使用 threading 实现并发执行，支持：
    - 最大并发数控制
    - 进度显示
    - 错误处理
    - 结果收集与顺序保持
    - 超时控制
    - 日志记录
    """
    
    def __init__(
        self,
        function: Callable,
        input_list: List[Any],
        max_workers: int = 4,
        timeout: Optional[float] = None,
        enable_progress: bool = True,
        enable_logging: bool = True,
        log_level: int = logging.INFO
    ):
        """
        初始化批处理对象
        
        Args:
            function: 要执行的函数
            input_list: 输入数据列表，每个元素将作为函数的参数
            max_workers: 最大并发线程数，默认为4
            timeout: 单个任务超时时间（秒），None表示不限制
            enable_progress: 是否显示进度条，默认为True
            enable_logging: 是否启用日志，默认为True
            log_level: 日志级别，默认为INFO
        """
        self.function = function
        self.input_list = input_list
        self.max_workers = max_workers
        self.timeout = timeout
        self.enable_progress = enable_progress
        self.enable_logging = enable_logging
        
        # 设置日志
        if self.enable_logging:
            self.logger = self._setup_logger(log_level)
        else:
            self.logger = None
        
        # 结果存储
        self.results: List[TaskResult] = []
        self._lock = threading.Lock()
        
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"BatchRun_{id(self)}")
        logger.setLevel(log_level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _log(self, level: int, message: str):
        """记录日志"""
        if self.logger:
            self.logger.log(level, message)
    
    def _execute_task(self, index: int, input_data: Any) -> TaskResult:
        """
        执行单个任务
        
        Args:
            index: 任务索引
            input_data: 输入数据
            
        Returns:
            TaskResult: 任务结果
        """
        result = TaskResult(index=index, input_data=input_data, status=TaskStatus.RUNNING)
        start_time = time.time()
        
        try:
            # 如果 input_data 是元组或列表，解包作为参数
            if isinstance(input_data, (tuple, list)):
                output = self.function(*input_data)
            else:
                output = self.function(input_data)
            
            result.output = output
            result.status = TaskStatus.COMPLETED
            result.execution_time = time.time() - start_time
            
            self._log(logging.DEBUG, f"Task {index} completed successfully in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.error = e
            result.status = TaskStatus.FAILED
            result.execution_time = time.time() - start_time
            
            self._log(logging.ERROR, f"Task {index} failed: {str(e)}")
        
        return result
    
    def run(self) -> List[TaskResult]:
        """
        执行批处理任务
        
        Returns:
            List[TaskResult]: 任务结果列表，保持输入顺序
        """
        if not self.input_list:
            self._log(logging.WARNING, "Input list is empty")
            return []
        
        self._log(logging.INFO, f"Starting batch processing: {len(self.input_list)} tasks, max_workers={self.max_workers}")
        
        # 初始化结果列表
        self.results = [None] * len(self.input_list)
        
        # 使用 ThreadPoolExecutor 进行并发执行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_index = {}
            for index, input_data in enumerate(self.input_list):
                if self.timeout:
                    future = executor.submit(self._execute_task, index, input_data)
                else:
                    future = executor.submit(self._execute_task, index, input_data)
                future_to_index[future] = index
            
            # 处理完成的任务
            completed_count = 0
            total_tasks = len(self.input_list)
            
            # 使用 as_completed 获取完成的任务
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                
                try:
                    if self.timeout:
                        result = future.result(timeout=self.timeout)
                    else:
                        result = future.result()
                except FutureTimeoutError:
                    # 处理超时
                    result = TaskResult(
                        index=index,
                        input_data=self.input_list[index],
                        status=TaskStatus.TIMEOUT,
                        error=TimeoutError(f"Task {index} exceeded timeout of {self.timeout}s")
                    )
                    self._log(logging.WARNING, f"Task {index} timed out")
                except Exception as e:
                    # 处理其他异常
                    result = TaskResult(
                        index=index,
                        input_data=self.input_list[index],
                        status=TaskStatus.FAILED,
                        error=e
                    )
                    self._log(logging.ERROR, f"Task {index} raised exception: {str(e)}")
                
                # 保存结果（保持顺序）
                self.results[index] = result
                completed_count += 1
                
                # 显示进度
                if self.enable_progress:
                    progress = (completed_count / total_tasks) * 100
                    print(f"\rProgress: {completed_count}/{total_tasks} ({progress:.1f}%)", end="", flush=True)
        
        if self.enable_progress:
            print()  # 换行
        
        # 统计结果
        self._log_statistics()
        
        return self.results
    
    def _log_statistics(self):
        """记录统计信息"""
        if not self.logger:
            return
        
        total = len(self.results)
        completed = sum(1 for r in self.results if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.results if r.status == TaskStatus.FAILED)
        timeout = sum(1 for r in self.results if r.status == TaskStatus.TIMEOUT)
        avg_time = sum(r.execution_time for r in self.results if r.execution_time > 0) / max(completed, 1)
        
        self._log(logging.INFO, f"Batch processing completed: Total={total}, Completed={completed}, Failed={failed}, Timeout={timeout}, AvgTime={avg_time:.2f}s")
    
    def get_results(self) -> List[Any]:
        """
        获取所有成功执行的结果（按顺序）
        
        Returns:
            List[Any]: 成功执行的结果列表
        """
        return [r.output for r in self.results if r.status == TaskStatus.COMPLETED]
    
    def get_failed_results(self) -> List[TaskResult]:
        """
        获取所有失败的任务结果
        
        Returns:
            List[TaskResult]: 失败的任务结果列表
        """
        return [r for r in self.results if r.status == TaskStatus.FAILED]
    
    def get_timeout_results(self) -> List[TaskResult]:
        """
        获取所有超时的任务结果
        
        Returns:
            List[TaskResult]: 超时的任务结果列表
        """
        return [r for r in self.results if r.status == TaskStatus.TIMEOUT]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取执行摘要
        
        Returns:
            Dict[str, Any]: 包含统计信息的字典
        """
        total = len(self.results)
        completed = sum(1 for r in self.results if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.results if r.status == TaskStatus.FAILED)
        timeout = sum(1 for r in self.results if r.status == TaskStatus.TIMEOUT)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "timeout": timeout,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }


def test_function(a: int, b: int) -> int:
    """测试函数"""
    print(f"Processing: a={a}, b={b}")
    time.sleep(0.5)  # 模拟耗时操作
    result = a + b
    print(f"Result: {a} + {b} = {result}")
    return result


def test_function_with_error(a: int, b: int) -> int:
    """测试函数（带错误）"""
    if a == 3:
        raise ValueError(f"Error occurred for a={a}")
    return a + b


if __name__ == "__main__":
    # 示例1: 基本使用
    print("=" * 50)
    print("Example 1: Basic Usage")
    print("=" * 50)
    batch_run = BatchRun(
        function=test_function,
        input_list=[(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)],
        max_workers=3,
        timeout=2.0,
        enable_progress=True,
        enable_logging=True
    )
    results = batch_run.run()
    
    print("\nResults:")
    for result in results:
        if result.status == TaskStatus.COMPLETED:
            print(f"  Task {result.index}: {result.output}")
        else:
            print(f"  Task {result.index}: {result.status.value} - {result.error}")
    
    print("\nSummary:", batch_run.get_summary())
    
    # 示例2: 错误处理
    print("\n" + "=" * 50)
    print("Example 2: Error Handling")
    print("=" * 50)
    batch_run2 = BatchRun(
        function=test_function_with_error,
        input_list=[(1, 2), (3, 4), (5, 6)],
        max_workers=2,
        enable_progress=True
    )
    results2 = batch_run2.run()
    
    print("\nFailed tasks:")
    for result in batch_run2.get_failed_results():
        print(f"  Task {result.index}: {result.error}")

