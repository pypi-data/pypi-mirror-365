import asyncio
import subprocess

import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加父目录到 Python 路径，以便导入 grasp_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

from grasp_sdk import Grasp
from playwright.async_api import async_playwright
import math

# 加载环境变量
load_dotenv("../.env.grasp")

async def main():
    grasp = Grasp()

    session = await grasp.launch({
        "browser": {
            # "type": "chrome-stable",
            "headless": False,
            # "args": [
            #     "--enable-webgl",
            #     "--ignore-gpu-blacklist",
            #     "--use-gl=swiftshader",
            #     "--headless=false",
            # ],
            # "adblock": True,
            "liveview": True,
        },
        "debug": True,
        "keepAliveMS": 10000,
        "timeout": 3600000,
    })

    terminal = session.terminal
    # response = await terminal.run_command(
    #     # "node -e \"console.log(process.env)\""
    #     "Xvfb :1 -screen 0 1024x768x24 & export DISPLAY=:1 && glxinfo | grep \"OpenGL renderer\""
    # )
    # response.stdout.pipe(process.stdout)
    # response.stderr.pipe(process.stderr)
    # print(await response.json())

    # await session.files.download_file(
    #     "/home/user/.env.json",
    #     "./output/.env.json"
    # )

    ws_url = session.browser.get_endpoint()
    print(ws_url)
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_url, timeout=150000)

        url = await session.browser.get_liveview_page_url()
        if url:
            # 使用 subprocess 打开 URL（替代 Node.js 的 open 包）
            subprocess.run(["open", url])  # macOS
            # subprocess.run(["xdg-open", url])  # Linux
            # subprocess.run(["start", url], shell=True)  # Windows

        page = await browser.new_page()

        # 打开一个可以玩拖拽的网页
        await page.goto("https://the-internet.herokuapp.com/drag_and_drop")

        box_a = page.locator("#column-a")
        box_b = page.locator("#column-b")

        box_a_box = await box_a.bounding_box()
        box_b_box = await box_b.bounding_box()
        
        if not box_a_box or not box_b_box:
            raise Exception("Could not get bounding boxes for elements")
            
        mouse = page.mouse

        # 🎯 Step 1: 炫技滑动到 Box A
        await mouse.move(0, 0, steps=20)
        await mouse.move(box_a_box["x"] + 30, box_a_box["y"] + 30, steps=40)

        # ⚡ Step 2: 快速点击一次
        await mouse.click(box_a_box["x"] + 30, box_a_box["y"] + 30)

        # 🧲 Step 3: 拖拽 Box A 到 Box B
        await mouse.move(box_a_box["x"] + 30, box_a_box["y"] + 30)
        await mouse.down()
        await mouse.move(box_b_box["x"] + 30, box_b_box["y"] + 30, steps=50)
        await mouse.up()

        # 🎡 Step 4: 鼠标绕 Box B 旋转一圈
        center_x = box_b_box["x"] + box_b_box["width"] / 2
        center_y = box_b_box["y"] + box_b_box["height"] / 2
        radius = 40
        for angle in range(0, 361, 10):
            rad = (angle * math.pi) / 180
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            await mouse.move(x, y)

        # 👋 Step 5: 优雅滑出屏幕
        await mouse.move(center_x + 100, center_y + 500, steps=30)

        # 下载liveview 截屏
        # screenshots_dir = await session.browser.get_replay_screenshots()
        # print(screenshots_dir)

        command = await terminal.run_command(
            "cd /home/user/downloads/grasp-screenshots && ls -1 | grep -v '^filelist.txt$' | sort | awk '{print \"file '\\''\" $0 \"'\\''\"}' > filelist.txt"
        )
        await command.end()

        command2 = await terminal.run_command(
            "cd /home/user/downloads/grasp-screenshots && ffmpeg -r 25 -f concat -safe 0 -i filelist.txt -vsync vfr -pix_fmt yuv420p output.mp4"
        )

        # Python 中处理流输出的方式
        def handle_stdout(data):
            print(data, end="")
        
        def handle_stderr(data):
            print(data, end="")
        
        # 注册事件处理器
        command2.on('stdout', handle_stdout)
        command2.on('stderr', handle_stderr)

        await command2.end()

        # 创建 ./output 目录
        Path("./output").mkdir(parents=True, exist_ok=True)

        await asyncio.gather(
            session.files.download_file(
                "/home/user/downloads/grasp-screenshots/filelist.txt",
                "./output/filelist.txt"
            ),
            session.files.download_file(
                "/home/user/downloads/grasp-screenshots/output.mp4",
                "./output/output.mp4"
            ),
        )

        await session.close()

if __name__ == "__main__":
    asyncio.run(main())