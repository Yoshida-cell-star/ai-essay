import streamlit as st
from google import genai
from PIL import Image

# === 画面の基本設定 ===
st.set_page_config(page_title="AI論文アシスタント", page_icon="📝")

# === パスワード認証機能 ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 パスワードを入力してください")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        # 裏側に設定する秘密のパスワードと照合
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop() # パスワードが合うまでここから下は実行させない

# === ここからメインのアプリ画面 ===
st.title(" AI論文アシスタント")
st.write("画像をアップロードすると、模範論文のスタイルに合わせて自動でリライトします。")



# 画像アップロードボタン
uploaded_file = st.file_uploader("画像を一つ選択してください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="ターゲット画像", use_container_width=True)
    
    # 実行ボタン
    reference_essay =st.text_area('お手本となる模範論文をここに貼り付けてください', height=300)
    if st.button("AIで解析＆リライトを実行"):
        with st.spinner("Googleの最新モデル（Gemini 3.8）が解析中..."):
            # APIキーはセキュリティのため裏側から読み込む
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            
            prompt = f"""
            あなたは超一流のゴーストライターです。
            添付した画像に書かれている文字を正確に読み取り、その内容をベースにして、
            以下の【模範論文のスタイル】の論理構造と文体に完全に同化させた、高度な文章に書き換えてください。

            【模範論文のスタイル】
            {reference_essay}
            
            出力は以下の2つのパートに分けてください：
            1. 【画像からの抽出テキスト（原文）】
            2. 【模範論文風にリライトした完成版】
            """
            
            try:
                response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=[prompt, image]
            )
            except Exception as e:
                st.warning("現在AIサーバーが混雑しています。3秒後に自動で再接続します...")
                import time
                time.sleep(3)
                response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=[prompt, image]
            )

            
            st.success("解析完了！")
            st.markdown("### 出力結果")
            st.write(response.text)
