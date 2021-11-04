import datetime
import hashlib
from datetime import datetime, timedelta
from urllib import parse

# pyJWT 패키지 설정
import jwt
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, redirect, url_for
# db 연결
from pymongo import MongoClient
from selenium import webdriver

client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.miniproject

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'


# 시작 페이지. 사용자 토큰을 확인 후 login 페이지나 list 페이지로 보내줍니다.
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('main.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    return render_template("login.html")


# 회원가입 API
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 로그인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_nick_dup', methods=['POST'])
def check_nick_dup():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': (datetime.utcnow() + timedelta(seconds=60 * 60 * 24))  # 로그인 24시간 유지
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/main')
def main():
    # 식당리스트 페이지
    return render_template("main.html")


@app.route('/vegan/delReview')
def delReview():
    # 리뷰작성페이지에서 본인이 작성한 리뷰 삭제시 상세페이지로 이동
    return render_template("detailView.html")


# 네이버 크롤링 ----------------------------------------------------
@app.route('/search', methods=['GET'])
def keyword():
    rest_list = []
    search = request.args.get('search_give')
    url = 'https://search.naver.com/search.naver?sm=tab_sug.top&where=nexearch&query='
    urlImg = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='
    newUrl = url + parse.quote(search + '비건맛집')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.86 Safari/537.36'}
    html = requests.get(newUrl, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    rests = soup.select('div#place-app-root.place-app-root > div#loc-main-section-root > section.sc_new._1hPYK > '
                        'div.api_subject_bx> '
                        'div.place_section_content > ul._3smbt > li._22p-O.m29At')

    for rest in rests:

        rest_name = rest.select_one('div._3ZU00._1rBq3 > a._3LMxZ > div._2w9xx > div._2s4DU > span._3Apve').get_text()
        rest_tag = rest.select_one('div._3ZU00._1rBq3 > a._3LMxZ > div._2w9xx > div._2s4DU > span._3B6hV').get_text()
        rest_url = rest.select_one('div._3ZU00._1rBq3 > a')['href']
        call = rest.select_one('div._3ZU00._1rBq3 > div._1oH7-._1lPUe')

        # 번호가 없는 경우
        if call is not None:
            callNum = call.get_text()
        else:
            callNum = "번호정보없음"
        print(rest_name, rest_tag, call, rest_url)

        # 이미지,주소 크롤링의 경우 다른 곳에 있어서 2차 크롤링 시작(주소인 newUrlImg 참고)
        chrome_options=webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
        newUrlImg = urlImg + parse.quote(search + " " + rest_name)
        print(newUrlImg)
        driver.get(newUrlImg)
        req = driver.page_source
        soupImg = BeautifulSoup(req, 'html.parser')
        # htmlImg = requests.get(newUrlImg, headers=headers)
        # soupImg = BeautifulSoup(htmlImg.text, 'html.parser')

        address1 = soupImg.select_one('#place_main_ct > div > section > div > div.ct_box_area > div.bizinfo_area > div '
                                      '> div:nth-child(2) > div > ul > li:nth-child(1) > span > a > '
                                      'span.txt')

        address2 = soupImg.select_one('#loc-main-section-root > section > div > div.place_section_content > '
                                      'div._1ubnL > div._3DQBL > div.Qgg-A._1hnfE > div')

        star_tag = soupImg.select_one(
            '#place_main_ct > div > section > div > div.default_info_area.booking_review_area > '
            'div > span.score > em')

        images = soupImg.select_one('div#place_main_ct > div._nx_place_wrapper > section.sc_new.nx_place > '
                                    'div.api_subject_bx > div.top_photo_area.type_v4 > div.thumb_area > '
                                    'a.thumb._top_thumb_wrapper > img')

        # 주소 selector가 다른 경우
        if address1 is not None:
            address = address1.get_text()
        elif address2 is not None:
            address = address2.get_text()
        else:
            address = "주소정보없음"

        # 별점 등록 안된식당
        if star_tag is not None:
            star = star_tag.get_text()
        else:
            star = "별점정보없음"

        # 이미지를 등록한 음식점과 없는 음식점이 있어서 if문 사용.
        if images is not None:
            image = images['src']
        else:
            image = "https://cdn.pixabay.com/photo/2016/04/21/13/48/vegan-1343429_1280.png"

        print(images, address, star)
        data = {
            'rest_name': rest_name,
            'rest_tag': rest_tag,
            'callNum': callNum,
            'rest_url': rest_url,
            'image': image,
            'address': address,
            'star': star
        }
        # 처음 선언한 리스트에 크롤링 결과를 저장
        rest_list.append(data)

    return jsonify({'rest_lists': rest_list})


@app.route('/detailView')
def detail():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('detailView.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/posting', methods=['POST'])
def review():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        comment = request.form['comment']
        # date = request.form['date']
        doc = {
            "username": user_info["username"],
            "comment": comment,
            # "date": date
        }
        db.review.insert_one(doc)
        return jsonify({"result": "success", "msg": "리뷰작성완료"})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 리뷰 리스트 가져오기 (최근 10개)
@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 최근등록 리뷰 10개까지
        posts = list(db.review.find({}).sort("date", -1).limit(10))
        for post in posts:
            post["_id"] = str(post["_id"])
        return jsonify({"result": " success", "msg": "리뷰를 로드 완료했습니다", "posts": post})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("detailView.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
