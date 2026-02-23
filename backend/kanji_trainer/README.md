# Kanji Trainer Data

Bu dizindeki kanji listesi (`n5_kanji_list.json`), mobil uygulama tarafından **yerel bir asset (bundled asset)** olarak kullanılmaktadır. 

## Önemli Not
Bu veri yapısı Firebase Firestore'a yüklenmek yerine doğrudan uygulama içine dahil edilmektedir. Yapılan her güncelleme, uygulama güncellendiğinde veya yeni bir asset sürümü yayınlandığında kullanıcıya ulaşır.

## Veri Yapısı
`data/n5_kanji_list.json` dosyası toplam **113** JLPT N5 kanjisini içermektedir. Her kanji dökümanı şu alanlara sahiptir:
- `id`: Benzersiz numara
- `kanji`: Kanji karakteri
- `meaning`: 5 dilde (TR, EN, DE, ES, FR) anlamlar
