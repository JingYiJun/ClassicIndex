"""
Streamlit 前端应用
提供语义搜索的用户界面
"""

import streamlit as st
import httpx

# 页面配置
st.set_page_config(
    page_title="经典著作索引",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS 样式
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=ZCOOL+XiaoWei&display=swap');
    
    /* 主容器样式 */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* 标题样式 */
    .main-title {
        font-family: 'ZCOOL XiaoWei', 'Noto Serif SC', serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #e94560, #ff6b6b, #feca57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-family: 'Noto Serif SC', serif;
        color: #a0aec0;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* 搜索框样式 */
    .stTextInput > div > div > input {
        font-family: 'Noto Serif SC', serif;
        font-size: 1.1rem;
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #4a5568;
        background: rgba(26, 32, 44, 0.8);
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #e94560;
        box-shadow: 0 0 20px rgba(233, 69, 96, 0.3);
    }
    
    /* 结果卡片样式 */
    .result-card {
        background: linear-gradient(145deg, rgba(45, 55, 72, 0.9), rgba(26, 32, 44, 0.95));
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #e94560;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(233, 69, 96, 0.2);
    }
    
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(160, 174, 192, 0.2);
    }
    
    .page-badge {
        background: linear-gradient(135deg, #e94560, #ff6b6b);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        font-family: 'Noto Serif SC', serif;
    }
    
    .score-badge {
        background: rgba(74, 85, 104, 0.6);
        color: #48bb78;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .result-content {
        font-family: 'Noto Serif SC', serif;
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.9;
        white-space: pre-wrap;
    }
    
    .book-name {
        color: #a0aec0;
        font-size: 0.9rem;
        margin-top: 0.8rem;
        font-style: italic;
    }
    
    /* 排名标记 */
    .rank-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e94560;
        margin-right: 0.8rem;
        font-family: 'Georgia', serif;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* 按钮样式 */
    .stButton > button {
        font-family: 'Noto Serif SC', serif;
        background: linear-gradient(135deg, #e94560, #ff6b6b);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(233, 69, 96, 0.4);
    }
    
    /* 统计信息样式 */
    .stats-container {
        background: rgba(45, 55, 72, 0.6);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* 空状态 */
    .empty-state {
        text-align: center;
        color: #a0aec0;
        padding: 3rem;
        font-family: 'Noto Serif SC', serif;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# API 配置
API_BASE_URL = st.sidebar.text_input(
    "🔗 API 地址", value="http://localhost:8000", help="FastAPI 后端服务地址"
)

# 标题
st.markdown('<h1 class="main-title">📚 经典著作索引</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">在浩瀚典籍中，寻觅思想的光芒</p>', unsafe_allow_html=True
)

# 侧边栏设置
with st.sidebar:
    st.markdown("### ⚙️ 搜索设置")

    top_k = st.slider(
        "返回结果数量",
        min_value=1,
        max_value=20,
        value=10,
        help="设置返回最相似结果的数量",
    )

    st.markdown("---")

    # 健康检查
    if st.button("🔍 检查服务状态"):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    st.success("✅ 服务运行正常")
                else:
                    st.error(f"❌ 服务异常: {response.status_code}")
        except Exception as e:
            st.error(f"❌ 无法连接服务: {str(e)}")

    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    1. 输入你想要查找的内容或概念
    2. 系统会在经典著作中搜索语义最相似的段落
    3. 结果按相似度排序，显示页码便于查阅
    """)

# 主搜索区域
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # 搜索输入
    query = st.text_input(
        "",
        placeholder="输入你想要查找的内容，例如：资本主义的本质是什么...",
        key="search_query",
        label_visibility="collapsed",
    )

    # 搜索按钮
    search_clicked = st.button("🔎 开始搜索", use_container_width=True)

# 执行搜索
if search_clicked and query.strip():
    with st.spinner("正在搜索经典著作..."):
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{API_BASE_URL}/search", json={"query": query, "top_k": top_k}
                )
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])

            if results:
                st.markdown(f"### 🎯 找到 {len(results)} 个相关段落")
                st.markdown("---")

                for idx, result in enumerate(results, 1):
                    score_percent = result["score"] * 100

                    st.markdown(
                        f"""
                    <div class="result-card">
                        <div class="result-header">
                            <div>
                                <span class="rank-number">#{idx}</span>
                                <span class="page-badge">📄 第 {result["page"]} 页</span>
                            </div>
                            <span class="score-badge">相似度: {score_percent:.1f}%</span>
                        </div>
                        <div class="result-content">{result["content"]}</div>
                        <div class="book-name">—— 《{result["book"]}》</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <h3>未找到相关内容</h3>
                    <p>请尝试使用不同的关键词或表达方式</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        except httpx.ConnectError:
            st.error("❌ 无法连接到后端服务，请确保 FastAPI 服务正在运行")
        except httpx.HTTPStatusError as e:
            st.error(f"❌ 请求失败: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")

elif search_clicked and not query.strip():
    st.warning("⚠️ 请输入搜索内容")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <p>基于 Qwen Embedding + Milvus 构建的语义搜索引擎</p>
    </div>
    """,
    unsafe_allow_html=True,
)
