# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Azure OpenAI を活用した社内向けAIチャットツール。FAQ対応、ドキュメント問い合わせ、要約補助などの用途で従業員の生産性向上を図る。

## 技術スタック

- **フロントエンド**: HTML + htmx（最小限のJavaScript）、Jinja2テンプレート
- **バックエンド**: Python（FastAPI）
- **AI/RAGサービス**: 
  - Azure OpenAI Service（GPT-3.5/GPT-4、Embeddings）
  - ChromaDB（ベクトルデータベース）
  - LangChain（文書処理）
- **Azureサービス**:
  - Azure OpenAI Service（チャット・埋め込み）
  - Azure Blob Storage（ログ保存用・将来）
  - Azure App Service（ホスティング）

## 開発コマンド

### Python バックエンド（uvを使用）
```bash
# uvのインストール（初回のみ）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトの初期化と仮想環境の作成
uv venv

# 仮想環境の有効化
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 依存関係のインストール
uv pip install -r requirements.txt

# パッケージの追加（例）
uv pip install fastapi uvicorn python-dotenv openai

# 開発サーバーの起動（FastAPI）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 開発サーバーの起動（Flask）
python app.py

# テストの実行
pytest

# コードフォーマット
black .

# リント
ruff check .
```

### 環境設定
```bash
# 環境変数テンプレートのコピー
cp .env.example .env

# .env ファイルに Azure の認証情報を設定
# 必要な変数:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT_NAME
# - AZURE_OPENAI_API_VERSION
```

## アーキテクチャ

### ディレクトリ構造
```
/
├── backend/
│   ├── main.py                # FastAPIメインアプリケーション
│   ├── routes/                # APIエンドポイント
│   │   ├── chat.py           # チャットエンドポイント（RAG統合済み）
│   │   └── documents.py      # 文書管理エンドポイント
│   └── services/             # ビジネスロジック
│       ├── openai_service.py     # Azure OpenAI連携（コンテキスト注入対応）
│       ├── session_service.py    # セッション管理
│       ├── vector_db_service.py  # ChromaDB・ベクトル検索
│       └── document_service.py   # 文書処理（PDF/TXT対応）
├── frontend/
│   ├── index.html             # メインチャット画面
│   ├── static/
│   │   ├── css/              # スタイルシート
│   │   └── js/               # htmx設定
│   └── templates/            # HTMLテンプレート
├── tests/                    # テストファイル
├── .env.example             # 環境変数テンプレート
├── requirements.txt         # Python依存関係
└── README.md               # セットアップ手順
```

### 主要実装ポイント

1. **RAG（Retrieval-Augmented Generation）**:
   - ChromaDBを使用したローカルベクトルデータベース
   - Azure OpenAI Embeddingsで文書の埋め込み生成
   - LangChainによる文書分割（1000文字チャンク、200文字オーバーラップ）
   - コサイン類似度による検索（上位3件取得）

2. **文書管理**:
   - PDF、TXT、MDファイル対応（最大10MB）
   - ドラッグ&ドロップアップロード機能
   - 文書一覧表示・削除機能
   - 一時ファイル処理によるセキュリティ確保

3. **チャットエンドポイント** (`/chat`, `/chat/stream`):
   - 自動RAG検索統合（質問に関連する文書を検索）
   - コンテキスト注入によるAI回答の精度向上
   - 参考資料の表示機能
   - ストリーミング・通常レスポンス両対応

4. **APIエンドポイント**:
   - `POST /api/documents/upload`: ファイルアップロード
   - `GET /api/documents/list`: 文書一覧取得
   - `DELETE /api/documents/{name}`: 文書削除
   - `POST /api/documents/search`: 文書検索

5. **UI/UX**:
   - モーダルベースの文書管理
   - リアルタイムアップロード進捗表示
   - 参考資料の自動表示
   - レスポンシブ対応

## 実装フェーズ

### フェーズ1（MVP）- ✅ 完了
- htmxを使った基本的なチャットUI
- Azure OpenAI連携（チャット・埋め込み）
- メモリ内セッション管理
- RAG機能統合（ChromaDB）
- 文書アップロード・管理機能
- PDF/TXT文書処理

### フェーズ2（将来）
- 永続的なログ保存
- ログ用管理画面
- 高度なセッション管理

### フェーズ3（将来）
- 設定UI
- 利用状況分析
- マルチモデル対応

## テスト戦略

- サービスのユニットテスト
- APIエンドポイントの統合テスト
- テストでAzure OpenAIレスポンスをモック
- セッション管理のエッジケースをテスト

## デプロイメモ

- Azure App Serviceでホスティング
- App Serviceで環境変数を設定
- ログ用のAzure Blob Storageセットアップ（フェーズ2）
- ヘルスチェックエンドポイントの実装

## プロジェクト要件（元の開発要件）

### API仕様例
```http
POST /chat
Content-Type: application/x-www-form-urlencoded

message=こんにちは、今日は何の日？

---

レスポンス（HTML部分）
<div id="chat-response">
  <p><strong>AI:</strong> 今日は「海の日」です。海に感謝する日として祝われています。</p>
</div>
```

### 非機能要件
- 日本語対応
- レスポンス応答時間：2秒以内（通常処理）、RAG検索：3-5秒以内
- レスポンシブUI（モバイル対応）
- セキュリティ：最小限のIP制限やBasic認証（初期）
- ファイルサイズ制限：10MB（PDF/TXT/MD）
- 同時アップロード：クライアント側で1ファイルずつ処理

## よくある開発タスク

### 新しいエンドポイント追加
1. `backend/routes/`に新規ルーターファイル作成
2. `backend/main.py`でルーターをインクルード
3. 必要に応じて`services/`にビジネスロジック追加

### UIの変更
1. `frontend/templates/index.html`を編集
2. htmx属性で動的更新部分を定義
3. `frontend/static/css/style.css`でスタイル調整

### RAG機能のカスタマイズ
- **チャンクサイズ変更**：`vector_db_service.py`の`SimpleTextSplitter`パラメータ
- **検索結果数調整**：`chat.py`の`search`メソッド呼び出し（デフォルト3件）
- **類似度しきい値**：`vector_db_service.py`でスコアフィルタリング追加

### Azure OpenAI設定変更
- モデル変更：`.env`の`AZURE_OPENAI_DEPLOYMENT_NAME`を更新
- 埋め込みモデル変更：`.env`の`AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`を更新
- パラメータ調整：`openai_service.py`の`get_chat_response`メソッド内で変更

## データ管理

### ベクトルDB管理
- **データ場所**：`./vector_db_data/documents.json`
- **バックアップ**：JSONファイルを定期的にバックアップ
- **リセット**：`/api/documents/reset` エンドポイント（開発環境のみ）

### ログとモニタリング
- **エラーログ**：コンソール出力（`print`文で確認）
- **埋め込み生成**：Azure OpenAI使用量の監視推奨
- **パフォーマンス**：大量文書では検索時間が線形増加

## 軽量RAG実装の設計判断

### 技術選定理由
1. **ChromaDB → 独自実装**：システム依存関係とコンパイル要件を回避
2. **LangChain → 標準ライブラリ**：複雑な依存関係ツリーを回避
3. **FAISS → コサイン類似度**：インストール簡素化とクロスプラットフォーム対応
4. **JSON保存**：データベース不要、ポータブル、デバッグ容易

### パフォーマンス特性
- **文書数**: 1000件程度まで高速（線形増加）
- **チャンク数**: 10000件程度まで実用的
- **メモリ使用量**: 埋め込み1536次元 × 文書数
- **検索速度**: Python実装のため中規模データセット向け