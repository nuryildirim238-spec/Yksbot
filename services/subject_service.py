from database.mongo import db

class SubjectService:
    
    @staticmethod
    async def init_default_subjects():
        """Eğer subjects collection boşsa default verileri ekle"""
        collection = db.get_collection("subjects")
        
        # Collection boş mu kontrol et
        count = await collection.count_documents({})
        
        if count == 0:
            default_subjects = [
                {"name": "matematik", "topics": ["problemler", "fonksiyonlar", "geometri"]},
                {"name": "turkce", "topics": ["paragraf", "dil_bilgisi"]},
                {"name": "fen", "topics": ["fizik", "kimya", "biyoloji"]}
            ]
            
            await collection.insert_many(default_subjects)
            print("✅ Default ders ve konular eklendi")
    
    @staticmethod
    async def get_all_subjects():
        """Tüm dersleri getir"""
        collection = db.get_collection("subjects")
        cursor = collection.find({})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def get_topics_by_subject(subject_name: str):
        """Bir dersin konularını getir"""
        collection = db.get_collection("subjects")
        subject = await collection.find_one({"name": subject_name})
        
        if subject:
            return subject.get("topics", [])
        return []
    
    @staticmethod
    async def subject_exists(subject_name: str):
        """Ders var mı kontrol et"""
        collection = db.get_collection("subjects")
        subject = await collection.find_one({"name": subject_name})
        return subject is not None
    
    @staticmethod
    async def add_subject(name: str, topics: list):
        """Yeni ders ekle (genişletilebilirlik)"""
        collection = db.get_collection("subjects")
        await collection.insert_one({"name": name, "topics": topics})
    
    @staticmethod
    async def add_topic_to_subject(subject_name: str, topic: str):
        """Derse yeni konu ekle"""
        collection = db.get_collection("subjects")
        await collection.update_one(
            {"name": subject_name},
            {"$addToSet": {"topics": topic}}
      )
