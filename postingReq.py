import requests
import bs4 as bs
import json
import re


class PostingReq(object):
    """
    cvbankas api
    """
    URL_MAIN = 'https://www.cvbankas.lt/'
    URL_FRAME = 'https://www.cvbankas.lt/?miestas={city}'\
        '&padalinys%5B%5D=&keyw={keyword}'
    URL_SODRA = 'https://www.sodra.lt/calculate'
    HEADER = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Dnt": "1",
        "Host": "httpbin.org",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    }

    HEADER_SODRA = {
        'Content-Type': 'application/json',
    }

    def __init__(self, city='', keyword=''):
        """
            Initialize default values for params
        """
        self.city = city
        self.keyword = keyword
        self.result = []

    def _get_soup(self, url, **kwargs):
        """send a request and return the JSON response as Python object"
        :param url: the url to which the request will be sent
        """
        s = requests.session()
        response = s.get(url=PostingReq.URL_FRAME.format(
            city=self.city,
            keyword=self.keyword,
            headers=PostingReq.HEADER
        ))
        print(PostingReq.URL_FRAME.format(
            city=self.city,
            keyword=self.keyword)
        )
        soup = bs.BeautifulSoup(response.text, 'lxml')

        return soup

    def _save_to_file(self, source):
        with open('_output.html', 'w') as file:
            file.write(str(source))
        return

    def _get_sodra_cookie(self):
        s = requests.session()
        r = s.get('https://www.sodra.lt')

        return dict(r.cookies.items())

    def _convert_to_netto(self, salary):
        request_payload = {
            "calculator": "darbo_vietos",
            "values": [
                "2020",
                "ant_popieriaus",
                str(salary),
                "auto",
                "0",
                "taip",
                "neterminuota",
                "lietuvos",
                "darbdavio_grupe_1"
            ]
        }
        payload_json = json.dumps(request_payload)

        response = requests.post(
            url=PostingReq.URL_SODRA,
            headers=PostingReq.HEADER_SODRA,
            cookies=self._get_sodra_cookie(),
            data=payload_json,
        )
        response = response.json()
        netto = int(float(response['atlyginimas_i_rankas']))

        return netto

    def postings_list(self, unify_salary=False):
        soup = self._get_soup(url=PostingReq.URL_FRAME, city=self.city)
        # self._save_to_file(soup)
        ad_ids = soup.find_all('input', {'name': 'ad_id'})
        ad_ids = [ad_id.get('value') for ad_id in ad_ids]
        pos_urls = soup.find_all(
            "a", class_="list_a can_visited list_a_has_logo"
        )
        pos_urls = [pos_url['href'] for pos_url in pos_urls]
        positions = soup.find_all("h3", class_="list_h3")
        positions = [position.get_text() for position in positions]
        companies = soup.find_all("span", class_="dib mt5")
        companies = [company.get_text() for company in companies]
        salaries = soup.find_all("span", class_="salary_amount")
        salaries = [salary.get_text() for salary in salaries]
        salary_calculations = soup.find_all(
            "span", class_="salary_calculation"
        )
        salary_calculations = [
            sal_cal.get_text() for sal_cal in salary_calculations
        ]
        zipped = zip(
            ad_ids,
            positions,
            companies,
            salaries,
            salary_calculations,
            pos_urls
        )

        for ad_id, pos, comp, sal, sal_calc, pos_url in zipped:
            if unify_salary:
                sal = int(re.findall(r'\d+', sal)[0])
                if 'rankas' not in sal_calc:
                    sal = self._convert_to_netto(sal)
                    sal_calc = 'Netto'
            position = {
                'ad_id': ad_id,
                'position': pos,
                'company': comp,
                'salary': sal,
                'sal_calc': sal_calc,
                'pos_url': pos_url
            }
            self.result.append(position)

        return self.result

    def postings_by_salary(self):
        postings = self.postings_list(unify_salary=True)
        postings_sorted = sorted(postings, key=lambda x: (
            x['salary'], x['ad_id']), reverse=True)

        return postings_sorted
