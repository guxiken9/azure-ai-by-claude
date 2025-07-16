# Azure AI チャットツール with RAG

**⚠️ 注意: このプロジェクトはClaude Code（claude.ai/code）によって作成された学習目的のプロジェクトです。**

Azure OpenAI Service を活用した社内向けAIチャットツールです。RAG（Retrieval-Augmented Generation）機能により、アップロードした文書に基づいた正確な回答を提供し、FAQ対応、ドキュメント問い合わせ、要約補助などの用途で従業員の生産性向上を支援します。

## ⚠️ 免責事項

- **学習目的**: このプロジェクトは学習・研究・実験目的でClaude Codeにより作成されました
- **責任の制限**: 本プロジェクトの使用により生じたいかなる損失、損害、責任についても、開発者は一切の責任を負いません
- **商用利用**: 商用環境での使用は推奨されません。本格的な商用利用の場合は、適切なセキュリティ監査と品質保証を実施してください
- **セキュリティ**: 本プロジェクトはプロトタイプレベルの実装であり、本番環境で求められるセキュリティレベルを満たしていない可能性があります
- **データ保護**: Azure OpenAI APIキーなどの機密情報の取り扱いは利用者の責任で行ってください
- **サポート**: 公式なサポートは提供されません。利用は自己責任でお願いします

## 🎯 主要機能

### コア機能
- 🤖 **AIチャット**: Azure OpenAI (GPT-3.5/GPT-4) を使用
- 📚 **RAG機能**: アップロードした文書に基づく回答生成
- 💬 **会話履歴管理**: コンテキスト保持によるスムーズな対話
- 📝 **Markdown対応**: リッチな応答表示

### 文書管理機能
- 📁 **ファイルアップロード**: PDF、TXT、MDファイル対応
- 🔍 **ベクトル検索**: Azure OpenAI Embeddingsによる類似度検索
- 📊 **文書管理**: アップロード済み文書の一覧表示・削除
- 🎯 **ソース表示**: 回答の参考資料を自動表示

### UI/UX機能
- 🚀 **htmx**: スムーズなリアルタイム更新
- 📱 **レスポンシブ**: モバイル対応デザイン
- 🔒 **セッション管理**: 個別の会話管理
- ⚡ **軽量実装**: 最小限の依存関係

## 🛠️ 技術スタック

- **バックエンド**: Python (FastAPI)
- **フロントエンド**: HTML + htmx + Jinja2
- **AI/RAG**: 
  - Azure OpenAI Service (GPT-3.5/GPT-4、Embeddings)
  - 独自ベクトル検索エンジン（コサイン類似度）
  - テキスト分割・チャンク処理
- **文書処理**: PyPDF、標準ライブラリ
- **データ保存**: JSON（軽量・永続化）
- **スタイリング**: CSS3
- **パッケージ管理**: uv

## 📋 前提条件

- Python 3.8以上
- Azure OpenAI Service のアカウントとAPIキー
- Azure OpenAI Embeddings デプロイメント（text-embedding-ada-002）
- uv（Pythonパッケージマネージャー）

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd azure-ai-by-claude
```

### 2. uvのインストール（未インストールの場合）

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. 仮想環境の作成と有効化

```bash
uv venv
```

**仮想環境の有効化:**

macOS/Linux:
```bash
source .venv/bin/activate
```

Windows:
```cmd
.venv\Scripts\activate
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
# Azure OpenAI 基本設定
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-01

# RAG機能用（重要）
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# セッション管理
SESSION_SECRET_KEY=your-secret-key-here
```

## 起動方法

### 開発サーバーの起動

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

アプリケーションは http://localhost:8000 でアクセスできます。

## 📖 使い方

### 基本的なチャット
1. ブラウザで http://localhost:8000 を開きます
2. テキストボックスにメッセージを入力します
3. Enterキーまたは送信ボタンをクリックして送信します
4. AIからの応答が表示されます

### RAG機能の使用
1. **文書アップロード**:
   - ヘッダーの「文書アップロード」ボタンをクリック
   - PDF、TXT、MDファイルをドラッグ&ドロップまたは選択
   - アップロード完了まで待機

2. **文書ベースの質問**:
   - アップロード後、通常通りにチャットで質問
   - システムが自動的に関連文書を検索
   - 回答に参考資料のソースが表示される

3. **文書管理**:
   - ヘッダーの「文書管理」ボタンで一覧表示
   - 不要な文書は削除ボタンで削除可能

## 🔌 API仕様

### チャットエンドポイント

```http
POST /chat
Content-Type: application/x-www-form-urlencoded

message=<user-message>&session_id=<session-id>
```

レスポンス: HTMXで更新されるHTMLフラグメント（参考資料情報含む）

### RAG文書管理API

```http
# 文書アップロード
POST /api/documents/upload
Content-Type: multipart/form-data

# 文書一覧取得
GET /api/documents/list

# 文書削除
DELETE /api/documents/{document_name}

# 文書検索
POST /api/documents/search
Content-Type: application/json
{"query": "検索クエリ", "n_results": 5}
```

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

## 📁 プロジェクト構造

```
azure-ai-by-claude/
├── backend/
│   ├── main.py                    # FastAPIアプリケーション
│   ├── routes/
│   │   ├── chat.py               # チャットエンドポイント（RAG統合）
│   │   └── documents.py          # 文書管理API
│   └── services/
│       ├── openai_service.py     # Azure OpenAI連携（コンテキスト注入対応）
│       ├── session_service.py    # セッション管理
│       ├── vector_db_service.py  # ベクトル検索エンジン
│       └── document_service.py   # 文書処理（PDF/TXT）
├── frontend/
│   ├── templates/
│   │   └── index.html            # メインページ（RAG UI含む）
│   └── static/
│       └── css/
│           └── style.css         # スタイルシート（モーダル含む）
├── vector_db_data/               # ベクトルDB保存ディレクトリ
│   └── documents.json           # 文書メタデータと埋め込み
├── .env.example                 # 環境変数テンプレート
├── requirements.txt             # Python依存関係（軽量）
├── CLAUDE.md                   # 開発ガイド
└── README.md                   # このファイル
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

## 🔧 トラブルシューティング

### Azure OpenAI API エラー

- APIキーが正しく設定されているか確認してください
- エンドポイントURLが正しい形式か確認してください
- デプロイメント名がAzure上の実際のデプロイメント名と一致しているか確認してください
- **RAG機能**: `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`が設定され、Embeddingsデプロイメントが存在するか確認

### ファイルアップロードエラー

- ファイルサイズが10MB以下であることを確認してください
- 対応形式（PDF、TXT、MD）であることを確認してください
- ブラウザのJavaScriptが有効になっているか確認してください

### RAG検索エラー

- 文書がアップロード済みであることを確認してください
- `vector_db_data/documents.json`ファイルが存在し、読み取り可能であることを確認
- Azure OpenAI Embeddingsの利用制限に達していないか確認

### セッションエラー

- ブラウザのCookieが有効になっているか確認してください
- セッションタイムアウト（デフォルト30分）を超えていないか確認してください

### Windows環境での注意事項

- `uvloop`はWindows非対応のため、自動的に除外されます（`requirements.txt`の条件式により）
- パスセパレータは自動的に処理されます（`pathlib`を使用）
- PowerShellでuvをインストールする際は、実行ポリシーの設定が必要な場合があります：
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 🎯 RAG機能の特徴

### 軽量実装
- **外部依存なし**: ChromaDB、LangChain不要
- **純粋Python**: 標準ライブラリ + numpy + pypdf のみ
- **高速インストール**: コンパイル不要
- **クロスプラットフォーム**: Windows/Linux/macOS対応

### 高性能検索
- **Azure OpenAI Embeddings**: 高品質な意味的検索
- **コサイン類似度**: 正確な関連度計算
- **チャンク分割**: 効率的な文書処理（1000文字/200文字オーバーラップ）
- **JSON保存**: 永続化とポータビリティ

### 企業利用対応
- **データローカル**: 文書データはローカル保存
- **セキュリティ**: 一時ファイル自動削除
- **スケーラブル**: 文書数に応じた線形スケーリング
- **メンテナンス性**: シンプルなアーキテクチャ

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

**ライセンス要約:**
- ✅ 商用利用可能（ただし免責事項を参照）
- ✅ 修正・配布可能
- ✅ 私的利用可能
- ❌ 責任・保証なし
- ❌ 特許権の保護なし

**重要**: MITライセンスに加えて、本プロジェクト固有の免責事項が適用されます。使用前に必ず上記の「免責事項」セクションをお読みください。

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容について議論してください。

## サポート

問題や質問がある場合は、GitHubのissueを作成してください。