import streamlit as st
import google.generativeai as genai
import base64
import requests
import os
from datetime import datetime
#from dotenv import load_dotenv

###Mermaid APIによるブロック図の生成とbase64エンコード(半角記号が含まれたコードも変換可能) 
###出力された構文が間違っていると動かないので生成AIへの指示の高度化が今後必要

#上記をstreamlitに移植
#一旦まとめて要約し、解説文を作ってからmermeiaコードを出力する構成

#樹形図　放射上Ver

# extract_mermaid_code関数の定義
def extract_mermaid_code(response_text):
    try:
        # response_textを行ごとに分割
        lines = response_text.split('\n')
        mermaid_code = []
        response_text = []

        # 各行をチェック
        in_mermaid_block = False
        for line in lines:
            if line.strip() == '```mermaid':
                in_mermaid_block = True
                continue
            elif line.strip() == '```':
                in_mermaid_block = False
                continue

            if in_mermaid_block:
                mermaid_code.append(line)
            else:
                response_text.append(line)

        # 結果を整形
        mermaid_code = '\n'.join(mermaid_code)
        response_text = '\n'.join(response_text)

        return response_text, mermaid_code
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

# Gemini APIの設定
genai.configure(api_key='AIzaSyA35e8FnZfrxjTP7_RBZQvAm7sjGwb6TWI')
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 環境変数の読み込み版
#load_dotenv()
#genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
#model = genai.GenerativeModel('gemini-pro')

# Streamlitのページ設定
st.set_page_config(page_title="マインドマップジェネレーター", layout="wide")
st.title("マインドマップ(放射状)")

# セッション状態の初期化
if 'img_data' not in st.session_state:
    st.session_state.img_data = None
if 'img_url' not in st.session_state:
    st.session_state.img_url = None
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = None
if 'response_text' not in st.session_state:
    st.session_state.response_text = None


# 入力フォームの作成
prompt1 = st.text_area("マップ化したい内容、キーワード：")
prompt2 = st.text_area("指示内容、注意点、参考情報：", value="特になし")
#prompt2 = st.text_area("保有技術のリストを入力してください：")

# 推論開始ボタンが押されたときの処理
if st.button("推論開始(マップを生成)"):
    if prompt1 and prompt2:
        try:
            # プロンプトの作成
            prompt = f"""
           「マップ化したい内容、キーワード」についてのマインドマップを作成し、  
            それをMermaid記法のmindmap形式で描画するコードを表示してください。 
            
            ###手順###
            「マップ化したい内容、キーワード」の内容がマインドマップの作成に充分多い情報があるかどうか確認します。
            内容が少ないか単一のキーワードの場合は、関連するキーワードを発想し、発想したキーワードから更に発想を広げて
            充分多い内容になるまで多くのアイデアを考案します。

            内容が充分多い場合、または充分増やした場合、その内容を要約し、それが表している概念や法則、項目間の関係性を考察して出力します。
            出力した内容を基にマインドマップの構成を決定し、それをMermaidで描画するコードを出力します。
            意味の近いグループはなるべく近くに並ぶようにし、中心から周囲に発想が拡がる構図がよいです。

            Mermaidのコード部分は「```mermaid」と「```」で囲むことで明示します。

            ###マップ化したい内容、キーワード###
            {prompt1}
            
            ###指示内容、注意点、参考情報###
            {prompt2}

            ##重要：mermaidコードの表記ルール##
            ( 、 ) 、 [ 、]、【、】などの括弧記号は項目ラベル名やグループ名に使わず、すべて「_」に置き換える。
            記号や特殊な文字は項目ラベル名やグループ名に使わず、すべて「_」に置き換える。
            テーマ名はRounded square形式の太字とし、項目名を()で囲む。例：(**テーマ**) 
            第一階層のキーワードはHexagon形式の太字とし、項目名を{{{{}}}}で囲む。例：{{{{**第一階層**}}}}
            第二階層のキーワードはSquare形式の太字とし、項目名を[]で囲む。例：[**第二階層**]
            第三階層より下のキーワードはRounded square形式とする。項目名を()で囲む。例：(第三階層) 
            テーマ名(root)、第一階層、第二階層までのキーワードは全て太字にする(項目の前と後に「**」をつける。例：**項目**)


            ##出力例
            %%{{init:{{'theme':'base','themeVariables':{{'primaryColor':'#e0f7fa','primaryTextColor':'#FAFBF9','fontSize':'34px'}}}}}}%%
            mindmap
            root(**健康な生活と充分な睡眠**)
                
                {{{{**健康的な生活**}}}}
                  [**栄養バランス**]
                    (果物と野菜)
                    (タンパク質)
                    (炭水化物)
                {{{{**適度な運動**}}}}
                    (有酸素運動)
                    (筋力トレーニング)
                  [**ストレス管理**]
                    (瞑想)
                    (趣味)
                    (人間関係)

                {{{{**充分な睡眠**}}}}
                  [**睡眠環境の最適化**]
                    (静かな環境)
                    (適温設定)
                    (快適な寝具)
                  [**規則正しい生活習慣**]
                    (就寝時間の固定)
                    (寝る前のリラックス)
                  [**睡眠の質向上**]
                    (ブルーライトカット)
                    (適度な疲労)
                    (睡眠時間の確保)
            """

            # Geminiでマインドマップのコードを生成
            response = model.generate_content(prompt)

            ## responseの結果を表示 エラー発生時のデバッグ用
            #st.write("### Geminiからの応答:")
            #st.write(response.text)

            # AIの応答を解説とMermaidコードに分割
            response_text, mermaid_code = extract_mermaid_code(response.text)


            # Mermaid形式のコードを抽出して整形
            #mermaid_code = response.text.strip()
            #if not mermaid_code.startswith('flowchart'):
            #    mermaid_code = 'flowchart LR\n' + mermaid_code
            
            # Mermaid APIのエンドポイント
            mermaid_api_url = "https://mermaid.ink/img/"
            
            # mermaidコードをbase64エンコード
            mermaid_code_bytes = mermaid_code.encode('utf-8')
            base64_code = base64.urlsafe_b64encode(mermaid_code_bytes).decode('utf-8')
            
            # 画像URLの生成
            img_url = f"{mermaid_api_url}{base64_code}"
            
            # 画像の取得と表示
            response = requests.get(img_url)
            if response.status_code == 200:
                # セッション状態に画像データとURLを保存
                st.session_state.img_data = response.content
                st.session_state.img_url = img_url
                st.session_state.mermaid_code = mermaid_code
                st.session_state.response_text = response_text

            else:
                st.session_state.img_data = []
                st.session_state.img_url = []
                st.session_state.mermaid_code = mermaid_code
                st.session_state.response_text = response_text
                st.error(f"画像の生成に失敗しました。コードとAIの回答を確認してください。ステータス: {response.status_code}")
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
    else:
        st.warning("入力データに不足があります")

               
# 現在の日時を使用してユニークなファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 画像の取得と表示
if st.session_state.img_data:
    # 生成されたマインドマップの表示
    st.image(st.session_state.img_url, caption="生成されたマップ", use_container_width=True)
 
    # 画像ダウンロードボタン
    st.download_button(
        label="マップをダウンロード",
        data=st.session_state.img_data,
        file_name=f"needs_map_{timestamp}.png",
        mime="image/png"
    )
                
if st.session_state.mermaid_code:
    # Mermaidコードの表示（オプション）
    with st.expander("描画コードを表示(Mermaid)"):
        st.code(st.session_state.mermaid_code, language="mermaid")

    # Mermaidコードダウンロードボタン
    st.download_button(
        label="描画コード ダウンロード",
        data=st.session_state.mermaid_code,
        file_name=f"needs_map_{timestamp}.txt",
        mime="text/plain"
    )

if st.session_state.response_text:
    # AIの解説部分の表示
    st.write("### AIの解説を表示:")
    st.write(st.session_state.response_text)

    # AIの解説ダウンロードボタン
    st.download_button(
        label="AIの解説 ダウンロード",
        data=st.session_state.response_text,
        file_name=f"AI_explanation_{timestamp}.txt",
        mime="text/plain"
    )



