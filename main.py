from datetime import datetime
import json
import os
import requests
from module.chrome_cookie_parser import get_chrome_cookies
import argparse

TISTORY_URL_ID = "pgh268400"
IS_DATETIME = False

# argparse는 파이썬에서 간단한 CLI를 만드는 데에 필요한 모든 기능을 제공한다.

# parser를 만든다.
parser = argparse.ArgumentParser(
    description="""
    티스토리 블로그의 HTML과 CSS를 백업하는 프로그램입니다.
    크롬 브라우저에서만 사용이 가능하며,
    크롬 브라우저에서 티스토리에서 로그인을 한 상태에서 사용해야 합니다.
    브라우저에서 티스토리 로그인을 한 상태에서 프로그램을 실행하면,
    프로그램이 자동으로 크롬 브라우저의 쿠키를 가져와서
    티스토리 블로그의 HTML과 CSS를 백업합니다.
    """)

# parser.add_argument로 받아들일 인수를 추가해나간다.
parser.add_argument(
    'id', help='티스토리 ID ex) abcd.tistory.com -> id : abcd')    # 필요한 인수를 추가

# 옵션 인수(지정하지 않아도 괜칞은 인수를 추가
parser.add_argument(
    '--enable-date', help="백업 파일 이름에 현재 시간(백업한 시간)을 포함시키는 옵션입니다", action='store_true')  # store_true = flag를 지정시에 사용 True / False

# parser.add_argument('-a', '--arg4')   # 자주 사용하는 인수라면 약칭이 있으면 사용할 때 편리하다

args = parser.parse_args()    # 인수를 분석 (인수가 올바르지 않으면 여기서 프로그램이 종료된다.)


# 인자값을 상수에 반영
TISTORY_URL_ID = args.id
IS_DATETIME = args.enable_date

try:
    cookies = get_chrome_cookies(
        target_domain=".tistory.com", for_requests_module=True)

    url = f"https://{TISTORY_URL_ID}.tistory.com/manage/design/skin/html.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Referer": f"https://{TISTORY_URL_ID}.tistory.com/manage/design/skin/edit",
        "X-XSRF-TOKEN": cookies["XSRF-TOKEN"],  # type: ignore
    }

    response = requests.get(url, headers=headers,
                            cookies=cookies)  # type: ignore

    # html.json 이라고 하는, html과 css를 포함한 json 파일을 가져온다. (main source 파일)
    html_json = response.json()

    # 현재 시간 가져오기 : 2021-07-01 PM 3:00:00
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d-%p-%I.%M")

    # 폴더가 없다면 폴더 생성하기
    if not os.path.isdir(TISTORY_URL_ID):
        os.mkdir(TISTORY_URL_ID)

    insert_str = ""
    if IS_DATETIME:
        insert_str = f"-{now_str}"
    # html_json 저장하기 (main source 파일)
    main_json_path = os.path.join(TISTORY_URL_ID, f"html{insert_str}.json")
    with open(main_json_path, "w", encoding="utf-8") as f:
        json.dump(html_json, f, ensure_ascii=False, indent=4)

    # HTML 저장하기 (by html.json)
    html_path = os.path.join(TISTORY_URL_ID, f"main-backup{insert_str}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_json["html"])

    # CSS 저장하기 (by html.json)
    css_path = os.path.join(TISTORY_URL_ID, f"style-backup{insert_str}.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(html_json["css"])

    print("데이터를 파일에 저장했습니다.")

except Exception as e:
    print(e)
