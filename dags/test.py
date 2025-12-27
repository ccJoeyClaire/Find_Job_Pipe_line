from datetime import datetime
import os
import sys
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")
if current_dir.endswith('Find_Job_Pipe_Line_V2'):
    project_root = current_dir
else:
    project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
lib_path = os.path.join(project_root, 'Lib')
sys.path.insert(0, lib_path)

print(f"Project root: {project_root}")
print(f"Lib path: {lib_path}")
import time

from Lib.Batch_Run import BatchRun
from Lib.json_yaml_IO import *

def test(a: int, b: int) -> int:
    print(f"Processing: a={a}, b={b}")
    time.sleep(0.5)
    result = a + b
    print(f"Result: {a} + {b} = {result}")
    return result

if __name__ == "__main__":
    today = datetime.now().strftime('%Y%m%d')
    batch_run = BatchRun(
        function=test,
        input_list=[(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)],
        max_workers=3,
        timeout=2.0,
        enable_progress=True,
        enable_logging=True
    )
    results = batch_run.run()
    output_list = {}
    for idx, result in enumerate(results):
        print(f"Result {idx}: {result.output}")
        output_list[idx] = result.output
    write_json(f'test_results_{today}.json', output_list)