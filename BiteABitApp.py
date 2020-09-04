from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('BiteABit.html')


@app.route('/post', methods=['POST'])
def post_post():
    # 1. 클라이언트로부터 데이터를 받기
    post_eng_receive = request.form['post_eng_give']
    post_kor_receive = request.form['post_kor_give']
    post_memo_receive = request.form['post_memo_give']

    # web-scraping
    text = post_eng_receive
    url = 'https://yarn.co/yarn-find?text=' + text

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    post_test = soup.select_one('.clip-wrap')
    print(post_test)

    print('url 부분')
    post_test = soup.select_one('.clip-wrap')

    # b = post_test.findAll("a")
    url = ""
    for link in post_test.findAll("a"):
        if 'href' in link.attrs:
            url = link.attrs['href']
            break

    print(url)
    post_url = 'http://yarn.co' + url

    print('img source')

    post_test = soup.select_one('.clip-wrap')
    post_image = ''
    for test in post_test.findAll("img"):
        try:
            post_image = test.get("src")
        except:
            print('here')

    print(post_image)

    post = {
        'post_image': post_image,
        'post_url': post_url,
        'post_eng': post_eng_receive,
        'post_kor': post_kor_receive,
        'post_memo': post_memo_receive
    }


    # 3. mongoDB에 데이터 넣기
    db.posts.insert_one(post)
    # 다했다고(성공했다고) 알려주기
    return jsonify({'result': 'success', 'msg': '등록되었습니다.'})

@app.route('/delete', methods=['POST'])
def delete_post():
    # 삭제할 데이터의 정보를 프론트에서 받아오기

    post_url_receive = request.form['post_url_give']
    post_image_receive = request.form['post_image_give']
    post_eng_receive = request.form['post_eng_give']
    post_kor_receive = request.form['post_kor_give']
    post_memo_receive = request.form['post_memo_give']
    # 2. posts 목록에서 delete_one으로 3가지가 모두 일치하는 칼럼을 찾아 삭제
    db.posts.delete_one({'post_image': post_image_receive, 'post_url': post_url_receive, 'post_eng':post_eng_receive, 'post_kor': post_kor_receive, 'post_memo': post_memo_receive})

    # 3. 성공하면 success 메시지를 반환합니다.제
    return jsonify({'result': 'success'})



@app.route('/post', methods=['GET'])
def read_posts():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기(Read)
    posts = list(db.posts.find({}, {'_id':0}))

    # 2. posts라는 키 값으로 posts 정보 보내주기
    return jsonify({'result': 'success', 'posts': posts})

@app.route('/post/edit', methods=["POST"])
def edit_post():
    post_eng_receive = request.form['post_eng_give']
    post_kor_receive = request.form['post_kor_give']
    post_memo_receive = request.form['post_memo_give']
    print(post_eng_receive)
    print(post_kor_receive)
    print(post_memo_receive)

	# username 기준으로 메시지를 찾아 내용과 생성 시각을 업데이트합니다.
    db.posts.update_one({'post_eng': post_eng_receive}, {
                           '$set': {'post_kor': post_kor_receive, 'post_memo': post_memo_receive}})

    return jsonify({'result': 'success', 'msg': '성공적으로 수정되었습니다.'})


@app.route('/search', methods=['GET'])
def search_post():
    # 1. 클라이언트로부터 데이터를 받기
    post_search_receive = request.args.get('post_search_give')

    search_result = []
    post_eng_list = list(db.posts.find({"post_eng":{"$regex":post_search_receive}}, {'_id': 0}))
    post_kor_list = list(db.posts.find({"post_kor":{"$regex":post_search_receive}}, {'_id': 0}))

    for post_eng in post_eng_list:
        search_result.append(post_eng)
    for post_kor in post_kor_list:
        search_result.append(post_kor)
    return jsonify({'result': 'success', 'search_result': search_result})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)