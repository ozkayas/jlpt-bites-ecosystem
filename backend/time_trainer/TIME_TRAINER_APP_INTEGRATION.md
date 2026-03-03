# Time Trainer — Uygulama Entegrasyon Paketi

Bu dosya, Time Trainer özelliğini Flutter uygulamasına entegre eden ajana yönelik hazırlanmıştır.

---

## Özellik Özeti

**Time Trainer**, kullanıcının Japonca saat okumayı öğrenmesini sağlayan bir pratik modülüdür.

- Ekranda rastgele bir saat gösterilir (dijital veya analog)
- Kullanıcı doğru Japonca okunuşu seçer (4 şık)
- Her soru için native speaker sesi çalınır
- Tüm sesler Firebase Storage'da hazır MP3 olarak bulunmaktadır

---

## Audio Sistemi

### Storage Yapısı

```
Firebase Storage bucket: jlpt-bites.firebasestorage.app
Path pattern: time_trainer/audio/HHMM.mp3
```

### URL Formatı

```
https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/{HHMM}.mp3
```

Örnekler:
- `0000` → `https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0000.mp3` (0時 / れいじ)
- `0130` → `https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0130.mp3` (1時30分)
- `1445` → `https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1445.mp3` (14時45分)

### HHMM Formatı

- 4 haneli, leading zero'lu string
- `0000` = 0時0分, `0100` = 1時, `1230` = 12時30分
- Flutter'da: `final hhmm = '${hour.toString().padLeft(2,'0')}${minute.toString().padLeft(2,'0')};`

---

## Mevcut Sesler (84 adet)

Aşağıdaki 84 saat için ses mevcuttur. Uygulama **yalnızca bu saatleri** soru olarak göstermelidir.

> **Not:** Tam 1440 saat için üretim devam etmektedir. Şu an için uygulama bu listeyi kullanır.

### Mevcut HHMM Listesi

```
0000  0008  0029
0100  0101  0130  0131  0153
0200  0209  0230
0300  0302  0307  0330  0333
0400  0410  0417  0430
0500  0503  0530  0536  0558
0600  0615  0618  0630
0700  0730  0738  0759
0800  0819  0820  0830
0900  0905  0930  0939
1000  1021  1025  1030
1100  1106  1130  1141
1200  1222  1230
1300  1343
1400  1423  1430
1500  1511  1546
1600  1624  1635
1700  1748  1755
1800  1826  1840
1900  1912  1949
2000  2027  2045
2100  2113  2151
2200  2228  2250
2300  2314  2352
```

### Dart/Flutter Sabit Listesi

```dart
const List<String> availableTimes = [
  '0000', '0008', '0029',
  '0100', '0101', '0130', '0131', '0153',
  '0200', '0209', '0230',
  '0300', '0302', '0307', '0330', '0333',
  '0400', '0410', '0417', '0430',
  '0500', '0503', '0530', '0536', '0558',
  '0600', '0615', '0618', '0630',
  '0700', '0730', '0738', '0759',
  '0800', '0819', '0820', '0830',
  '0900', '0905', '0930', '0939',
  '1000', '1021', '1025', '1030',
  '1100', '1106', '1130', '1141',
  '1200', '1222', '1230',
  '1300', '1343',
  '1400', '1423', '1430',
  '1500', '1511', '1546',
  '1600', '1624', '1635',
  '1700', '1748', '1755',
  '1800', '1826', '1840',
  '1900', '1912', '1949',
  '2000', '2027', '2045',
  '2100', '2113', '2151',
  '2200', '2228', '2250',
  '2300', '2314', '2352',
];

String audioUrl(String hhmm) =>
    'https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/$hhmm.mp3';
```

---

## Tam URL Listesi (84 adet)

| HHMM | Saat | URL |
|------|------|-----|
| 0000 | 0時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0000.mp3 |
| 0008 | 0時8分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0008.mp3 |
| 0029 | 0時29分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0029.mp3 |
| 0100 | 1時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0100.mp3 |
| 0101 | 1時1分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0101.mp3 |
| 0130 | 1時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0130.mp3 |
| 0131 | 1時31分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0131.mp3 |
| 0153 | 1時53分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0153.mp3 |
| 0200 | 2時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0200.mp3 |
| 0209 | 2時9分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0209.mp3 |
| 0230 | 2時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0230.mp3 |
| 0300 | 3時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0300.mp3 |
| 0302 | 3時2分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0302.mp3 |
| 0307 | 3時7分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0307.mp3 |
| 0330 | 3時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0330.mp3 |
| 0333 | 3時33分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0333.mp3 |
| 0400 | 4時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0400.mp3 |
| 0410 | 4時10分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0410.mp3 |
| 0417 | 4時17分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0417.mp3 |
| 0430 | 4時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0430.mp3 |
| 0500 | 5時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0500.mp3 |
| 0503 | 5時3分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0503.mp3 |
| 0530 | 5時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0530.mp3 |
| 0536 | 5時36分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0536.mp3 |
| 0558 | 5時58分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0558.mp3 |
| 0600 | 6時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0600.mp3 |
| 0615 | 6時15分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0615.mp3 |
| 0618 | 6時18分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0618.mp3 |
| 0630 | 6時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0630.mp3 |
| 0700 | 7時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0700.mp3 |
| 0730 | 7時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0730.mp3 |
| 0738 | 7時38分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0738.mp3 |
| 0759 | 7時59分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0759.mp3 |
| 0800 | 8時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0800.mp3 |
| 0819 | 8時19分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0819.mp3 |
| 0820 | 8時20分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0820.mp3 |
| 0830 | 8時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0830.mp3 |
| 0900 | 9時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0900.mp3 |
| 0905 | 9時5分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0905.mp3 |
| 0930 | 9時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0930.mp3 |
| 0939 | 9時39分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/0939.mp3 |
| 1000 | 10時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1000.mp3 |
| 1021 | 10時21分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1021.mp3 |
| 1025 | 10時25分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1025.mp3 |
| 1030 | 10時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1030.mp3 |
| 1100 | 11時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1100.mp3 |
| 1106 | 11時6分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1106.mp3 |
| 1130 | 11時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1130.mp3 |
| 1141 | 11時41分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1141.mp3 |
| 1200 | 12時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1200.mp3 |
| 1222 | 12時22分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1222.mp3 |
| 1230 | 12時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1230.mp3 |
| 1300 | 13時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1300.mp3 |
| 1343 | 13時43分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1343.mp3 |
| 1400 | 14時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1400.mp3 |
| 1423 | 14時23分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1423.mp3 |
| 1430 | 14時30分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1430.mp3 |
| 1500 | 15時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1500.mp3 |
| 1511 | 15時11分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1511.mp3 |
| 1546 | 15時46分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1546.mp3 |
| 1600 | 16時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1600.mp3 |
| 1624 | 16時24分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1624.mp3 |
| 1635 | 16時35分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1635.mp3 |
| 1700 | 17時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1700.mp3 |
| 1748 | 17時48分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1748.mp3 |
| 1755 | 17時55分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1755.mp3 |
| 1800 | 18時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1800.mp3 |
| 1826 | 18時26分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1826.mp3 |
| 1840 | 18時40分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1840.mp3 |
| 1900 | 19時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1900.mp3 |
| 1912 | 19時12分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1912.mp3 |
| 1949 | 19時49分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/1949.mp3 |
| 2000 | 20時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2000.mp3 |
| 2027 | 20時27分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2027.mp3 |
| 2045 | 20時45分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2045.mp3 |
| 2100 | 21時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2100.mp3 |
| 2113 | 21時13分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2113.mp3 |
| 2151 | 21時51分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2151.mp3 |
| 2200 | 22時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2200.mp3 |
| 2228 | 22時28分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2228.mp3 |
| 2250 | 22時50分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2250.mp3 |
| 2300 | 23時 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2300.mp3 |
| 2314 | 23時14分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2314.mp3 |
| 2352 | 23時52分 | https://storage.googleapis.com/jlpt-bites.firebasestorage.app/time_trainer/audio/2352.mp3 |

---

## Entegrasyon Talimatları (Ajan için)

Aşağıdaki görevleri Flutter uygulamasında gerçekleştir:

### 1. Mevcut saat listesini tanımla

`availableTimes` listesini yukarıdaki Dart bloğunu kullanarak ekle. Bu liste hem soru havuzu hem de audio URL'i oluşturmak için kullanılır.

### 2. Audio çalma

Bir soru gösterildiğinde, HHMM key'i ile URL oluştur ve `just_audio` veya mevcut audio paketini kullanarak çal:

```dart
final url = audioUrl(hhmm); // yukarıdaki helper fonksiyon
// → AudioPlayer ile çal
```

### 3. Soru üretimi

Her soru için:
- `availableTimes`'tan rastgele bir HHMM seç (doğru cevap)
- `availableTimes`'tan 3 farklı HHMM daha seç (yanlış şıklar) — aynı saat tekrar seçilmemelidir
- 4 şıkkı karıştır, doğru cevabın indeksini kaydet
- Ekranda saati göster (HHMM'i saat:dakika formatına çevirerek)
- Sesi otomatik çal

### 4. Şık metni

Her şık için gösterilecek metin: Japonca okunuş (romaji veya kana)

Örnek dönüşüm tablosu (uygulamada zaten varsa mevcut olanı kullan):

| HHMM | Japonca metin |
|------|--------------|
| 0000 | れいじ / 0時 |
| 0130 | いちじさんじゅっぷん / 1時30分 |
| 1200 | じゅうにじ / 12時 |

### 5. Gelecek genişleme

Yeni sesler eklendiğinde (tam 1440 hedefleniyor), `availableTimes` listesine ekleme yapılacak — başka bir değişiklik gerekmez. URL pattern sabittir.

---

## Teknik Notlar

- Tüm MP3'ler public erişimlidir, auth token gerekmez
- Format: MP3, ~48kbps, Japonca native speaker (Gemini TTS / Kore voice)
- Dosya boyutları: ~20–60KB (leading silence trim edildi)
- Bucket: `jlpt-bites.firebasestorage.app`
