"""
超軽量ベクトルデータベース管理サービス（依存関係最小）
"""
import os
import json
import math
from typing import List, Dict, Optional
from openai import AzureOpenAI
import hashlib
from datetime import datetime


class SimpleTextSplitter:
    """シンプルなテキスト分割器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", "。", "、", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """テキストをチャンクに分割"""
        chunks = []
        
        # 基本的な分割
        for separator in self.separators:
            if separator in text:
                parts = text.split(separator)
                current_chunk = ""
                
                for part in parts:
                    if len(current_chunk + separator + part) <= self.chunk_size:
                        current_chunk += separator + part if current_chunk else part
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = part
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                break
        else:
            # セパレータが見つからない場合は単純に分割
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunk = text[i:i + self.chunk_size]
                if chunk.strip():
                    chunks.append(chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 50]  # 短すぎるチャンクは除外


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """コサイン類似度を計算"""
    try:
        # 内積を計算
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # ベクトルの大きさを計算
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    except:
        return 0.0


class VectorDBService:
    def __init__(self):
        # データ保存ディレクトリ
        self.data_dir = "./vector_db_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # メタデータ保存
        self.metadata_file = os.path.join(self.data_dir, "documents.json")
        self.documents = []  # ドキュメントのリスト（埋め込み含む）
        
        # Azure OpenAI クライアント
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002")
        
        # テキスト分割器
        self.text_splitter = SimpleTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # 既存データの読み込み
        self._load_existing_data()
    
    def _load_existing_data(self):
        """既存のデータを読み込み"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
        except Exception as e:
            print(f"既存データ読み込みエラー: {e}")
            self.documents = []
    
    def _save_data(self):
        """データを保存"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"データ保存エラー: {e}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """テキストの埋め込みを取得"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_deployment,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"埋め込み生成エラー: {e}")
            return None
    
    def generate_document_id(self, content: str, metadata: Dict) -> str:
        """ドキュメントのユニークIDを生成"""
        unique_string = f"{content}{metadata.get('source', '')}{metadata.get('page', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    async def add_document(self, content: str, metadata: Dict) -> Dict:
        """ドキュメントを追加"""
        try:
            # テキストをチャンクに分割
            chunks = self.text_splitter.split_text(content)
            
            chunk_docs = []
            successful_chunks = 0
            
            for i, chunk in enumerate(chunks):
                # 埋め込み生成
                embedding = self._get_embedding(chunk)
                if embedding is None:
                    continue
                
                # チャンクメタデータ
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'created_at': datetime.now().isoformat(),
                    'content': chunk,
                    'embedding': embedding,  # 埋め込みも保存
                    'doc_id': self.generate_document_id(chunk, chunk_metadata)
                })
                
                chunk_docs.append(chunk_metadata)
                successful_chunks += 1
            
            if successful_chunks == 0:
                return {'status': 'error', 'message': '埋め込み生成に失敗しました'}
            
            # ドキュメントをリストに追加
            self.documents.extend(chunk_docs)
            
            # データ保存
            self._save_data()
            
            return {
                'status': 'success',
                'chunks_added': successful_chunks,
                'document_name': metadata.get('source', 'Unknown')
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """類似度検索を実行"""
        try:
            if len(self.documents) == 0:
                return []
            
            # クエリの埋め込み生成
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                return []
            
            # 各ドキュメントとの類似度を計算
            similarities = []
            for doc in self.documents:
                if 'embedding' in doc:
                    similarity = cosine_similarity(query_embedding, doc['embedding'])
                    similarities.append((similarity, doc))
            
            # 類似度順にソート
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            # 上位n_results件を返す
            results = []
            for similarity, doc in similarities[:n_results]:
                results.append({
                    'content': doc['content'],
                    'metadata': {k: v for k, v in doc.items() if k not in ['content', 'embedding']},
                    'score': similarity
                })
            
            return results
            
        except Exception as e:
            print(f"検索エラー: {e}")
            return []
    
    def list_documents(self) -> List[Dict]:
        """保存されているドキュメントの一覧を取得"""
        try:
            # ソースごとにグループ化
            documents_by_source = {}
            for doc in self.documents:
                source = doc.get('source', 'Unknown')
                if source not in documents_by_source:
                    documents_by_source[source] = {
                        'source': source,
                        'chunks': 0,
                        'created_at': doc.get('created_at', '')
                    }
                documents_by_source[source]['chunks'] += 1
            
            return list(documents_by_source.values())
            
        except Exception as e:
            print(f"ドキュメント一覧取得エラー: {e}")
            return []
    
    def delete_document(self, source: str) -> bool:
        """特定のソースのドキュメントを削除"""
        try:
            # 削除前のドキュメント数
            original_count = len(self.documents)
            
            # 指定されたソース以外のドキュメントのみ残す
            self.documents = [doc for doc in self.documents if doc.get('source') != source]
            
            # 削除されたかチェック
            if len(self.documents) < original_count:
                self._save_data()
                return True
            else:
                return False
            
        except Exception as e:
            print(f"ドキュメント削除エラー: {e}")
            return False
    
    def reset_database(self):
        """データベースをリセット（開発用）"""
        try:
            self.documents = []
            
            # ファイル削除
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            
            return True
        except Exception as e:
            print(f"データベースリセットエラー: {e}")
            return False


# シングルトンインスタンス
vector_db_service = VectorDBService()