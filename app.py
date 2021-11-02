from urllib import parse
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/vegan/login')
def main_login():
    return render_template("index.html")


@app.route('/vegan/join')
def join():
    return render_template("join.html")


@app.route('/vegan/logout')
def logout():
    # 로그아웃은 따로 열리는 html페이지 없이 바로 로그인 페이지 연결
    return render_template("login.html")


@app.route('/vegan/list')
def list():
    # 식당리스트 페이지
    return render_template("list.html")


@app.route('/vegan/detailView')
def detail():
    return render_template("detailView.html")


@app.route('/vegan/writeReview')
def writeReview():
    return render_template("login.html")


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
        call = rest.select_one('div._3ZU00._1rBq3 > div._1oH7-._1lPUe').get_text()
        print(rest_name, rest_tag, call, rest_url)

        # 이미지,주소 크롤링의 경우 다른 곳에 있어서 2차 크롤링 시작(주소인 newUrlImg 참고)
        newUrlImg = urlImg + parse.quote(search + rest_name)
        print(newUrlImg)
        htmlImg = requests.get(newUrlImg, headers=headers)
        soupImg = BeautifulSoup(htmlImg.text, 'html.parser')
        images = soupImg.select_one('div#place_main_ct > div._nx_place_wrapper > section.sc_new.nx_place > '
                                    'div.api_subject_bx > div.top_photh_area.type_v4 > div>thumb_area > '
                                    'a.thumb._top_thumb_wrapper > img')
        address = soupImg.select_one('div#place_main_ct > div._nx_place_wrapper > section.sc_new.nx_place > '
                                     'div.api_subject_bx > div.ct_box_area > div.bizinfo_area > div.list_bizinfo > '
                                     'div.list_item > div.txt > ul.list_address > li > span.addr > a.address > '
                                     'span.txt')
        star = soupImg.select_one('div#place_main_ct > div._nx_place_wrapper > section.sc_new.nx_place > '
                                  'div.api_subject_bx > div.default_info_area.booking_review_area > div.star_area > '
                                  'span.score > em')
        print(images, address, star)
        # 이미지를 등록한 음식점과 없는 음식점이 있어서 if문 사용.
        if images is not None:
            image = images['src']
        else:
            image = "https://3.bp.blogspot.com/-ZKBbW7TmQD4/U6P_DTbE2MI/AAAAAAAADjg/wdhBRyLv5e8/s1600/noimg.gif"

        data = {
            'rest_name': rest_name,
            'rest_tag': rest_tag,
            'call': call,
            'rest_url': rest_url,
            'images': images,
            'address': address,
            'star': star
        }
        # 처음 선언 했는 리스트에 크롤링 결과를 저장
        rest_list.append(data)

        # # 크롤링 결과는 최대 20개까지로 하고 그 이후는 break걸어둠
        # n += 1
        # if n > 20:
        #     break
    return jsonify({'rest_lists': rest_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
