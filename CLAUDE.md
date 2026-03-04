# JLPT Bites Ecosystem — Claude Kuralları

## Zorunlu: Değişiklik Günlüğü ve Yetenek Belgelendirmesi

**1. Bir modülde iş bittiğinde, konuşmayı kapatmadan önce ilgili log dosyasına giriş ekle.**

**2. Yeni bir Agent Skill oluşturulduğunda, ilgili modülün ana README.md dosyasına yetenek bilgilerini ekle.**

### Yetenek Belgelendirme Yapısı
Eğer bir modüle (`backend/listening` gibi) yeni bir yetenek eklendiyse, o modülün `README.md` dosyasına şu formatta ekle:
```markdown
### Kullanılabilir Agent Yetenekleri (Skills)
- `yetenek-adi`: Kısa açıklama.
```

### Log Yapısı

```
logs/
  backend/
    time_trainer/CHANGELOG.md
    listening/CHANGELOG.md
    reading/CHANGELOG.md
    n5_vocabulary/CHANGELOG.md
    ...
  (yeni modül eklenince logs/ altında aynı hiyerarşiyi oluştur)
```

### Giriş Formatı

```markdown
## YYYY-MM-DD

### Kısa başlık

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `path/to/file` | YENİ / DEĞİŞTİRİLDİ / SİLİNDİ | Ne yaptığı |

**Yapılanlar:**
- Madde madde özet

**Bağlam:** (isteğe bağlı — neden yapıldı)
```

### Kural

- Her konuşma sonunda, en az bir dosya değiştirildiyse log ekle
- Log dosyası yoksa oluştur (`logs/{modül_yolu}/CHANGELOG.md`)
- Tarih formatı: `YYYY-MM-DD`
- Aynı günde birden fazla değişiklik varsa aynı `## YYYY-MM-DD` başlığı altında alt bölümler aç
