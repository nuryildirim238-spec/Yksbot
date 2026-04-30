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
                # ========== TYT ==========
                {
                    "name": "tyt_matematik",
                    "display_name": "📐 TYT Matematik",
                    "topics": ["temel kavramlar", "sayı basamakları", "bölme bölünebilme", "ebob ekok", "rasyonel sayılar", "basit eşitsizlikler", "mutlak değer", "üslü sayılar", "köklü sayılar", "çarpanlara ayırma", "oran orantı", "denklem çözme", "problemler", "yüzde kâr zarar", "faiz problemleri", "karışım problemleri", "sayı problemleri", "kesir problemleri"]
                },
                {
                    "name": "tyt_geometri",
                    "display_name": "📐 TYT Geometri",
                    "topics": ["doğruda açı", "üçgende açı", "üçgende alan", "dik üçgen", "ikizkenar eşkenar üçgen", "üçgende kenarortay", "üçgende açıortay", "üçgende yükseklik", "çokgenler", "dörtgenler", "çember ve daire", "noktanın analitiği", "doğrunun analitiği"]
                },
                {
                    "name": "tyt_turkce",
                    "display_name": "📖 TYT Türkçe",
                    "topics": ["ses bilgisi", "yazım kuralları", "noktalama işaretleri", "sözcükte anlam", "cümlede anlam", "paragrafta anlam", "paragrafın yapısı", "anlatım biçimleri", "sözcük türleri", "fiiller", "ekler", "cümle türleri", "cümlenin öğeleri", "anlatım bozuklukları"]
                },
                {
                    "name": "tyt_fizik",
                    "display_name": "⚡ TYT Fizik",
                    "topics": ["fizik bilimine giriş", "madde ve özellikleri", "basınç", "kaldırma kuvveti", "ısı ve sıcaklık", "hareket", "kuvvet ve hareket", "newton'un hareket yasaları", "iş-güç-enerji", "itme ve momentum", "elektrostatik", "elektrik akımı"]
                },
                {
                    "name": "tyt_kimya",
                    "display_name": "🧪 TYT Kimya",
                    "topics": ["kimya bilimi", "atom ve periyodik sistem", "kimyasal türler", "kimyasal hesaplamalar (mol)", "kimyasal tepkimeler", "asit-baz", "tuzlar", "çözeltiler", "kimyasal denge", "gazlar"]
                },
                {
                    "name": "tyt_biyoloji",
                    "display_name": "🧬 TYT Biyoloji",
                    "topics": ["canlıların ortak özellikleri", "inorganik maddeler", "organik maddeler", "enzimler", "vitaminler", "nükleik asitler", "hücre yapısı", "hücre bölünmeleri", "kalıtım", "ekosistem ekolojisi"]
                },
                {
                    "name": "tyt_tarih",
                    "display_name": "📜 TYT Tarih",
                    "topics": ["tarih bilimi", "uygarlıkların doğuşu", "anadolu uygarlıkları", "ilk türk devletleri", "isl. öncesi türk devletleri", "isl. sonrası türk devletleri", "osmanlı kuruluş", "osmanlı yükselme", "osmanlı duraklama-gerileme", "yenileşme dönemi", "birinci dünya savaşı", "milli mücadele", "ataturk ilkeleri"]
                },
                {
                    "name": "tyt_cografya",
                    "display_name": "🌍 TYT Coğrafya",
                    "topics": ["coğrafya bilimi", "dünyanın şekli ve hareketleri", "harita bilgisi", "koordinat sistemi", "türkiye'nin konumu", "iklim bilgisi", "türkiye'de iklim", "akarsular", "göller", "denizler", "türkiye'nin toprakları", "doğal afetler", "nüfus", "ekonomik faaliyetler"]
                },
                {
                    "name": "tyt_felsefe",
                    "display_name": "💭 TYT Felsefe",
                    "topics": ["felsefenin tanımı", "bilgi felsefesi", "varlık felsefesi", "ahlak felsefesi", "sanat felsefesi", "siyaset felsefesi", "bilim felsefesi", "felsefe tarihi"]
                },
                # ========== AYT ==========
                {
                    "name": "ayt_matematik",
                    "display_name": "🔢 AYT Matematik",
                    "topics": ["fonksiyonlar", "polinomlar", "parabol", "trigonometri", "logaritma", "diziler", "limit", "türev", "integral", "olasılık", "permütasyon", "kombinasyon", "binom", "matrisler", "determinant", "karmaşık sayılar"]
                },
                {
                    "name": "ayt_geometri",
                    "display_name": "📏 AYT Geometri",
                    "topics": ["yamuk", "paralelkenar", "eşkenar dörtgen", "dikdörtgen", "kare", "deltoid", "çember ve daire", "katı cisimler", "prizmalar", "piramitler", "koni", "küre", "dönüşüm geometrisi", "vektörler"]
                },
                {
                    "name": "ayt_edebiyat",
                    "display_name": "📚 AYT Edebiyat",
                    "topics": ["güzel sanatlar", "edebiyat-din ilişkisi", "türk edebiyatının dönemleri", "islamiyet öncesi türk edebiyatı", "islami dönem türk edebiyatı", "halk edebiyatı", "divan edebiyatı", "batı etkisinde türk edebiyatı", "milli edebiyat", "cumhuriyet dönemi edebiyatı", "şiir bilgileri", "nesir bilgileri", "edebi akımlar"]
                },
                {
                    "name": "ayt_fizik",
                    "display_name": "⚛️ AYT Fizik",
                    "topics": ["tork", "basit makineler", "manyetizma", "indüksiyon", "alternatif akım", "transformatörler", "dalgalar", "girişim-kırınım", "optik", "kuantum fiziği", "modern fizik", "görelilik", "atom fiziği", "radyoaktivite"]
                },
                {
                    "name": "ayt_kimya",
                    "display_name": "🧪 AYT Kimya",
                    "topics": ["kimyasal tepkimelerde hız", "kimyasal tepkimelerde denge", "sulu çözelti dengeleri", "elektrokimya", "organik kimya", "aldehitler-ketonlar", "esterler-yağlar", "aminler-amidler", "polimerler"]
                },
                {
                    "name": "ayt_biyoloji",
                    "display_name": "🧬 AYT Biyoloji",
                    "topics": ["nükleik asitlerin keşfi", "genetik mühendisliği", "protein sentezi", "endokrin sistem", "duyu organları", "sinir sistemi", "destek-hareket sistemi", "bitki biyolojisi", "insanda üreme", "bitkilerde üreme", "bağışıklık sistemi", "çevre sorunları", "evrim"]
                },
                {
                    "name": "ayt_sosyal1_tarih",
                    "display_name": "🏛️ AYT Tarih-1",
                    "topics": ["osmanlı kültür ve medeniyeti", "osmanlıda yenileşme", "tanzimat", "birinci dünya savaşı", "milli mücadele", "misak-ı milli", "tbmm", "kurtuluş savaşı", "cumhuriyetin ilanı", "ataturk ilkeleri", "ataturk dış politikası"]
                },
                {
                    "name": "ayt_sosyal1_cografya",
                    "display_name": "🗺️ AYT Coğrafya-1",
                    "topics": ["türkiye'nin yeryüzü şekilleri", "türkiye'de dış kuvvetler", "türkiye'nin iklimi", "türkiye'nin bitki örtüsü", "türkiye'de nüfus", "türkiye'de göçler", "türkiye'de yerleşme", "türkiye'de tarım", "türkiye'de hayvancılık", "türkiye'de madencilik", "türkiye'de sanayi", "türkiye'de ulaşım"]
                },
                {
                    "name": "ayt_sosyal2_felsefe",
                    "display_name": "🧠 AYT Felsefe",
                    "topics": ["psikoloji", "sosyoloji", "mantık", "bilgi felsefesi"]
                },
                {
                    "name": "ayt_sosyal2_din",
                    "display_name": "🕌 AYT Din Kültürü",
                    "topics": ["islam ve bilgi", "islam ve ibadet", "islam ve ahlak", "kelam ilmi", "hristiyanlık", "yahudilik", "diğer dinler", "din ve hoşgörü", "islam düşüncesinde yorumlar"]
                }
            ]
            
            await collection.insert_many(default_subjects)
            print("✅ TYT & AYT ders ve konular eklendi")
    
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
