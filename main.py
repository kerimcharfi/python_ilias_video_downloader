import os
import re

import requests
import bs4
from bs4 import BeautifulSoup
import shutil

cookies = {
    "ilClientId": "produktiv",  # maybe not needed
    "_shibsession_***...": "_*****...",
    "PHPSESSID": "***..."
}

# maybe not needed
headers = {
    # "referer": "",
}


def download_videos(page_url, target_dir):
    global cookies, headers

    i_page = 0

    while page_url:

        # hit landing page
        res = requests.get(page_url, cookies=cookies, headers=headers)

        res = requests.get(
            "https://ilias.studium.kit.edu/" + re.search("url *: *'(.*?)'", res.text).group(1).replace("\\", ""),
            cookies=cookies, headers=headers
        )

        redirected_soup: bs4.BeautifulSoup = BeautifulSoup(res.content, "html.parser")

        video_links = list(filter(lambda e: "Abspielen" in e.decode_contents(), redirected_soup.findAll("a")))

        # get video titles
        titles = []
        table_wrapper = redirected_soup.find('div', attrs={'class': 'ilTableOuter'})
        table = table_wrapper.find('table')
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            titles.append(cols[2].text.strip())  # Get rid of empty values

        # download videos
        for i, link in enumerate(video_links):
            res = requests.get(
                "https://ilias.studium.kit.edu/" + video_links[i]["href"], cookies=cookies, headers=headers
            )

            response = requests.get(re.search('"src" *: *"(.*?)"', res.text).group(1).replace("\\", ""),
                                    cookies=cookies, headers=headers, stream=True)
            with open(os.path.join(target_dir, f'{titles[i]}_video{i}_page{i_page}.mp4'), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

            print("finished " + os.path.join(target_dir, f'video{i}_page{i_page}.mp4'))

        # get next page
        weiter_links = list(filter(lambda e: "weiter" in e.decode_contents(), redirected_soup.findAll("a")))
        if len(weiter_links) > 0:
            page_url = "https://ilias.studium.kit.edu/" + weiter_links[0]["href"]
        else:
            page_url = None

        i_page += 1


if __name__ == '__main__':
    while True:
        source = input("source_url: ")
        target = input("target_dir: ")
        download_videos(source, target)
