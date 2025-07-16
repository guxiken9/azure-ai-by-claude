"""
文書管理のAPIエンドポイント
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os

from services.document_service import document_service
from services.vector_db_service import vector_db_service

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """文書をアップロードしてベクトルDBに保存"""
    try:
        # ファイルの検証
        validation = document_service.validate_file(file.filename, file.size)
        if not validation['valid']:
            raise HTTPException(status_code=400, detail=validation['error'])
        
        # ファイルを一時保存
        file_content = await file.read()
        temp_file_path = await document_service.save_uploaded_file(file_content, file.filename)
        
        try:
            # 文書を処理してテキストを抽出
            result = await document_service.process_document(temp_file_path, file.filename)
            
            if result['status'] == 'error':
                raise HTTPException(status_code=400, detail=result['error'])
            
            # ベクトルDBに保存
            db_result = await vector_db_service.add_document(
                content=result['text'],
                metadata=result['metadata']
            )
            
            if db_result['status'] == 'error':
                raise HTTPException(status_code=500, detail=db_result['message'])
            
            return JSONResponse(content={
                "status": "success",
                "message": f"文書「{file.filename}」をアップロードしました",
                "chunks": db_result['chunks_added']
            })
            
        finally:
            # 一時ファイルをクリーンアップ
            document_service.cleanup_temp_file(temp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アップロードエラー: {str(e)}")


@router.get("/list")
async def list_documents():
    """保存されている文書の一覧を取得"""
    try:
        documents = vector_db_service.list_documents()
        return JSONResponse(content={
            "status": "success",
            "documents": documents
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"一覧取得エラー: {str(e)}")


@router.delete("/{document_name}")
async def delete_document(document_name: str):
    """文書を削除"""
    try:
        success = vector_db_service.delete_document(document_name)
        if success:
            return JSONResponse(content={
                "status": "success",
                "message": f"文書「{document_name}」を削除しました"
            })
        else:
            raise HTTPException(status_code=404, detail="文書が見つかりません")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"削除エラー: {str(e)}")


@router.post("/search")
async def search_documents(query: dict):
    """文書を検索"""
    try:
        search_query = query.get("query", "")
        n_results = query.get("n_results", 5)
        
        if not search_query:
            raise HTTPException(status_code=400, detail="検索クエリが必要です")
        
        results = await vector_db_service.search(search_query, n_results)
        
        return JSONResponse(content={
            "status": "success",
            "results": results
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")


@router.post("/reset")
async def reset_database():
    """データベースをリセット（開発用）"""
    try:
        # 開発環境でのみ有効
        if os.getenv("ENV", "development") != "development":
            raise HTTPException(status_code=403, detail="本番環境ではリセットできません")
        
        success = vector_db_service.reset_database()
        if success:
            return JSONResponse(content={
                "status": "success",
                "message": "データベースをリセットしました"
            })
        else:
            raise HTTPException(status_code=500, detail="リセットに失敗しました")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"リセットエラー: {str(e)}")