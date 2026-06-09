from html import escape
from secrets import token_urlsafe
from time import time
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse


app = FastAPI(title="Jenkins Demo API")

users: dict[str, str] = {}
sessions: dict[str, str] = {}
failed_login_attempts: dict[str, dict[str, float]] = {}

SESSION_COOKIE = "jenkins_demo_session"
MAX_LOGIN_ATTEMPTS = 3
LOGIN_LOCK_SECONDS = 10 * 60


def current_time() -> float:
    return time()


def render_page(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jenkins Demo</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                min-height: 100vh;
                padding: 24px;
                display: grid;
                place-items: center;
                color: #1f2937;
                font-family: Arial, sans-serif;
                background:
                    radial-gradient(circle at top, rgba(59, 130, 246, 0.18), transparent 30%),
                    linear-gradient(135deg, #eff6ff, #f8fafc 55%, #e0f2fe);
            }}
            main {{
                width: min(100%, 920px);
                display: grid;
                gap: 24px;
                padding: 36px;
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 28px;
                box-shadow: 0 20px 60px rgba(15, 23, 42, 0.14);
            }}
            .hero {{
                display: grid;
                gap: 12px;
            }}
            .eyebrow {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                width: fit-content;
                padding: 10px 16px;
                color: #166534;
                font-weight: 700;
                background: #dcfce7;
                border-radius: 999px;
            }}
            .dot {{
                width: 10px;
                height: 10px;
                background: #22c55e;
                border-radius: 50%;
            }}
            h1 {{
                margin: 0;
                color: #2563eb;
                font-size: clamp(2.4rem, 4vw, 3.4rem);
            }}
            p {{
                margin: 0;
                color: #475569;
                line-height: 1.7;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 20px;
            }}
            .card {{
                padding: 24px;
                background: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 22px;
            }}
            .card h2 {{
                margin: 0 0 16px;
                font-size: 1.2rem;
            }}
            form {{
                display: grid;
                gap: 12px;
            }}
            label {{
                display: grid;
                gap: 8px;
                font-weight: 600;
                color: #0f172a;
            }}
            input {{
                width: 100%;
                padding: 12px 14px;
                border: 1px solid #cbd5e1;
                border-radius: 14px;
                font: inherit;
            }}
            button {{
                border: 0;
                padding: 12px 16px;
                color: #fff;
                font: inherit;
                font-weight: 700;
                background: linear-gradient(135deg, #2563eb, #0f766e);
                border-radius: 14px;
                cursor: pointer;
            }}
            .message {{
                padding: 14px 16px;
                color: #7c2d12;
                background: #ffedd5;
                border-radius: 14px;
            }}
            .welcome {{
                display: grid;
                gap: 18px;
                align-items: start;
            }}
            .welcome strong {{
                color: #0f172a;
                font-size: 1.3rem;
            }}
            .logout {{
                width: fit-content;
                text-decoration: none;
                padding: 12px 16px;
                color: #0f172a;
                font-weight: 700;
                background: #e2e8f0;
                border-radius: 14px;
            }}
        </style>
    </head>
    <body>
        <main>
            {content}
        </main>
    </body>
    </html>
    """


def render_login_page(message: str = "") -> str:
    message_block = f'<div class="message">{escape(message)}</div>' if message else ""
    return render_page(
        f"""
        <section class="hero">
            <span class="eyebrow"><span class="dot"></span>Service Online</span>
            <h1>Jenkins Demo</h1>
            <p>请输入账号密码登录，进入 Jenkins Demo 首页1。</p>
            {message_block}
        </section>
        <section class="card">
            <h2>登录</h2>
            <form action="/login" method="post">
                <label>
                    用户名
                    <input type="text" name="username" placeholder="请输入用户名" required />
                </label>
                <label>
                    密码
                    <input type="password" name="password" placeholder="请输入密码" required />
                </label>
                <button type="submit">立即登录</button>
            </form>
            <p>没有账号？<a href="/register">立即注册</a></p>
        </section>
        """
    )


def render_register_page(message: str = "") -> str:
    message_block = f'<div class="message">{escape(message)}</div>' if message else ""
    return render_page(
        f"""
        <section class="hero">
            <span class="eyebrow"><span class="dot"></span>Service Online</span>
            <h1>Jenkins Demo</h1>
            <p>先注册账号，注册完成后返回登录页。</p>
            {message_block}
        </section>
        <section class="card">
            <h2>注册</h2>
            <form action="/register" method="post">
                <label>
                    用户名
                    <input type="text" name="username" placeholder="请输入用户名" required />
                </label>
                <label>
                    密码
                    <input type="password" name="password" placeholder="请输入密码" required />
                </label>
                <button type="submit">立即注册</button>
            </form>
            <p>已有账号？<a href="/">立即登录</a></p>
        </section>
        """
    )


def render_welcome_page(username: str, message: str = "") -> str:
    safe_username = escape(username)
    message_block = f'<div class="message">{escape(message)}</div>' if message else ""
    return render_page(
        f"""
        <section class="hero">
            <span class="eyebrow"><span class="dot"></span>Service Online</span>
            <h1>Jenkins Demo</h1>
            <p>账号已登录，当前会话正常。</p>
            {message_block}
        </section>
        <section class="grid">
            <section class="card welcome">
                <strong>{safe_username}，欢迎来到 jenkis 的大家庭</strong>
                <p>你现在已经进入系统首页，可以继续扩展更多 Jenkins 相关功能。</p>
                <a class="logout" href="/logout">退出登录</a>
            </section>
            <section class="card">
                <h2>修改密码</h2>
                <form action="/change-password" method="post">
                    <label>
                        当前密码
                        <input type="password" name="current_password" placeholder="请输入当前密码" required />
                    </label>
                    <label>
                        新密码
                        <input type="password" name="new_password" placeholder="请输入新密码" required />
                    </label>
                    <button type="submit">确认修改</button>
                </form>
            </section>
        </section>
        """
    )


async def parse_credentials(request: Request) -> tuple[str, str]:
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    username = data.get("username", [""])[0].strip()
    password = data.get("password", [""])[0].strip()
    return username, password


async def parse_password_change(request: Request) -> tuple[str, str]:
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    current_password = data.get("current_password", [""])[0].strip()
    new_password = data.get("new_password", [""])[0].strip()
    return current_password, new_password


def get_current_user(request: Request) -> str | None:
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        return None
    return sessions.get(session_id)


def build_redirect(path: str = "/", message: str | None = None) -> RedirectResponse:
    target = path if message is None else f"{path}?message={message}"
    return RedirectResponse(url=target, status_code=303)


def get_login_attempt_state(username: str) -> dict[str, float]:
    state = failed_login_attempts.get(username)
    if state is None:
        state = {"count": 0, "locked_until": 0.0}
        failed_login_attempts[username] = state
    return state


def clear_login_attempt_state(username: str) -> None:
    failed_login_attempts.pop(username, None)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, message: str = "") -> str:
    current_user = get_current_user(request)
    if current_user:
        return render_welcome_page(current_user, message)
    return render_login_page(message)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, message: str = "") -> str:
    current_user = get_current_user(request)
    if current_user:
        return render_welcome_page(current_user, message)
    return render_register_page(message)


@app.post("/register")
async def register(request: Request) -> RedirectResponse:
    username, password = await parse_credentials(request)

    if not username or not password:
        return build_redirect(path="/register", message="用户名和密码不能为空")
    if username in users:
        return build_redirect(path="/register", message="该用户名已存在，请直接登录")

    users[username] = password
    return build_redirect(message="注册成功，请登录")


@app.post("/login")
async def login(request: Request) -> RedirectResponse:
    username, password = await parse_credentials(request)
    state = get_login_attempt_state(username)
    now = current_time()

    if state["locked_until"] > now:
        return build_redirect(message="密码输入错误三次，请 10 分钟后再试")

    if state["locked_until"] and state["locked_until"] <= now:
        clear_login_attempt_state(username)
        state = get_login_attempt_state(username)

    if users.get(username) != password:
        state["count"] += 1
        if state["count"] >= MAX_LOGIN_ATTEMPTS:
            state["count"] = 0
            state["locked_until"] = now + LOGIN_LOCK_SECONDS
            return build_redirect(message="密码输入错误三次，请 10 分钟后再试")
        return build_redirect(message="用户名或密码错误")

    clear_login_attempt_state(username)
    session_id = token_urlsafe(24)
    sessions[session_id] = username
    response = build_redirect()
    response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="lax")
    return response


@app.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    session_id = request.cookies.get(SESSION_COOKIE)
    if session_id:
        sessions.pop(session_id, None)

    response = build_redirect(message="你已退出登录")
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.post("/change-password")
async def change_password(request: Request) -> RedirectResponse:
    current_user = get_current_user(request)
    if current_user is None:
        return build_redirect(message="请先登录后再修改密码")

    current_password, new_password = await parse_password_change(request)

    if not current_password or not new_password:
        return build_redirect(message="当前密码和新密码不能为空")
    if users.get(current_user) != current_password:
        return build_redirect(message="当前密码不正确")

    users[current_user] = new_password
    clear_login_attempt_state(current_user)
    return build_redirect(message="密码修改成功")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9875)
