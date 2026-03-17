#!/usr/bin/env python3
"""Batch generate 29 Point Comprehension questions (003-031) as variations of source clips."""
import json
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

questions = [
    # --- 003: Variation of ewHktqEnxTQ Q2 (buluşma yeri / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "にちようびの　やくそく (Sunday Plans)", "audio_url": None},
        "options": [
            "えきの　まえで　あいます",
            "でぱーとで　あいます",
            "こうえんで　あいます",
            "びょういんの　まえで　あいます"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。ふたりは　どこで　あいますか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "にちようびに　いっしょに　さんぽしませんか。"},
                {"speaker": "おんなのひと", "text": "いいですね。どこで　あいましょうか。"},
                {"speaker": "おとこのひと", "text": "えきの　まえは　どうですか。"},
                {"speaker": "おんなのひと", "text": "えきは　ちょっと　とおいです。こうえんの　いりぐちは　どうですか。"},
                {"speaker": "おとこのひと", "text": "ああ、そうですね。じゃあ　そこで　あいましょう。"}
            ],
            "question": "ふたりは　どこで　あいますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "さんぽ", "tr": "yürüyüş", "en": "walk/stroll"},
                {"word": "いりぐち", "tr": "giriş", "en": "entrance"},
                {"word": "とおい", "tr": "uzak", "en": "far"}
            ],
            "grammar": [
                {"point": "～ませんか", "tr": "teklif (yapmaz mısınız?)", "en": "invitation (won't you?)"},
                {"point": "～ましょう", "tr": "hadi yapalım", "en": "let's do"}
            ]
        },
        "logic": {
            "tr": "Erkek istasyon önünü (えきのまえ) teklif ediyor ama kadın uzak olduğunu söylüyor. Kadın parkın girişini (こうえんのいりぐち) öneriyor ve erkek kabul ediyor. Doğru cevap parktır.",
            "en": "The man suggests in front of the station (えきのまえ), but the woman says it's too far. She suggests the park entrance (こうえんのいりぐち) and the man agrees. The correct answer is the park."
        }
    },
    # --- 004: Variation of ewHktqEnxTQ Q3 (içecek / sipariş) ---
    {
        "metadata": {"level": "N5", "topic": "のみものの　ちゅうもん (Ordering Drinks)", "audio_url": None},
        "options": [
            "こーひー",
            "おちゃ",
            "じゅーす",
            "みず"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "きっさてんで　おんなのひとと　おみせのひとが　はなしています。おんなのひとは　なにを　のみますか。",
            "dialogue": [
                {"speaker": "おみせのひと", "text": "のみものは　なにに　しますか。こーひーと　おちゃと　じゅーすが　あります。"},
                {"speaker": "おんなのひと", "text": "こーひーを　おねがいします。あ、やっぱり　おちゃに　します。"},
                {"speaker": "おみせのひと", "text": "おちゃですね。つめたいのと　あたたかいのと　どちらが　いいですか。"},
                {"speaker": "おんなのひと", "text": "あたたかいのを　おねがいします。"}
            ],
            "question": "おんなのひとは　なにを　のみますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "きっさてん", "tr": "kahvehane", "en": "coffee shop"},
                {"word": "やっぱり", "tr": "yine de / vazgeçip", "en": "after all / on second thought"},
                {"word": "つめたい", "tr": "soğuk", "en": "cold"}
            ],
            "grammar": [
                {"point": "～にします", "tr": "karar vermek / seçmek", "en": "to decide on / choose"}
            ]
        },
        "logic": {
            "tr": "Kadın önce kahve (こーひー) istiyor ama 'やっぱり' diyerek fikrini değiştirip çaya (おちゃ) karar veriyor. Doğru cevap おちゃ (çay). Kahve ilk teklif ama vazgeçildi, jüs ve su hiç seçilmedi.",
            "en": "The woman first orders coffee (こーひー) but changes her mind ('やっぱり') and switches to tea (おちゃ). The correct answer is tea. Coffee was the initial choice but abandoned."
        }
    },
    # --- 005: Variation of ewHktqEnxTQ Q4 (hastane odası / olumsuz eleme) ---
    {
        "metadata": {"level": "N5", "topic": "ほてるの　へやの　もの (Hotel Room Items)", "audio_url": None},
        "options": [
            "てれび",
            "れいぞうこ",
            "でんわ",
            "ぱそこん"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "ほてるで　おんなのひとが　おとこのひとに　はなしています。へやには　なにが　ありますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "おへやに　てれびが　あります。りもこんは　つくえの　うえです。"},
                {"speaker": "おんなのひと", "text": "れいぞうこは　へやには　ありませんが　ろびーに　あります。"},
                {"speaker": "おんなのひと", "text": "でんわも　へやには　ありません。ふろんとに　でんわが　あります。"}
            ],
            "question": "へやには　なにが　ありますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "ほてる", "tr": "otel", "en": "hotel"},
                {"word": "りもこん", "tr": "uzaktan kumanda", "en": "remote control"},
                {"word": "ろびー", "tr": "lobi", "en": "lobby"},
                {"word": "ふろんと", "tr": "resepsiyon", "en": "front desk"}
            ],
            "grammar": [
                {"point": "～は　ありません", "tr": "... yoktur", "en": "there is no ..."},
                {"point": "～の　うえ", "tr": "... üzerinde", "en": "on top of ..."}
            ]
        },
        "logic": {
            "tr": "Buzdolabı (れいぞうこ) lobide, telefon (でんわ) resepsiyonda, ikisi de odada yok. Odada (へやに) sadece televizyon (てれび) var. Bilgisayar (ぱそこん) hiç bahsedilmiyor.",
            "en": "The fridge (れいぞうこ) is in the lobby, the phone (でんわ) is at the front desk — neither is in the room. Only the TV (てれび) is in the room. The PC (ぱそこん) is never mentioned."
        }
    },
    # --- 006: Variation of ewHktqEnxTQ Q5 (sonraki eylem / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "これからの　よてい (Upcoming Plans)", "audio_url": None},
        "options": [
            "しゅくだいを　します",
            "あるばいとに　いきます",
            "ともだちと　かいものに　いきます",
            "うちで　ねます"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。おんなのひとは　このあと　なにを　しますか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "このあと　なにを　しますか。"},
                {"speaker": "おんなのひと", "text": "しゅくだいを　します。あしたまでですから。"},
                {"speaker": "おとこのひと", "text": "えっ、しゅくだいは　らいしゅうまでですよ。"},
                {"speaker": "おんなのひと", "text": "ほんとうですか。じゃあ　ともだちと　かいものに　いきます。"},
                {"speaker": "おとこのひと", "text": "いいですね。"}
            ],
            "question": "おんなのひとは　このあと　なにを　しますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "しゅくだい", "tr": "ödev", "en": "homework"},
                {"word": "かいもの", "tr": "alışveriş", "en": "shopping"},
                {"word": "らいしゅう", "tr": "gelecek hafta", "en": "next week"}
            ],
            "grammar": [
                {"point": "～まで", "tr": "-e kadar", "en": "until"},
                {"point": "～から (sebep)", "tr": "çünkü", "en": "because"}
            ]
        },
        "logic": {
            "tr": "Kadın önce ödev yapacağını (しゅくだい) söylüyor çünkü yarına kadar sanıyor. Erkek ödevin gelecek haftaya kadar olduğunu söyleyince kadın fikrini değiştirip arkadaşıyla alışverişe (かいもの) gitmeye karar veriyor.",
            "en": "The woman initially plans to do homework (しゅくだい) thinking it's due tomorrow. When the man says it's due next week, she changes her mind and decides to go shopping (かいもの) with a friend."
        }
    },
    # --- 007: Variation of 0e0duD8_LFE Q1 (unutulan çanta / düzeltme) ---
    {
        "metadata": {"level": "N5", "topic": "わすれた　ふくろ (Forgotten Bag)", "audio_url": None},
        "options": [
            "ほんと　かぎ",
            "ほんと　めがね",
            "かぎと　めがね",
            "ほんと　かぎと　めがね"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "おみせで　おんなのひとと　おみせのひとが　はなしています。おんなのひとの　ふくろの　なかに　なにが　ありますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "すみません。きのう　ここに　ふくろを　わすれましたが。"},
                {"speaker": "おみせのひと", "text": "どんな　ふくろですか。"},
                {"speaker": "おんなのひと", "text": "ちいさい　しろい　ふくろです。なかに　ほんと　めがねと　かぎが　はいっています。"},
                {"speaker": "おんなのひと", "text": "あ、かぎは　ぽけっとに　いれましたから　ほんと　めがねだけです。"},
                {"speaker": "おみせのひと", "text": "これですか。"},
                {"speaker": "おんなのひと", "text": "あ、はい。ありがとうございます。"}
            ],
            "question": "おんなのひとの　ふくろの　なかに　なにが　ありますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "ふくろ", "tr": "torba/çanta", "en": "bag"},
                {"word": "わすれる", "tr": "unutmak", "en": "to forget"},
                {"word": "めがね", "tr": "gözlük", "en": "glasses"},
                {"word": "かぎ", "tr": "anahtar", "en": "key"}
            ],
            "grammar": [
                {"point": "～だけ", "tr": "sadece", "en": "only"}
            ]
        },
        "logic": {
            "tr": "Kadın önce kitap, gözlük ve anahtar olduğunu söylüyor. Sonra anahtarın (かぎ) cebinde olduğunu hatırlayıp düzeltiyor. Torbada sadece kitap (ほん) ve gözlük (めがね) kalmıştır.",
            "en": "The woman initially says the bag contains a book, glasses, and keys. She then corrects herself, saying the keys (かぎ) are in her pocket. Only the book (ほん) and glasses (めがね) remain in the bag."
        }
    },
    # --- 008: Variation of 0e0duD8_LFE Q2 (yarınki plan / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "やすみの　ひの　よてい (Day Off Plans)", "audio_url": None},
        "options": [
            "ぷーるで　およぎます",
            "うちで　えいがを　みます",
            "こうえんを　さんぽします",
            "としょかんで　べんきょうします"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "おんなのひとと　おとこのひとが　はなしています。ふたりは　あした　なにを　しますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "あした　やすみですね。いっしょに　ぷーるへ　いきませんか。"},
                {"speaker": "おとこのひと", "text": "すみません。あしたは　あさ　ともだちと　てにすを　します。ちょっと　つかれますから。"},
                {"speaker": "おんなのひと", "text": "じゃあ　ぷーるじゃなくて　こうえんを　さんぽしませんか。"},
                {"speaker": "おとこのひと", "text": "いいですね。そうしましょう。"}
            ],
            "question": "ふたりは　あした　なにを　しますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "ぷーる", "tr": "havuz", "en": "pool"},
                {"word": "つかれる", "tr": "yorulmak", "en": "to get tired"},
                {"word": "さんぽ", "tr": "yürüyüş", "en": "walk/stroll"}
            ],
            "grammar": [
                {"point": "～じゃなくて", "tr": "... değil de", "en": "not ... but"},
                {"point": "～ましょう", "tr": "hadi yapalım", "en": "let's do"}
            ]
        },
        "logic": {
            "tr": "Kadın havuza (ぷーる) gitmeyi teklif ediyor. Erkek sabah tenis oynayacağı için yorgun olacağını söylüyor. Kadın havuz yerine parkta yürüyüş (こうえんをさんぽ) önerince erkek kabul ediyor.",
            "en": "The woman suggests going to the pool (ぷーる). The man says he'll be tired after tennis. She suggests a walk in the park (こうえんをさんぽ) instead, which he agrees to."
        }
    },
    # --- 009: Variation of 0e0duD8_LFE Q3 (müze / olumsuz eleme) ---
    {
        "metadata": {"level": "N5", "topic": "えんそくの　もちもの (Field Trip Items)", "audio_url": None},
        "options": [
            "おべんとうと　のみもの",
            "おべんとうと　かめら",
            "のみものと　かめら",
            "おべんとうと　のみものと　かめら"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "がっこうで　せんせいが　がくせいに　はなしています。がくせいは　あした　なにを　もっていきますか。",
            "dialogue": [
                {"speaker": "せんせい", "text": "あしたは　みんなで　やまへ　いきます。おべんとうと　のみものを　もってきてください。"},
                {"speaker": "せんせい", "text": "かめらを　もってきたい　ひとも　いると　おもいますが　こんかいは　だめです。"},
                {"speaker": "せんせい", "text": "それから　げーむも　もってこないでくださいね。"}
            ],
            "question": "がくせいは　あした　なにを　もっていきますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "えんそく", "tr": "gezi", "en": "field trip/excursion"},
                {"word": "おべんとう", "tr": "yemek kutusu", "en": "boxed lunch"},
                {"word": "かめら", "tr": "kamera", "en": "camera"}
            ],
            "grammar": [
                {"point": "～てください", "tr": "lütfen yapın", "en": "please do"},
                {"point": "～ないでください", "tr": "lütfen yapmayın", "en": "please don't do"}
            ]
        },
        "logic": {
            "tr": "Öğretmen yemek kutusu (おべんとう) ve içecek (のみもの) getirilmesini istiyor. Kamera (かめら) ve oyun (げーむ) yasak. Doğru cevap yemek kutusu ve içecektir.",
            "en": "The teacher asks students to bring a boxed lunch (おべんとう) and drinks (のみもの). Camera (かめら) and games (げーむ) are forbidden. The correct answer is boxed lunch and drinks."
        }
    },
    # --- 010: Variation of 0e0duD8_LFE Q4 (hediye / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "ははの　ぷれぜんと (Mother's Present)", "audio_url": None},
        "options": [
            "はなを　かいます",
            "ぼうしを　かいます",
            "くつを　かいます",
            "かばんを　かいます"
        ],
        "correct_option": 3,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。おんなのひとは　おかあさんの　ぷれぜんとに　なにを　かいますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "らいしゅう　ははの　たんじょうびです。なにが　いいと　おもいますか。"},
                {"speaker": "おとこのひと", "text": "はなは　どうですか。"},
                {"speaker": "おんなのひと", "text": "はなは　すぐ　だめに　なりますから。"},
                {"speaker": "おとこのひと", "text": "じゃあ　ぼうしや　くつとかは？"},
                {"speaker": "おんなのひと", "text": "ああ、このまえ　はは が　あたらしい　かばんが　ほしいと　いっていましたから　それにします。"}
            ],
            "question": "おんなのひとは　おかあさんの　ぷれぜんとに　なにを　かいますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "はな", "tr": "çiçek", "en": "flower"},
                {"word": "ぼうし", "tr": "şapka", "en": "hat"},
                {"word": "かばん", "tr": "çanta", "en": "bag"},
                {"word": "ほしい", "tr": "istemek", "en": "to want (something)"}
            ],
            "grammar": [
                {"point": "～にします", "tr": "karar vermek", "en": "to decide on"},
                {"point": "～と　いっていました", "tr": "... demişti", "en": "was saying that ..."}
            ]
        },
        "logic": {
            "tr": "Çiçek (はな) çabuk solar. Şapka (ぼうし) ve ayakkabı (くつ) önerilir ama seçilmez. Annesinin yeni bir çanta (かばん) istediğini hatırlayan kadın çanta almaya karar veriyor.",
            "en": "Flowers (はな) wilt quickly. Hat (ぼうし) and shoes (くつ) are suggested but not chosen. The woman remembers her mother said she wanted a new bag (かばん) and decides on that."
        }
    },
    # --- 011: Variation of 0e0duD8_LFE Q5 (kardeşlerin işi / dikkat dağıtıcı) ---
    {
        "metadata": {"level": "N5", "topic": "かぞくの　しごと (Family's Jobs)", "audio_url": None},
        "options": [
            "びょういんで　はたらいています",
            "がっこうで　おしえています",
            "ぎんこうで　はたらいています",
            "れすとらんで　はたらいています"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "おんなのひとと　おとこのひとが　はなしています。おとこのひとの　あねは　どんな　しごとを　していますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "たなかさんは　きょうだいが　いますか。"},
                {"speaker": "おとこのひと", "text": "あねと　おとうとが　います。"},
                {"speaker": "おとこのひと", "text": "わたしは　ぎんこうで　はたらいています。あねは　がっこうで　えいごを　おしえています。おとうとは　びょういんで　はたらいています。"},
                {"speaker": "おんなのひと", "text": "そうですか。みんな　いそがしいですね。"}
            ],
            "question": "おとこのひとの　あねは　どんな　しごとを　していますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "あね", "tr": "abla", "en": "older sister"},
                {"word": "おしえる", "tr": "öğretmek", "en": "to teach"},
                {"word": "えいご", "tr": "İngilizce", "en": "English"},
                {"word": "ぎんこう", "tr": "banka", "en": "bank"}
            ],
            "grammar": [
                {"point": "～ています", "tr": "süregelen durum", "en": "ongoing state / is doing"}
            ]
        },
        "logic": {
            "tr": "Erkek kendi bankada (ぎんこう), küçük kardeşi hastanede (びょういん) çalışıyor. Ablası (あね) okulda İngilizce öğretiyor (がっこうでおしえています). Soru ablayı sorduğu için doğru cevap okulda öğretmendir.",
            "en": "The man works at a bank (ぎんこう), his younger brother at a hospital (びょういん). His older sister (あね) teaches English at a school (がっこうでおしえています). The question asks about the sister."
        }
    },
    # --- 012: Variation of 0e0duD8_LFE Q6 (geç kalma / neden) ---
    {
        "metadata": {"level": "N5", "topic": "ちこくの　りゆう (Reason for Being Late)", "audio_url": None},
        "options": [
            "あめで　ばすが　おくれました",
            "あさ　おきられませんでした",
            "みちが　わかりませんでした",
            "でんしゃを　まちがえました"
        ],
        "correct_option": 3,
        "transcription": {
            "intro": "がっこうで　せんせいと　がくせいが　はなしています。がくせいは　どうして　おくれましたか。",
            "dialogue": [
                {"speaker": "せんせい", "text": "すずきさん、どうして　おくれましたか。あたまが　いたいですか。"},
                {"speaker": "がくせい", "text": "いいえ、げんきです。"},
                {"speaker": "せんせい", "text": "じゃあ　どうしてですか。"},
                {"speaker": "がくせい", "text": "きょうは　はじめて　でんしゃで　きましたが　のる　でんしゃを　まちがえて　ちがう　えきに　いってしまいました。"},
                {"speaker": "せんせい", "text": "そうですか。きをつけてくださいね。"}
            ],
            "question": "がくせいは　どうして　おくれましたか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "おくれる", "tr": "gecikmek", "en": "to be late"},
                {"word": "まちがえる", "tr": "yanlış yapmak", "en": "to make a mistake"},
                {"word": "はじめて", "tr": "ilk kez", "en": "first time"}
            ],
            "grammar": [
                {"point": "～てしまいました", "tr": "maalesef ... yaptı (pişmanlık)", "en": "unfortunately did (regret)"},
                {"point": "どうして", "tr": "neden", "en": "why"}
            ]
        },
        "logic": {
            "tr": "Öğretmen baş ağrısı mı (あたまがいたい) diye soruyor ama öğrenci sağlıklı olduğunu söylüyor. Asıl sebep: ilk kez trenle gelirken yanlış trene binmesi (でんしゃをまちがえた). Yağmur ve yolu bilmemek bahsedilmiyor.",
            "en": "The teacher asks if it's a headache (あたまがいたい) but the student says he's fine. The real reason: he took the wrong train (でんしゃをまちがえた) because it was his first time commuting by train."
        }
    },
    # --- 013: Variation of f9xIi2z5RVk Q1 (aile hobileri / dikkat dağıtıcı) ---
    {
        "metadata": {"level": "N5", "topic": "かぞくの　しゅみ (Family Hobbies)", "audio_url": None},
        "options": [
            "りょうりを　つくります",
            "おんがくを　ききます",
            "えを　かきます",
            "すぽーつを　します"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "おんなのひとと　おとこのひとが　はなしています。おとこのひとの　いもうとは　なにが　すきですか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "やすみのひは　なにを　しますか。"},
                {"speaker": "おとこのひと", "text": "わたしは　おんがくを　ききます。あには　えを　かくことが　すきです。"},
                {"speaker": "おとこのひと", "text": "いもうとは　りょうりを　つくることが　すきで　いつも　あたらしい　りょうりを　つくっています。"},
                {"speaker": "おんなのひと", "text": "いいですね。"}
            ],
            "question": "おとこのひとの　いもうとは　なにが　すきですか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "おんがく", "tr": "müzik", "en": "music"},
                {"word": "え", "tr": "resim", "en": "drawing/picture"},
                {"word": "りょうり", "tr": "yemek yapmak", "en": "cooking"}
            ],
            "grammar": [
                {"point": "～ことが　すきです", "tr": "... yapmayı sevmek", "en": "to like doing ..."}
            ]
        },
        "logic": {
            "tr": "Erkek müzik dinliyor, ağabeyi resim çiziyor. Kız kardeşi (いもうと) yemek yapmayı (りょうりをつくること) seviyor. Soru kız kardeşi soruyor, doğru cevap yemek yapmaktır.",
            "en": "The man listens to music, his older brother draws. His younger sister (いもうと) likes cooking (りょうりをつくること). The question asks about the sister."
        }
    },
    # --- 014: Variation of f9xIi2z5RVk Q2 (alışveriş hesaplama) ---
    {
        "metadata": {"level": "N5", "topic": "くだものの　かいもの (Fruit Shopping)", "audio_url": None},
        "options": [
            "さんびゃくえん",
            "よんひゃくえん",
            "ごひゃくえん",
            "ろっぴゃくえん"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "おみせで　おんなのひとと　おみせのひとが　はなしています。おんなのひとは　いくら　はらいますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "すみません。この　りんごは　いくらですか。"},
                {"speaker": "おみせのひと", "text": "ひとつ　ひゃくごじゅうえんです。でも　みっつで　よんひゃくえんですよ。"},
                {"speaker": "おんなのひと", "text": "じゃあ　みっつ　ください。あと　この　ひゃくえんの　みかんを　ひとつ　ください。"},
                {"speaker": "おみせのひと", "text": "はい、ありがとうございます。"}
            ],
            "question": "おんなのひとは　いくら　はらいますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "りんご", "tr": "elma", "en": "apple"},
                {"word": "みかん", "tr": "mandalina", "en": "mandarin orange"},
                {"word": "いくら", "tr": "ne kadar", "en": "how much"}
            ],
            "grammar": [
                {"point": "～で（ねだん）", "tr": "... fiyatına (toplam)", "en": "for ... (total price)"}
            ]
        },
        "logic": {
            "tr": "Elma 3 tane = 400 yen (set fiyatı). Mandalina 1 tane = 100 yen. Toplam 400 + 100 = 500 yen. Tek elma 150 yen (3 × 150 = 450 değil, set 400). Doğru cevap 500 yen.",
            "en": "3 apples = 400 yen (set price). 1 mandarin = 100 yen. Total: 400 + 100 = 500 yen. Individual apple price (150) is a distractor. Correct answer: 500 yen."
        }
    },
    # --- 015: Variation of f9xIi2z5RVk Q3 (ulaşım / dikkat dağıtıcı) ---
    {
        "metadata": {"level": "N5", "topic": "がっこうへの　いきかた (How to Get to School)", "audio_url": None},
        "options": [
            "じてんしゃで　いきました",
            "ばすで　いきました",
            "あるいて　いきました",
            "たくしーで　いきました"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "だいがくで　おとこのがくせいと　おんなのがくせいが　はなしています。おんなのがくせいは　きょう　どうやって　がっこうに　きましたか。",
            "dialogue": [
                {"speaker": "おとこのがくせい", "text": "きょうは　ばすで　きましたか。"},
                {"speaker": "おんなのがくせい", "text": "いつもは　じてんしゃですが　きょうは　あめですから　ばすで　きました。"},
                {"speaker": "おとこのがくせい", "text": "わたしは　あるいて　きましたよ。"},
                {"speaker": "おんなのがくせい", "text": "あめなのに　すごいですね。"}
            ],
            "question": "おんなのがくせいは　きょう　どうやって　がっこうに　きましたか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "じてんしゃ", "tr": "bisiklet", "en": "bicycle"},
                {"word": "ばす", "tr": "otobüs", "en": "bus"},
                {"word": "あるく", "tr": "yürümek", "en": "to walk"}
            ],
            "grammar": [
                {"point": "～ですから", "tr": "... olduğu için", "en": "because ..."}
            ]
        },
        "logic": {
            "tr": "Kadın normalde bisikletle (じてんしゃ) geliyor ama bugün yağmur yağdığı için otobüsle (ばす) gelmiş. Erkek yürüyerek gelmiş ama soru kadını soruyor. Doğru cevap otobüs.",
            "en": "The woman usually comes by bicycle (じてんしゃ) but today came by bus (ばす) because of rain. The man walked but the question asks about the woman. Correct answer: bus."
        }
    },
    # --- 016: Variation of f9xIi2z5RVk Q4 (buluşma / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "まちあわせ (Meeting Up)", "audio_url": None},
        "options": [
            "えいがかんの　まえ",
            "えきの　なか",
            "かふぇ",
            "ほんやの　まえ"
        ],
        "correct_option": 3,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。ふたりは　どこで　あいますか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "あしたの　えいがは　さんじからですね。えいがかんの　まえで　あいましょうか。"},
                {"speaker": "おんなのひと", "text": "えいがかんの　まえは　ひとが　おおいですから　ちかくの　ほんやの　まえは　どうですか。"},
                {"speaker": "おとこのひと", "text": "いいですね。じゃあ　にじはんに　そこで　あいましょう。"},
                {"speaker": "おんなのひと", "text": "はい。"}
            ],
            "question": "ふたりは　どこで　あいますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "えいがかん", "tr": "sinema", "en": "movie theater"},
                {"word": "ほんや", "tr": "kitapçı", "en": "bookstore"},
                {"word": "ひと", "tr": "insan/kişi", "en": "person/people"}
            ],
            "grammar": [
                {"point": "～ましょうか", "tr": "yapalım mı?", "en": "shall we?"}
            ]
        },
        "logic": {
            "tr": "Erkek sinema önünü (えいがかんのまえ) teklif ediyor. Kadın kalabalık olduğunu söyleyip yakındaki kitapçının önünü (ほんやのまえ) öneriyor. Erkek kabul ediyor. Doğru cevap kitapçının önü.",
            "en": "The man suggests in front of the theater (えいがかんのまえ). The woman says it's crowded and suggests the bookstore nearby (ほんやのまえ). The man agrees. Correct answer: bookstore."
        }
    },
    # --- 017: Variation of f9xIi2z5RVk Q5 (ödev iade / zaman çıkarımı) ---
    {
        "metadata": {"level": "N5", "topic": "てすとの　ひ (Exam Day)", "audio_url": None},
        "options": [
            "げつようび",
            "かようび",
            "すいようび",
            "もくようび"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "がっこうで　せんせいが　がくせいに　はなしています。てすとは　いつですか。",
            "dialogue": [
                {"speaker": "せんせい", "text": "みなさん、こんしゅうの　げつようびに　しゅくだいを　だしてください。"},
                {"speaker": "せんせい", "text": "わたしが　しゅくだいを　みて　つぎのひに　かえします。"},
                {"speaker": "せんせい", "text": "そして　しゅくだいを　かえした　つぎのひに　てすとです。よく　べんきょうしてくださいね。"}
            ],
            "question": "てすとは　いつですか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "しゅくだい", "tr": "ödev", "en": "homework"},
                {"word": "だす", "tr": "teslim etmek", "en": "to submit"},
                {"word": "つぎのひ", "tr": "ertesi gün", "en": "the next day"}
            ],
            "grammar": [
                {"point": "～てください", "tr": "lütfen yapın", "en": "please do"}
            ]
        },
        "logic": {
            "tr": "Ödev Pazartesi teslim. Öğretmen ertesi gün (Salı) iade eder. İadenin ertesi günü (Çarşamba) sınav var. Doğru cevap すいようび (Çarşamba).",
            "en": "Homework is due Monday. Teacher returns it the next day (Tuesday). The test is the day after that (Wednesday). Correct answer: すいようび (Wednesday)."
        }
    },
    # --- 018: Variation of f9xIi2z5RVk Q6 (seyahat kişi / hesaplama) ---
    {
        "metadata": {"level": "N5", "topic": "りょこうの　にんずう (Travel Group Size)", "audio_url": None},
        "options": [
            "さんにん",
            "よにん",
            "ごにん",
            "ろくにん"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "おんなのひとと　おとこのひとが　はなしています。おんなのひとは　なんにんで　りょこうに　いきましたか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "きれいな　しゃしんですね。どこですか。"},
                {"speaker": "おんなのひと", "text": "きょうとです。おっとと　こどもたちと　いっしょに　いきました。"},
                {"speaker": "おとこのひと", "text": "おこさんは　なんにんですか。"},
                {"speaker": "おんなのひと", "text": "さんにんです。むすこが　ふたりと　むすめが　ひとりです。"}
            ],
            "question": "おんなのひとは　なんにんで　りょこうに　いきましたか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "おっと", "tr": "koca", "en": "husband"},
                {"word": "こども", "tr": "çocuk", "en": "child/children"},
                {"word": "むすこ", "tr": "oğul", "en": "son"},
                {"word": "むすめ", "tr": "kız çocuk", "en": "daughter"}
            ],
            "grammar": [
                {"point": "～と　いっしょに", "tr": "... ile birlikte", "en": "together with ..."}
            ]
        },
        "logic": {
            "tr": "Kadın + kocası (1) + çocuklar (3: 2 oğul + 1 kız) = toplam 5 kişi. Çocuk sayısı (3) ve koca dahil (4) yanlış hesaplardır. Doğru cevap ごにん (5 kişi).",
            "en": "Woman + husband (1) + children (3: 2 sons + 1 daughter) = 5 total. Children count (3) and husband+children (4) are partial calculations. Correct: ごにん (5 people)."
        }
    },
    # --- 019: Variation of sY7L5cfCWno Q1 (doğum günü / zaman çıkarımı) ---
    {
        "metadata": {"level": "N5", "topic": "たんじょうび (Birthday)", "audio_url": None},
        "options": [
            "さんがつ　みっか",
            "さんがつ　いつか",
            "さんがつ　なのか",
            "さんがつ　ここのか"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。おんなのひとの　たんじょうびは　いつですか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "きのう　きれいな　けーきが　ありましたね。"},
                {"speaker": "おんなのひと", "text": "ええ、おとといの　たんじょうびに　かぞくが　つくってくれました。"},
                {"speaker": "おとこのひと", "text": "そうですか。おととい　なんにちでしたか。"},
                {"speaker": "おんなのひと", "text": "いつかです。さんがつ　いつかです。"},
                {"speaker": "おとこのひと", "text": "へえ、もうすぐ　はるですね。"}
            ],
            "question": "おんなのひとの　たんじょうびは　いつですか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "おととい", "tr": "evvelsi gün", "en": "the day before yesterday"},
                {"word": "いつか", "tr": "ayın beşi", "en": "5th of the month"},
                {"word": "けーき", "tr": "pasta", "en": "cake"}
            ],
            "grammar": [
                {"point": "～てくれました", "tr": "benim için ... yaptı", "en": "did ... for me"}
            ]
        },
        "logic": {
            "tr": "Kadın doğum gününün evvelsi gün (おととい) yani Mart 5'i (さんがついつか) olduğunu açıkça söylüyor. Doğru cevap 3月5日.",
            "en": "The woman explicitly states her birthday was the day before yesterday (おととい), which is March 5th (さんがついつか). Correct answer: March 5th."
        }
    },
    # --- 020: Variation of sY7L5cfCWno Q2 (öğle yeri / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "ひるごはんの　ばしょ (Lunch Location)", "audio_url": None},
        "options": [
            "がくせいしょくどう",
            "きょうしつ",
            "こうえん",
            "こんびに"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "だいがくで　おとこのがくせいと　おんなのがくせいが　はなしています。ふたりは　どこで　たべますか。",
            "dialogue": [
                {"speaker": "おとこのがくせい", "text": "おひる　いっしょに　たべませんか。こうえんで　たべましょうか。"},
                {"speaker": "おんなのがくせい", "text": "きょうは　あめですから　そとは　ちょっと。"},
                {"speaker": "おとこのがくせい", "text": "そうですね。じゃあ　がくせいしょくどうは　どうですか。"},
                {"speaker": "おんなのがくせい", "text": "いいですね。そうしましょう。"}
            ],
            "question": "ふたりは　どこで　たべますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "がくせいしょくどう", "tr": "öğrenci yemekhanesi", "en": "school cafeteria"},
                {"word": "あめ", "tr": "yağmur", "en": "rain"},
                {"word": "そと", "tr": "dışarı", "en": "outside"}
            ],
            "grammar": [
                {"point": "～ましょうか", "tr": "yapalım mı?", "en": "shall we?"},
                {"point": "～は　ちょっと", "tr": "... biraz zor (nazik ret)", "en": "... is a bit (polite refusal)"}
            ]
        },
        "logic": {
            "tr": "Erkek parkı (こうえん) teklif ediyor ama yağmur yağdığı için kadın dışarıyı reddediyor. Erkek yemekhaneyi (がくせいしょくどう) önerince kadın kabul ediyor. Doğru cevap yemekhane.",
            "en": "The man suggests the park (こうえん) but the woman declines because of rain. He then suggests the cafeteria (がくせいしょくどう) and she agrees. Correct: cafeteria."
        }
    },
    # --- 021: Variation of sY7L5cfCWno Q3 (restoran / sipariş) ---
    {
        "metadata": {"level": "N5", "topic": "れすとらんの　ちゅうもん (Restaurant Order)", "audio_url": None},
        "options": [
            "ぎゅうにく",
            "さかな",
            "とりにく",
            "やさい"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "れすとらんで　おとこのひとと　てんいんが　はなしています。おとこのひとは　なにを　たべますか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "すみません。きょうの　おすすめは　なんですか。"},
                {"speaker": "てんいん", "text": "さかなと　ぎゅうにくが　あります。"},
                {"speaker": "おとこのひと", "text": "さかなは　ちょっと。ぎゅうにくを　おねがいします。"},
                {"speaker": "てんいん", "text": "はい、かしこまりました。"}
            ],
            "question": "おとこのひとは　なにを　たべますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "ぎゅうにく", "tr": "sığır eti", "en": "beef"},
                {"word": "さかな", "tr": "balık", "en": "fish"},
                {"word": "おすすめ", "tr": "tavsiye", "en": "recommendation"}
            ],
            "grammar": [
                {"point": "～は　ちょっと", "tr": "biraz zor (nazik ret)", "en": "is a bit... (polite refusal)"}
            ]
        },
        "logic": {
            "tr": "Garson balık (さかな) ve sığır eti (ぎゅうにく) önerir. Erkek balığı nazikçe reddedip (ちょっと) sığır eti sipariş ediyor. Tavuk (とりにく) ve sebze (やさい) bahsedilmiyor.",
            "en": "The waiter recommends fish (さかな) and beef (ぎゅうにく). The man politely declines fish (ちょっと) and orders beef. Chicken (とりにく) and vegetables (やさい) are never mentioned."
        }
    },
    # --- 022: Variation of sY7L5cfCWno Q4 (parti katılım / hesaplama) ---
    {
        "metadata": {"level": "N5", "topic": "ぱーてぃーの　にんずう (Party Attendance)", "audio_url": None},
        "options": [
            "じゅうごにん",
            "じゅうはちにん",
            "にじゅうにん",
            "にじゅうさんにん"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "だいがくで　おとこのがくせいと　おんなのがくせいが　はなしています。あしたの　ぱーてぃーに　なんにん　きますか。",
            "dialogue": [
                {"speaker": "おとこのがくせい", "text": "あしたの　ぱーてぃーは　なんにん　きますか。"},
                {"speaker": "おんなのがくせい", "text": "くらすは　にじゅうにんですが　こない　ひとが　よにん　います。"},
                {"speaker": "おとこのがくせい", "text": "じゃあ　じゅうろくにんですね。せんせいも　きますか。"},
                {"speaker": "おんなのがくせい", "text": "はい、やまだせんせいと　さとうせんせいが　きます。"},
                {"speaker": "おとこのがくせい", "text": "じゃあ　ぜんぶで　じゅうはちにんですね。"}
            ],
            "question": "あしたの　ぱーてぃーに　なんにん　きますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "くらす", "tr": "sınıf", "en": "class"},
                {"word": "ぜんぶで", "tr": "toplamda", "en": "in total"},
                {"word": "にん", "tr": "kişi (sayaç)", "en": "person (counter)"}
            ],
            "grammar": [
                {"point": "～ですが", "tr": "... ama", "en": "... but"}
            ]
        },
        "logic": {
            "tr": "Sınıf 20 kişi, 4'ü gelmiyor = 16 öğrenci. 2 öğretmen katılıyor. Toplam 16 + 2 = 18 kişi. Doğru cevap じゅうはちにん (18).",
            "en": "Class has 20 students, 4 won't come = 16 students. 2 teachers attending. Total: 16 + 2 = 18. Correct: じゅうはちにん (18)."
        }
    },
    # --- 023: Variation of sY7L5cfCWno Q5 (yarınki plan / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "あしたの　ごごの　よてい (Tomorrow Afternoon Plans)", "audio_url": None},
        "options": [
            "としょかんで　べんきょうします",
            "ともだちと　かいものに　いきます",
            "えいがを　みに　いきます",
            "うちで　そうじを　します"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。あしたの　ごご　おんなのひとは　なにを　しますか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "あしたの　ごご　えいがを　みに　いきませんか。"},
                {"speaker": "おんなのひと", "text": "すみません、あしたは　としょかんで　べんきょうします。もくようびに　てすとが　ありますから。"},
                {"speaker": "おとこのひと", "text": "あれ、てすとは　らいしゅうの　もくようびですよ。"},
                {"speaker": "おんなのひと", "text": "えっ、ほんとうですか。じゃあ　いきたいです。"},
                {"speaker": "おとこのひと", "text": "じゃ、いきましょう。"}
            ],
            "question": "あしたの　ごご　おんなのひとは　なにを　しますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "としょかん", "tr": "kütüphane", "en": "library"},
                {"word": "てすと", "tr": "sınav", "en": "test"},
                {"word": "ほんとう", "tr": "gerçekten", "en": "really/truly"}
            ],
            "grammar": [
                {"point": "～から (sebep)", "tr": "çünkü", "en": "because"}
            ]
        },
        "logic": {
            "tr": "Kadın kütüphanede (としょかん) çalışacağını söylüyor çünkü sınavı Perşembe sanıyor. Erkek sınavın gelecek hafta olduğunu söyleyince kadın sinemaya (えいが) gitmeye karar veriyor.",
            "en": "The woman plans to study at the library (としょかん) thinking the test is this Thursday. The man corrects her — it's next week. She then decides to go to the movies (えいが)."
        }
    },
    # --- 024: Variation of sY7L5cfCWno Q6 (içecek / fikir değiştirme+sipariş) ---
    {
        "metadata": {"level": "N5", "topic": "のみものを　えらぶ (Choosing Drinks)", "audio_url": None},
        "options": [
            "つめたい　おちゃ",
            "あたたかい　こーひー",
            "じゅーす",
            "みず"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。おんなのひとは　なにを　のみますか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "なにを　のみますか。こーひーと　おちゃと　じゅーすが　ありますよ。"},
                {"speaker": "おんなのひと", "text": "こーひーを　おねがいします。"},
                {"speaker": "おとこのひと", "text": "あたたかい　こーひーと　つめたい　こーひーが　ありますが。"},
                {"speaker": "おんなのひと", "text": "んー、やっぱり　つめたい　おちゃに　します。きょうは　あついですから。"},
                {"speaker": "おとこのひと", "text": "はい、わかりました。"}
            ],
            "question": "おんなのひとは　なにを　のみますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "あたたかい", "tr": "sıcak/ılık", "en": "warm/hot"},
                {"word": "つめたい", "tr": "soğuk", "en": "cold"},
                {"word": "あつい", "tr": "sıcak (hava)", "en": "hot (weather)"}
            ],
            "grammar": [
                {"point": "～にします", "tr": "karar vermek", "en": "to decide on"},
                {"point": "やっぱり", "tr": "yine de / vazgeçip", "en": "after all"}
            ]
        },
        "logic": {
            "tr": "Kadın önce kahve (こーひー) istiyor. Sıcak mı soğuk mu sorulunca 'やっぱり' diyerek fikrini tamamen değiştirip soğuk çay (つめたいおちゃ) seçiyor. Doğru cevap soğuk çay.",
            "en": "The woman first wants coffee (こーひー). When asked hot or cold, she changes her mind entirely ('やっぱり') and chooses cold tea (つめたいおちゃ). Correct: cold tea."
        }
    },
    # --- 025: Variation of YBAJDQ_zDJg Q1 (ilaç / olumsuz eleme) ---
    {
        "metadata": {"level": "N5", "topic": "くすりの　のみかた (How to Take Medicine)", "audio_url": None},
        "options": [
            "しろい　くすりだけ",
            "あおい　くすりだけ",
            "しろいのと　あおいの",
            "みっつ　ぜんぶ"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "びょういんで　おんなのひとが　おとこのひとに　はなしています。おとこのひとは　よる　どの　くすりを　のみますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "しろい　くすりは　あさと　よる　ごはんのあとに　のんでください。"},
                {"speaker": "おんなのひと", "text": "あおい　くすりは　よるだけ　ねるまえに　のんでください。"},
                {"speaker": "おんなのひと", "text": "あかい　くすりは　おなかが　いたいときだけ　のんでください。"},
                {"speaker": "おとこのひと", "text": "わかりました。ありがとうございます。"}
            ],
            "question": "おとこのひとは　よる　どの　くすりを　のみますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "くすり", "tr": "ilaç", "en": "medicine"},
                {"word": "しろい", "tr": "beyaz", "en": "white"},
                {"word": "あおい", "tr": "mavi", "en": "blue"},
                {"word": "あかい", "tr": "kırmızı", "en": "red"}
            ],
            "grammar": [
                {"point": "～まえに", "tr": "-den önce", "en": "before"},
                {"point": "～ときだけ", "tr": "sadece ... olduğunda", "en": "only when ..."}
            ]
        },
        "logic": {
            "tr": "Beyaz ilaç sabah ve akşam (よる dahil). Mavi ilaç sadece akşam. Kırmızı ilaç sadece karın ağrısında. Akşam: beyaz + mavi. Doğru cevap しろいのとあおいの.",
            "en": "White medicine: morning and night (よる included). Blue medicine: night only. Red medicine: only when stomach hurts. At night: white + blue. Correct: both white and blue."
        }
    },
    # --- 026: Variation of YBAJDQ_zDJg Q2 (kopya / hesaplama) ---
    {
        "metadata": {"level": "N5", "topic": "ぷりんとの　じゅんび (Preparing Handouts)", "audio_url": None},
        "options": [
            "じゅうまい",
            "にじゅうまい",
            "さんじゅうまい",
            "よんじゅうまい"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "がっこうで　せんせいと　がくせいが　はなしています。がくせいは　なんまい　こぴーしますか。",
            "dialogue": [
                {"speaker": "せんせい", "text": "たなかさん、この　ぷりんとを　こぴーしてください。"},
                {"speaker": "がくせい", "text": "はい、なんまいですか。"},
                {"speaker": "せんせい", "text": "がくせいは　にじゅうごにんですが　ひとりに　いちまいずつです。"},
                {"speaker": "がくせい", "text": "にじゅうごまいですね。"},
                {"speaker": "せんせい", "text": "あ、せんせいも　ごにんいますから　せんせいのぶんも　おねがいします。"},
                {"speaker": "がくせい", "text": "わかりました。"}
            ],
            "question": "がくせいは　なんまい　こぴーしますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "ぷりんと", "tr": "baskı/çıktı", "en": "printout/handout"},
                {"word": "こぴー", "tr": "fotokopi", "en": "copy"},
                {"word": "ぶん", "tr": "... için / payı", "en": "share / portion for"}
            ],
            "grammar": [
                {"point": "～ずつ", "tr": "her birine", "en": "each"}
            ]
        },
        "logic": {
            "tr": "25 öğrenci + 5 öğretmen = 30 kişi. Her birine 1 kopya = 30 kopya. 25 (sadece öğrenci) yanlış hesaptır. Doğru cevap さんじゅうまい (30 adet).",
            "en": "25 students + 5 teachers = 30 people. 1 copy each = 30 copies. 25 (students only) is a partial calculation. Correct: さんじゅうまい (30)."
        }
    },
    # --- 027: Variation of YBAJDQ_zDJg Q3 (varış saati / hesaplama) ---
    {
        "metadata": {"level": "N5", "topic": "おきた　じかん (Wake-up Time)", "audio_url": None},
        "options": [
            "ごじ",
            "ろくじ",
            "しちじ",
            "はちじ"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。おんなのひとは　きょう　なんじに　おきましたか。",
            "dialogue": [
                {"speaker": "おとこのひと", "text": "きょうは　はやいですね。"},
                {"speaker": "おんなのひと", "text": "ええ、きょうは　ともだちと　あさ　くうこうへ　いきますから。"},
                {"speaker": "おとこのひと", "text": "いつもは　しちじに　おきますよね。"},
                {"speaker": "おんなのひと", "text": "はい、でも　きょうは　いつもより　にじかん　はやく　おきました。"},
                {"speaker": "おとこのひと", "text": "たいへんですね。"}
            ],
            "question": "おんなのひとは　きょう　なんじに　おきましたか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "おきる", "tr": "kalkmak", "en": "to wake up"},
                {"word": "くうこう", "tr": "havaalanı", "en": "airport"},
                {"word": "はやい", "tr": "erken", "en": "early"}
            ],
            "grammar": [
                {"point": "～より", "tr": "-den daha", "en": "than (comparison)"},
                {"point": "～まえ", "tr": "-den önce", "en": "before"}
            ]
        },
        "logic": {
            "tr": "Kadın normalde saat 7'de (しちじ) kalkıyor. Bugün normalden 2 saat erken kalktı: 7 - 2 = 5. Doğru cevap ごじ (5:00).",
            "en": "The woman usually wakes up at 7 (しちじ). Today she woke up 2 hours earlier: 7 - 2 = 5. Correct: ごじ (5:00)."
        }
    },
    # --- 028: Variation of YBAJDQ_zDJg Q4 (film günü / fikir değiştirme) ---
    {
        "metadata": {"level": "N5", "topic": "かいものの　ひ (Shopping Day)", "audio_url": None},
        "options": [
            "どようび",
            "にちようび",
            "げつようび",
            "きんようび"
        ],
        "correct_option": 1,
        "transcription": {
            "intro": "おんなのひとと　おとこのひとが　はなしています。ふたりは　いつ　かいものに　いきますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "こんしゅうの　どようび　いっしょに　かいものに　いきませんか。"},
                {"speaker": "おとこのひと", "text": "すみません、どようびは　あるばいとが　あります。"},
                {"speaker": "おんなのひと", "text": "にちようびは　どうですか。"},
                {"speaker": "おとこのひと", "text": "にちようびは　ごぜんは　あるばいとですが　ごご　さんじに　おわります。"},
                {"speaker": "おんなのひと", "text": "じゃあ　にちようびの　ごご　いきましょう。"},
                {"speaker": "おとこのひと", "text": "はい、そうしましょう。"}
            ],
            "question": "ふたりは　いつ　かいものに　いきますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "どようび", "tr": "Cumartesi", "en": "Saturday"},
                {"word": "にちようび", "tr": "Pazar", "en": "Sunday"},
                {"word": "あるばいと", "tr": "yarı zamanlı iş", "en": "part-time job"}
            ],
            "grammar": [
                {"point": "～ませんか", "tr": "yapmaz mısınız? (teklif)", "en": "won't you? (invitation)"}
            ]
        },
        "logic": {
            "tr": "Cumartesi (どようび) erkek çalışıyor. Pazar (にちようび) sabah işi var ama öğleden sonra 3'te bitiyor. İkisi Pazar öğleden sonra buluşmaya karar veriyor. Doğru cevap にちようび.",
            "en": "Saturday (どようび) the man works. Sunday (にちようび) he works in the morning but finishes at 3 PM. They agree to go Sunday afternoon. Correct: にちようび."
        }
    },
    # --- 029: Variation of YBAJDQ_zDJg Q5 (doğum günü / zaman çıkarımı) ---
    {
        "metadata": {"level": "N5", "topic": "たんじょうびの　ひにち (Birthday Date)", "audio_url": None},
        "options": [
            "じゅうがつ　とおか",
            "じゅうがつ　じゅうよっか",
            "じゅういちがつ　とおか",
            "じゅういちがつ　じゅうよっか"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "おとこのひとと　おんなのひとが　はなしています。おとこのひとの　たんじょうびは　いつですか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "たなかさんの　たんじょうびは　いつですか。"},
                {"speaker": "おとこのひと", "text": "じゅうがつです。"},
                {"speaker": "おんなのひと", "text": "なんにちですか。"},
                {"speaker": "おとこのひと", "text": "わたしの　たんじょうびは　たいいくのひと　おなじです。"},
                {"speaker": "おんなのひと", "text": "じゃあ　じゅうがつ　とおかですね。"},
                {"speaker": "おとこのひと", "text": "はい、そうです。"}
            ],
            "question": "おとこのひとの　たんじょうびは　いつですか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "じゅうがつ", "tr": "Ekim", "en": "October"},
                {"word": "とおか", "tr": "ayın onuncu günü", "en": "10th of the month"},
                {"word": "たいいくのひ", "tr": "Spor Günü", "en": "Sports Day (national holiday)"}
            ],
            "grammar": [
                {"point": "～と　おなじ", "tr": "... ile aynı", "en": "same as ..."}
            ]
        },
        "logic": {
            "tr": "Erkek doğum gününün Spor Günü (たいいくのひ) ile aynı olduğunu söylüyor. Spor Günü Ekim 10 (じゅうがつとおか). Kadın bunu teyit ediyor. Doğru cevap 10月10日.",
            "en": "The man says his birthday is the same as Sports Day (たいいくのひ), which is October 10th (じゅうがつとおか). The woman confirms. Correct: October 10th."
        }
    },
    # --- 030: Variation of YBAJDQ_zDJg Q6 (randevu / zaman çıkarımı) ---
    {
        "metadata": {"level": "N5", "topic": "つぎの　よやく (Next Appointment)", "audio_url": None},
        "options": [
            "すいようび",
            "もくようび",
            "きんようび",
            "どようび"
        ],
        "correct_option": 2,
        "transcription": {
            "intro": "びょういんで　いしゃと　おんなのひとが　はなしています。おんなのひとは　つぎ　いつ　びょういんへ　きますか。",
            "dialogue": [
                {"speaker": "いしゃ", "text": "つぎは　らいしゅう　きてください。すいようびは　どうですか。"},
                {"speaker": "おんなのひと", "text": "すみません、すいようびから　もくようびまで　しゅっちょうです。"},
                {"speaker": "いしゃ", "text": "じゃあ　そのつぎのひは？"},
                {"speaker": "おんなのひと", "text": "きんようびですね。はい、だいじょうぶです。"},
                {"speaker": "いしゃ", "text": "じゃあ　ごぜんじゅうじで　いいですか。"},
                {"speaker": "おんなのひと", "text": "はい。"}
            ],
            "question": "おんなのひとは　つぎ　いつ　びょういんへ　きますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "しゅっちょう", "tr": "iş seyahati", "en": "business trip"},
                {"word": "つぎ", "tr": "sonraki", "en": "next"},
                {"word": "ごぜん", "tr": "sabah/öğleden önce", "en": "morning/AM"}
            ],
            "grammar": [
                {"point": "～から～まで", "tr": "-den -e kadar", "en": "from ... to ..."},
                {"point": "そのつぎのひ", "tr": "ondan sonraki gün", "en": "the day after that"}
            ]
        },
        "logic": {
            "tr": "Çarşamba (すいようび) ve Perşembe (もくようび) iş seyahati var. Doktor 'ondan sonraki gün' deyince Cuma (きんようび) oluyor. Kadın kabul ediyor. Doğru cevap きんようび.",
            "en": "Wednesday (すいようび) and Thursday (もくようび) she's on a business trip. 'The day after that' is Friday (きんようび). She agrees. Correct: きんようび (Friday)."
        }
    },
    # --- 031: Extra variation — tatil planı (hafta sonu / dikkat dağıtıcı) ---
    {
        "metadata": {"level": "N5", "topic": "しゅうまつの　よてい (Weekend Plans)", "audio_url": None},
        "options": [
            "うみへ　いきます",
            "やまへ　いきます",
            "うちで　やすみます",
            "ともだちと　てにすを　します"
        ],
        "correct_option": 0,
        "transcription": {
            "intro": "おんなのひとと　おとこのひとが　はなしています。おとこのひとは　しゅうまつに　なにを　しますか。",
            "dialogue": [
                {"speaker": "おんなのひと", "text": "しゅうまつは　なにを　しますか。"},
                {"speaker": "おとこのひと", "text": "かぞくと　うみへ　いきます。すずきさんは？"},
                {"speaker": "おんなのひと", "text": "わたしは　やまへ　いきたいですが　しゅうまつは　うちで　やすみます。つかれていますから。"},
                {"speaker": "おとこのひと", "text": "そうですか。わたしも　きのう　ともだちと　てにすを　して　つかれましたが　うみが　たのしみです。"}
            ],
            "question": "おとこのひとは　しゅうまつに　なにを　しますか。"
        },
        "analysis": {
            "vocabulary": [
                {"word": "しゅうまつ", "tr": "hafta sonu", "en": "weekend"},
                {"word": "うみ", "tr": "deniz", "en": "sea/beach"},
                {"word": "やすむ", "tr": "dinlenmek", "en": "to rest"},
                {"word": "たのしみ", "tr": "dört gözle beklemek", "en": "looking forward to"}
            ],
            "grammar": [
                {"point": "～たいです", "tr": "... yapmak istemek", "en": "want to do ..."},
                {"point": "～ています", "tr": "süregelen durum", "en": "ongoing state"}
            ]
        },
        "logic": {
            "tr": "Kadın dağa (やま) gitmek istiyor ama evde dinlenecek. Erkek dün tenis oynadı ama bu hafta sonu planı değil. Erkek açıkça ailesiyle denize (うみ) gideceğini söylüyor. Doğru cevap うみへいきます.",
            "en": "The woman wants to go to the mountains (やま) but will rest at home. The man played tennis yesterday but that's not his weekend plan. He clearly states he'll go to the beach (うみ) with his family. Correct: go to the beach."
        }
    }
]


def main():
    start_id = 3  # 002 already saved manually
    for i, q in enumerate(questions):
        qid = str(start_id + i).zfill(3)
        folder = os.path.join(OUTPUT_DIR, qid)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, "question_data.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(q, f, ensure_ascii=False, indent=4)
        print(f"  {qid}/question_data.json")
    print(f"\nToplam {len(questions)} soru kaydedildi (003-{str(start_id + len(questions) - 1).zfill(3)})")


if __name__ == "__main__":
    main()
