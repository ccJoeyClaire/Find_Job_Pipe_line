# %%
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement
import time
from datetime import datetime
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup

import os
import sys
import importlib

from action import driver_manager
from action import element_manager

import json_yaml_IO

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
config_path = os.path.join(project_root, 'Lib', 'config_this_before_action.yaml')
config_info = json_yaml_IO.read_yaml(config_path) # type: ignore
# %%
class linkedin_job_scraper(driver_manager):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.linkedin.com/jobs/search/"
        self.save_dir = None
        self.job_details_css_selector = "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__detail.overflow-x-hidden.jobs-search__job-details > div"
        self.job_list_css_selector = "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__list > div"
        self.pagination_css_selector = "#jobs-search-results-footer > div.jobs-search-pagination.jobs-search-results-list__pagination.p4 > p"
        self.job_card_class = "scaffold-layout__list-item"

        self.login_button_css_selector = "#base-contextual-sign-in-modal > div > section > div > div > div.contextual-sign-in-modal__right-content > button"
        self.email_input_id = "csm-v2_session_key"
        self.password_input_id = "csm-v2_session_password"
        self.submit_button_css_selector = "#base-contextual-sign-in-modal > div > section > div > div > div.contextual-sign-in-modal__right-content > form > div.flex.justify-between.sign-in-form__footer--full-width > button"

    def login(self):
        try:
            login_button = self.get_element(
                By.CSS_SELECTOR, 
                self.login_button_css_selector, 
                wait_time=15
                )
            for i in range(3):
                if login_button is None:
                    self.get_url(target_url=self.base_url)
                    time.sleep(10)
                    login_button = self.get_element(
                        By.CSS_SELECTOR, 
                        self.login_button_css_selector, 
                        wait_time=15
                    )
                    if login_button is None:
                        print(f"could not find login button after {i+1} attempts")
                    continue
                else:
                    break
            self.click_element(login_button)
        except Exception as e:
            print(f"Error logging in: could not find login button")
            print(f"Error logging in: {e}")
            return False
        time.sleep(0.5)
        try:
            email_input = self.get_element(By.ID, self.email_input_id, wait_time=60)
            self.send_keys(config_info["your_linkedin_username"], email_input)
            time.sleep(0.5)
            password_input = self.get_element(By.ID, self.password_input_id, wait_time=60)
            self.send_keys(config_info["your_linkedin_password"], password_input)
            time.sleep(0.5)
            login_button2 = self.get_element(
                By.CSS_SELECTOR, 
                self.submit_button_css_selector, 
                wait_time=15
            )
            self.click_element(login_button2)
        except Exception as e:
            print(f"Error logging in: could not find email or password input")
            print(f"Error logging in: {e}")
            return False
        return True

    def check_login_success(self):
        for i in range(20):
            job_list_element = self.get_element(By.CSS_SELECTOR, self.job_list_css_selector, wait_time=60)
            if job_list_element is None:
                time.sleep(120)
                print(f"page not loaded, waiting for {180 * i} seconds")
                continue
            else:
                print(f"login successful")
                return True
        print(f"login failed")
        return False

    def get_inner_soup(self, element: WebElement):
        inner_soup = BeautifulSoup(
            element.get_attribute("innerHTML"),
            "html.parser"
        )
        return inner_soup

    def get_job_detail_soup(self):
        job_details_element = self.get_element(By.CSS_SELECTOR, self.job_details_css_selector)
        if job_details_element is None:
            return None
        else:
            job_details_soup = self.get_inner_soup(job_details_element)
            return job_details_soup

    def get_full_job_detail_soup(self):
        # 先获取 job_details_element (WebElement) 用于点击按钮
        job_details_element = self.get_element(By.CSS_SELECTOR, self.job_details_css_selector)
        if job_details_element is None:
            return None
        
        # 查找 company_box 的 WebElement
        company_box_element = None
        for i in range(5):
            try:
                # 尝试查找 company_box
                company_box_element = job_details_element.find_element(By.CSS_SELECTOR, "section.jobs-company")
                if company_box_element is not None:
                    break
            except:
                pass
            
            # 如果找不到，向下滚动
            if company_box_element is None:
                self.scroll_element(direction='down')
                time.sleep(0.5)
                # 重新获取 job_details_element（可能已更新）
                job_details_element = self.get_element(By.CSS_SELECTOR, self.job_details_css_selector)
                if job_details_element is None:
                    return None
        
        # 如果找到了 company_box，点击其中的所有"展开"按钮
        if company_box_element is not None:
            try:
                # 查找所有"展开"按钮（class 包含 inline-show-more-text__button，文本为"展开"）
                # 使用 normalize-space() 处理文本中的空白字符
                expand_buttons = company_box_element.find_elements(
                    By.XPATH, 
                    ".//button[contains(@class, 'inline-show-more-text__button') and normalize-space(text())='展开']"
                )
                
                # 点击所有找到的按钮
                for button in expand_buttons:
                    try:
                        # 滚动到按钮位置，确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.3)
                        # 点击按钮
                        self.click_element(button)
                        time.sleep(0.5)  # 等待内容展开
                    except Exception as e:
                        print(f"Error clicking expand buttons: {e}")
                        continue
            except Exception as e:
                print(f"Error finding expand buttons: {e}")
        
        # 等待内容完全展开
        time.sleep(1)
        
        # 获取更新后的 soup
        job_details_soup = self.get_job_detail_soup()
        return job_details_soup

    def get_id_set(self):
        job_list_element = self.get_element(By.CSS_SELECTOR, self.job_list_css_selector, wait_time=60)
        pagination_element = self.get_element(By.CSS_SELECTOR, self.pagination_css_selector, wait_time=60)
        
        # 检查 job_list_element 是否存在
        if job_list_element is None:
            print(f"Error: job_list_element not found with selector: {self.job_list_css_selector}")
            return None, None, None, None
        
        # 只有当 job_list_element 存在且 pagination_element 不存在时，才尝试滚动
        if pagination_element is None and job_list_element is not None:
            self.scroll_until_element_appears(
                job_list_element, 
                pagination_element
            )
            # 重新获取元素
            job_list_element = self.get_element(By.CSS_SELECTOR, self.job_list_css_selector)
            pagination_element = self.get_element(By.CSS_SELECTOR, self.pagination_css_selector)
            # 再次检查元素是否存在
            if job_list_element is None:
                print(f"Error: job_list_element not found after scrolling")
                return None, None, None, None

        # 滚动到顶部（使用窗口滚动，避免 stale element）
        self.scroll_element(direction='top', element=None)
        time.sleep(1)  # 等待滚动完成
        
        # 重新获取元素，避免 stale element 问题
        job_list_element = self.get_element(By.CSS_SELECTOR, self.job_list_css_selector)
        if job_list_element is None:
            print(f"Error: job_list_element not found after scrolling to top")
            return None, None, None, None
        
        job_list_soup = self.get_inner_soup(job_list_element)
        try:
            job_cards = job_list_soup.find_all("li", class_=lambda x:x and self.job_card_class in x)
        except Exception as e:
            print(f"Error getting job cards: {e}")
            return None, None, None, None

        id_set = {}
        job_id_list = []
        for job_card in job_cards:
            job_card_id = job_card.get("id", "")
            job_id = job_card.get("data-occludable-job-id", "")
            if job_id and job_id not in job_id_list:
                id_set[job_id] = job_card_id
                job_id_list.append(job_id)

        print(f"job_id_list length: {len(job_id_list)}")

        return id_set, job_id_list
        

    def click_follow_button(self):
        follow_button = self.get_element(By.CSS_SELECTOR, ".jobs-save-button__text")
        self.click_element(follow_button)
        time.sleep(1)
        
    def get_1page_job_details(self):
        id_set, job_id_list = self.get_id_set()
        job_details_set = {}

        for job_id in job_id_list:

            job_card_id = id_set[job_id]

            job_card_element = self.get_element(By.ID, job_card_id)
            self.click_element(job_card_element)
            time.sleep(1)

            job_details_soup = self.get_full_job_detail_soup()
            job_details_set[job_id] = job_details_soup

        return job_details_set

    def get_all_job_details(self, page_num, search_keywords):
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d')
        all_job_details_set = {}
        for page in range(page_num):
            print(f"Processing page {page + 1}/{page_num}...")

            old_params_keys = ['start', 'keywords']
            new_params_values = [page * 25 if page > 0 else 0, search_keywords]

            # 使用页面加载检测，检查 job_list_element 是否存在
            page_loaded, error_page_info = self.switch_to_url(
                old_params_keys, 
                new_params_values,
                check_element=(By.CSS_SELECTOR, self.job_list_css_selector)
            )
            
            if not page_loaded:
                print(f"Warning: Page {page + 1} cannot be loaded")
                print(f"Collected {len(all_job_details_set)} job details, exiting and saving...")
                info = {
                    'page': page + 1,
                    'page_num': page_num,
                    'search_keywords': search_keywords,
                    'error_page_info': error_page_info
                }
                json_yaml_IO.write_json(f"{project_root}/data/Linkedin_Scraping_Log/{now}_info.json", info)
                if all_job_details_set:
                    return all_job_details_set
            time.sleep(3)

            job_details_set = self.get_1page_job_details()
            all_job_details_set.update(job_details_set)
            print(f"Page {page + 1} successfully collected {len(job_details_set)} job details, total {len(all_job_details_set)}")

        info = {
            'page': page_num,
            'page_num': page_num,
            'success_message': f"Successfully collected {len(all_job_details_set)} job details"
        }
        json_yaml_IO.write_json(f"{project_root}/data/Linkedin_Scraping_Log/{now}_info.json", info)

        return all_job_details_set

    def save_job_details(self, job_id, job_details_soup):
        os.makedirs(self.save_dir, exist_ok=True)
        with open(f"{self.save_dir}/{job_id}.html", "w", encoding="utf-8") as f:
            f.write(job_details_soup.prettify())
        print(f"Saved job details for job_id: {job_id}")

# %%
if __name__ == "__main__":
    today = datetime.now().strftime('%Y%m%d')
    scraper = linkedin_job_scraper()
    scraper.get_url(target_url=scraper.base_url)

    # %%
    scraper.login()
    if scraper.check_login_success():
        print("Login successful")
    else:
        print("Login failed")
    # %%
    from minio import Minio
    from minio.error import S3Error

    import io

    client = Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    bucket_name = "jobdatabucket"
    object_name = f"raw/Linkedin_html/dt={today}/"

    def up_load_to_minio(file_bytes, bucket_name, object_name, object_type):
        data_stream = io.BytesIO(file_bytes)
        client.put_object(
            bucket_name=bucket_name, 
            object_name=object_name, 
            data=data_stream, 
            length=len(file_bytes),
            content_type=object_type
        )

    # %%
    job_details_set = scraper.get_all_job_details(page_num=16, search_keywords='data engineer')
    
    # %%
    for job_id, job_details_soup in job_details_set.items():
        file_bytes = job_details_soup.prettify().encode('utf-8')
        up_load_to_minio(
            file_bytes, 
            bucket_name, 
            f"raw/Linkedin_html/dt={today}/{job_id}.html",
            "text/html"
        )


# %%
