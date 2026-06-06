from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(title="Jenkins Demo API")


@app.get("/", response_class=HTMLResponse)
async def read_root() -> str:
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jenkins Demo</title>
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                min-height: 100vh;
                display: grid;
                place-items: center;
                padding: 24px;
                color: #1f2937;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #eff6ff, #f8fafc);
            }
            main {
                width: min(100%, 560px);
                padding: 48px;
                text-align: center;
                background: #fff;
                border-radius: 20px;
                box-shadow: 0 16px 40px rgba(15, 23, 42, 0.12);
            }
            h1 { margin: 0 0 16px; color: #2563eb; font-size: 36px; }
            p { margin: 0 0 28px; color: #64748b; line-height: 1.7; }
            .status {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                color: #166534;
                font-weight: 700;
                background: #dcfce7;
                border-radius: 999px;
            }
            .dot {
                width: 10px;
                height: 10px;
                background: #22c55e;
                border-radius: 50%;
            }
        </style>
    </head>
    <body>
        <main>
            <h1>Jenkins Demo</h1>
            <p>FastAPI 你好 jenkins,这是一个测试</p>
            <p>hello jenkins</p>
            <span class="status"><span class="dot"></span>Service Online</span>
        </main>
    </body>
    </html>
    """


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9875)
