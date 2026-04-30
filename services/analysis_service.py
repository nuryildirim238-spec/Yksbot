from database.mongo import db
from datetime import datetime, timedelta

class AnalysisService:
    
    @staticmethod
    async def get_category_average(user_id: int, category: str):
        """
        TYT veya AYT kategorisindeki derslerin ortalama başarısı
        category: "tyt" veya "ayt"
        """
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return None
        
        category_subjects = []
        for subject_name, topics in user["subjects"].items():
            if subject_name.startswith(category):
                if topics:
                    avg = sum(topics.values()) / len(topics)
                    category_subjects.append(avg)
        
        if not category_subjects:
            return None
        
        return round(sum(category_subjects) / len(category_subjects))
    
    @staticmethod
    async def get_subject_average(user_id: int, subject_name: str):
        """Bir dersin ortalama puanı"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user or subject_name not in user["subjects"]:
            return 0
        
        topics = user["subjects"][subject_name]
        if not topics:
            return 0
        
        return round(sum(topics.values()) / len(topics))
    
    @staticmethod
    async def get_subject_averages(user_id: int):
        """Her dersin ortalama puanını hesapla"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return {}
        
        averages = {}
        for subject, topics in user["subjects"].items():
            if topics:
                avg = sum(topics.values()) / len(topics)
                averages[subject] = round(avg)
        
        return averages
    
    @staticmethod
    async def get_weak_topics(user_id: int, threshold: int = 40):
        """Zayıf konuları getir (threshold altı)"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return []
        
        weak = []
        for subject, topics in user["subjects"].items():
            for topic, score in topics.items():
                if score < threshold:
                    weak.append({
                        "subject": subject,
                        "topic": topic,
                        "score": score
                    })
        
        return sorted(weak, key=lambda x: x["score"])
    
    @staticmethod
    async def get_strong_topics(user_id: int, threshold: int = 70):
        """Güçlü konuları getir (threshold üstü)"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return []
        
        strong = []
        for subject, topics in user["subjects"].items():
            for topic, score in topics.items():
                if score >= threshold:
                    strong.append({
                        "subject": subject,
                        "topic": topic,
                        "score": score
                    })
        
        return sorted(strong, key=lambda x: x["score"], reverse=True)
    
    @staticmethod
    async def get_overall_average(user_id: int):
        """Genel ortalama (tüm konular)"""
        averages = await AnalysisService.get_subject_averages(user_id)
        if not averages:
            return 0
        
        total = sum(averages.values())
        return round(total / len(averages))
    
    @staticmethod
    async def get_last_7_days_logs(user_id: int):
        """Son 7 günün günlük loglarını getir"""
        collection = db.get_collection("daily_logs")
        
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor = collection.find({
            "user_id": user_id,
            "date": {"$gte": seven_days_ago}
        }).sort("date", -1)
        
        logs = await cursor.to_list(length=7)
        return logs
