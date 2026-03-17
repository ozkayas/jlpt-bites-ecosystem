# N5 Vocabulary Backend Scriptleri

Bu klasörde 3 script var. Her biri farklı bir işi yapar.

---

## Scriptlere Genel Bakış

| Script | Ne yapar |
|--------|----------|
| `generate_and_upload_audio.py` | TTS ses üretir, Firebase Storage'a yükler, **JSON dosyasındaki** `audioUrl` alanlarını günceller |
| `upload_n5_vocabulary.py` | `n5_vocabulary.json` içeriğini (audioUrl'ler dahil) Firestore'a yazar |
| `upload_vocabulary_index.py` | Flutter uygulaması için hafif bir özet doküman (`vocabulary_meta/n5_vocabulary`) yazar |
| `upload_active_recall_pool.py` | `active_recall_pool.json`'daki checkpoint'leri `n5_active_recall_pool` Firestore collection'ına yükler |
| `add_language_to_pool.py` | Mevcut `n5_active_recall_pool` collection'ına yeni bir UI dili ekler (update, set değil) |

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

Belirtilen JSON dosyasındaki her kelimeyi `n5_vocabulary/{word_id}` dokümanına yazar.

**`--file` parametresi:** Hangi JSON dosyasının yükleneceğini seçer (varsayılan: `n5_vocabulary.json`).
Yeni bir versiyon yüklemek için `--file n5_vocabulary_v01.json` gibi kullanılır.

**`--clear` parametresi:** Yüklemeden önce koleksiyondaki tüm mevcut dokümanları siler.
Tam sıfırlama / versiyon geçişi yapılırken kullanılır.

**`--clear` olmadan davranış:** Yalnızca JSON'daki ID'lere `set()` uygular.
JSON'da olmayan eski Firestore dokümanları olduğu gibi kalır.

**Desteklenen şema (v01+):** `translations` artık `ko` (Korece) içerir; `sentences` altında `furigana` alanı mevcuttur.

```bash
python3 upload_n5_vocabulary.py --dry-run                          # önizle
python3 upload_n5_vocabulary.py                                    # varsayılan dosyayı yükle
python3 upload_n5_vocabulary.py --file n5_vocabulary_v01.json      # belirli versiyonu yükle
python3 upload_n5_vocabulary.py --file n5_vocabulary_v01.json --clear  # sıfırla + yükle
python3 upload_n5_vocabulary.py --tag 動詞                         # sadece fiilleri yükle
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

---

### 4. `upload_active_recall_pool.py`

`active_recall_pool.json`'daki her checkpoint'i `n5_active_recall_pool/{cp_id}` dokümanına yazar.
Dosya 1.1 MB (Firestore 1 MB limiti aşıyor), bu yüzden checkpoint başına bir doküman mimarisi kullanılır (~7 KB/doküman).

**Idempotent:** `set()` kullandığı için tekrar çalıştırmak güvenlidir.

```bash
python3 upload_active_recall_pool.py --dry-run                  # önizle (152 checkpoint)
python3 upload_active_recall_pool.py --checkpoint cp_15         # tek checkpoint test
python3 upload_active_recall_pool.py                            # tümünü yükle
python3 upload_active_recall_pool.py --clear                    # sil + yükle
```

---

### 5. `add_language_to_pool.py`

Mevcut Firestore collection'ına yeni bir UI dili ekler.
Kaynak JSON dosyasındaki yeni dil çevirilerini alıp her checkpoint dokümanına `update()` ile yazar.
Diğer dillere dokunmaz.

```bash
python3 add_language_to_pool.py --lang pt --file active_recall_pool_pt.json --dry-run
python3 add_language_to_pool.py --lang pt --file active_recall_pool_pt.json
python3 add_language_to_pool.py --lang zh --file active_recall_pool.json --checkpoint cp_15
```

---

## Gereksinimler

```bash
pip install firebase-admin gtts
```

`service-account-key.json` dosyası `backend/` klasöründe olmalıdır.
Firebase Console → Project Settings → Service Accounts → Generate New Private Key
