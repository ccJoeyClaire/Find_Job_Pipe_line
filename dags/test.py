from datetime import datetime
import os
import sys
import traceback

from minio import Minio
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

import site

def print_python_environment():
    print("=" * 60)
    print("Python Environment Information")
    print("=" * 60)
    
    # 1. Python 解释器信息
    print(f"Python Interpreter: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Python Prefix: {sys.prefix}")
    
    # 2. 工作目录
    print(f"Current Working Directory: {os.getcwd()}")
    
    # 3. 模块搜索路径
    print("\nModule Search Paths (sys.path):")
    for i, path in enumerate(sys.path[:20], 1):  # 只显示前20个
        print(f"  {i:2d}. {path}")
    if len(sys.path) > 20:
        print(f"  ... {len(sys.path)-20} more paths")
    
    # 4. 用户 site-packages
    print("\nUser site-packages Directory:")
    user_site = site.getusersitepackages()
    print(f"  {user_site}")
    if os.path.exists(user_site):
        print("  Exists")
    else:
        print("  Does not exist")
    
    # 5. 系统 site-packages
    print("\nSystem site-packages Directories:")
    for site_dir in site.getsitepackages():
        print(f"  {site_dir}")
        if os.path.exists(site_dir):
            print(f"    Exists")
    
    # 6. 环境变量
    print("\nRelated Environment Variables:")
    for var in ['PYTHONPATH', 'PATH', 'CONDA_PREFIX', 'VIRTUAL_ENV']:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value[:100]}..." if len(value) > 100 else f"  {var}: {value}")
        else:
            print(f"  {var}: Not set")
    
    # 7. 检查 selenium 包
    print("\nselenium Package Information:")
    try:
        import selenium
        print(f"  Successfully imported selenium")
        print(f"  Path: {selenium.__file__}")
        print(f"  Version: {selenium.__version__}")
    except ImportError as e:
        print(f"  Cannot import selenium: {e}")
        # 搜索 selenium
        print("  Searching for selenium package...")
        for path in sys.path:
            selenium_path = os.path.join(path, 'selenium')
            if os.path.exists(selenium_path):
                print(f"    Found selenium in {path}")
    
    print("=" * 60)

    print("Testing driver manager...")
    try:
        from Lib.action import driver_manager
        driver_manager = driver_manager()
        driver_manager.get_url('https://www.google.com')
        print(f"  Driver manager initialized successfully")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Traceback: {traceback.format_exc()}")


def test_connect_to_minio():
    client = Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    if not client.bucket_exists("testdatabucket"):
        client.make_bucket("testdatabucket")

    from io import BytesIO
    data = BytesIO(b"Hello, MinIO!")

    client.put_object(
        bucket_name="testdatabucket",
        object_name="testssh.txt",
        data=data,
        length=len(data.getvalue())
    )
    print(f"  Object uploaded to testdatabucket")
    return client

    

# 在脚本的合适位置调用
if __name__ == "__main__":
    print_python_environment()
    test_connect_to_minio()
    # 您原来的代码...