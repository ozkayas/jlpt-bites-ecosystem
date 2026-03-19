# Listening Module — Claude Kuralları ve Teknik Notlar

## İmaj Üretimi (Imagen / Gemini)

### Aktif Model

**`imagen-4.0-fast-generate-001`** — tüm skill'lerde bu kullanılmalı.

```python
response = client.models.generate_images(
    model='imagen-4.0-fast-generate-001',
    ...
)
```

### Model Karşılaştırması (Mart 2026)

#### Imagen 4 Ailesi (`/docs/imagen`)
Text-to-image, bağımsız API. Sadece İngilizce prompt, max 480 token.

| Model | Fiyat/İmaj | Not |
|-------|-----------|-----|
| `imagen-4.0-fast-generate-001` | **$0.02** | ✅ Aktif kullanım |
| `imagen-4.0-generate-001` | $0.04 | Gereksiz yere pahalı |
| `imagen-4.0-ultra-generate-001` | $0.06 | JLPT için gereğinden yüksek kalite |

#### Gemini Native Image (`/docs/image-generation`)
Metin + imaj birlikte üretir, sohbet tabanlı, çok dilli.

| Model | Fiyat/İmaj (1K) | Not |
|-------|----------------|-----|
| `gemini-2.5-flash-image` | $0.039 | Preview |
| `gemini-3.1-flash-image-preview` | $0.067 | Preview |
| `gemini-3-pro-image-preview` | $0.134 | Preview |

### Önemli Notlar
- **Imagen 3 tamamen kapatıldı.** `imagen-3.0-generate-002` ve `imagen-3.0-generate-001` artık çalışmıyor.
- **Free tier yok.** Tüm modeller ilk istekten itibaren ücretlidir.
- Kota proje bazlıdır — birden fazla API anahtarı limiti artırmaz.
- Kota her gece yarısı (Pacific time) sıfırlanır.
- Imagen 4 Standard'ın günlük kotası 70 istek/gün (paid tier 1).
- İmaj üretim hataları: büyük dosya (>700 KB) döndüyse muhtemelen yanlış içerik (fotoğraf, hayvan) — tekrar dene.

### Tercih Nedeni
- `imagen-4.0-fast-generate-001`: $0.02/imaj, JLPT manga çizimleri için kalite yeterli, Imagen 4 Standard'ın yarı fiyatı.
- Gemini Native modeller henüz preview aşamasında ve fiyatlandırması karmaşık (token bazlı).

---

## selectAudio İmaj Stili (ZORUNLU)

Tüm JLPT N5 selectAudio imajlarında **manga stili** kullanılmalı:

```
Simple manga-style line drawing, black and white.
[sahne tanımı]
Cartoon style with simple round faces, clean outlines, white background,
no shading, no color, no text, no arrows.
Same style as JLPT N5 textbook manga illustrations.
```

**Kesinlikle kullanma:** `JLPT exam textbook line drawing` → gerçekçi/Batılı yüzler üretiyor.

**Her zaman ekle:** `simple round head`, `Cartoon style with simple round faces`

---

## TTS Sesleri

| Rol | Voice ID | Gemini Ses |
|-----|----------|-----------|
| Narrator (intro + question) | `Intro_Voice` | Kore |
| Erkek karakter | `Male_1` | Puck |
| Kadın karakter | `Female_1` | Zephyr |

---

## API Anahtarları

- `JLPT_IMAGE_GEMINI_API_KEY` → Imagen 4 imaj üretimi
- `GEMINI_API_KEY` / `GEMINI_API_KEYS` → TTS ses üretimi (4 anahtar, rate limit rotation)
