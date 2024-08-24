from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import parse
import math
from time import sleep


class GG_Bibtex(object):
    def __init__(self, driver_path, gg_search_url):
        self.driver = None
        self.gg_search_url = gg_search_url
        self.driver_path = driver_path
        self.reset(driver_path)

    def reset(self, driver_path):
        self.service = Service(driver_path)
        option = webdriver.ChromeOptions()
        # option.add_argument('headless')  # no show window
        # self.driver = webdriver.Chrome(service=self.service, options=option)
        self.driver = webdriver.Chrome(executable_path=driver_path, options=option)
        self.driver.set_window_size(800, 800)

    def get_bib_text(self, paper_title):
        elements_xpath = {
            'qoute_btn':  '/html/body/div/div[4]/div/div[2]/div/a[2]/span',
            'bibtex_btn': '/html/body/div/div[4]/div/div[2]/div/div[2]/a[1]',
            'bib_text': '/html/body/pre'
        }
        strto_pn = parse.quote(paper_title)
        url = self.gg_search_url + strto_pn
        self.driver.get(url)
        # import ipdb
        # ipdb.set_trace()
        qoute_btn = self.driver.find_element(By.CLASS_NAME, 'gs_or_cit')
        # qoute_btn = WebDriverWait(self.driver, 15, 0.1).until(
        #     EC.presence_of_element_located((By.XPATH, elements_xpath['qoute_btn']))
        # )
        qoute_btn.click()

        bibtex_btn = WebDriverWait(self.driver, 15, 0.1).until(
            EC.presence_of_element_located((By.XPATH, elements_xpath['bibtex_btn']))
        )
        # bibtex_btn = self.driver.find_element(By.CLASS_NAME, 'gs_citi')
        bibtex_btn.click()

        bib_text = WebDriverWait(self.driver, 15, 0.1).until(
            EC.presence_of_element_located((By.XPATH, elements_xpath['bib_text']))
        )
        bib_text = bib_text.text
        return bib_text

    def _quit_driver(self):
        self.driver.quit()
        self.service.stop()

    def results_writter(self, results, output_file_path='output.txt'):
        wtf = []
        for re_key in results.keys():
            context = results[re_key]
            # wtf.append(re_key + '\n')
            wtf.append(context + '\n\n')
        with open(output_file_path, 'a+') as f:
            f.writelines(wtf)

    def run(self, paper_names, output_file_path, reset_len=100):
        """
        @params:
            paper_names: [LIST], your paper names.
            reset_len: [INT], for avoid the robot checking, you need to reset the driver for more times, default is 10 papers
        """
        paper_len = len(paper_names)
        rest = paper_len % reset_len
        task_packs = []
        if paper_len > reset_len:
            groups_len = int(math.floor(paper_len / reset_len))  # 21/20 = 1
            for i in range(groups_len):
                sub_names = paper_names[(i) * reset_len:(i + 1) * reset_len]
                task_packs.append(sub_names)

        task_packs.append(paper_names[-1 * rest:])
        results = {}
        for ti in task_packs:
            for pn in ti:
                if len(pn) < 3:
                    continue
                print('\n---> Searching paper: {} ---> \n'.format(pn))
                try:
                    bibtex = self.get_bib_text(pn)
                    print(bibtex)
                    results[pn] = bibtex
                except:
                    results[pn] = f"Not Found: {pn}"
            # self._quit_driver()
            sleep(1)
            # self.reset(self.driver_path)
            print('-' * 10 + '\n Reset for avoiding robot check')
        self.results_writter(results, output_file_path)
        return results


if __name__ == "__main__":
    driver_path = r"C:\Users\Lenovo\Downloads\chromedriver-win64\chromedriver-win64/chromedriver.exe"
    input_file_path = 'refs_word.txt'
    output_file_path = 'refs_latex.txt'

    gg_search_url = r'https://scholar.google.com.hk/scholar?hl=zh-CN&as_sdt=0%2C5&q='
    with open(input_file_path, 'rb') as f:
        content = f.read().decode()
    paper_names = content.split("\r\n")
    paper_names = [pn.replace('\n', '') for pn in paper_names][296:]

    steps = len(paper_names) // 10 + 1
    for step in range(steps):
        ggb = GG_Bibtex(driver_path=driver_path, gg_search_url=gg_search_url)
        results = ggb.run(paper_names=paper_names[10 * step: 10 * step + 10], output_file_path=output_file_path)
