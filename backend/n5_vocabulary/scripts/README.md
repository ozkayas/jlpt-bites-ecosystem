# N5 Vocabulary Backend Scriptleri

Bu klasörde 3 script var. Her biri farklı bir işi yapar.

---

## Scriptlere Genel Bakış

| Script | Ne yapar |
|--------|----------|
| `generate_and_upload_audio.py` | TTS ses üretir, Firebase Storage'a yükler, **JSON dosyasındaki** `audioUrl` alanlarını günceller |
| `upload_n5_vocabulary.py` | `n5_vocabulary.json` içeriğini (audioUrl'ler dahil) Firestore'a yazar |
| `upload_vocabulary_index.py` | Flutter uygulaması için hafif bir özet doküman (`vocabulary_meta/n5_vocabulary`) yazar |

---

## Çalıştırma Sırası

```
1. generate_and_upload_audio.py   → ses üret, Storage'a yükle, JSON'daki audioUrl'leri doldur
2. upload_n5_vocabulary.py        → güncel JSON'u (audioUrl'lerle birlikte) Firestore'a yaz
3. upload_vocabulary_index.py     → Flutter index'ini güncelle
```

**Neden bu sıra?**

- `generate_and_upload_audio.py` Firestore'a dokunmaz; sadece ses dosyalarını Storage'a yükler ve kaynak JSON'u günceller.
- `upload_n5_vocabulary.py` JSON'u olduğu gibi Firestore'a yazar — dolayısıyla `audioUrl` alanlarının JSON'da dolu olması için ses scripti önce çalışmalıdır.
- `upload_vocabulary_index.py` her zaman en son çalışır — index Firestore'daki güncel veriyi özetlediği için diğer ikisi bitmeden çalıştırılmamalıdır.

---

## Her Scriptin Detayı

### 1. `generate_and_upload_audio.py`

Her kelime ve cümle için gTTS ile Japonca ses dosyası üretir, Firebase Storage'a yükler,
ardından **`n5_vocabulary.json` dosyasındaki** `audioUrl` alanlarını günceller.

**Firestore'a dokunmaz.** JSON'u günceller, Firestore güncellemesi bir sonraki scriptin işidir.

Varsayılan davranış: Storage'da zaten ses dosyası olan kelimeleri atlar.
`--force` ile mevcut dosyaların üzerine yazılabilir.

**Storage yolları:**
```
sounds/n5_vocabulary/words/{word_id}.mp3
sounds/n5_vocabulary/sentences/{word_id}_s1.mp3
                              {word_id}_s2.mp3
                              {word_id}_s3.mp3
```

```bash
python3 generate_and_upload_audio.py --dry-run        # önizle
python3 generate_and_upload_audio.py                  # tümü
python3 generate_and_upload_audio.py --words-only     # sadece kelimeler
python3 generate_and_upload_audio.py --sentences-only # sadece cümleler
python3 generate_and_upload_audio.py --force          # mevcut seslerin üzerine yaz
```

---

### 2. `upload_n5_vocabulary.py`

`n5_vocabulary.json`'daki her kelimeyi `n5_vocabulary/{word_id}` dokümanına yazar.

**Mevcut Firestore verilerini siler mi?**

Hayır — ama sadece JSON'daki alanlara bakar. `set()` kullanır: JSON'daki tüm alanlar
(audioUrl dahil) Firestore'a yazılır. JSON'da `audioUrl: null` olan bir kelime varsa
Firestore'a da `null` olarak yazılır — bu yüzden ses scriptinin önce çalışması önemlidir.

**JSON'da bulunmayan eski Firestore dokümanları:**
Script yalnızca JSON'daki ID'lere dokunur. JSON'da artık olmayan eski kelimeler
Firestore'da olduğu gibi kalır — otomatik temizleme yapılmaz.

```bash
python3 upload_n5_vocabulary.py --dry-run   # önizle
python3 upload_n5_vocabulary.py             # tümünü yükle
python3 upload_n5_vocabulary.py --tag 動詞  # sadece fiilleri yükle
```

---

### 3. `upload_vocabulary_index.py`

Flutter uygulaması her açıldığında 712 kelimeyi Firestore'dan çekmek yerine tek bir
hafif doküman (`vocabulary_meta/n5_vocabulary`) okur. Bu script o dokümanı oluşturur.

**İçeriği:** Her kelime için sadece `{id, word, reading, tag}` — cümle, çeviri, ses yok.
**Boyutu:** ~20 KB (tam koleksiyon 485 KB'dır)

`vocabulary_meta/n5_vocabulary` dokümanını tamamen overwrite eder.
`n5_vocabulary` koleksiyonuna dokunmaz.

```bash
python3 upload_vocabulary_index.py --dry-run               # önizle
python3 upload_vocabulary_index.py                         # n5 için yükle
python3 upload_vocabulary_index.py --collection n4_vocabulary
```

---

## Gereksinimler

```bash
pip install firebase-admin gtts
```

`service-account-key.json` dosyası `backend/` klasöründe olmalıdır.
Firebase Console → Project Settings → Service Accounts → Generate New Private Key
