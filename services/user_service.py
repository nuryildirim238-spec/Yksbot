from datetime import datetime
from database.mongo import db

class UserService:
    
    @staticmethod
    async def register_or_update(user_id: int, name: str):
        """Kullanıcı kaydı veya güncelleme (upsert)"""
        collection = db.get_collection("users")
        
        await collection.update_one(
            {"user_id": user_id},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "name": name,
                    "created_at": datetime.utcnow(),
                    "is_active": True,
                    "subjects": {},
                    "stats": {
                        "total_study_hours": 0,
                        "total_questions": 0,
                        "total_days": 0
                    }
                }
            },
            upsert=True
        )
    
    @staticmethod
    async def get_user(user_id: int):
        """Kullanıcı bilgilerini getir"""
        collection = db.get_collection("users")
        return await collection.find_one({"user_id": user_id, "is_active": True})
    
    @staticmethod
    async def update_subject_score(user_id: int, subject: str, topic: str, score: int):
        """Konu puanını güncelle"""
        collection = db.get_collection("users")
        
        await collection.update_one(
            {"user_id": user_id},
            {"$set": {f"subjects.{subject}.{topic}": score}}
        )
    
    @staticmethod
    async def update_stats(user_id: int, hours: float, questions: int):
        """İstatistikleri güncelle"""
        collection = db.get_collection("users")
        
        await collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "stats.total_study_hours": hours,
                    "stats.total_questions": questions,
                    "stats.total_days": 1
                }
            }
        )
    
    @staticmethod
    async def soft_delete_user(user_id: int):
        """Soft delete - kullanıcıyı devre dışı bırak"""
        collection = db.get_collection("users")
        
        await collection.update_one(
            {"user_id": user_id},
            {"$set": {"is_active": False}}
        )
