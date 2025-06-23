from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

from flask import Flask, request, render_template
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

def read_url(url):
    try:
        options = Options()

        for _ in [
            "headeless",
            "window-size=1920x1080",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage"
        ]:
            
            options.add_argument(_)

        driver = Chrome(options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)

        driver.get("http://127.0.0.1:8080")
        
        print("[LOG] url : ", url)
        driver.get(url)
    except Exception as e:
        print(e)
        driver.quit()
        return False
    driver.quit()
    return True

def check_xss(detail):
    url = f"http://127.0.0.1:8080/report?detail={urllib.parse.quote(detail)}"
    return read_url(url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template('report.html')

    elif request.method == 'POST':
        url = request.args.get('url')
        if not check_xss(url):
            return render_template('report.html', msg='전달이 완료되었습니다!')

        return render_template('report.html', msg='실패했습니다. 입력 값을 다시 확인해주세요.')
    
@app.route('/mypage', methods=["GET"])
def mypage():
    if request.remote_addr == '127.0.0.1':
        return render_template('mypage.html', message="KCTF_Jr{18ae1748dcfc629cb72b76af28300027}")

    return render_template('mypage.html', message="Hello User!")

@app.route('/hello', methods=["GET"])
def user():
    if request.args.get('msg', None):
        return request.args.get('msg')

    return 'hello!'

app.run(host='0.0.0.0', port=8080)