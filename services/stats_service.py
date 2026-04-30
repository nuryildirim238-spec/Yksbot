from database.mongo import db
from datetime import datetime

class StatsService:
    
    @staticmethod
    async def add_daily_log(user_id: int, hours: float, questions: int):
        """Günlük çalışma logu ekle"""
        collection = db.get_collection("daily_logs")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        await collection.update_one(
            {"user_id": user_id, "date": today},
            {
                "$set": {
                    "study_hours": hours,
                    "questions": questions,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    @staticmethod
    async def get_today_log(user_id: int):
        """Bugünün logunu getir"""
        collection = db.get_collection("daily_logs")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        return await collection.find_one({"user_id": user_id, "date": today})
    
    @staticmethod
    async def has_daily_entry(user_id: int):
        """Bugün giriş yapılmış mı kontrol et"""
        log = await StatsService.get_today_log(user_id)
        return log is not None
    
    @staticmethod
    async def get_total_stats(user_id: int):
        """Toplam istatistikleri getir"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user:
            return {"total_study_hours": 0, "total_questions": 0, "total_days": 0}
        
        return user.get("stats", {
            "total_study_hours": 0,
            "total_questions": 0,
            "total_days": 0
        })
    
    @staticmethod
    async def get_daily_average(user_id: int):
        """Günlük ortalama çalışma saati"""
        stats = await StatsService.get_total_stats(user_id)
        total_days = stats.get("total_days", 1)
        total_hours = stats.get("total_study_hours", 0)
        
        if total_days == 0:
            return 0
        
        return round(total_hours / total_days, 1)
