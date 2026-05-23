import streamlit as st
from google import genai
 
# ─── ページ設定 ───────────────────────────────────────────
st.set_page_config(
    page_title="✨ SNS投稿メーカー",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)
 
# ─── カスタムCSS ──────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');
  html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; }
  .stApp { background: #FFF5F8; }
  .main-title {
    text-align: center; font-size: 28px; font-weight: 900;
    background: linear-gradient(135deg, #FF6B9D, #7B61FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 4px;
  }
  .main-sub { text-align: center; color: #999; font-size: 13px; margin-bottom: 20px; }
  .char-ok  { color: #1A7A3A; font-weight: 700; font-size: 13px; }
  .char-ng  { color: #C0392B; font-weight: 700; font-size: 13px; }
  .stButton > button {
    background: linear-gradient(135deg, #FF6B9D, #7B61FF) !important;
    color: white !important; font-weight: 700 !important;
    border: none !important; border-radius: 12px !important;
    padding: 12px 24px !important; width: 100% !important; font-size: 15px !important;
  }
  .stButton > button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)
 
# ─── SNS データ ───────────────────────────────────────────
SNS_DATA = {
    "📸 Instagram": {
        "role": "世界観・ブランディング SNS",
        "emotion": "憧れ・理想・成長・自己肯定感",
        "curve": "欠乏感 → 希望 → 理想未来 → 保存したい",
        "algo": "保存数・視聴維持率が最重要",
        "hint": "「え？」「実は」「知らなかった」で理想と欠乏を刺激するタイトル",
        "struct": (
            "1. 最初の125文字以内で「え？」と思わせるつかみ\n"
            "2. 欠乏感・共感\n3. 希望\n4. 理想の未来へ誘導\n"
            "5. 保存したくなるメッセージで締める\n6. ハッシュタグ5〜10個（末尾）"
        ),
    },
    "👥 Facebook": {
        "role": "信頼構築・コミュニティ SNS",
        "emotion": "信頼・共感・人生ストーリー・弱さを見せる",
        "curve": "苦労 → 本音 → 学び → 共感 → 信頼",
        "algo": "コメント数が最重要",
        "hint": "「正直に言うと」「実は〜だった」など本音・信頼感を演出するタイトル",
        "struct": (
            "1. 強烈な感情的一文でつかむ\n2. 昔の苦悩・失敗を正直に語る\n"
            "3. 転機・気づき\n4. 今の考え・学び\n"
            "5. 「あなたはどうですか？」でコメント誘導して締める"
        ),
    },
    "🎵 TikTok": {
        "role": "爆発拡散・新規集客 SNS",
        "emotion": "驚き・衝撃・ギャップ・爽快感",
        "curve": "衝撃（1秒）→ 危機感 → 好奇心 → 快感 → 中毒感",
        "algo": "視聴維持率（冒頭1〜3秒）が最重要",
        "hint": "「ヤバい」「え！？」「AIで人生変わった」などギャップ・衝撃ワードを使うタイトル",
        "struct": (
            "1. 冒頭1行で「なにこれ!?」という衝撃ワード\n"
            "2. 危機感（「知らないと損」）\n3. 好奇心を煽る\n4. 爽快感で締める"
        ),
    },
    "🧵 Threads": {
        "role": "共感・ファン化 SNS",
        "emotion": "本音・孤独・共感・安心・未完成感",
        "curve": "孤独感 → 共感 → 安心 → 親近感",
        "algo": "共感いいね・リポストが最重要",
        "hint": "「〜って私だけ？」「誰にも言えなかったこと」など本音・孤独感を演出するタイトル",
        "struct": (
            "1. 本音の一言（「〜って私だけかな」）\n2. 共感できる感情\n"
            "3. 安心感・気づき\n4. 完成させすぎない余白で締める\n※500文字以内厳守"
        ),
    },
    "𝕏 X": {
        "role": "情報拡散・権威性 SNS",
        "emotion": "知識・優越感・怒り・知的快感・拡散欲",
        "curve": "驚き → 優越感 → 納得/怒り → 拡散欲",
        "algo": "初速拡散（投稿直後のエンゲージメント）が最重要",
        "hint": "「実は」「99%知らない」「これヤバい」など知的優越感・拡散欲を刺激するタイトル",
        "struct": (
            "1. 1行目で完全に勝負（強い結論・数字・「実は」）\n"
            "2. 核心・データを簡潔に\n3. 結論を先出し\n"
            "4. 共有したくなる締め\n※280文字以内絶対厳守"
        ),
    },
}
 
LEN_DATA = {
    "📸 Instagram": {"短め": (125, "60〜125文字"),  "普通": (600,  "300〜600文字"),  "長め": (1500, "600〜1500文字")},
    "👥 Facebook":  {"短め": (500, "200〜500文字"), "普通": (1500, "500〜1500文字"), "長め": (4000, "1500〜4000文字")},
    "🎵 TikTok":    {"短め": (80,  "30〜80文字"),   "普通": (130,  "80〜130文字"),   "長め": (150,  "130〜150文字")},
    "🧵 Threads":   {"短め": (150, "50〜150文字"),  "普通": (350,  "150〜350文字"),  "長め": (500,  "350〜500文字")},
    "𝕏 X":          {"短め": (100, "50〜100文字"),  "普通": (200,  "100〜200文字"),  "長め": (280,  "200〜280文字")},
}
 
STY_DATA = {
    "🌟 今村奈々スタイル": "温かく自然体。短文×改行×本音×問いかけ。今村奈々スタイルを忠実に",
    "🌸 可愛い":           "明るくふんわり。「〜だよ」「〜だね」など友達口調でやわらかく",
    "📚 真面目":           "誠実で信頼感がある。「〜です」「〜ます」調で丁寧かつ真摯に",
    "😄 おもしろい":       "ユーモアと意外性。思わず笑えるか驚けるような展開を含む",
}
 
NANA_STYLE = """【今村奈々スタイルの書き方ルール（必ず守ること）】
・1文を短く（15〜25文字以内）、必ず1文ごとに改行する
・段落間に空行を入れて「呼吸感」を作る
・読者への問いかけを必ず入れる（「〜ですか？」「〜だけかな？」）
・自分の本音・体験・感情を正直に書く（「実は私も〜だった」）
・柔らかい語尾（「〜ですね」「〜かもしれません」「〜だよ」）
・共感から始まり、気づきへ誘導する
・接続詞で感情の流れを作る（「でも」「だから」「実は」「そして」）
・最後はやさしいメッセージか問いかけで締める
 
【今村奈々の文章例】
2026年、勝つ人の共通点
それは「頑張ること」じゃない。
 
売れる魔法を、先に作っていること。
 
実績がなくていい。
フォロワーが少なくていい。
 
でも、
本気で変わりたいならーー
ここで差がつく。
 
私と、仕事を前に行く。
一緒にいきませんか？"""
 
# ─── Gemini API 呼び出し ──────────────────────────────────
def call_claude(prompt: str) -> str:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("⚠️ APIキーが設定されていません。Streamlit Cloud の Settings → Secrets に GEMINI_API_KEY を追加してください。")
        st.stop()
    client = genai.Client(api_key=api_key)
    with st.spinner("✨ AIが生成中…少々お待ちください"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
    return response.text
 
# ─── ヘッダー ─────────────────────────────────────────────
st.markdown('<div class="main-title">✨ SNS投稿メーカー</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">今村奈々スタイル × 感情設計 — 5媒体対応</div>', unsafe_allow_html=True)
 
# ─── タブ ─────────────────────────────────────────────────
tab1, tab2 = st.tabs(["① タイトル生成", "② 本文生成"])
 
# ══════════════════════════════════════════════════════════
# TAB 1: タイトル生成
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### 📝 基本設定")
 
    kw = st.text_input("テーマ・キーワード *", placeholder="例：AIで時短する方法、自分らしく生きること")
    kc = st.text_area("内容・補足（任意）", placeholder="伝えたいメッセージ、エピソードなど", height=80)
 
    col1, col2 = st.columns(2)
    with col1:
        sns_t = st.selectbox("SNS媒体", list(SNS_DATA.keys()), key="sns_t")
    with col2:
        gen_t = st.radio("ターゲット（性別）", ["👩 女性", "👨 男性"], horizontal=True, key="gen_t")
 
    age_t = st.select_slider(
        "ターゲット（年代）",
        options=["10代", "20代", "30代", "40代", "50代", "60代"],
        value="30代", key="age_t"
    )
 
    info = SNS_DATA[sns_t]
    st.info(f"**{sns_t}** — {info['role']}  \n📊 アルゴリズム：{info['algo']}")
 
    if st.button("✨ タイトル候補を3パターン生成する", key="btn_title"):
        if not kw:
            st.warning("テーマ・キーワードを入力してください")
        else:
            prompt = f"""SNS投稿のプロライターとして、{sns_t}でバズるタイトルを3パターン作成してください。
 
テーマ：{kw}{chr(10)+'補足：'+kc if kc else ''}
SNS：{sns_t}（{info['role']}）
ターゲット：{gen_t}・{age_t}
動かす感情：{info['emotion']}
感情曲線：{info['curve']}
タイトルのコツ：{info['hint']}
 
ルール：各15〜40文字、「続きが読みたい」「これ私のこと？」と思わせること。
番号付きで3つのみ出力（説明文なし）。
 
1.
2.
3."""
            result = call_claude(prompt)
            st.session_state["title_result"] = result
 
    if "title_result" in st.session_state:
        st.markdown("#### 🎯 生成されたタイトル候補")
        st.code(st.session_state["title_result"], language=None)
        st.caption("↑ 右上のコピーボタンでコピーできます。気に入ったタイトルを② 本文生成タブに貼り付けてください。")
 
# ══════════════════════════════════════════════════════════
# TAB 2: 本文生成
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### ⚙️ 本文オプション")
 
    bt = st.text_input("選んだタイトル *", placeholder="①で生成したタイトルをここに貼り付けてください", key="bt")
    bc = st.text_area("補足・内容（任意）", placeholder="伝えたいメッセージ、エピソードなど", height=80, key="bc")
 
    col3, col4 = st.columns(2)
    with col3:
        sns_b = st.selectbox("SNS媒体", list(SNS_DATA.keys()), key="sns_b")
    with col4:
        gen_b = st.radio("ターゲット（性別）", ["👩 女性", "👨 男性"], horizontal=True, key="gen_b")
 
    age_b = st.select_slider(
        "ターゲット（年代）",
        options=["10代", "20代", "30代", "40代", "50代", "60代"],
        value="30代", key="age_b"
    )
 
    col5, col6, col7 = st.columns(3)
    with col5:
        emoji_b = st.radio("絵文字", ["😊 あり", "🚫 なし"], key="emoji_b")
    with col6:
        style_b = st.selectbox("文章スタイル", list(STY_DATA.keys()), key="style_b")
    with col7:
        len_b = st.radio("文章の長さ", ["短め", "普通", "長め"], index=1, key="len_b")
 
    info_b = SNS_DATA[sns_b]
    len_info = LEN_DATA[sns_b][len_b]
    max_chars, target_str = len_info
    st.info(
        f"**{sns_b}** — {info_b['role']}  \n"
        f"📏 目標文字数：{target_str}（上限 **{max_chars}文字**）  \n"
        f"📊 アルゴリズム：{info_b['algo']}"
    )
 
    if st.button("✍️ 本文を生成する", key="btn_body"):
        if not bt:
            st.warning("タイトルを入力してください")
        else:
            sg = STY_DATA[style_b]
            em_rule = "絵文字を自然に使う（1行に1〜2個まで）" if "あり" in emoji_b else "絵文字は一切使わない"
 
            prompt = f"""SNS投稿のプロライターとして、今村奈々スタイルで{sns_b}の投稿本文を作成してください。
 
{NANA_STYLE}
 
■ SNS：{sns_b}（{info_b['role']}）
■ タイトル：{bt}{chr(10)+'■ 補足内容：'+bc if bc else ''}
■ 文章スタイル：{sg}
■ 絵文字ルール：{em_rule}
■ ターゲット：{gen_b}・{age_b}
 
━━━━━━━━━━━━━━━━━━━━
【文字数ルール（絶対厳守・最優先）】
目標文字数：{target_str}
最大文字数：{max_chars}文字
※出力前に必ず文字数を数え、{max_chars}文字を超えていたら削ること
━━━━━━━━━━━━━━━━━━━━
 
■ アルゴリズム重視：{info_b['algo']}
■ 感情曲線：{info_b['curve']}
 
【感情設計構成（必ず従うこと）】
{info_b['struct']}
 
【出力ルール】
・タイトルは本文に含めない
・投稿本文のみ出力（前置き・説明・ラベル不要）
・文字数制限を絶対に超えないこと"""
 
            result_b = call_claude(prompt)
            st.session_state["body_result"] = result_b
            st.session_state["body_max"] = max_chars
 
    if "body_result" in st.session_state:
        body_text = st.session_state["body_result"]
        saved_max = st.session_state.get("body_max", max_chars)
        char_count = len(body_text)
        is_over = char_count > saved_max
 
        st.markdown("#### 📱 生成された投稿本文")
 
        if is_over:
            st.markdown(
                f'<p class="char-ng">⚠️ {char_count}文字（上限{saved_max}文字を{char_count - saved_max}文字オーバー）→ もう一度生成してください</p>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<p class="char-ok">✅ {char_count}文字 / 上限{saved_max}文字（OK）</p>',
                unsafe_allow_html=True
            )
 
        st.code(body_text, language=None)
        st.caption("↑ 右上のコピーボタンでコピーしてSNSに投稿してください 🎉")
 
# ─── フッター ─────────────────────────────────────────────
st.divider()
st.caption("✨ SNS投稿メーカー — 今村奈々スタイル × 感情設計")
 

