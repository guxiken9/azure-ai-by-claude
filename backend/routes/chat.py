from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import Optional
import logging
import json
import markdown

from services.openai_service import AzureOpenAIService
from services.session_service import session_service

# ロガーの設定
logger = logging.getLogger(__name__)

# ルーターの初期化
router = APIRouter()

# Azure OpenAI サービスのインスタンス
openai_service = AzureOpenAIService()

# Markdownパーサーの設定
md = markdown.Markdown(extensions=['fenced_code', 'tables'])

@router.post("/chat", response_class=HTMLResponse)
async def chat(
    request: Request,
    message: str = Form(...),
    session_id: Optional[str] = Form(None)
):
    """
    チャットエンドポイント
    
    Args:
        request: FastAPIリクエストオブジェクト
        message: ユーザーからのメッセージ
        session_id: セッションID（オプション）
        
    Returns:
        HTMXで更新されるHTMLフラグメント
    """
    try:
        # セッションの取得または作成
        if not session_id or not session_service.get_session(session_id):
            session_id = session_service.create_session()
            logger.info(f"新しいセッションを作成: {session_id}")
        
        # ユーザーメッセージをセッションに追加
        session_service.add_message(session_id, "user", message)
        
        # 会話履歴を取得（最新の10メッセージ）
        messages = session_service.get_messages(session_id, limit=20)
        
        # Azure OpenAI APIを呼び出し
        ai_response = await openai_service.get_chat_response(messages)
        
        # AIの応答をセッションに追加
        session_service.add_message(session_id, "assistant", ai_response)
        
        # Markdown形式のレスポンスをHTMLに変換
        html_content = md.convert(ai_response)
        
        # HTMXレスポンスを生成
        response_html = f"""
        <div class="chat-message assistant-message">
            <div class="message-header">AI</div>
            <div class="message-content">{html_content}</div>
        </div>
        <input type="hidden" name="session_id" value="{session_id}" />
        """
        
        return response_html
        
    except Exception as e:
        logger.error(f"チャット処理中にエラー: {str(e)}")
        error_html = f"""
        <div class="chat-message error-message">
            <div class="message-header">エラー</div>
            <div class="message-content">申し訳ございません。エラーが発生しました: {str(e)}</div>
        </div>
        """
        return error_html

@router.post("/chat/stream")
async def chat_stream(
    request: Request,
    message: str = Form(...),
    session_id: Optional[str] = Form(None)
):
    """
    ストリーミング形式のチャットエンドポイント
    
    Args:
        request: FastAPIリクエストオブジェクト
        message: ユーザーからのメッセージ
        session_id: セッションID（オプション）
        
    Returns:
        Server-Sent Events形式のストリーミングレスポンス
    """
    try:
        # セッションの取得または作成
        if not session_id or not session_service.get_session(session_id):
            session_id = session_service.create_session()
        
        # ユーザーメッセージをセッションに追加
        session_service.add_message(session_id, "user", message)
        
        # 会話履歴を取得
        messages = session_service.get_messages(session_id, limit=20)
        
        async def generate():
            """SSE形式でレスポンスを生成"""
            full_response = ""
            
            try:
                # 初期イベント：セッションIDを送信
                yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
                
                # ストリーミングレスポンスを取得
                async for chunk in openai_service.get_streaming_response(messages):
                    full_response += chunk
                    # チャンクをSSE形式で送信
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # 完了イベント
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
                # 完全なレスポンスをセッションに保存
                session_service.add_message(session_id, "assistant", full_response)
                
            except Exception as e:
                logger.error(f"ストリーミング中にエラー: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        logger.error(f"ストリーミングチャット処理中にエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    セッション情報を取得（デバッグ用）
    
    Args:
        session_id: セッションID
        
    Returns:
        セッション情報
    """
    session_info = session_service.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    return session_info

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    セッションを削除
    
    Args:
        session_id: セッションID
        
    Returns:
        削除結果
    """
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    return {"message": "セッションを削除しました", "session_id": session_id}