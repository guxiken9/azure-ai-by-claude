from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
import json
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self, session_timeout_minutes: int = 30):
        """
        セッション管理サービスの初期化
        
        Args:
            session_timeout_minutes: セッションのタイムアウト時間（分）
        """
        # メモリ内でセッションを管理
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        
        # 定期的なクリーンアップタスクを開始
        asyncio.create_task(self._cleanup_expired_sessions())
    
    def create_session(self) -> str:
        """
        新しいセッションを作成
        
        Returns:
            セッションID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "messages": [],
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "metadata": {}
        }
        logger.info(f"新しいセッションを作成: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        セッション情報を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            セッション情報、存在しない場合はNone
        """
        session = self.sessions.get(session_id)
        if session:
            # 最終アクセス時刻を更新
            session["last_accessed"] = datetime.now()
            
            # セッションの有効期限をチェック
            if self._is_session_expired(session):
                self.delete_session(session_id)
                return None
                
        return session
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        セッションにメッセージを追加
        
        Args:
            session_id: セッションID
            role: メッセージの役割（user, assistant, system）
            content: メッセージ内容
            
        Returns:
            追加に成功した場合True
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session["messages"].append(message)
        logger.debug(f"セッション {session_id} にメッセージを追加: {role}")
        return True
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        セッションのメッセージ履歴を取得
        
        Args:
            session_id: セッションID
            limit: 取得するメッセージ数の上限
            
        Returns:
            メッセージのリスト
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session["messages"]
        
        # APIに送信する形式に変換（timestampを除外）
        api_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        if limit:
            return api_messages[-limit:]
        return api_messages
    
    def delete_session(self, session_id: str) -> bool:
        """
        セッションを削除
        
        Args:
            session_id: セッションID
            
        Returns:
            削除に成功した場合True
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"セッションを削除: {session_id}")
            return True
        return False
    
    def update_metadata(self, session_id: str, metadata: Dict) -> bool:
        """
        セッションのメタデータを更新
        
        Args:
            session_id: セッションID
            metadata: 更新するメタデータ
            
        Returns:
            更新に成功した場合True
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session["metadata"].update(metadata)
        return True
    
    def _is_session_expired(self, session: Dict) -> bool:
        """
        セッションが期限切れかチェック
        
        Args:
            session: セッション情報
            
        Returns:
            期限切れの場合True
        """
        last_accessed = session.get("last_accessed", session["created_at"])
        return datetime.now() - last_accessed > self.session_timeout
    
    async def _cleanup_expired_sessions(self):
        """
        期限切れセッションを定期的にクリーンアップ
        """
        while True:
            try:
                # 10分ごとにクリーンアップを実行
                await asyncio.sleep(600)
                
                expired_sessions = []
                for session_id, session in self.sessions.items():
                    if self._is_session_expired(session):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    self.delete_session(session_id)
                
                if expired_sessions:
                    logger.info(f"{len(expired_sessions)} 個の期限切れセッションを削除")
                    
            except Exception as e:
                logger.error(f"セッションクリーンアップ中にエラー: {str(e)}")
    
    def get_active_sessions_count(self) -> int:
        """アクティブなセッション数を取得"""
        return len(self.sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        セッションの詳細情報を取得（デバッグ用）
        
        Args:
            session_id: セッションID
            
        Returns:
            セッションの詳細情報
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "id": session["id"],
            "created_at": session["created_at"].isoformat(),
            "last_accessed": session["last_accessed"].isoformat(),
            "message_count": len(session["messages"]),
            "metadata": session["metadata"]
        }

# グローバルインスタンス
session_service = SessionService()