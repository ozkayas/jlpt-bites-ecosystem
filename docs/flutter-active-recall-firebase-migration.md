# Flutter — Active Recall: Assets → Firestore Geçişi

## Özet

`active_recall_pool.json` artık Firebase Firestore'da (`n5_active_recall_pool` collection).
Uygulamada yapılacak tek iş: assets'ten okuyan `AssetActiveRecallService`'i, Firestore'dan okuyan yeni bir implementasyonla değiştirmek.

Mevcut interface, BLoC, repository ve view'a **dokunmana gerek yok**.

---

## Firestore Yapısı

```
Collection: n5_active_recall_pool
  Document: cp_15
  Document: cp_20
  Document: cp_25
  ...
  Document: cp_770   (toplam 152 doküman)
```

### Doküman Şeması (`cp_15` örneği)

```json
{
  "id": "cp_15",
  "learned_word_count": 15,
  "uploaded_at": "2026-03-14T...",
  "sentences": [
    {
      "id": "cp15_s1",
      "prompts": {
        "tr": "Hangisi?",
        "en": "Which one?",
        "de": "Welches?",
        "es": "¿Cuál?",
        "fr": "Lequel ?",
        "ko": "어느 것입니까?"
      },
      "japanese_target": "どれですか。",
      "grammar_hints": {
        "tr": "Basit soru kalıbı: ___ですか。 ...",
        "en": "Simple question pattern: ___ですか。 ...",
        "de": "...",
        "es": "...",
        "fr": "...",
        "ko": "..."
      }
    },
    ...  // toplam 5 cümle
  ]
}
```

**Mevcut Dart modelleriyle birebir uyumlu** — alan isimleri aynı (`learned_word_count`, `japanese_target`, `grammar_hints`).

---

## Yapılacak Değişiklikler

### Adım 1 — `FirestoreActiveRecallService` oluştur

**Dosya:** `packages/vocabulary_srs/lib/src/data/services/active_recall_service.dart`

Mevcut `AssetActiveRecallService`'in yanına yeni bir implementasyon ekle:

```dart
import 'package:cloud_firestore/cloud_firestore.dart';

class FirestoreActiveRecallService implements ActiveRecallService {
  final FirebaseFirestore _firestore;

  FirestoreActiveRecallService({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  @override
  Future<ActiveRecallPool> loadPool() async {
    final snapshot = await _firestore
        .collection('n5_active_recall_pool')
        .orderBy('learned_word_count')
        .get();

    final checkpoints = snapshot.docs
        .map((doc) => ActiveRecallCheckpoint.fromMap(doc.data()))
        .toList();

    return ActiveRecallPool(checkpoints: checkpoints);
  }
}
```

> `orderBy('learned_word_count')` — checkpoint'lerin kelime sayısına göre sıralı gelmesini garantiler.

---

### Adım 2 — `fromMap` metodlarını kontrol et

**Dosya:** `packages/vocabulary_srs/lib/src/data/models/active_recall_models.dart`

`ActiveRecallCheckpoint.fromMap()` ve `ActiveRecallSentence.fromMap()` zaten varsa ve alan isimlerini (`learned_word_count`, `japanese_target`, `grammar_hints`) doğru parse ediyorsa **değişiklik gerekmez**.

Kontrol edilecek noktalar:
- `sentences` alanı `List<dynamic>` olarak gelir → `List<ActiveRecallSentence>` cast'i olmalı
- `uploaded_at` alanı modelde yoksa görmezden gel (Firestore'a özgü metadata)

Örnek (zaten varsa dokunma):
```dart
factory ActiveRecallCheckpoint.fromMap(Map<String, dynamic> map) {
  return ActiveRecallCheckpoint(
    id: map['id'] as String,
    learnedWordCount: map['learned_word_count'] as int,
    sentences: (map['sentences'] as List<dynamic>)
        .map((s) => ActiveRecallSentence.fromMap(s as Map<String, dynamic>))
        .toList(),
  );
}
```

---

### Adım 3 — DI / servis kaydını güncelle

**Dosya:** `lib/features/home/home_page.dart`

Şu an:
```dart
activeRecallAssetPath: 'assets/data/vocabulary/active_recall_pool.json',
```

Bu parametre `VocabularyPage`'e geçiriliyor ve içeride `AssetActiveRecallService` oluşturuluyor.

**`VocabularyPage`'in `ActiveRecallService` kabul ettiği yere bak.**
Eğer `AssetActiveRecallService`'i doğrudan `VocabularyPage` içinde oluşturuyorsa, oraya `FirestoreActiveRecallService` geçir:

```dart
// Eski
activeRecallAssetPath: 'assets/data/vocabulary/active_recall_pool.json',

// Yeni — VocabularyPage'e servis doğrudan geçiriliyorsa:
activeRecallService: FirestoreActiveRecallService(),
```

Eğer `VocabularyPage` constructor'ı sadece `assetPath` kabul ediyorsa, şu iki seçenek var:

**Seçenek A — Constructor'ı genişlet (önerilen):**
```dart
// VocabularyPage constructor'ına ekle
final ActiveRecallService? activeRecallService;

// İçeride:
final service = widget.activeRecallService
    ?? AssetActiveRecallService(assetPath: widget.activeRecallAssetPath!);
```

**Seçenek B — `AssetActiveRecallService` kullanımını doğrudan değiştir:**
`VocabularyPage` veya `ActiveRecallRepository` içinde `AssetActiveRecallService` nerede instantiate ediliyorsa orada `FirestoreActiveRecallService()` ile değiştir.

---

### Adım 4 — Cache davranışı (isteğe bağlı ama önerilir)

`ActiveRecallRepository`'de zaten cache var. Firestore geçişi sonrası:

- **İlk açılış:** Firestore'dan çeker, cache'e yazar
- **Sonraki açılışlar:** Cache geçerliyse Firestore'a gitmez

Ekstra olarak Firestore offline persistence açıksa (varsayılan olarak açık) uygulama offline'da da çalışır.

---

## Seçici Okuma (Gelecek Optimizasyon)

Tüm 152 checkpoint'i tek seferde çekmek yerine, sadece gerekli checkpoint'i çek:

```dart
// Sadece cp_30'u getir
final doc = await FirebaseFirestore.instance
    .collection('n5_active_recall_pool')
    .doc('cp_30')
    .get();

final checkpoint = ActiveRecallCheckpoint.fromMap(doc.data()!);
```

Bu, kullanıcı 30 kelime öğrendiğinde tetiklenecek checkpoint için yeterli.
Şu an için tüm pool'u çekmek de sorunsuz çalışır (~1.1 MB, 152 doküman × ~7 KB).

---

## Assets Temizliği (Opsiyonel, Sonraya Bırakılabilir)

Firebase geçişi stabil olduktan sonra:

1. `pubspec.yaml`'dan kaldır:
   ```yaml
   # Kaldır:
   - assets/data/vocabulary/active_recall_pool.json
   ```
2. `assets/data/vocabulary/active_recall_pool.json` dosyasını sil
3. `AssetActiveRecallService` kullanımlarını temizle

> Geçiş dönemi için her ikisini de tutabilirsin — assets fallback olarak çalışır.

---

## Özet Değişiklik Tablosu

| Dosya | Aksiyon | Ne yapılacak |
|-------|---------|--------------|
| `packages/vocabulary_srs/lib/src/data/services/active_recall_service.dart` | DEĞİŞTİR | `FirestoreActiveRecallService` sınıfı ekle |
| `packages/vocabulary_srs/lib/src/data/models/active_recall_models.dart` | KONTROL ET | `fromMap` Firestore verisini doğru parse ediyor mu |
| `lib/features/home/home_page.dart` | DEĞİŞTİR | `AssetActiveRecallService` → `FirestoreActiveRecallService` |
| `pubspec.yaml` | OPSİYONEL | assets kaydını kaldır (stabil olduktan sonra) |
| `assets/data/vocabulary/active_recall_pool.json` | OPSİYONEL | Sil (stabil olduktan sonra) |

**BLoC, repository, view, evaluator → dokunma.**
