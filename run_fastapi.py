from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi  import FastAPI, Request
import uvicorn
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的请求方法
    allow_headers=["*"],  # 允许所有请求头
)

@app.route("/ping", methods=["GET", "POST"])
async def ping(request: Request):
    return JSONResponse({"message": "Hello World"})

# 定义一个接口，接受相对路径并返回路径图片的响应体
@app.get("/get_player_best_50/{file_name:path}")
async def get_image(file_name: str):
    # 将相对路径转换为绝对路径
    absolute_path = Path(f"temp/img/player_best_50/{file_name}.png").resolve()

    # 检查文件是否存在
    if not absolute_path.is_file():
        return {"error": "文件不存在"}

    # 返回文件响应
    return FileResponse(str(absolute_path))

# 定义一个接口，接受相对路径并返回路径图片的响应体
@app.get("/get_music_info/{file_name:path}")
async def get_image(file_name: str):
    # 将相对路径转换为绝对路径
    absolute_path = Path(f"temp/img/music_info/{file_name}.png").resolve()

    # 检查文件是否存在
    if not absolute_path.is_file():
        return {"error": "文件不存在"}

    # 返回文件响应
    return FileResponse(str(absolute_path))


# 定义一个接口，接受相对路径并返回路径图片的响应体
@app.get("/get_player_music_score/{file_name:path}")
async def get_image(file_name: str):
    # 将相对路径转换为绝对路径
    absolute_path = Path(f"temp/img/player_music_score/{file_name}.png").resolve()

    # 检查文件是否存在
    if not absolute_path.is_file():
        return {"error": "文件不存在"}

    # 返回文件响应
    return FileResponse(str(absolute_path))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=13812)