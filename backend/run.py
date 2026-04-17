# run.py - 启动脚本
import uvicorn
import os

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "true").lower() == "true"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=debug,          # 生产环境设 DEBUG=false 关闭热重载
        workers=1 if debug else None,  # reload 模式不支持多 worker
    )
