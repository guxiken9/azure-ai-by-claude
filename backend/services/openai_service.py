import os
from typing import List, Dict, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

class AzureOpenAIService:
    def __init__(self):
        """Azure OpenAI サービスの初期化"""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not all([self.api_key, self.endpoint]):
            raise ValueError("Azure OpenAI の認証情報が設定されていません。.env ファイルを確認してください。")
        
        # Azure OpenAI クライアントの初期化
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        # デフォルト設定
        self.default_temperature = 0.7
        self.default_max_tokens = 1000
        self.default_top_p = 0.95
    
    async def get_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        チャットメッセージに対するAIの応答を取得
        
        Args:
            messages: チャット履歴（role と content を含む辞書のリスト）
            temperature: 応答の創造性（0.0-2.0）
            max_tokens: 最大トークン数
            stream: ストリーミング応答を使用するか
            
        Returns:
            AIの応答テキスト
        """
        try:
            # パラメータのデフォルト値設定
            temperature = temperature or self.default_temperature
            max_tokens = max_tokens or self.default_max_tokens
            
            # システムメッセージを確認・追加
            if not messages or messages[0].get("role") != "system":
                system_message = {
                    "role": "system",
                    "content": "あなたは親切で有能なAIアシスタントです。日本語で丁寧に応答してください。"
                }
                messages = [system_message] + messages
            
            # Azure OpenAI APIを呼び出し
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.default_top_p,
                stream=stream
            )
            
            if stream:
                # ストリーミング応答の場合は、ジェネレータを返す
                return response
            else:
                # 通常の応答
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Azure OpenAI API エラー: {str(e)}")
            raise Exception(f"AI応答の取得中にエラーが発生しました: {str(e)}")
    
    async def get_streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        ストリーミング形式でAIの応答を取得
        
        Yields:
            応答のチャンク
        """
        stream = await self.get_chat_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content