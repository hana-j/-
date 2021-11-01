from flask import Flask, render_template

app = Flask(__name__)


@app.route('/vegan/login')
def main_login():
    return render_template("index.html")


@app.route('/vegan/join')
def join():
    return render_template("join.html")


@app.route('/vegan/logout')
def logout():
    #로그아웃은 따로 열리는 html페이지 없이 바로 로그인 페이지 연결
    return render_template("login.html")


@app.route('/vegan/list')
def list():
    #식당리스트 페이지
    return render_template("list.html")


@app.route('/vegan/detailView')
def detail():
    return render_template("detailView.html")


@app.route('/vegan/writeReview')
def writeReview():
    return render_template("review.html")


@app.route('/vegan/delReview')
def delReview():
    #리뷰작성페이지에서 본인이 작성한 리뷰 삭제시 상세페이지로 이동
    return render_template("detailView.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
