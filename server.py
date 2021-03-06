# from datetime import timedelta
from datetime import timedelta

from flask import Flask, render_template, Response, jsonify, request, session, url_for, redirect
from camera import VideoCamera

app = Flask(__name__)

# session配置
app.secret_key = "fM3PEZwSRcbLkk2Ew82yZFffdAYsNgOddWoANdQo/U3VLZ/qNsOKLsQPYXDPon2t"
app.permanent_session_lifetime = timedelta(days=7)

video_camera = None
global_frame = None


# 主页
@app.route('/')
def index():
    # 模板渲染
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    return render_template("index.html")


# 登录
@app.route("/login", methods=["GET", "POST"])
def login():
    username = session.get("username")

    if username:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html")
    # 获取参数
    username = request.form.get("username")
    password = request.form.get("password")
    # 校验参数
    if not all([username, password]):
        return render_template("login.html", errmsg="参数不足")

    # 校验对应的管理员用户数据
    if not username == "admin" and password == "admin":
        return render_template("login.html", errmsg="用户名或密码错误")
    # 验证通过
    session["username"] = username

    return redirect(url_for("index"))


# 退出登录
@app.route("/logout")
def logout():
    # 删除session数据
    session.pop("username", None)
    # 返回登录页面
    return redirect(url_for("login"))


# 录制状态
@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        return jsonify(result="stopped")


# 获取视频流
def video_stream():
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()

    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


# 视频流
@app.route('/video_viewer')
def video_viewer():
    # 模板渲染
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
