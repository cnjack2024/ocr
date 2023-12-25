import datetime
import httpx
import pytesseract

from io import BytesIO
from PIL import Image

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.status import *


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/ocr",
    response_model=str,
    summary="OCR(输入图像URL)",
)
async def ocr(request: Request) -> str:
    url = request.query_params.get("url")

    if not url:
        raise HTTPException(
            detail="参数错误(需要图像URL)",
            status_code=HTTP_400_BAD_REQUEST,
        )

    content = None

    try:
        r = httpx.get(url)

        if r.status_code == 200:
            content = r.content
    except Exception:
        pass

    if content is None:
        raise HTTPException(
            detail="获取图像文件失败",
            status_code=HTTP_400_BAD_REQUEST,
        )

    try:
        image = Image.open(BytesIO(content))
    except Exception:
        raise HTTPException(
            detail="解析图像文件失败",
            status_code=HTTP_400_BAD_REQUEST,
        )

    try:
        text = pytesseract.image_to_string(image, lang="chi_sim")
    except Exception:
        text = ""

    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])


@app.post(
    "/ocr_content",
    response_model=str,
    summary="OCR(输入图像内容)",
)
async def ocr_content(request: Request) -> str:
    content = await request.body()

    try:
        image = Image.open(BytesIO(content))
    except Exception:
        raise HTTPException(
            detail="解析图像文件失败",
            status_code=HTTP_400_BAD_REQUEST,
        )

    try:
        text = pytesseract.image_to_string(image, lang="chi_sim")
    except Exception:
        text = ""

    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
