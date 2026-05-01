from database.mongo import db
from datetime import datetime, timedelta
from services.subject_service import SubjectService

class AnalysisService:
    
    @staticmethod
    async def get_subject_average(user_id: int, subject_name: str):
        """Bir dersin ortalama puani (tum konular dahil, puansizlar 0)"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return 0
        
        # Kullanicinin bu derste puan verdigi konular
        user_topics = user["subjects"].get(subject_name, {})
        
        # Bu dersin TUM konulari
        all_topics = await SubjectService.get_topics_by_subject(subject_name)
        
        if not all_topics:
            return 0
        
        total_score = 0
        for topic in all_topics:
            score = user_topics.get(topic, 0)  # puan verilmeyen konular 0
            total_score += score
        
        return round(total_score / len(all_topics))
    
    @staticmethod
    async def get_category_average(user_id: int, category: str):
        """TYT veya AYT kategorisindeki derslerin ortalama başarısı"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return None
        
        category_subjects = []
        all_subjects = await SubjectService.get_all_subjects()
        
        for subject in all_subjects:
            subject_name = subject["name"]
            if subject_name.startswith(category):
                avg = await AnalysisService.get_subject_average(user_id, subject_name)
                category_subjects.append(avg)
        
        if not category_subjects:
            return None
        
        return round(sum(category_subjects) / len(category_subjects))
    
    @staticmethod
    async def get_subject_averages(user_id: int):
        """Her dersin ortalama puanını hesapla"""
        all_subjects = await SubjectService.get_all_subjects()
        averages = {}
        
        for subject in all_subjects:
            subject_name = subject["name"]
            avg = await AnalysisService.get_subject_average(user_id, subject_name)
            averages[subject_name] = avg
        
        return averages
    
    @staticmethod
    async def get_weak_topics(user_id: int, threshold: int = 40):
        """Zayif konulari getir (puan verilmeyenler de zayif sayilir)"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return []
        
        weak = []
        all_subjects = await SubjectService.get_all_subjects()
        
        for subject in all_subjects:
            subject_name = subject["name"]
            user_topics = user["subjects"].get(subject_name, {})
            
            for topic in subject["topics"]:
                score = user_topics.get(topic, 0)  # puan verilmeyen 0
                if score < threshold:
                    weak.append({
                        "subject": subject_name,
                        "topic": topic,
                        "score": score
                    })
        
        return sorted(weak, key=lambda x: x["score"])
    
    @staticmethod
    async def get_strong_topics(user_id: int, threshold: int = 70):
        """Guclu konulari getir"""
        user = await db.get_collection("users").find_one({"user_id": user_id})
        if not user or "subjects" not in user:
            return []
        
        strong = []
        all_subjects = await SubjectService.get_all_subjects()
        
        for subject in all_subjects:
            subject_name = subject["name"]
            user_topics = user["subjects"].get(subject_name, {})
            
            for topic in subject["topics"]:
                score = user_topics.get(topic, 0)
                if score >= threshold:
                    strong.append({
                        "subject": subject_name,
                        "topic": topic,
                        "score": score
                    })
        
        return sorted(strong, key=lambda x: x["score"], reverse=True)
    
    @staticmethod
    async def get_overall_average(user_id: int):
        """Genel ortalama (tum dersler)"""
        averages = await AnalysisService.get_subject_averages(user_id)
        if not averages:
            return 0
        
        total = sum(averages.values())
        return round(total / len(averages))
    
    @staticmethod
    async def get_last_7_days_logs(user_id: int):
        """Son 7 gunun gunluk loglarini getir"""
        collection = db.get_collection("daily_logs")
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor = collection.find({
            "user_id": user_id,
            "date": {"$gte": seven_days_ago}
        }).sort("date", -1)
        logs = await cursor.to_list(length=7)
        return logs
