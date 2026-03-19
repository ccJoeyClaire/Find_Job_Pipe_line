from typing import Any, List, Union
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

import time
from datetime import datetime

import json
import os

import requests
from bs4 import BeautifulSoup

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse




def scroll_script(
    direction: str = 'down', # 'up' / 'down' or 'top' / 'bottom'
    step: int = 300
    ):
    
    if direction in ['top', 'bottom']:
        if direction == 'top':
            script = "if (arguments[0]) { arguments[0].scrollTop = 0; } else { window.scrollTo(0, 0); }"
        elif direction == 'bottom':
            script = "if (arguments[0]) { arguments[0].scrollTop = arguments[0].scrollHeight; } else { window.scrollTo(0, document.body.scrollHeight); }"
        
    else:
        if direction == 'down':
            step = step
        else:
            step = -step
        script = f"if (arguments[0]) {{ arguments[0].scrollTop += {step}; }} else {{ window.scrollBy(0, {step}); }}"
        
    return script



class driver_manager:
    def __init__(self, chrome_driver_path: str | None = None):
        if chrome_driver_path is None:
            chrome_driver_path = r"C:\Users\JoeyC\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe"
        else:
            chrome_driver_path = chrome_driver_path
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)

    def is_page_loaded(self, expected_url: str = None, check_element: tuple = None, wait_time: int = 10) -> bool:
        """
        args:
            expected_url: str
            check_element: tuple
            wait_time: int
        return: bool, dict
        """
        try:
            # 等待页面 readyState 为 complete
            WebDriverWait(self.driver, wait_time).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 检查特定元素是否存在（如果提供了）
            if check_element is not None:
                by, value = check_element
                element = self.get_element(by, value, wait_time=5)
                if element is None:
                    print(f" Expected element not found: {by}={value}")
                    page_info = {
                        'url': self.driver.current_url,
                        'page_source': self.driver.page_source,
                    }
                    return False, page_info
            
            return True, {}
            
        except Exception as e:
            print(f" Page load detection failed: {e}")
            return False, f"页面加载检测失败: {e}"

    def get_url(self, target_url: str = None, check_element: tuple = None):
        """
        访问 URL 并等待页面加载
        
        Args:
            target_url: 目标 URL
            check_element: 可选，要检查的元素定位器 (By, value) 用于验证页面是否加载成功
        """
        if target_url is not None:
            self.base_url = target_url
        
        self.driver.get(self.base_url)
        time.sleep(2)  # 等待页面加载
        
        # 可选：检查页面是否成功加载
        if check_element is not None:
            if not self.is_page_loaded(expected_url=self.base_url, check_element=check_element):
                print(f" Warning: Page may not have been loaded: {self.base_url}")

    def switch_to_url(self, old_params_keys: List[str], new_params_values: List[str], check_element: tuple = None) -> bool:
        """
        切换 URL 参数并等待页面加载
        
        Args:
            old_params_keys: 要修改的参数键列表
            new_params_values: 新的参数值列表
            check_element: 可选，要检查的元素定位器 (By, value) 用于验证页面是否加载成功
        
        Returns:
            bool: True 表示页面加载成功，False 表示加载失败
        """
        parsed = urlparse(self.driver.current_url)
        params = parse_qs(parsed.query)
        if type(old_params_keys) == list:
            for old_params_key, new_params_value in zip(old_params_keys, new_params_values):
                params[old_params_key] = [str(new_params_value)]
        else:
            params[old_params_keys] = [str(new_params_values)]

        new_query = urlencode(params, doseq=True)
        new_url = urlunparse((parsed.scheme, 
                              parsed.netloc, 
                              parsed.path, 
                              parsed.params, 
                              new_query, 
                              parsed.fragment))
        self.driver.get(new_url)
        time.sleep(2)  # 等待页面加载
        
        # 检查页面是否成功加载
        page_loaded, error_message = self.is_page_loaded(expected_url=new_url, check_element=check_element)
        return page_loaded, error_message

    def get_element(self, by, value, wait_time=10):
        """
        args:
            by*: By
            value*: str
            wait_time: int
        return: WebElement
        """
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            self.current_element = element
            return element
        except Exception as e:
            print(f"Error getting element: {e}")
            return None

    def get_element_with_fallbacks(
        self,
        locators: List[tuple],
        wait_time_per_try: int = 5,
    ):
        """
        Try multiple locators in order; return the first element found.
        Makes selectors more resilient to frontend changes.

        Args:
            locators: List of (by, value) tuples, e.g. [(By.CSS_SELECTOR, ".btn"), (By.XPATH, "//button[.='Sign in']")]
            wait_time_per_try: Max seconds to wait for each locator before trying the next.

        Returns:
            WebElement or None if no locator matches.
        """
        for by, value in locators:
            try:
                element = self.get_element(by, value, wait_time=wait_time_per_try)
                if element is not None:
                    return element
            except Exception:
                continue
        return None
    
    def click_element(self, element=None, by=None, value=None):
        """
        Click an element, handling stale element references.
        
        Args:
            element: WebElement to click (optional)
            by: By locator type (optional, used if element is stale)
            value: Locator value (optional, used if element is stale)
        """
        if element is None:
            element = self.current_element
        
        try:
            element.click()
        except StaleElementReferenceException:
            # If element is stale and we have locator info, try to re-find it
            if by is not None and value is not None:
                print(f"Element became stale, re-finding...")
                element = self.get_element(by, value)
                if element is not None:
                    element.click()
                else:
                    raise Exception(f"Could not re-find element after stale reference: {by}={value}")
            else:
                raise
        time.sleep(0.5)  # 等待执行结束，避免频繁执行脚本
        return element

    def send_keys(self, keys, element=None):
        if element is None:
            element = self.current_element
        element.send_keys(keys)
        time.sleep(0.5)  # 等待执行结束，避免频繁执行脚本
        return element

    def execute_script(self, script, element=None):
        if element is None:
            element = self.current_element
        self.driver.execute_script(script, element)
        time.sleep(0.5)  # 等待执行结束，避免频繁执行脚本

    def scroll_element(
        self, direction: str = 'down', # 'up' or 'down'
        step: int = 300,
        element=None):

        if element is None:
            element = self.current_element

        # 如果 element 为 None，仍然执行滚动（使用 window 滚动）
        self.execute_script(scroll_script(direction, step), element=element)
        return True

    def scroll_until_element_appears(
        self, element: WebElement, 
        target_element: WebElement, 
        max_attempts: int = 20, 
        wait_time: int = 2, 
        step: int = 300
        ):
        """
        args:
            element: WebElement (可滚动元素，可以为 None，使用 window 滚动)
            target_element: WebElement (目标元素，可以为 None)
            max_attempts: int
            wait_time: int
            step: int
        return: bool
        """
        # 如果 target_element 为 None，直接返回 False
        if target_element is None:
            return False
            
        for i in range(max_attempts):
            self.scroll_element(direction='down', step=step, element=element)
            time.sleep(wait_time)
            try:
                if target_element.is_displayed():
                    return True
            except Exception:
                # 元素可能已失效，继续尝试
                pass
        return False

    def save_cookies(self, cookies_path: str):
        """
        保存当前浏览器的 cookies 到文件
        
        Args:
            cookies_path: cookies 文件的保存路径
        """
        import json
        import os
        
        # 确保目录存在
        os.makedirs(os.path.dirname(cookies_path), exist_ok=True)
        
        # 获取当前 cookies
        cookies = self.driver.get_cookies()
        
        # 保存到文件
        with open(cookies_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f" Cookies saved to: {cookies_path}")
        return cookies_path

    def load_cookies(self, cookies_path: str, target_url: str = None):
        """
        从文件加载 cookies 到当前浏览器
        
        Args:
            cookies_path: cookies 文件的路径
            target_url: 加载 cookies 前需要先访问的 URL（通常是网站首页）
        """
        
        if not os.path.exists(cookies_path):
            raise FileNotFoundError(f"Cookies 文件不存在: {cookies_path}")
        
        # 读取 cookies
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        # 如果提供了 target_url，先访问该 URL（加载 cookies 前需要先访问目标域名）
        if target_url:
            self.get_url(target_url)
        
        # 加载 cookies
        for cookie in cookies:
            try:
                # 移除可能存在的 'expiry' 键（如果过期时间格式有问题）
                if 'expiry' in cookie:
                    # 确保 expiry 是整数
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(f" Loading cookie failed: {cookie.get('name', 'unknown')} - {e}")
        
        # 刷新页面以应用 cookies
        if target_url:
            self.driver.refresh()
            time.sleep(2)
        
        print(f" Cookies loaded from {cookies_path}")
        return True


class element_manager:
    """
    元素管理器：用于获取 WebElement 或复制 HTML 的定位信息。
    支持两种输入方式：
    1. Selenium WebElement — 需先通过 driver 找到元素
    2. 从浏览器复制的 HTML 字符串 — 直接粘贴即可得到定位器，无需先 get element
    """
    def __init__(self, element: Union[WebElement, str]):
        """
        初始化元素管理器
        
        Args:
            element: Selenium WebElement 对象，或从浏览器复制的元素 HTML 字符串
                     （如右键元素 -> Copy -> Copy element）
        """
        self.element = element
        self._locator_info = None
        self._from_html = isinstance(element, str)
    
    def get_locator_info(self) -> dict:
        """
        获取元素的完整定位信息
        
        Returns:
            dict: 包含各种定位方式的字典
                {
                    'id': str,                    # ID 定位
                    'class_name': str,            # Class 定位
                    'tag_name': str,              # Tag 定位
                    'name': str,                  # Name 定位
                    'xpath': str,                 # XPath 定位
                    'css_selector': str,           # CSS Selector 定位
                    'link_text': str,             # Link Text 定位（如果是链接）
                    'partial_link_text': str,      # Partial Link Text 定位
                    'attributes': dict,           # 所有属性
                    'text': str,                  # 元素文本
                    'location': dict,             # 元素位置 {'x': int, 'y': int}
                    'size': dict                  # 元素大小 {'width': int, 'height': int}
                }
        """
        if self._locator_info is not None:
            return self._locator_info
        
        # 从复制的 HTML 字符串直接解析定位信息（无需先 get element）
        if self._from_html:
            self._locator_info = self._parse_html_locator_info()
            return self._locator_info
        
        info = {}
        
        # 1. ID 定位
        element_id = self.element.get_attribute('id')
        info['id'] = element_id if element_id else None
        if element_id:
            info['id_locator'] = (By.ID, element_id)
        
        # 2. Class Name 定位
        class_name = self.element.get_attribute('class')
        info['class_name'] = class_name if class_name else None
        if class_name:
            # 取第一个 class
            first_class = class_name.split()[0] if class_name else None
            info['class_name_locator'] = (By.CLASS_NAME, first_class) if first_class else None
        
        # 3. Tag Name 定位
        tag_name = self.element.tag_name
        info['tag_name'] = tag_name
        info['tag_name_locator'] = (By.TAG_NAME, tag_name)
        
        # 4. Name 定位
        name = self.element.get_attribute('name')
        info['name'] = name if name else None
        if name:
            info['name_locator'] = (By.NAME, name)
        
        # 5. XPath 定位（通过 JavaScript 生成）
        try:
            xpath_locator = self._get_xpath_locator()
            if xpath_locator:
                info['xpath'] = xpath_locator[1]  # 提取 XPath 字符串
                info['xpath_locator'] = xpath_locator
            else:
                info['xpath'] = None
                info['xpath_locator'] = None
        except:
            info['xpath'] = None
            info['xpath_locator'] = None
        
        # 6. CSS Selector 定位
        try:
            css_locator = self._get_css_selector_locator()
            if css_locator:
                info['css_selector'] = css_locator[1]  # 提取 CSS Selector 字符串
                info['css_selector_locator'] = css_locator
            else:
                info['css_selector'] = None
                info['css_selector_locator'] = None
        except:
            info['css_selector'] = None
            info['css_selector_locator'] = None
        
        # 7. Link Text 定位（如果是链接元素）
        if tag_name == 'a':
            link_text = self.element.text.strip()
            info['link_text'] = link_text if link_text else None
            if link_text:
                info['link_text_locator'] = (By.LINK_TEXT, link_text)
            else:
                info['link_text_locator'] = None
            info['partial_link_text'] = link_text[:20] if link_text else None
        else:
            info['link_text'] = None
            info['link_text_locator'] = None
            info['partial_link_text'] = None
        
        # 8. 所有属性
        info['attributes'] = self._get_all_attributes()
        
        # 9. 元素文本
        info['text'] = self.element.text.strip()
        
        # 10. 元素位置和大小
        location = self.element.location
        size = self.element.size
        info['location'] = {'x': location['x'], 'y': location['y']}
        info['size'] = {'width': size['width'], 'height': size['height']}
        
        self._locator_info = info
        return info
    
    def _parse_html_locator_info(self) -> dict:
        """
        从复制的 HTML 字符串解析定位信息（无需 Selenium WebElement）。
        用于在浏览器中复制元素后，直接得到可用的定位器。
        
        Returns:
            dict: 与 get_locator_info() 结构一致（location/size 为 None）
        """
        html = self.element.strip()
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup.find(True)  # 第一个标签即复制的根元素
        if tag is None:
            return {
                'id': None, 'class_name': None, 'tag_name': None, 'name': None,
                'xpath': None, 'css_selector': None, 'link_text': None, 'partial_link_text': None,
                'id_locator': None, 'class_name_locator': None, 'tag_name_locator': (By.TAG_NAME, 'body'),
                'name_locator': None, 'xpath_locator': None, 'css_selector_locator': None,
                'link_text_locator': None, 'attributes': {}, 'text': '', 'location': None, 'size': None,
            }
        
        tag_name = tag.name.lower() if tag.name else None
        if not tag_name:
            tag_name = 'div'
        
        attrs = dict(tag.attrs) if tag.attrs else {}
        element_id = attrs.get('id') or None
        class_val = attrs.get('class')
        if isinstance(class_val, list):
            class_str = ' '.join(class_val) if class_val else None
            first_class = class_val[0] if class_val else None
        else:
            class_str = class_val if class_val else None
            first_class = class_str.split()[0] if class_str else None
        name_attr = attrs.get('name') or None
        text = tag.get_text(separator=' ', strip=True) if tag else ''
        
        info = {}
        info['id'] = element_id
        info['id_locator'] = (By.ID, element_id) if element_id else None
        info['class_name'] = class_str
        info['class_name_locator'] = (By.CLASS_NAME, first_class) if first_class else None
        info['tag_name'] = tag_name
        info['tag_name_locator'] = (By.TAG_NAME, tag_name)
        info['name'] = name_attr
        info['name_locator'] = (By.NAME, name_attr) if name_attr else None
        
        # XPath：优先 id，其次 data-* 等唯一属性，再 class
        if element_id:
            xpath = f"//*[@id='{element_id}']"
        else:
            data_attr = next((k for k in attrs if k.startswith('data-')), None)
            if data_attr:
                val = attrs[data_attr]
                xpath = f"//{tag_name}[@{data_attr}='{val}']"
            elif first_class:
                xpath = f"//{tag_name}[contains(@class,'{first_class}')]"
            else:
                xpath = f"//{tag_name}"
        info['xpath'] = xpath
        info['xpath_locator'] = (By.XPATH, xpath)
        
        # CSS Selector：优先 id，再 class，再 tag
        if element_id:
            css = f"#{element_id}"
        elif first_class:
            css = f".{first_class}"
        else:
            css = tag_name
        info['css_selector'] = css
        info['css_selector_locator'] = (By.CSS_SELECTOR, css)
        
        if tag_name == 'a':
            info['link_text'] = text if text else None
            info['link_text_locator'] = (By.LINK_TEXT, text) if text else None
            info['partial_link_text'] = text[:20] if text else None
        else:
            info['link_text'] = None
            info['link_text_locator'] = None
            info['partial_link_text'] = None
        
        info['attributes'] = attrs
        info['text'] = text
        info['location'] = None
        info['size'] = None
        
        return info
    
    def parse_browser_selector(self, browser_selector: str) -> dict:
        """
        从浏览器复制的 CSS Selector 或 XPath 中提取相对和绝对路径
        
        Args:
            browser_selector: 从浏览器复制的 selector（CSS Selector 或 XPath）
        
        Returns:
            dict: 包含以下键的字典
                {
                    'type': 'css' 或 'xpath',
                    'absolute': str,  # 绝对路径（精确查找单个元素）
                    'relative': str,  # 相对路径（查找多个相同类型元素）
                    'absolute_locator': tuple,  # (By, value) 绝对路径定位器
                    'relative_locator': tuple    # (By, value) 相对路径定位器
                }
        
        示例:
            CSS Selector: "#main > div > ul > li:nth-child(1)"
            - absolute: "#main > div > ul > li:nth-child(1)"  # 精确查找第1个
            - relative: "#main > div > ul > li"                # 查找所有 li
            
            XPath: "/html/body/div[1]/ul/li[1]"
            - absolute: "/html/body/div[1]/ul/li[1]"          # 精确查找
            - relative: "//div[@id='main']//li"               # 查找所有 li
        """
        import re
        
        result = {
            'type': None,
            'absolute': None,
            'relative': None,
            'absolute_locator': None,
            'relative_locator': None
        }
        
        if not browser_selector:
            return result
        
        browser_selector = browser_selector.strip()
        
        # 判断是 XPath 还是 CSS Selector
        if browser_selector.startswith('/') or browser_selector.startswith('//'):
            # XPath
            result['type'] = 'xpath'
            result['absolute'] = browser_selector
            result['absolute_locator'] = (By.XPATH, browser_selector)
            
            # 提取相对路径：将绝对路径转换为相对路径
            relative_xpath = self._convert_xpath_to_relative(browser_selector)
            result['relative'] = relative_xpath
            result['relative_locator'] = (By.XPATH, relative_xpath) if relative_xpath else None
        else:
            # CSS Selector
            result['type'] = 'css'
            result['absolute'] = browser_selector
            result['absolute_locator'] = (By.CSS_SELECTOR, browser_selector)
            
            # 提取相对路径：去掉位置信息（nth-child, nth-of-type 等）
            relative_css = self._convert_css_to_relative(browser_selector)
            result['relative'] = relative_css
            result['relative_locator'] = (By.CSS_SELECTOR, relative_css) if relative_css else None
        
        return result
    
    def _convert_css_to_relative(self, css_selector: str) -> str:
        """
        将 CSS Selector 转换为相对路径（去掉位置信息）
        
        Args:
            css_selector: 完整的 CSS Selector，如 "#main > div > ul > li:nth-child(1)"
        
        Returns:
            str: 相对路径，如 "#main > div > ul > li"
        """
        import re
        
        # 去掉位置相关的伪类选择器
        # 如 :nth-child(1), :nth-of-type(2), :first-child, :last-child 等
        relative = re.sub(r':nth-child\(\d+\)', '', css_selector)
        relative = re.sub(r':nth-of-type\(\d+\)', '', relative)
        relative = re.sub(r':first-child', '', relative)
        relative = re.sub(r':last-child', '', relative)
        relative = re.sub(r':first-of-type', '', relative)
        relative = re.sub(r':last-of-type', '', relative)
        
        # 清理多余的空格和 >
        relative = re.sub(r'\s*>\s*', ' > ', relative)
        relative = relative.strip()
        
        return relative
    
    def _convert_xpath_to_relative(self, xpath: str) -> str:
        """
        将绝对 XPath 转换为相对 XPath
        
        Args:
            xpath: 绝对 XPath，如 "/html/body/div[1]/ul/li[1]"
        
        Returns:
            str: 相对 XPath，如 "//div[@id='main']//li" 或 "//li"
        """
        import re
        
        # 如果已经是相对路径（以 // 开头），直接返回
        if xpath.startswith('//'):
            # 去掉位置信息 [1], [2] 等
            relative = re.sub(r'\[\d+\]', '', xpath)
            return relative
        
        # 绝对路径转相对路径
        # 策略1：提取有 ID 的父元素，然后使用 // 查找
        # 例如：/html/body/div[1]/ul/li[1] -> //div[@id='main']//li
        
        # 先去掉位置信息
        relative = re.sub(r'\[\d+\]', '', xpath)
        
        # 将开头的 /html/body 替换为 //
        relative = re.sub(r'^/html/body/', '//', relative)
        
        # 如果路径中有 ID，可以优化
        # 这里简化处理，直接使用 // 开头
        if not relative.startswith('//'):
            # 找到最后一个有意义的元素
            parts = relative.split('/')
            if len(parts) > 0:
                last_part = parts[-1]
                # 使用 // 查找最后一个元素类型
                relative = f"//{last_part}"
            else:
                relative = "//*"
        
        return relative
    
    def _get_xpath_locator(self, xpath: str = None, full_xpath: str = None) -> tuple:
        """
        获取 XPath 定位器
        
        Args:
            xpath: 相对 XPath（以 // 开头）
            full_xpath: 绝对 XPath（以 / 开头）
        
        Returns:
            tuple: (By, value) 或 None
        """
        if xpath is not None:
            return (By.XPATH, xpath)
        elif full_xpath is not None:
            return (By.XPATH, full_xpath)
        else:
            # 自动生成 XPath（优先使用 ID）
            try:
                element_id = self.element.get_attribute('id')
                if element_id:
                    return (By.XPATH, f"//*[@id='{element_id}']")
                
                # 使用 JavaScript 生成完整 XPath
                script = """
                function getElementXPath(element) {
                    if (element.id !== '') {
                        return '//*[@id="' + element.id + '"]';
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return getElementXPath(arguments[0]);
                """
                driver = self.element._parent
                generated_xpath = driver.execute_script(script, self.element)
                return (By.XPATH, generated_xpath) if generated_xpath else None
            except:
                return None
    
    def _get_css_selector_locator(self, css_selector: str = None) -> tuple:
        """
        获取 CSS Selector 定位器
        
        Args:
            css_selector: 从浏览器复制的 CSS Selector
        
        Returns:
            tuple: (By, value) 或自动生成的简化 selector
        """
        # 如果提供了浏览器复制的 selector，直接使用
        if css_selector is not None:
            return (By.CSS_SELECTOR, css_selector)
        
        # 否则自动生成简化版
        # 优先使用 ID
        element_id = self.element.get_attribute('id')
        if element_id:
            return (By.CSS_SELECTOR, f"#{element_id}")
        
        # 使用 class（取第一个）
        class_name = self.element.get_attribute('class')
        if class_name:
            first_class = class_name.split()[0]
            return (By.CSS_SELECTOR, f".{first_class}")
        
        # 使用 tag name
        tag_name = self.element.tag_name
        return (By.CSS_SELECTOR, tag_name)
    
    def _get_all_attributes(self) -> dict:
        """
        获取元素的所有属性
        
        Returns:
            dict: 属性字典
        """
        script = """
        var items = {};
        for (index = 0; index < arguments[0].attributes.length; ++index) {
            items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
        }
        return items;
        """
        driver = self.element._parent
        attributes = driver.execute_script(script, self.element)
        return attributes
    
    def get_best_locator(self) -> tuple:
        """
        获取最佳定位方式（优先级：ID > Class > XPath > CSS Selector > Tag）
        
        Returns:
            tuple: (By, value) 定位元组，可直接用于 find_element
        """
        info = self.get_locator_info()
        
        # 优先级顺序
        if info.get('id_locator'):
            return info['id_locator']
        elif info.get('class_name_locator'):
            return info['class_name_locator']
        elif info.get('xpath_locator'):
            return info['xpath_locator']
        elif info.get('css_selector_locator'):
            return info['css_selector_locator']
        elif info.get('name_locator'):
            return info['name_locator']
        else:
            return info['tag_name_locator']
    
    def print_locator_info(self):
        """
        打印元素的定位信息（用于调试）
        """
        info = self.get_locator_info()
        print("=" * 50)
        print("Element location information:")
        print("=" * 50)
        
        if info['id']:
            print(f"ID: {info['id']}")
            print(f"  → By.ID: '{info['id']}'")
        
        if info['class_name']:
            print(f"Class Name: {info['class_name']}")
            if info.get('class_name_locator'):
                print(f"  → By.CLASS_NAME: '{info['class_name_locator'][1]}'")
        
        print(f"Tag Name: {info['tag_name']}")
        print(f"  → By.TAG_NAME: '{info['tag_name']}'")
        
        if info['name']:
            print(f"Name: {info['name']}")
            print(f"  → By.NAME: '{info['name']}'")
        
        if info['xpath']:
            print(f"XPath: {info['xpath']}")
            print(f"  → By.XPATH: \"{info['xpath']}\"")
        
        if info['css_selector']:
            print(f"CSS Selector: {info['css_selector']}")
            print(f"  → By.CSS_SELECTOR: '{info['css_selector']}'")
        
        if info['link_text']:
            print(f"Link Text: {info['link_text']}")
            print(f"  → By.LINK_TEXT: '{info['link_text']}'")
        
        print(f"\nElement text: {info['text'][:50]}..." if len(info['text']) > 50 else f"\nElement text: {info['text']}")
        if info.get('location') is not None:
            print(f"Location: x={info['location']['x']}, y={info['location']['y']}")
        if info.get('size') is not None:
            print(f"Size: width={info['size']['width']}, height={info['size']['height']}")
        
        best_locator = self.get_best_locator()
        print(f"\nRecommended location method: By.{best_locator[0].upper()} = '{best_locator[1]}'")
        print("=" * 50)


