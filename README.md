# Azure AI チャットツール

Azure OpenAI Service を活用した社内向けAIチャットツールです。FAQ対応、ドキュメント問い合わせ、要約補助などの用途で従業員の生産性向上を支援します。

## 機能

- 🤖 Azure OpenAI (GPT-3.5/GPT-4) を使用したAIチャット
- 💬 会話履歴の管理とコンテキスト保持
- 🚀 htmxによるスムーズなユーザー体験
- 📝 Markdown形式の応答対応
- 🔒 セッション管理による個別の会話管理
- 📱 レスポンシブデザイン

## 技術スタック

- **バックエンド**: Python (FastAPI)
- **フロントエンド**: HTML + htmx
- **AI**: Azure OpenAI Service
- **スタイリング**: CSS3
- **パッケージ管理**: uv

## 前提条件

- Python 3.8以上
- Azure OpenAI Service のアカウントとAPIキー
- uv（Pythonパッケージマネージャー）

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd azure-ai-by-claude
```

### 2. uvのインストール（未インストールの場合）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 仮想環境の作成と有効化

```bash
uv venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows
```

### 4. 依存関係のインストール

```bash
uv pip install -r requirements.txt
```

### 5. 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集し、Azure OpenAI の認証情報を設定してください：

```env
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-01
SESSION_SECRET_KEY=your-secret-key-here
```

## 起動方法

### 開発サーバーの起動

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

アプリケーションは http://localhost:8000 でアクセスできます。

## 使い方

1. ブラウザで http://localhost:8000 を開きます
2. テキストボックスにメッセージを入力します
3. Enterキーまたは送信ボタンをクリックして送信します
4. AIからの応答が表示されます

## API仕様

### チャットエンドポイント

```http
POST /chat
Content-Type: application/x-www-form-urlencoded

message=<user-message>&session_id=<session-id>
```

レスポンス: HTMXで更新されるHTMLフラグメント

### ヘルスチェック

```http
GET /health
```

レスポンス:
```json
{
  "status": "healthy",
  "service": "Azure AI Chat Tool"
}
```

## プロジェクト構造

```
azure-ai-by-claude/
├── backend/
│   ├── main.py              # FastAPIアプリケーション
│   ├── routes/
│   │   └── chat.py         # チャットエンドポイント
│   ├── services/
│   │   ├── openai_service.py    # Azure OpenAI連携
│   │   └── session_service.py   # セッション管理
│   ├── models/             # データモデル（将来実装）
│   └── utils/              # ユーティリティ（将来実装）
├── frontend/
│   ├── templates/
│   │   └── index.html      # メインページ
│   └── static/
│       └── css/
│           └── style.css   # スタイルシート
├── tests/                  # テスト（将来実装）
├── .env.example           # 環境変数テンプレート
├── requirements.txt       # Python依存関係
├── CLAUDE.md             # 開発ガイド
└── README.md             # このファイル
```

## 開発

### コードフォーマット

```bash
black .
```

### リント

```bash
ruff check .
```

### テスト

```bash
pytest
```

## デプロイ

### Azure App Service へのデプロイ

1. Azure App Service リソースを作成
2. 環境変数を設定
3. デプロイメントセンターからGitHubリポジトリを接続
4. 自動デプロイを設定

## トラブルシューティング

### Azure OpenAI API エラー

- APIキーが正しく設定されているか確認してください
- エンドポイントURLが正しい形式か確認してください
- デプロイメント名がAzure上の実際のデプロイメント名と一致しているか確認してください

### セッションエラー

- ブラウザのCookieが有効になっているか確認してください
- セッションタイムアウト（デフォルト30分）を超えていないか確認してください

## ライセンス

[ライセンスタイプを記載]

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容について議論してください。

## サポート

問題や質問がある場合は、GitHubのissueを作成してください。