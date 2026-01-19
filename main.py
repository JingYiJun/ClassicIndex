"""
Classic Index - 经典著作语义搜索应用
主入口文件
"""

import subprocess
import sys


def run_import():
    """运行数据导入"""
    from scripts.import_data import main as import_main

    import_main()


def run_backend():
    """启动 FastAPI 后端"""
    from backend.main import start_server

    start_server()


def run_frontend():
    """启动 Streamlit 前端"""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "frontend/app.py",
            "--server.port",
            "8501",
        ]
    )


def main():
    """主函数 - 显示帮助信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           📚 Classic Index - 经典著作语义搜索                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  使用方法:                                                   ║
║                                                              ║
║  1. 导入数据到 Milvus:                                       ║
║     python -c "from main import run_import; run_import()"    ║
║     或者: python scripts/import_data.py                      ║
║                                                              ║
║  2. 启动后端服务:                                            ║
║     python -c "from main import run_backend; run_backend()"  ║
║     或者: uvicorn backend.main:app --reload                  ║
║                                                              ║
║  3. 启动前端界面:                                            ║
║     python -c "from main import run_frontend; run_frontend()"║
║     或者: streamlit run frontend/app.py                      ║
║                                                              ║
║  注意: 请先配置 .env 文件中的 API 密钥                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
