from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class driver_manager:
    def __init__(self, chrome_driver_path: str | None = None):
        """
        初始化浏览器驱动管理器

        Args:
            chrome_driver_path: ChromeDriver 路径（可选）。不传则按本机 Chrome 版本自动下载匹配的驱动。
        """
        import os
        import glob

        try:
            if chrome_driver_path:
                # 使用指定的 ChromeDriver 路径
                if not os.path.exists(chrome_driver_path):
                    raise FileNotFoundError(f"ChromeDriver does not exist: {chrome_driver_path}")
                service = Service(chrome_driver_path)
            else:
                # 优先使用系统安装的 ChromeDriver（Docker 构建时安装）
                system_chromedriver = "/usr/local/bin/chromedriver"
                print(f" Checking system ChromeDriver: {system_chromedriver}")
                service = None
                
                if os.path.exists(system_chromedriver):
                    # 检查文件是否可执行
                    if os.access(system_chromedriver, os.X_OK):
                        print(f" Using system ChromeDriver: {system_chromedriver}")
                        service = Service(system_chromedriver)
                    else:
                        print(f" System ChromeDriver exists but is not executable, trying to add execution permission")
                        try:
                            os.chmod(system_chromedriver, 0o755)
                            if os.access(system_chromedriver, os.X_OK):
                                print(f" Using system ChromeDriver: {system_chromedriver}")
                                service = Service(system_chromedriver)
                            else:
                                print(f" Cannot set execution permission, trying other methods")
                        except Exception as e:
                            print(f" Setting execution permission failed: {e}，trying other methods")
                else:
                    print(f" System ChromeDriver does not exist: {system_chromedriver}")
                
                # 如果系统 ChromeDriver 不可用，尝试其他方法
                if service is None:
                    # Windows 下优先用 webdriver_manager 按本机 Chrome 版本下载匹配的 ChromeDriver
                    is_windows = os.name == "nt"
                    if is_windows:
                        chrome_version = _get_chrome_major_version()
                        driver_version = f" (Chrome {chrome_version})" if chrome_version else ""
                        print(f" Attempting to download ChromeDriver{driver_version}...")
                        try:
                            if chrome_version:
                                service = Service(
                                    ChromeDriverManager(driver_version=chrome_version).install()
                                )
                            else:
                                service = Service(ChromeDriverManager().install())
                            print(f" ChromeDriver download successful")
                        except Exception as e:
                            print(f" ChromeDriverManager download failed: {e}, trying local cache...")
                            service = None
                    if service is None:
                        # 查找本地已下载的 ChromeDriver（webdriver_manager 的缓存位置）
                        print(f" Finding local cached ChromeDriver...")
                        local_driver_path = self._find_local_chromedriver()
                        if local_driver_path and os.path.exists(local_driver_path):
                            print(f" Using local ChromeDriver: {local_driver_path}")
                            service = Service(local_driver_path)
                        elif is_windows:
                            raise ConnectionError(
                                f"Cannot download ChromeDriver\n"
                                "Solutions:\n"
                                "1. Check network connection (need to access Chrome for Testing)\n"
                                "2. Manually download ChromeDriver matching your Chrome version and pass chrome_driver_path=...\n"
                                "3. Or update Chrome to the latest so ChromeDriver 145 can be used"
                            )
                        else:
                            # Linux/Docker: 尝试自动下载（可选按 Chrome 版本）
                            chrome_version = _get_chrome_major_version()
                            print(f" Attempting to download ChromeDriver...")
                            try:
                                if chrome_version:
                                    service = Service(
                                        ChromeDriverManager(driver_version=chrome_version).install()
                                    )
                                else:
                                    service = Service(ChromeDriverManager().install())
                                print(f" ChromeDriver download successful")
                            except Exception as e:
                                print(f" ChromeDriverManager download failed: {e}")
                                raise ConnectionError(
                                    f"Cannot download ChromeDriver: {e}\n"
                                    "Solutions:\n"
                                    "1. Check network connection\n"
                                    "2. Manually download ChromeDriver and specify path\n"
                                    "4. Ensure ChromeDriver in /usr/local/bin/chromedriver when building Docker"
                                )
            
            # 配置 Chrome 选项（支持 Docker 环境）
            
            chrome_options = Options()

            
            # chrome_options.add_argument('--headless')  # 无头模式
            # chrome_options.add_argument('--no-sandbox')  # Docker 环境必需
            # chrome_options.add_argument('--disable-dev-shm-usage')  # 避免共享内存问题
            # chrome_options.add_argument('--disable-gpu')  # 禁用 GPU
            # chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小
            # chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被检测

            # 检测是否在 Docker 环境中
            if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
                # Docker 环境：使用系统安装的 Chrome
                chrome_options.binary_location = '/usr/bin/google-chrome'
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.base_url = None
            self.current_element = None
        except ConnectionError:
            raise
        except Exception as e:
            print(f" Initialization of browser driver failed: {e}")
            raise
    
    def _find_local_chromedriver(self) -> str:
        """
        查找本地已下载的 ChromeDriver（webdriver_manager 缓存位置）
        
        Returns:
            str: ChromeDriver 路径，如果未找到返回 None
        """
        import os
        import glob
        
        # webdriver_manager 的默认缓存位置（支持 Windows 和 Linux）
        possible_base_paths = [
            os.path.expanduser("~/.wdm/drivers/chromedriver"),
            os.path.join(os.environ.get("USERPROFILE", ""), ".wdm", "drivers", "chromedriver"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), ".wdm", "drivers", "chromedriver"),
            os.path.join(os.environ.get("HOME", ""), ".wdm", "drivers", "chromedriver"),
        ]
        
        # 查找所有可能的 ChromeDriver 文件（Windows: .exe, Linux: 无扩展名）
        driver_patterns = [
            "**/chromedriver.exe",  # Windows
            "**/chromedriver-linux64/chromedriver",  # Linux (新版本)
            "**/chromedriver",  # Linux (旧版本或直接文件)
        ]
        
        all_matches = []
        for base_path in possible_base_paths:
            if not base_path or not os.path.exists(base_path):
                continue
            for pattern in driver_patterns:
                full_pattern = os.path.join(base_path, pattern)
                matches = glob.glob(full_pattern, recursive=True)
                if matches:
                    # 过滤出可执行的文件
                    for match in matches:
                        if os.path.isfile(match) and os.access(match, os.X_OK):
                            all_matches.append(match)
        
        if all_matches:
            # 返回最新的（按修改时间排序）
            return max(all_matches, key=os.path.getmtime)
        
        return None    