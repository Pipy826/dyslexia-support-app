# run.py - 启动脚本
import uvicorn
import os

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "true").lower() == "true"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,          # 关闭热重载，避免文件变化导致意外退出
        workers=1,
    )
