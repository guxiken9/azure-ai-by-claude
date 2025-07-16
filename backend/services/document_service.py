"""
文書処理サービス（PDF、テキストファイルの読み込みと処理）
"""
import os
from typing import Dict, Optional
from pathlib import Path
import pypdf
# LangChainは使用せず、標準ライブラリで実装
import tempfile


class DocumentService:
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt', '.md'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def validate_file(self, filename: str, file_size: int) -> Dict:
        """ファイルの検証"""
        # ファイル拡張子の確認
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.supported_extensions:
            return {
                'valid': False,
                'error': f"サポートされていないファイル形式です。対応形式: {', '.join(self.supported_extensions)}"
            }
        
        # ファイルサイズの確認
        if file_size > self.max_file_size:
            return {
                'valid': False,
                'error': f"ファイルサイズが大きすぎます。最大サイズ: {self.max_file_size / 1024 / 1024}MB"
            }
        
        return {'valid': True}
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """PDFからテキストを抽出"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF読み込みエラー: {str(e)}")
    
    async def extract_text_from_txt(self, file_path: str) -> str:
        """テキストファイルからテキストを抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # UTF-8で読めない場合は、Shift-JISで試す
            try:
                with open(file_path, 'r', encoding='shift-jis') as file:
                    return file.read()
            except Exception as e:
                raise Exception(f"テキストファイル読み込みエラー: {str(e)}")
    
    async def process_document(self, file_path: str, filename: str) -> Dict:
        """ドキュメントを処理してテキストとメタデータを返す"""
        try:
            file_ext = Path(filename).suffix.lower()
            
            # ファイル形式に応じてテキストを抽出
            if file_ext == '.pdf':
                text = await self.extract_text_from_pdf(file_path)
            elif file_ext in ['.txt', '.md']:
                text = await self.extract_text_from_txt(file_path)
            else:
                raise Exception(f"サポートされていないファイル形式: {file_ext}")
            
            # メタデータの作成
            metadata = {
                'source': filename,
                'file_type': file_ext,
                'file_size': os.path.getsize(file_path)
            }
            
            return {
                'text': text,
                'metadata': metadata,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """アップロードされたファイルを一時的に保存"""
        try:
            # 一時ディレクトリにファイルを保存
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return file_path
        except Exception as e:
            raise Exception(f"ファイル保存エラー: {str(e)}")
    
    def cleanup_temp_file(self, file_path: str):
        """一時ファイルを削除"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                # 親ディレクトリも削除
                parent_dir = os.path.dirname(file_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
        except Exception as e:
            print(f"一時ファイル削除エラー: {e}")


# シングルトンインスタンス
document_service = DocumentService()