//페이지 열릴때 리뷰리스트 가져오기
$(document).ready(function () {
    get_posts()
})
// url 파라미터 값 받아오기

//리뷰작성
function post() {
    let url = location.search
    let params = new URLSearchParams(url);
    let rest = params.get('name');
    let comment = $("#textarea-post").val()
    let today = new Date().toISOString()
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            rest : rest,
            comment: comment,
            date: today
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active")
            window.location.reload()
        }
    })
}

//리뷰가져오기
function get_posts() {
    $("#post-box").empty()
    $.ajax({
        type: "GET",
        url: "/get_posts",
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"]
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i]
                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)
                    let html_temp = `<div class="box" id="${post["_id"]}">
                                        <article class="media">
                                            <div class="media-left">

                                            </div>
                                            <div class="media-content">
                                                <div class="content">
                                                    <p>
                                                        <strong>${post['username']}</strong> <small>@</small> <small>${time_before}</small>
                                                        <br>
                                                        ${post['comment']}
                                                    </p>
                                                </div>
                                                <nav class="level is-mobile">
                                                    <div class="level-left">
                                                        <span class="description__button--delete" onclick="deletePost('${post["_id"]}')">
                                                         <i class="far fa-trash-alt"></i>
                                                        </a>
           
                                                    </div>

                                                </nav>
                                            </div>
                                        </article>
                                    </div>`
                    $("#post-box").append(html_temp)
                }
            }
        }
    })
}


//로그아웃 버튼클릭
function to_logout() {
    $.removeCookie('my_token', {path: '/'});
    alert('로그아웃 합니다!!')
    window.location.href = "/login"
}

//로그인 버튼클릭
function to_login() {
    window.location.href = '/login'
}

//날짜표시
function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

//리뷰삭제
function deletePost(postId) {
    $.ajax({
        type: 'DELETE',
        url: `/post/${postId}`,
        data: {},
        success: function ({result, msg, userId}) {
            alert(msg);
            if (result === 'success') {
                window.location.href = "/detailView";
            } else {
                window.location.href = "/"
            }
        }
    })
}