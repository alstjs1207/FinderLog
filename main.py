from flask import Flask, render_template, request, send_file
from werkzeug.utils import redirect
from functions import getCourses
from export import export
from db import languages, db, localdb
import json
import urllib.parse
from datetime import datetime
import pytz


app = Flask(__name__, template_folder="templates")


@app.route("/")
def main():
    return render_template("index.html", languages=languages)

@app.route("/export")
def file():
    keywords = localdb.get('keyword')
    if not keywords:
        raise Exception()
    export()
    return send_file("keywords.csv")

@app.route("/log")
def getCourseLog():
    keywords = []
    # JSON 파일 읽기
    with open('keyword.db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    localDB = localdb.get('keyword')
    if localDB:
        keywords = localDB
    else:
        # 각 데이터에 대해 처리
        for entry in data:
            # httpRequest가 존재하는지 확인
            timestamp = entry.get("timestamp", "No timestamp found")
            utc_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            # UTC 시간대 설정
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            # KST로 변환
            kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
            formatted_time = kst_time.strftime('%Y-%m-%d %H:%M:%S')
            if 'httpRequest' in entry:
                request_url = entry["httpRequest"].get("requestUrl", "")

                # URL에서 query string 파싱
                parsed_url = urllib.parse.urlparse(request_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)

                # keyword 값을 디코딩
                if 'keyword' in query_params:
                    encoded_keyword = query_params['keyword'][0]
                    decoded_keyword = urllib.parse.unquote(encoded_keyword)
                    keywords.append({'timestamp': timestamp, 'decoded_keyword': decoded_keyword})
                else:
                    print("No keyword found in URL")
            else:
                print("No httpRequest found in entry")

        localdb['keyword']=keywords

    return render_template("result1.html", keywords=keywords, count=len(keywords))



if __name__ == "__main__":
    # 정적 파일로 변환
    with app.test_request_context():
        if not os.path.exists('static_site'):
            os.makedirs('static_site')

        pages = ['result1.html', 'index.html']
        for page in pages:
            with open(f'static_site/{page}', 'w') as f:
                f.write(render_template(page))

    app.run(debug=True)
