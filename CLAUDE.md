# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Azure OpenAI を活用した社内向けAIチャットツール。FAQ対応、ドキュメント問い合わせ、要約補助などの用途で従業員の生産性向上を図る。

## 技術スタック

- **フロントエンド**: HTML + htmx（最小限のJavaScript）
- **バックエンド**: Python（FastAPI または Flask）
- **Azureサービス**:
  - Azure OpenAI Service（gpt-4/gpt-3.5）
  - Azure Blob Storage（ログ保存用）
  - Azure App Service（ホスティング）
  - Azure Table Storage または SQLite（データ保存）

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
│   ├── app.py or main.py      # メインアプリケーション
│   ├── routes/                 # APIエンドポイント
│   │   └── chat.py            # チャットエンドポイント
│   ├── services/              # ビジネスロジック
│   │   ├── openai_service.py  # Azure OpenAI連携
│   │   └── session_service.py # セッション管理
│   ├── models/                # データモデル
│   └── utils/                 # ユーティリティ関数
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

1. **チャットエンドポイント** (`/chat`):
   - POSTリクエストで `message` パラメータを受信
   - htmx更新用のHTMLフラグメントを返却
   - セッション内で会話コンテキストを維持

2. **セッション管理**:
   - サーバーサイドセッション（Redisまたはメモリ内）
   - セッションごとに会話履歴を保存
   - セッションタイムアウトの実装

3. **Azure OpenAI連携**:
   - Azure設定で `openai` Python SDKを使用
   - レート制限とリトライの処理
   - より良いUXのためのレスポンスストリーミング

4. **htmxフロントエンド**:
   - フォーム送信に `hx-post` を使用
   - レスポンス挿入に `hx-target`
   - スムーズな更新に `hx-swap`
   - タイピングインジケーターの実装

5. **セキュリティ考慮事項**:
   - 全入力の検証とサニタイズ
   - セッションごとのレート制限
   - シークレットは環境変数で管理
   - 必要に応じてCORS設定

## 実装フェーズ

### フェーズ1（MVP）- 現在の焦点
- htmxを使った基本的なチャットUI
- Azure OpenAI連携
- メモリ内セッション管理
- シンプルな会話フロー

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
- レスポンス応答時間：2秒以内（通常処理）
- レスポンシブUI（モバイル対応）
- セキュリティ：最小限のIP制限やBasic認証（初期）