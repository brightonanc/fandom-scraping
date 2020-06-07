"""
Originally created to parse fandom wikis for popular pages and create CSVs for
use in skribbl.io
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re


def get_page_url(fandom, sort, page_num):
    return 'https://{}.fandom.com/wiki/Special:Insights/popularpages' \
            '?sort=pv{}&page={}'.format(fandom, sort, page_num)

def post_process(term_arr):
    for i in range(len(term_arr)):
        term = term_arr[i]
        term = re.sub('\(.*?\)', '', term)
        term = term.strip()
        term_arr[i] = term
    return term_arr


if __name__ == '__main__':
    if 4 > len(sys.argv):
        print('scrape.py [fandom] [sort] [ct]')
        print('  fandom: name of fandom, e.g. https://[fandom].fandom.com/wiki')
        print('  sort:    7: last week')
        print('          28: last 4 weeks')
        print('          Diff: recent increase in page views')
        print('  ct:     Number of terms to collect')
        exit(0)
    fandom = sys.argv[1]
    sort = sys.argv[2]
    term_ct = int(sys.argv[3])
    assert sort in ('7', '28', 'Diff')
    assert term_ct > 0
    term_arr = [''] * term_ct
    page_num = 1
    term_num = 0
    while term_num < term_ct:
        page_url = get_page_url(fandom, sort, page_num)
        page = requests.get(page_url)
        assert 200 == page.status_code
        soup = BeautifulSoup(page.content, 'html.parser')
        a_elem_arr = soup.find('table', class_='insights-list') \
                .find_all('a', class_='insights-list-item-title')
        a_elem_ct = len(a_elem_arr)
        a_elem_num = 0
        while (a_elem_num < a_elem_ct) and (term_num < term_ct):
            term_arr[term_num] = a_elem_arr[a_elem_num].text
            a_elem_num += 1
            term_num += 1
        page_num += 1
    term_arr = post_process(term_arr)
    basename = '{}_{}.csv'.format(fandom, term_ct)
    filepath = os.path.join(os.path.dirname(__file__), basename)
    with open(filepath, 'w') as file:
        print(',\n'.join(term_arr) + ',\n', file=file)
