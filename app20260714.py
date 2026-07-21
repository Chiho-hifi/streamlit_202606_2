import json
import os
import streamlit as st
from google import genai
from google.genai import types

# ページ基本設定
st.set_page_config(
    page_title="パラレルワールド色紙 - セルフ寄せ書きアプリ",
    page_icon="📜",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Google Fonts から手書き風フォント「Zen Kurenaido」を読み込み */
    @import url('https://fonts.googleapis.com/css2?family=Zen+Kurenaido&display=swap');

    /* 寄せ書きカード全体のスタイル */
    .yosegaki-card {
        background-color: #fefcf3; /* 色紙風のやわらかい生成り色 */
        border: 1px solid #e2d9c8;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 2px 3px 6px rgba(0, 0, 0, 0.08);
        font-family: 'Zen Kurenaido', sans-serif; /* 手書き風フォント適用 */
        color: #2b2b2b;
    }

    /* 送り主（名前・立場）のスタイル */
    .yosegaki-sender {
        font-size: 1.15rem;
        font-weight: bold;
        color: #1e3a8a;
        border-bottom: 1px dashed #d1c7b7;
        padding-bottom: 6px;
        margin-bottom: 10px;
    }

    /* メッセージ本文のスタイル */
    .yosegaki-text {
        font-size: 1.1rem;
        line-height: 1.7;
        white-space: pre-wrap; /* 改行を有効化 */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📜 パラレルワールド寄せ書きアプリ")
st.caption("平行世界のあなたへ。10人の仲間たちからメッセージが届きます。")

# 1. APIキーの設定
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "APIキーが設定されていません。\n\n"
        "・Streamlit Secrets: `.streamlit/secrets.toml` に `GEMINI_API_KEY` を記述\n"
        "・環境変数: `export GEMINI_API_KEY=\"あなたのキー\"` を設定"
    )
    st.stop()

# 2. Gemini クライアントの作成
client = genai.Client(api_key=api_key)
MODEL_CANDIDATES = [
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# 3. サイドバー：入力フォームの配置
with st.sidebar:
    st.header("⚙️ シチュエーション設定")

    user_name = st.text_input("あなたの名前", value="たろう")

    # 属性の選択（自由入力も可能に）
    group_options = [
        "幼稚園児",
        "小学生",
        "中学生",
        "高校生",
        "大学生",
        "大人書道サークルのみんな",
        "大人手品クラブのみんな",
        "じゃんけん必勝法セミナーのみんな",
        "その他（自由入力）",
    ]
    selected_group = st.selectbox("あなたの属性・所属", group_options)

    if selected_group == "その他（自由入力）":
        group_name = st.text_input("具体的な属性・所属を入力", value="魔法使い養成学校")
    else:
        group_name = selected_group

    character = st.text_input(
        "あなたのキャラクター", value="ムードメーカーでちょっとおっちょこちょい"
    )

    achievement = st.text_input(
        "成し遂げたこと", value="運動会の大玉転がしで奇跡の大逆転勝利"
    )

    # 状況・イベント選択
    event_type = st.selectbox(
        "状況・イベント",
        [
            "誕生日",
            "別れ（転校・退職・移動・卒業など）",
            "表彰・達成のお祝い",
            "その他（自由入力）",
        ],
    )

    if event_type == "その他（自由入力）":
        event_name = st.text_input("具体的な状況を入力", value="世界一周の旅へ出発")
    else:
        event_name = event_type

    generate_btn = st.button("✨ 寄せ書きを届けてもらう", type="primary")

# 4. メッセージ生成ロジック
if generate_btn:
    with st.spinner("平行世界の仲間たちからメッセージを集めています..."):
        prompt = f"""
あなたはパラレルワールドの仲間たちの代弁者です。
以下のシチュエーションに基づき、主人公「{user_name}」に対する10人からの寄せ書きメッセージを作成してください。

【シチュエーション】
- 送り主たちの集まり・属性: {group_name}
- 主人公の名前: {user_name}
- 主人公のキャラクター: {character}
- 主人公が成し遂げたこと: {achievement}
- 状況: {event_name}

【要求事項】
- それぞれ立場の異なる10人の仲間（関係者）からの、個性豊かで温かい（またはクスッと笑える）メッセージ（各40文字程度）を作成してください。
- 各メッセージには「差出人の名前や立場（例: ライバルの佐々木、隣の席のマイ、講師の山本など）」を含めてください。
- 本文「('text')」には、差出人の名前は含めないでください。
- 「{group_name}」ならではの口調やトーン、および主人公のキャラクター「{character}」、「{achievement}」のエピソードをしっかりと反映させてください。
"""

        response = None
        last_error = None

        # 候補モデルを順番に試す（503混雑エラー自動回避ロジック）
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema={
                            "type": "OBJECT",
                            "properties": {
                                "messages": {
                                    "type": "ARRAY",
                                    "items": {
                                        "type": "OBJECT",
                                        "properties": {
                                            "sender": {"type": "STRING"},
                                            "text": {"type": "STRING"},
                                        },
                                        "required": ["sender", "text"],
                                    },
                                }
                            },
                            "required": ["messages"],
                        },
                    ),
                )
                # 取得に成功したらループを抜ける
                if response and response.text:
                    break
            except Exception as e:
                last_error = e
                continue

        # 成功時のデータ保持処理
        if response and response.text:
            try:
                data = json.loads(response.text)
                st.session_state["yosegaki_data"] = data.get("messages", [])
                st.session_state["current_info"] = {
                    "name": user_name,
                    "group": group_name,
                    "event": event_name,
                }
            except Exception as e:
                st.error(f"データの解析に失敗しました: {e}")
        else:
            st.error(
                f"現在サーバーが混雑しています。少し時間をおいて再度お試しください。\n（詳細: {last_error}）"
            )

# 5. メッセージの表示（色紙風カードレイアウト）
if "yosegaki_data" in st.session_state and st.session_state["yosegaki_data"]:
    info = st.session_state["current_info"]

    st.subheader(
        f"🎁 {info['group']} のみんなから {info['name']} への寄せ書き（{info['event']}）"
    )
    st.markdown("---")

    messages = st.session_state["yosegaki_data"]

    # 2列に分けてカード型表示（色紙に敷き詰められているような見た目）
    col1, col2 = st.columns(2)

    for idx, msg in enumerate(messages):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            # カスタムHTMLを使用して手書き風フォントを適用したカードを出力
            card_html = f"""
            <div class="yosegaki-card">
                <div class="yosegaki-sender">✍️ {msg.get('sender')}</div>
                <div class="yosegaki-text">{msg.get('text')}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)