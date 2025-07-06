import streamlit as st
import requests
import time
from pyecharts.charts import Bar
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts

st.set_page_config(page_title="HUD 网络暴力识别系统", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600&display=swap');

html, body, .stApp {
    background: radial-gradient(circle at center, #0a0f1a 0%, #050c1a 100%);
    font-family: 'Orbitron', sans-serif;
    color: #00eaff;
}

h1, h2 {
    text-align: center;
    color: #00eaff;
    font-weight: 600;
}

.radar-center {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 200px;
    height: 200px;
    transform: translate(-50%, -50%);
    border: 2px solid #00eaff;
    border-radius: 50%;
    animation: rotate 10s linear infinite;
    box-shadow: 0 0 20px #00eaff88;
    z-index: 2;
    pointer-events: none;
}

@keyframes rotate {
    0% {transform: translate(-50%, -50%) rotate(0deg);}
    100% {transform: translate(-50%, -50%) rotate(360deg);}
}

.hud-panel {
    background-color: rgba(0, 238, 255, 0.05);
    border: 1px solid #00eaff;
    border-radius: 10px;
    padding: 20px;
    margin: 20px;
    box-shadow: 0 0 15px #00eaff22;
    z-index: 1;
}
</style>

<div class="radar-center"></div>
""", unsafe_allow_html=True)

st.markdown("## 🧠 HUD 网络暴力识别系统")
st.markdown("### 语义识别界面")

left, right = st.columns([2, 3])

API_URL = "https://api.deepseek.com/v1/chat/completions"
API_TOKEN = "Bearer sk-fc601fa2a4a848918a80629ce702964c"  # 请替换成你自己的有效密钥

def call_deepseek_api(user_text: str):
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }
    prompt = f"""
你是一个网络暴力语言识别系统。请对下列评论进行语义和暴力识别，输出如下结构化信息：
1. 是否为网络暴力（是/否）
2. 涉及关键词
3. 类型分类（请选择一个或多个：辱骂 / 性别歧视 / 威胁 / 冷嘲热讽 / 羞辱 / 歧视 / 正常言论）
4. 暴力等级（轻度 / 中度 / 重度）
5. 语义分类（请选择一个或多个：外貌攻击 / 能力攻击 / 身份贬低 / 性别歧视 / 恐吓威胁 / 情绪发泄 / 正常评论）
6. 简要判断理由（不超过40字）

评论内容如下：
“{user_text}”

请以如下格式输出（用 markdown 格式）：
- 是否网络暴力：是
- 涉及关键词：废物、蠢
- 类型分类：辱骂
- 暴力等级：中度
- 语义分类：能力攻击、情绪发泄
- 判断说明：评论包含明显侮辱性语言，表达贬低他人能力的情绪。
"""
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "top_p": 1,
        "n": 1
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP错误: {e}, 状态码: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

with left:
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    user_input = st.text_area("请输入评论内容：", height=150, placeholder="例如：你怎么这么蠢，真是个废物")
    if st.button("🛡️ 开始识别"):
        if not user_input.strip():
            st.warning("⚠️ 请输入评论内容")
        else:
            with st.spinner("🚀 识别中，请稍候..."):
                result = call_deepseek_api(user_input)
                time.sleep(1)

            if "error" in result:
                st.error(f"识别失败: {result['error']}")
            else:
                try:
                    answer = result["choices"][0]["message"]["content"]
                except Exception:
                    answer = "未能解析API返回结果。"

                st.success("✅ 识别完成，结果如下：")
                st.markdown(f"```\n{answer}\n```")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    bar = (
        Bar()
        .add_xaxis(["辱骂", "威胁", "歧视", "正常"])
        .add_yaxis("类型分布", [60, 20, 15, 5])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="暴力类型占比"),
            visualmap_opts=opts.VisualMapOpts(max_=100),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(),
        )
    )
    st_pyecharts(bar)
    st.markdown('</div>', unsafe_allow_html=True)