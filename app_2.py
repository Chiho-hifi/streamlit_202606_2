import streamlit as st
from PIL import Image, ImageFilter
import time

# 1. クイズデータの設定（ジャンル別の辞書構造に拡張）
QUIZ_DATA = {
    "食べ物": [
        {
            "id": 1,
            "image_path": "q-bro.jpg",
            "choices": ["ブロッコリー", "小松菜", "枝豆"],
            "correct_answer": "ブロッコリー"
        },
        {
            "id": 2,
            "image_path": "q-tomato.jpg",
            "choices": ["リンゴ", "トマト", "パプリカ"],
            "correct_answer": "トマト"
        },
        {
            "id": 3,
            "image_path": "q-ebif.jpg",
            "choices":["白身魚のフライ","エビフライ","コロッケ"],
            "correct_answer": "エビフライ"
        },
        {
            "id": 4,
            "image_path": "q-yakiimo.jpg",
            "choices":["アサイーボウル","やきいも","マンゴー"],
            "correct_answer": "やきいも"
        }
    ],
    "漢字": [
        {
            "id": 1,
            "image_path": "qk-son.jpg",  
            "choices": ["緑", "権", "孫"],
            "correct_answer": "孫"
        },
        {
            "id": 2,
            "image_path": "qk-yume.jpg",  
            "choices": ["夢", "憂", "安"],
            "correct_answer": "夢"
        },
        {
            "id": 3,
            "image_path": "qk-ha.jpg",  
            "choices": ["歩", "面", "歯"],
            "correct_answer": "歯"
        },
        {
            "id": 4,
            "image_path": "qk-tamashi.jpg",  
            "choices": ["鬼", "謎", "魂"],
            "correct_answer": "魂"
        }
    ],
    "都道府県": [
        {
        "id": 1,
        "image_path": "qp-niigata.png",  
        "choices": ["富山県", "長野県", "新潟県"],
        "correct_answer": "新潟県"
        },
        {
        "id": 2,
        "image_path": "qp-fukushima.png",  
        "choices": ["青森県", "宮城県", "福島県"],
        "correct_answer": "福島県"
        },
        {
        "id": 3,
        "image_path": "qpoita.png",  
        "choices": ["福岡県", "熊本県", "大分県"],
        "correct_answer": "大分県"
        },
        {
        "id": 4,
        "image_path": "qp-hiroshima.png",  
        "choices": ["岡山県", "山口県", "広島県"],
        "correct_answer": "広島県"
        }
    ],
    "動物": [
        {
        "id": 1,
        "image_path": "qa_cat.jpg",  
        "choices": ["いぬ", "うさぎ", "ねこ"],
        "correct_answer": "ねこ"
        },
        {
        "id": 2,
        "image_path": "qa_dack.jpg",  
        "choices": ["ニワトリ", "アヒル", "ヒヨコ"],
        "correct_answer": "アヒル"
        },
        {
        "id": 3,
        "image_path": "qa_tora.jpg",  
        "choices": ["トラ","ライオン", "チーター" ],
        "correct_answer": "トラ"
        },
        {
        "id": 4,
        "image_path": "qa_whitekuma.jpg",  
        "choices": ["アザラシ", "サル", "シロクマ"],
        "correct_answer": "シロクマ"
        }
    ]

}

# --- スコア履歴の初期化 ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- ジャンル選択（サイドバーに配置） ---
selected_genre = st.sidebar.selectbox("クイズのジャンルを選んでね：", list(QUIZ_DATA.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("🏆 スコア履歴")
if st.sidebar.button("履歴をクリア"):
    st.session_state.history = []
    st.rerun()
for record in reversed(st.session_state.history):
    st.sidebar.write(record)

# ジャンルが切り替わったら、セッション状態（進捗やスコア）を自動でリセット
if "current_genre" not in st.session_state or st.session_state.current_genre != selected_genre:
    st.session_state.current_genre = selected_genre
    st.session_state.current_question = 0
    st.session_state.quiz_cleared = False
    st.session_state.user_answer = None
    st.session_state.total_score = 0
    st.session_state.current_radius = 50 if selected_genre in ["漢字", "動物"] else 100
    st.session_state.earned_score = 0

# 現在選択されているジャンルの問題リストを取得
current_quiz_list = QUIZ_DATA[st.session_state.current_genre]

# 難易度設定
initial_radius = 50 if st.session_state.current_genre in ["漢字", "動物"] else 100
blur_step = -1 if st.session_state.current_genre in ["漢字", "動物"] else -5


# 2. セッション状態（記憶）の初期化
if "current_question" not in st.session_state:
    st.session_state.current_question = 0  # 0からスタート（1問目）
if "quiz_cleared" not in st.session_state:
    st.session_state.quiz_cleared = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "total_score" not in st.session_state:
    st.session_state.total_score = 0       # 合計得点
if "current_radius" not in st.session_state:
    st.session_state.current_radius = initial_radius  # 現在のぼかし具合を記憶
if "earned_score" not in st.session_state:
    st.session_state.earned_score = 0      # その問題で獲得した得点


# 全問題が終わっている場合の画面
if st.session_state.quiz_cleared:
    st.header("クイズ終了！")
    st.write(f"【{st.session_state.current_genre}】のすべての問題が終了しました。")
    
    # 結果のスコア表示を追加
    st.subheader(f"あなたの合計得点: {st.session_state.total_score} 点")
    
    if st.button("もう一度遊ぶ"):
        st.session_state.current_question = 0
        st.session_state.quiz_cleared = False
        # リセット処理を追加
        st.session_state.total_score = 0
        st.session_state.current_radius = initial_radius
        st.session_state.earned_score = 0
        st.rerun()
    st.stop()  # ここで処理を中断して以下のコードを実行させない


# 現在の問題データを取得
current_idx = st.session_state.current_question
q_data = current_quiz_list[current_idx]


# 3. 画面の表示（フォーマット部分）
st.header(f"ぼやかしクイズ ({st.session_state.current_genre})")
st.caption("boyakashi quiz")
st.write("どれくらい早く正解できるかな？")

# 現在の合計得点を端に表示
st.write(f"現在のスコア: {st.session_state.total_score} 点")

st.subheader(f"【第{q_data['id']}問】")

# 画像の読み込み（変数から取得）
image = Image.open(q_data["image_path"]).convert("RGB")

st.caption("この写真は...")

# 答えを表示する前に溜めの演出を表示するためのプレースホルダー（カラムの外に配置して位置を固定）
suspense_placeholder = st.empty()

# 選択肢ボタンの動的生成（リストから自動でカラムを作って配置）
cols = st.columns(len(q_data["choices"]))

for i, choice in enumerate(q_data["choices"]):
    with cols[i]:
        # ボタンが押されたら、溜めてから回答をセッションステートに保存
        if st.button(choice, key=f"btn_{current_idx}_{i}"):
            # 答えを表示する前に溜めの演出を追加
            suspense_placeholder.markdown("<h3 style='text-align: center;'>正解は．．．</h3>", unsafe_allow_html=True)
            time.sleep(2)
            suspense_placeholder.empty()
            
            st.session_state.user_answer = choice
            
            # --- ボタンが押された瞬間にスコアを計算・加算 ---
            if choice == q_data["correct_answer"]:
                score = st.session_state.current_radius 
                st.session_state.earned_score = score
                st.session_state.total_score += score
            else:
                st.session_state.earned_score = 0
                
            st.rerun()

progress_placeholder = st.empty()
image_placeholder = st.empty()


# 4. 回答判定・アニメーションロジック
if st.session_state.user_answer is not None:
    # 正誤判定（変数から取得した正解と比較）
    if st.session_state.user_answer == q_data["correct_answer"]:
        st.success(f"正解！{q_data['correct_answer']}です！")
        # 獲得した点数を表示
        st.info(f"ぼかし {st.session_state.current_radius}％ の状態で正解！ **{st.session_state.earned_score}点** 獲得！")
    else:
        st.error(f"残念、はずれです！正解は{q_data['correct_answer']}です！")
        st.warning("不正解のため、0点です。")
        
    image_placeholder.image(image)
    
    # --- 次の問題に進むためのボタン ---
    if st.button("次の問題へ ", key=f"next_{current_idx}"):
        # 回答状態をリセットして次の問題へ
        st.session_state.user_answer = None
        st.session_state.current_radius = initial_radius # 次の問題のために初期値に戻す
        
        if current_idx + 1 < len(current_quiz_list):
            st.session_state.current_question += 1
        else:
            st.session_state.quiz_cleared = True
            # クイズ終了時にジャンルと合計得点を履歴に記録
            st.session_state.history.append(f"{st.session_state.current_genre}: {st.session_state.total_score} 点")
        st.rerun()

else:
    start_button = st.button("スタート", type="primary", key=f"start_{current_idx}", use_container_width=True)
    
    if start_button:
        # じわじわバーが減る（元に戻る）演出
        for radius in range(initial_radius, -1, blur_step):
            
            # 今のぼかし具合を記憶
            st.session_state.current_radius = radius 
            
            progress_placeholder.progress(1.0 - (radius / initial_radius))
            if radius > 0:
                processed_image = image.filter(ImageFilter.GaussianBlur(radius))
            else:
                processed_image = image

            image_placeholder.image(
                processed_image,
                caption=f"ぼかしの強さ{radius}"
            )
            time.sleep(0.5) 

    # elseブロックの画像表示は、start_buttonが押されていない場合にのみ実行されるべき
    else:
        init_image = image.filter(ImageFilter.GaussianBlur(initial_radius))
        image_placeholder.image(
            init_image,
            caption=f"ぼかしの強さ{initial_radius}"
        )