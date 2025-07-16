# 🚀 クイックスタートガイド

Azure AI チャットツール with RAG の最速セットアップガイドです。

## ⚡ 3分でセットアップ

### 1. 依存関係インストール
```bash
# uvがない場合
curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境作成とパッケージインストール
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. 環境変数設定
```bash
cp .env.example .env
```

`.env`ファイルを編集：
```env
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
SESSION_SECRET_KEY=any-random-string
```

### 3. サーバー起動
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. アクセス
http://localhost:8000 を開いて完了！

## 📚 RAG機能を試す

1. **文書アップロード**ボタンをクリック
2. PDF、TXT、MDファイルをドラッグ&ドロップ
3. アップロード完了後、文書について質問

## 🎯 特徴

- ✅ **3分セットアップ**: 複雑な設定不要
- ✅ **軽量**: numpy + pypdf のみ
- ✅ **高精度**: Azure OpenAI Embeddings使用
- ✅ **日本語対応**: 完全日本語サポート
- ✅ **クロスプラットフォーム**: Windows/macOS/Linux

## 🔧 トラブル時

- **権限エラー**: `chmod +x .venv/bin/activate`
- **Azure APIエラー**: `.env`の設定を再確認
- **ファイルアップロードエラー**: ファイルサイズ(10MB以下)と形式を確認

詳細は [README.md](./README.md) を参照してください。