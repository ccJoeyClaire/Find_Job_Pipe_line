from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString
import os
import re

from json_yaml_IO import write_json

class HtmlAnalist:
    '''
    This class is used to analyze the html file and get the head, info, company_box, and job_details_container.
    Args:
        html_file: the path of the html file
    Returns:
        head: the head of the html file
        info: the info of the html file
        company_box: the company box of the html file
        job_details_container: the job details container of the html file
    '''
    def __init__(self, html_content, base_url='https://www.linkedin.com/'):
        self.html_content = html_content
        self.base_url = base_url
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.get_head_info(base_url)
        
        info_container = self.soup.find('span', dir="ltr")
        if info_container:
            self.info = info_container.text.replace("领英站外管理的回复", "").strip()
        else:
            self.info = None

        self.company_box = self.soup.find('div', class_='jobs-company__box')
        self.job_details_container = self.soup.find('div', id='job-details')
        # find the company url element, the href is the company url, and the target is _self
        # Support both absolute and relative paths
        url_pattern = re.compile(r'(https://www\.linkedin\.com)?/company/')
        # Try to find with target="_self" first, if not found, try without target
        self.company_url_element = self.soup.find('a', 
            href=lambda href: href and url_pattern.search(str(href)), 
            target="_self")
        if not self.company_url_element:
            # Fallback: try without target attribute
            self.company_url_element = self.soup.find('a', 
                href=lambda href: href and url_pattern.search(str(href)))


    def get_head_info(self, base_url='https://www.linkedin.com/'):
        try:
            self.head_container = self.soup.find('h1')
            self.head = self.head_container.find('a').text
            self.head_url = urljoin(base_url, self.head_container.find('a')['href'])
            return {'head': self.head, 'head_url': self.head_url}
        except Exception as e:
            print(f'Error getting head info: {e}')
            self.head = None
            self.head_url = None
            return {'head': None, 'head_url': None}
    

    def get_company_url_and_name(self):
        try:
            url = self.company_url_element['href'].replace(
                '/life', '/about'
            )
            if url.startswith('/'):
                url = urljoin(self.base_url, url)
            name = self.company_url_element.text

            self.company_url = url
            self.company_name = name
            return {'company_url': self.company_url, 'company_name': self.company_name}
            
        except Exception as e:
            print(f'Error getting company url and name: {e}')
            self.company_url = None
            self.company_name = None
            return {'company_url': None, 'company_name': None}

    # def get_job_details_content_list(self):

    #     soup = self.job_details_container
    #     content_list = []

    #     try:
    #         for element in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
    #             if element.text.strip() == '':
    #                 continue
                
    #             elif element.name == 'h2':
    #                 cleaned_text = element.text.replace('\n', '')
    #                 content = [f"##{cleaned_text}"]
                
    #             elif element.name in ['h3', 'h4', 'h5', 'h6']:
    #                 cleaned_text = element.text.replace('\n', '')
    #                 content = [f"###{cleaned_text}"]

    #             elif element.name in ['ul', 'ol']:
    #                 content = []
    #                 i = 1
    #                 for li in element.find_all('li'):
    #                     cleaned_li_text = li.text.replace('\n', '')
    #                     content.append(f"{i}. {cleaned_li_text}")
    #                     i += 1

    #             elif element.name == 'p':
    #                 if element.find('p'):
    #                     continue
    #                 else:
    #                     content = element.get_text(separator=';').split(';')
    #             else:
    #                 continue

    #             content_list.extend(content)
    #             content_list = [item for item in content_list if item not in ['', '\n', ' ', '\r']]
                
    #     except Exception as e:
    #         print(f'Error: {e}')
    #         return None
    #     return content_list

    def get_job_details_content(self):
        try:
            content = self.job_details_container.get_text(separator=';', strip=True)
            return content
        except Exception as e:
            print(f'Error getting job details content: {e}')
            return None


    def get_company_box_content(self):
        try:
            content = self.company_box.get_text(separator=';', strip=True)
            return content
        except Exception as e:
            print(f'Error getting company box content: {e}')
            return None
    

    # def get_company_box_content_list(self):
    #     soup = self.company_box
    #     content_list = []
    #     try:
    #         for element in soup.find_all(['p', 'ul', 'ol']):
    #             content = element.get_text(separator=';').split(';')
    #             content_list.extend(content)
    #             content_list = [item for item in content_list if item not in ['', '\n', ' ', '\r']]
    #     except Exception as e:
    #         print(f'Error: {e}')
    #         return None
            
    #     return content_list

    def user_input_for_LLM_job_details(self):
        return {
            'head': self.head,
            'head_url': self.head_url,
            'info': self.info,
            'job_details_content': self.get_job_details_content(),
            'company_box_content': self.get_company_box_content()
        }

if __name__ == "__main__":
    test_data = []
    for html_file in os.listdir('html_folder_Data')[:20]:
        html_analist = HtmlAnalist(open(f'html_folder_Data/{html_file}', 'r', encoding='utf-8').read())
        job_details_content = html_analist.get_job_details_content()
        company_box_content = html_analist.get_company_box_content()
        test_data.append({
            'head': html_analist.head,
            'head_url': html_analist.head_url,
            'company_url': html_analist.company_url,
            'company_name': html_analist.company_name,
            'info': html_analist.info,
            'job_details_content': job_details_content,
            'company_box_content': company_box_content
        })

    write_json('test_data_Data.json', test_data)