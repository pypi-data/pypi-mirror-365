import sqlite3
import io
from PIL import Image, ImageFile

from pytessng.ToolInterface.public import BaseTool


class BackgroundMapSaver(BaseTool):
    def export(self, input_file_path: str, file_path: str) -> None:
        # 连接TESSNG数据库
        conn = sqlite3.connect(input_file_path)
        cursor = conn.cursor()

        # 读取底图
        cursor.execute("SELECT backgroundMap FROM Configuration")
        image_data = cursor.fetchone()[0]
        if image_data is None:
            raise Exception("No background map found in the database.")

        # 取消大图片限制
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.MAX_IMAGE_PIXELS = None
        # 从数据库中读取图片数据
        image = Image.open(io.BytesIO(image_data))
        # 保存图像为 PNG 格式
        image.save(file_path, format="PNG")
