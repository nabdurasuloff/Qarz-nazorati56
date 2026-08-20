# Qarz Nazorat va Talabnoma Tizimi

Bitta kompyuterda, internetsiz (oflayn) ishlaydigan dastur. Portfelni tahlil
qiladi, 45 kundan ko'p muddati o'tgan mijozlarni ajratadi va ularga
Ogohlantirish xati (jismoniy shaxs) / Talabnoma (yuridik shaxs) tayyorlaydi.

## 1. Kompyuterda ishga tushirish (test uchun, .exe siz)

Kompyuteringizda **Python 3.10+** o'rnatilgan bo'lishi kerak
(https://python.org — o'rnatishda "Add Python to PATH" belgisini bosing).

```
pip install -r requirements.txt
python main.py
```

Dastur ochiladi. Birinchi marta ishga tushganda `qarz_nazorat.db` fayli
avtomatik yaratiladi — bu sizning bazangiz, uni o'chirmang.

## 2. .EXE qilib yig'ish (Windows'da)

1. Ushbu papkani (`qarz_nazorat`) Windows kompyuteringizga ko'chiring.
2. Python o'rnatilganini tekshiring (`cmd` da `python --version`).
3. Papka ichida `build_exe.bat` faylini ikki marta bosing.
4. Bir necha daqiqadan so'ng `dist\QarzNazorat.exe` fayli tayyor bo'ladi.
5. Shu `.exe` faylni istalgan joyga (masalan Desktop'ga) ko'chirib, ishlatishingiz mumkin — endi Python ham, internet ham kerak emas.

**Muhim:** `.exe` ishga tushganda, u joylashgan papkada `qarz_nazorat.db`
va `yaratilgan_xatlar` papkasi avtomatik hosil bo'ladi — shu papkani
zaxira nusxalashni unutmang.

## 3. Navigatsiya tuzilishi (2026-yil yangilanishi)

Dastur menyusi endi quyidagi tartibda joylashgan — ba'zi bo'limlar endi
o'z ichida bir nechta **kichik bo'lim** (sub-tab)ga ega:

| Asosiy bo'lim | Kichik bo'limlari |
|---|---|
| **Bosh sahifa** | — |
| **Portfel** | — |
| **Mijozlar bazasi** | — |
| **Tahlil** *(yangi)* | — (portfel bo'yicha umumiy statistik tahlil) |
| **Reja Grafik** *(yangi)* | — (kunlik ish rejasi + tarmoq kesimida bajarilish) |
| **Talabnoma** | Yuborilishi kerak bo'lgan xatlar / Yuborilgan xatlar hisoboti / Sozlamalar |
| **Davo Ariza** | Tayyorlash — SSPga yuborish — Tasdiqlash / Sozlamalar |
| **SUD Ishlari** | SSPdan sudga jo'natiladiganlar / Suddan o'tkazilgan — MIB jarayonida / Hisobot |
| **MIB ijro harakatlari** | MIBda jarayondagi hujjatlar / Harakatsiz qolganlar / MIB Sozlamalari |
| **Vafot etganlar** | Qilingan ishlar / Sozlamalar |
| **95413** | — |
| **Chora ko'rish** | — |

Eslatma: yagona umumiy "Sozlamalar" bo'limi endi yo'q — har bir sozlama
o'ziga tegishli modulning "Sozlamalar" kichik bo'limiga ko'chirildi
(masalan bank/filial ma'lumotlari — Talabnoma, Davo ariza shablonlari —
Davo Ariza, BXM/MIB muddatlari — MIB ijro harakatlari, sug'urta
xabarnomasi shabloni — Vafot etganlar ichida).

### 3.1. Tahlil (yangi)

Butun portfel bo'yicha umumiy statistik ko'rinish:
- Jami portfeldagi mijozlar soni va jami EAD qoldiq
- Jismoniy va yuridik shaxslar bo'yicha alohida soni/summasi (portfeldagi
  "Мижоз тури" — LE/Individual — ustuniga asoslanadi, bu eng ishonchli
  manba)
- Stage 1 / Stage 2 / Stage 3 bo'yicha soni, summasi va portfeldagi
  **ulushi (%)** — progress-bar bilan
- Tarmoq (soha) kesimida EAD summasi — gorizontal bar-chart bilan

**"📄 Hisobotni yuklab olish"** — shu tahlilni Word yoki PDF formatda,
chinakam grafik (chart) rasmi bilan hisobot qilib chiqarib beradi.

### 3.2. Reja Grafik (yangi)

Bugungi kun uchun qilinishi kerak bo'lgan ishlar rejasi (Ogohlantirish
xati, Davo ariza, MIB ijro harakati) — har biri uchun alohida "Kerak /
Bajarildi / Qolib ketyapti" va umumiy bajarilish foizi. Pastda esa
**tarmoq kesimida**: qaysi tarmoqdan nechta xat tayyorlangani/
yuborilgani, Davo ariza qilingani, sudga va MIBga o'tkazilgani — jadval
ko'rinishida. Bu yerda ham Word/PDF hisobot eksporti mavjud.

## 4. Ishlatish tartibi (batafsil)

0. **Bosh sahifa** — umumiy holat, statistikalar va **"Bugungi ish kuni
   rejasi"** paneli shu yerda. Portfelda "Chora ko'rish" kerak bo'lgan
   barcha ishlar (xat yuborish, Davo ariza tayyorlash, MIB harakatlari)
   joriy oyning **20-sanasigacha** qolgan **ish kunlariga** (dushanba-juma,
   hafta oxiri hisobga olinmaydi) avtomatik **teng taqsimlanadi** —
   va bu **har bir ish turi uchun alohida-alohida** hisoblanadi:
   - **Ogohlantirish/Talabnoma xati** — kerak / bajarildi / qolib
     ketyapti (mini progress-bar bilan)
   - **Davo ariza** — kerak / bajarildi / qolib ketyapti
   - **MIB ijro harakati** — kerak / bajarildi / qolib ketyapti
   - **Kunlik ish rejasi umumiy bajarilishi** — foiz ko'rinishida
     (70%+ yashil, 30-70% sariq, 30%dan past qizil rangda)
   - Muddat (20-sana), qolgan ish kunlari soni
   - **Ish vaqti: 18:00 gacha** — agar soat 18:00dan o'tgan bo'lsa, "Bugungi
     ish vaqti tugagan — bajarilmagan ishlar ertangi rejaga o'tkaziladi"
     deb alohida ko'rsatiladi

   **Muhim:** bu reja **har safar sahifa yangilanganda, joriy qolgan ish
   sonidan qayta hisoblanadi** — shuning uchun bugun bajarilmay qolgan
   ishlar avtomatik ravishda ertangi (va undan keyingi) kunlarning
   rejasiga qo'shilib ketaveradi, qo'lda hech narsa qilish shart emas.
   Masalan, agar bugun 1600 ta ishdan faqat 5 tasi bajarilsa, ertaga
   tizim "qolgan ~1595 ta ÷ qolgan ish kunlari" asosida yangi, kattaroq
   kunlik rejani ko'rsatadi.

1. **Portfel** bo'limi — IFRS portfel hisobotini (`.xlsb`) yuklang.

   **Portfelni yangilash:** yangi oy/kunlik hisobot faylini xuddi shu tugma
   orqali qayta yuklashingiz kifoya. Dastur eski ma'lumotni o'chirmaydi —
   mavjud kreditlarni **yangilaydi** (yangi DPD, qarz summasi va h.k. bilan)
   va yangi kreditlarni qo'shadi. Bu orqali avval yaratilgan xatlar va
   Davo arizalarning tegishli kreditga bog'lanishi **saqlanib qoladi**.
2. **Mijozlar bazasi** — ikkita usul bor:
   - **Tavsiya etiladi:** bank tizimidan olingan xom matn (`.txt` yoki uni
     ichiga olgan `.zip`) faylni to'g'ridan-to'g'ri yuklang. Bu fayl Excel
     orqali o'tmagani uchun ma'lumot buzilmaydi, ustunlarni moslashtirish
     shart emas — dastur o'zi jismoniy/yuridik shaxsni aniqlaydi va
     ID_CLIENT/STIR/PINFL orqali avtomatik portfel bilan bog'laydi.
   - Muqobil: Excel (.xlsx) fayl — ustunlarni qo'lda moslashtirasiz.
3. **Tahlil / Talabnoma** — "Tahlil qilish" tugmasi 45+ kun (sozlamalarda
   o'zgartirish mumkin) muddati o'tgan mijozlarni ro'yxat qilib beradi.
   Ro'yxatda, standart holatda, faqat hali xati yaratilmagan yoki
   muddati o'tib ketgan mijozlar ko'rinadi — xat yaratilganlar avtomatik
   chiqib ketadi (checkbox orqali barchasini ko'rish mumkin).

   **Paketlarga bo'lib ishlash** (masalan 150 tani 30 tadan 5 paket qilib):
   - "Paket hajmi" (10/30/50/100/Barchasi) tanlang
   - "① Birinchi paketni belgilash" — ro'yxatdagi birinchi N tani avtomatik
     belgilaydi (yoki Ctrl/Shift bosib o'zingiz ham tanlashingiz mumkin)

   **Manzilni tekshirish/to'g'irlash** (xat yaratishdan oldin):
   - "📊 Excel'ga eksport qilish" — tanlangan mijozlar ro'yxatini (Ism,
     Manzil, Telefon va h.k.) Excel qilib beradi
   - Excel'da kerakli manzil/telefonni to'g'irlaysiz
   - "📥 Tahrirlangan Excel'ni yuklash" — tuzatilgan faylni qaytarib
     yuklaysiz, dastur o'zgargan manzilni **mijozlar bazasiga saqlab qoladi**
     (keyingi safar ham eslab qoladi)
   - So'ng "✉ Tanlanganlar uchun xat yaratish (ommaviy)" bosasiz — endi
     to'g'irlangan manzil bilan tayyorlanadi

   Yoki anketa raqami bo'yicha qidirib, bitta mijozga alohida xat
   yaratishingiz mumkin. Xatlar `yaratilgan_xatlar` papkasiga saqlanadi.

   **Fayl formati (Word / PDF):** shu bo'limda "Xat fayl formati" ochiladigan
   ro'yxatidan tanlaysiz. PDF formatini ishlatish uchun kompyuterda
   **Microsoft Word o'rnatilgan bo'lishi shart** (PDF Word orqali generatsiya
   qilinadi). Agar Word bo'lmasa, "Word (.docx)" ni tanlang.

3.1. **Chora ko'rish** — portfelni avtomatik tahlil qilib, har bir
   qoniqarsiz (muddati o'tgan) mijoz uchun **aynan qaysi chora zarurligini**
   ko'rsatadi:
   - **DPD 50+ kun**, so'nggi **2 oyda** xat yuborilmagan bo'lsa →
     "Ogohlantirish/Talabnoma xati yuborilishi kerak"
   - **DPD 60+ kun** (hali sudga/MIBga o'tmagan bo'lsa):
     - so'nggi **1 oyda** xat yuborilgan bo'lsa → "Davo ariza tayyorlab
       sudga yuborish kerak"
     - yuborilmagan bo'lsa → "Xat yuborilishi kerak (keyin Davo arizaga
       o'tkazish uchun)"
   - **MIBga o'tkazilgan**, lekin hali birorta ijro harakati qilinmagan
     bo'lsa → "MIBda ijro harakatlarini boshlash kerak"

   Yuqoridagi 4 xil chora bo'yicha yuqorida statistik kartochkalar, pastda
   esa filtrlash mumkin bo'lgan to'liq jadval ko'rsatiladi. "📊 Excel'ga
   eksport qilish" orqali bu ro'yxatni ham Excel faylga olishingiz mumkin.
   DPD chegaralari va oy muddatlari **Sozlamalar** bo'limidan
   o'zgartiriladi.

3.2. **95413 nazorati** — portfelda **"Колдик 95413"** deb nomlangan
   alohida balans ustuni bor: bu — balansdan maxsus nazoratga o'tkazilgan
   (odatda "ҳисобдан чиқарилган"/off-balance) kreditlarni bildiradi. Bunday
   kreditlarning DPD (muddati o'tgan kun) ko'rsatkichi odatda **deyarli
   nolga teng** bo'lib qoladi — shuning uchun ular "Tahlil" va
   "Chora ko'rish" kabi DPD-asoslangan bo'limlarda **umuman ko'rinmay**
   qolar edi.

   Bu bo'lim aynan shu muammoni hal qiladi: "Колдик 95413" balansiga ega
   **barcha** kreditlarni, DPD kunidan qat'i nazar, to'liq bosqichma-bosqich
   holati bilan ko'rsatadi — xat yuborilganmi, Davo ariza tayyorlanganmi,
   sudga topshirilganmi, MIBga o'tkazilganmi, yig'ma jild mavjudmi va
   (agar MIB bosqichida bo'lsa) MIB nazorat holati qanday. Yuqorida
   statistik kartochkalar (bosqichlar bo'yicha son va jami balans summasi),
   pastda esa filtrlash mumkin bo'lgan to'liq jadval bor. "📊 Excel'ga
   eksport qilish" orqali bu ro'yxatni ham Excel faylga olishingiz mumkin.

   Vafot etgan mijozlar bu ro'yxatdan ham avtomatik chiqarib tashlanadi.

4. **Xatlar holati** — yaratilgan barcha xatlar va ularning holati
   (Tayyor / Yuborildi / Muddati o'tgan) shu yerda ko'rinadi. Xat jo'natilgach
   "Yuborildi deb belgilash" tugmasini bosing. Agar xodim **3 kun** ichida
   belgilamasa, dastur ochilganda avtomatik ogohlantirish chiqadi.

5. **Davo ariza** — xati "Yuborildi" deb belgilangan barcha mijozlar shu
   bo'limda avtomatik ro'yxatga tushadi (agar xat hali yuborilmagan bo'lsa,
   Davo ariza tayyorlash imkonsiz — dastur buni aniq xabar bilan bildiradi
   va avval xatni yuborishni so'raydi).

   - **Ariza turi** tanlaysiz — 6 xil variant mavjud (real namunalaringiz
     asosida tayyorlangan):
     1. Jismoniy shaxs — oddiy (kafilsiz)
     2. Jismoniy shaxs — kafil bilan
     3. Yuridik/Ф.Х — oddiy (kafilsiz, Savdo-Sanoat Palatasiga)
     4. Yuridik shaxs — kafil bilan (foiz-penya undirish)
     5. Yuridik shaxs — kafil + garov mulkiga qaratish
     6. Shartnomani bekor qilish (muddatidan oldin undirish)
   - **Kafil/garov ma'lumotlari** (2, 4, 5, 6-turlar uchun kerak) — chunki
     bu ma'lumot portfelda yo'q, xodim **"✏ Kafil/garov ma'lumotini
     kiritish"** oynasi orqali qo'lda kiritadi (kafil F.I.Sh, manzil,
     PINFL, passport, garov mulki tavsifi va bahosi). Bir marta kiritilgan
     ma'lumot **anketa raqami bo'yicha saqlanib qoladi** — keyingi safar
     qayta kiritish shart emas.
   - **Avtomatik tavsiya**: jadvalda **"Tavsiya etilgan turi"** ustuni bor —
     agar mijoz uchun kafil/garov ma'lumoti kiritilgan bo'lsa, dastur mos
     Davo ariza turini o'zi aniqlab beradi (masalan kafillik bor bo'lsa —
     "kafil bilan" varianti). Ro'yxatdan bitta mijozni tanlaganingizda,
     **"Ariza turi" ochiladigan ro'yxati avtomatik shu tavsiyaga
     o'zgaradi** — kerak bo'lsa qo'lda boshqasini ham tanlashingiz mumkin.
   - **Excel orqali ommaviy tekshirish**: "📊 Ta'minot Excel'ini eksport
     qilish" — tanlangan mijozlar ro'yxatini (kafil/garov ustunlari bilan)
     Excel qilib beradi, siz to'ldirib/tuzatib, "📥 Tahrirlangan Excel'ni
     yuklash" orqali qaytarasiz — **saqlanib qoladi va eslab qolinadi**.
   - **Paket yoki bittalab**: Ctrl/Shift bilan bir nechta mijozni tanlab
     "⚖ Tanlanganlar uchun Davo ariza tayyorlash" bosasiz — barchasi bir
     vaqtda, tanlangan turdagi shablon bilan tayyorlanadi. Yoki bitta
     mijozni tanlab, alohida ham tayyorlash mumkin.
   - **Format**: Word yoki PDF — xuddi oddiy xatlardagi kabi tanlanadi.

   **"Olib kelindi" tasdiqlash va muddat kuzatuvi:** Davo ariza tayyorlab,
   Palata/sudga topshirilgandan (imzodan chiqarilgandan) keyin, uni
   **5 kun ichida qaytarib olib kelish** kerak. Olib kelingach, **"✓ Olib
   kelindi deb belgilash"** tugmasini bosing — shunda **ish raqami** va
   **imzodan chiqqan sana**ni kiritish so'raladi. Agar 5 kun ichida "Olib
   kelindi" deb belgilanmasa, ro'yxatda qator **qizil rangda** va "⚠ N kun
   o'tib ketdi" deb ko'rinadi, dastur ochilganda avtomatik ogohlantirish
   chiqadi, Bosh sahifada ham alohida ko'rsatkich sifatida ko'rinadi.

   **Davo summasi va qarzdorlik farqi nazorati:** Davo ariza yaratilgan
   paytda, o'sha kundagi jami muddati o'tgan qarz (asosiy qarz, foiz,
   jarima) **"surat" sifatida saqlanadi**. "Olib kelindi" deb
   belgilanganda, dastur bu saqlangan summani **bugungi joriy
   qarzdorlik** bilan avtomatik solishtiradi. Agar farq **BXMning bir
   barobaridan ko'p** bo'lsa (ya'ni qarz Davo ariza tayyorlangandan
   beri sezilarli o'sgan bo'lsa):
   - Darhol ogohlantirish chiqadi: farq summasiga **yangi (qo'shimcha)
     SSP davo ariza kiritish** va uni **sudga yo'naltirish** talab
     qilinadi
   - Jadvalda **"Summa farqi"** ustunida "⚠ Farq bor — qo'shimcha ariza
     kerak" deb, qator qizil rangda ko'rinadi

   **"📥 Imzodan kelganlarni Excel'ga eksport qilish"** — Palatadan/
   imzodan qaytgan barcha Davo arizalarni Excel faylga oladi. Faylda:
   mijoz, **PINFL**, ish raqami, chiqqan sana, Davo ariza yaratilgandagi
   summa (asosiy/foiz/jarima alohida-alohida va jami), bugungi joriy
   qarzdorlik, farq va "qo'shimcha ariza kerakmi" ustunlari bor.

   ⚠️ **Muhim:** Davo ariza matnlari sizning **haqiqiy namunalaringiz**
   asosida tayyorlangan (aynan matni saqlab qolingan, faqat o'zgaruvchi
   qismlar — ism, sana, summa — avtomatlashtirilgan). Shunga qaramay,
   ayniqsa **5 va 6-turlar** (garov mulki, shartnomani bekor qilish)
   har bir holat uchun individual bo'lgani sabab, yaratilgan hujjatni
   sudga/Palataga yuborishdan oldin **yuridik bo'lim albatta tekshirib
   chiqishi tavsiya etiladi**.

6. **Sud bazasi** — Davo ariza Palatadan (SSPdan) imzolanib qaytgach
   ("Olib kelindi" deb belgilangach), o'sha mijoz avtomatik shu bo'limga
   tushadi. Mijoz turiga qarab kerakli sud nomi (jismoniy shaxs uchun
   Fuqarolik sudi, yuridik shaxs uchun Iqtisodiy sudi) avtomatik ko'rsatiladi.

   **Kafil/Garov ustuni:** agar mijoz uchun kafil yoki garov ma'lumoti
   kiritilgan bo'lsa (Davo ariza bo'limida), qarzdor ismi yonida
   **"Kafil: F.I.Sh"** yoki **"Garov: tavsifi"** ko'rinishida darhol
   ko'rinadi — bu bosqichda kafil/garov borligini eslab qolish uchun.

   **Muddat:** Palatadan qaytgandan keyin, hujjat **5 kun ichida** sudga
   topshirilishi kerak. "✓ Sudga topshirildi deb belgilash" tugmasi orqali
   **sud ish raqami** va **topshirilgan sana**ni kiritasiz. Agar 5 kun
   ichida belgilanmasa, ro'yxatda qator qizil rangda ko'rinadi va dastur
   ochilganda avtomatik ogohlantirish chiqadi (Bosh sahifada ham alohida
   ko'rsatkich bor).

7. **MIB bazasi** — sudga topshirilgan hujjatlar bo'yicha ish yakunlangach,
   o'sha mijoz shu bo'limga tushadi (undirish jarayoni — Ijro byurosi
   bosqichi):
   - **"📤 MIBga o'tkazildi deb belgilash"** — ijro varaqasi (PDF) yuklaysiz,
     MIB ish raqamini kiritasiz. Solishtirish uchun sud ish raqami ham
     ko'rsatiladi.
   - **"➕ Yangi harakat qo'shish"** — MIBda amalga oshirilgan har bir
     harakatni sana bilan qayd qilib borasiz. 10 xil harakat turi mavjud:
     - **Oylik ish haqqiga qaratildi** — ushbu safar undirilgan summa
       (so'm) kiritiladi, shu orqali dastur oylik ish haqqidan qancha
       pul kelayotganini kuzatib boradi
     - Avto transportga taqiq qo'yildi
     - Avto transport qidiruvga berildi
     - Chetga chiqishga taqiq qo'yilgan
     - **Majburiy xatlov o'tkazildi** — mulk nomi, soni, summasi kiritiladi,
       dalolatnoma nusxasi (PDF) yuklanadi
     - **To'g'ridan-to'g'ri sotildi** — sotilgan mulk nomi, soni, summasi
     - **Auksion yo'li bilan sotildi** — auksion sanasi, narxi, lot raqami
       kiritiladi, lot rasmlari (.jpg/.png, bir nechtasi) yuklanadi
     - **Kafil bo'yicha ish qilindi** — mijozda kafil bo'lsa, unga nisbatan
       qilingan ishni qayd qilish uchun
     - **Garov mulkiga xatlov o'tkazildi** / **Garov mulki sotildi** —
       garov mulki (agar mavjud bo'lsa) bo'yicha jarayonlarni qayd qilish
       uchun (xuddi oddiy xatlov/sotish kabi, mulk ma'lumotlari bilan)
   - **"📋 Harakatlar tarixini ko'rish"** — bitta mijoz uchun barcha
     qilingan harakatlarni xronologik tartibda, fayllariga (dalolatnoma,
     rasmlar) bosib ochish imkoniyati bilan ko'rsatadi.

   **Kafil/Garov bo'yicha eslatma:** MIBga o'tkazish tasdiqlangan zahoti,
   agar mijozda kafil yoki garov mavjud bo'lsa, dastur alohida ogohlantirish
   ko'rsatadi — kafil bo'yicha ham, garov mulki bo'yicha ham MIB jarayoni
   ("Yangi harakat qo'shish" orqali) alohida kiritilib borilishi kerakligini
   eslatadi.

   **Nazorat holati (avtomatik solishtirish):** MIBga o'tkazish paytida
   qarzdorlik summasi "surat" sifatida saqlanadi (**MIB ijro summasi**).
   Shundan keyin dastur har safar quyidagilarni **avtomatik tekshirib
   boradi** va "Nazorat holati" ustunida ko'rsatadi:
   - **"⚠ To'xtatish/yakunlash kerak"** (qizil) — agar qarzdorlik tugagan
     bo'lsa, yoki DPD kuni **30 kundan kam** bo'lib qolgan bo'lsa, yoki
     MIB orqali undirilgan summa (oylik ish haqqi + sotilgan mulklar
     yig'indisi) MIBga o'tkazilgan summaga teng yoki undan ko'p bo'lsa —
     MIB harakatini to'xtatib, ishni yakunlash tavsiya etiladi.
   - **"⚠ Farq qo'shish kerak"** (sariq) — agar joriy qarzdorlik (foiz/jarima
     o'sishi hisobiga) MIBga o'tkazilgandagi summadan **BXMning bir
     barobaridan ko'proq** oshib ketgan bo'lsa — farq summasini qo'shimcha
     ijro harakatiga kiritish tavsiya etiladi.
   - Bo'sh (—) — hech qanday alohida chora talab qilinmaydi.

   BXM miqdori va to'xtatish uchun DPD chegarasi **Sozlamalar**dan
   o'zgartiriladi.

   **Harakatsizlik ogohlantirishi:** agar hujjat MIBga o'tkazilgandan
   (yoki oxirgi harakatdan) keyin **15 kun** ichida yangi harakat qayd
   qilinmasa, ro'yxatda qator qizil rangda ko'rinadi, dastur ochilganda
   avtomatik ogohlantirish chiqadi ("ijro harakati to'xtab qolgan bo'lishi
   mumkin") va Bosh sahifada ham alohida ko'rsatkich bo'ladi.

   **"📁 Eski MIB ishini kiritish"** — agar bu dasturdan tashqarida
   (avvalroq) MIBga topshirilgan ish bo'lsa, uni ham bazaga kiritib,
   nazorat ostiga olishingiz mumkin: anketa raqami bo'yicha portfeldan
   mijozni topib tanlaysiz, so'ng MIB ish raqami, o'tkazilgan sana va
   (agar mavjud bo'lsa) ijro varaqasini kiritasiz. Shundan keyin bu ish
   ham MIB bazasida, harakatlar jurnalida va 15 kunlik harakatsizlik
   nazoratida boshqa ishlar kabi to'liq kuzatib boriladi.

   **Yig'ma jild (Ijro harakati papkasi):** MIBga o'tkazish tasdiqlangan
   zahoti, dastur o'sha ish uchun **haqiqiy, doimiy papka** ochadi
   (`Yigma_jildlar/Mijoz_Ismi_Anketa_MIBIshRaqami/`) va unga avtomatik
   ravishda:
   - **Titul (muqova) hujjati** (`00_Titul.docx`) — ish raqami, mijoz,
     kredit va barcha bosqichlar (xat, Davo ariza, sud, MIB) sanalarini
     bir joyda ko'rsatuvchi hujjat
   - **Ijro varaqasi nusxasi** (`01_Ijro_varaqasi_...`)

   joylashtiriladi. Titul tayyor bo'lishi bilan tizim shu ish uchun
   **"Yig'ma jild mavjud"** deb belgilaydi (jadvalda alohida ustunda
   ko'rinadi) va titul hujjatini avtomatik ochib ko'rsatadi. Shundan
   keyin har safar "Yangi harakat qo'shish" orqali dalolatnoma yoki
   auksion lot rasmlari yuklaganingizda, ular ham **avtomatik shu bir
   jildga** qo'shilib boradi — shu bilan ish bo'yicha barcha hujjatlar
   doimiy ravishda bitta joyda to'planib boradi. Jildni istalgan vaqtda
   **"🗂 Yig'ma jildni ochish"** tugmasi orqali ochib ko'rish mumkin.

   **Avtomashinalar nazorati:** MIBga o'tkazilgan mijoz uchun **"🚗
   Avtomashinalar ro'yxati"** tugmasi orqali unga tegishli avtomashina(lar)ni
   qo'lda ro'yxatga olasiz (mashina rusumi, davlat raqami, mijoz PINFL).
   Har bir mashina quyidagi holatlardan birida bo'ladi:
   - **Xatlanmagan** — hali hech qanday chora ko'rilmagan (dastlabki holat)
   - **Taqiq qo'yilgan** — mashinaga taqiq qo'yilgan (asoslovchi hujjat va
     modda kiritilishi shart)
   - **Qidiruvda** — mashina topilmay, qidiruvga berilgan (asoslovchi
     hujjat va modda kiritilishi shart). Bu holatdagi mashinalar bo'yicha
     "MIB bazasi" sahifasida avtomatik ogohlantirish chiqadi: *"topilsa
     xatlash (majburiy xatlov) buyrug'i berilishi kerak"*
   - **Xatlangan (topilgan)** — mashina topilib, majburiy xatlov
     o'tkazilgan (yakuniy holat)

   **"📥 Excel orqali mashinalarni yuklash"** — bir nechta avtomashinani
   birdaniga, Excel jadval orqali ommaviy kiritish uchun. Kerakli ustunlar:
   **"Mashina rusumi"**, **"Davlat raqami"**, va kamida bittasi —
   **"Anketa raqami"** yoki **"Mijoz PINFL"**. Dastur har bir qatorni
   shu ustunlar orqali **avtomatik tegishli MIB ishiga bog'laydi** — qo'lda
   qaysi mijozga tegishli ekanini izlashning hojati yo'q. (Faqat allaqachon
   MIBga o'tkazilgan ishlarga bog'lanadi; agar mos ish topilmasa, natija
   xabarida "topilmadi" deb ko'rsatiladi.)

   **"📊 Xatlanmagan mashinalarni Excel'ga eksport qilish"** — hali hech
   qanday chora ko'rilmagan barcha avtomashinalarni (barcha mijozlar
   bo'yicha, bitta umumiy ro'yxatda) Excel faylga oladi: mashina rusumi,
   davlat raqami, mijoz PINFL, anketa raqami, mijoz nomi.

8. **Vafot etganlar** — vafot etgan mijozlarga nisbatan **hech qanday
   undirish chorasi (xat, Davo ariza, MIB) ko'rilmaydi** — bunday mijozlar
   avtomatik ravishda "Tahlil" va "Chora ko'rish" ro'yxatlaridan chiqarib
   tashlanadi. Faqat sug'urta polisi mavjud va muddati o'tmagan bo'lsa,
   sug'urta kompaniyasidan kreditni qoplashni so'rash jarayoni shu bo'limda
   yuritiladi:
   - **"➕ Yangi vafot etgan mijoz"** — anketa raqami bo'yicha portfeldan
     mijozni topib tanlaysiz, vafot sanasini kiritasiz, **o'limlik
     guvohnomasi** va **pasport nusxasini** (.pdf/.jpg/.png) yuklaysiz.
     Dastur darhol **avtomatik aniqlaydi**: sug'urta polisi muddati
     o'tganmi yoki yo'qmi — bu odatda kredit tugash sanasi bilan bir xil
     bo'lgani uchun, portfeldagi shartnoma tugash sanasi bilan solishtirib
     hisoblanadi.
   - Agar polis **"✓ Amalda"** bo'lsa:
     - **"💼 Sug'urta ma'lumotini kiritish"** — sug'urta kompaniya nomi,
       polis raqami va polis nusxasini (PDF) kiritasiz
     - **"✉ Xabarnoma tayyorlash"** — sug'urta kompaniyasiga yuboriladigan
       xabarnoma hujjatini avtomatik tayyorlaydi (mijoz, kredit, vafot va
       sug'urta ma'lumotlari bilan to'ldirilgan holda). Yonidagi
       **"Format"** ochiladigan ro'yxatidan **Word (.docx)** yoki
       **PDF (.pdf)** tanlash mumkin — xuddi Davo arizadagi kabi (PDF
       uchun Microsoft Word o'rnatilgan bo'lishi shart).
     - **"✓ Yuborildi deb belgilash"** — xabarnoma yuborilgan sanani
       kiritasiz
     - **"✓ Javob keldi deb belgilash"** — sug'urta kompaniyasidan javob
       kelgach, sanasini (va ixtiyoriy ravishda javob xatini) kiritasiz
   - Agar polis **"⚠ Muddati o'tgan"** bo'lsa — sug'urta orqali qoplash
     imkoni yo'q, jarayon shu yerda to'xtaydi.

   **Javob muddati nazorati:** xabarnoma yuborilgandan keyin, sug'urta
   kompaniyasidan **40 ish kuni** (dam olish kunlarisiz) ichida javob
   kelishi kutiladi. Agar shu muddatda javob kelmasa, ro'yxatda qator
   qizil rangda ko'rinadi, dastur ochilganda avtomatik ogohlantirish
   chiqadi va Bosh sahifada ham alohida ko'rsatkich bo'ladi.

   **"📎 Hujjatlarni ko'rish"** — bitta mijoz uchun yuklangan barcha
   hujjatlarni (o'limlik guvohnomasi, pasport, polis, sug'urta javobi)
   bir joydan ochib ko'rish imkonini beradi.

   Javob kutish muddati (ish kuni) **Sozlamalar**dan o'zgartiriladi.
   Xabarnoma shabloni ham **Sozlamalar** bo'limidan yuklab
   almashtirilishi mumkin (standart namunaviy shablon allaqachon
   o'rnatilgan).

9. **Davo ariza hisoboti** — barcha tayyorlangan Davo arizalar bo'yicha
   to'liq jadval: mijoz, qarzdorlik summasi, ariza qachon tayyorlangani,
   Palatadan qachon/qancha vaqtda qaytgani (ish raqami bilan), va sudga
   qachon topshirilgani (sud ish raqami bilan) — bitta joyda, boshidan
   oxirigacha butun jarayon. "📊 Excel'ga eksport qilish" orqali bu
   hisobotni Excel faylga ham olishingiz mumkin.

10. **Sozlamalar** — bank nomi, filial nomi, telefon, 45 kunlik chegara,
   3 kunlik xat yuborish muddati, 5 kunlik Davo ariza "olib kelish"
   muddati, 5 kunlik sudga topshirish muddati, 15 kunlik MIB
   harakatsizlik ogohlantirish muddati, 40 ish kunlik sug'urta javob
   kutish muddati, sud nomlari, Savdo-Sanoat Palatasi rekvizitlari va
   davo ariza imzolovchisi shu yerdan o'zgartiriladi.

   **Shablonni yangilash** — xat shabloni (Word) o'zgarsa, shu yerdan yangi
   `.docx` faylni yuklaysiz. Yuklagach, hali yuborilmagan ("Tayyor"
   holatidagi) barcha xatlar avtomatik ravishda yangi shablon bilan
   qayta tayyorlanadi (savol chiqadi — "Ha" desangiz).

   **Davo ariza shablonlarini yangilash** — shu bo'limning pastida, 6 xil
   Davo ariza turidan birini tanlab, uning shablonini alohida yangilashingiz
   mumkin ("Davo ariza shablonlari" qismi). Yangilagach, shu turdagi, hali
   "Olib kelindi" deb belgilanmagan arizalarni yangi shablon bilan qayta
   tayyorlash so'raladi (savol chiqadi — "Ha" desangiz).

## 3.1. Fayllar qanday saqlanadi

Yaratilgan barcha hujjatlar `yaratilgan_xatlar` papkasi ichida, **tayyorlangan
kuniga mos sana bo'yicha**, so'ng **hujjat turiga qarab** alohida papkalarga
saqlanadi. Masalan, 15.08.2026 kunlik tuzilma shunday ko'rinadi:

```
yaratilgan_xatlar/
└── 15.08.2026/
    ├── Xatlar/           ← Ogohlantirish / Talabnoma
    ├── Davo ariza/       ← barcha turdagi Davo arizalar
    ├── Sud buyrug'i/     ← sudning qarori (agar yuklangan bo'lsa)
    └── Ijro varaqa/      ← MIBga o'tkazishda yuklangan ijro varaqasi
```

Dalolatnoma va auksion lot rasmlari kabi qo'shimcha MIB fayllari esa
alohida `mib_hujjatlar` papkasida, xuddi shunday sana bo'yicha saqlanadi.

## 3.2. Mijozni anketa raqami bo'yicha qidirish

**Bosh sahifa**da, "So'nggi harakatlar" bo'limi ustida qidiruv qutisi bor.
Anketa raqamini kiritib qidirsangiz, o'sha mijoz (yoki agar bir nechta
kreditga tegishli bo'lsa — barchasi) uchun **to'liq bosqich holati**
ko'rsatiladi: xat yuborilganmi, Davo ariza qaysi bosqichda, sudga
topshirilganmi va ish raqami, MIBga o'tkazilganmi va u yerda so'nggi qanday
harakat (masalan "Oylik ish haqqiga qaratildi") qilingani. Bu — har bir
mijozning ayni damda qaysi jarayonda turganini tezda bilib olish uchun
mo'ljallangan.

## 4. Hozircha ochiq qolgan masalalar

- **Mijozlar bazasi**: endi bank tizimidan olingan xom matn (`.txt`/`.zip`)
  fayldan to'g'ridan-to'g'ri, aniq import qilinadi (`CODE_SUBJECT` ustuni
  orqali jismoniy/yuridik avtomatik aniqlanadi; ID_CLIENT, STIR va PINFL —
  uchalasi bo'yicha ham saqlanadi, shunda portfel bilan bog'lanish ehtimoli
  maksimal bo'ladi). Test qilingan real ma'lumotda 45+ kun muddati o'tgan
  mijozlarning ~16% i uchun real manzil/telefon topildi — bu ko'rsatkich
  mijozlar bazasi qanchalik to'liq bo'lishiga bog'liq (baza qanchalik keng
  bo'lsa, moslik foizi shunchalik oshadi).
- **Talabnoma matni**: hozircha Ogohlantirish xatiga o'xshab, faqat sarlavha
  "ТАЛАБНОМА" deb almashtirilgan. Matn boshqacha bo'lishi kerak bo'lsa,
  ayting — alohida shablon tuzib beraman.

## 5. Fayl tuzilishi

```
qarz_nazorat/
├── main.py              # Dastur oynasi (GUI)
├── database.py          # SQLite baza
├── importer.py          # Excel/XLSB import
├── letters.py           # Word xat generatsiyasi
├── templates/
│   └── xat_shablon.docx # Xat shabloni
├── requirements.txt
├── build_exe.bat        # .exe yig'ish uchun
└── README.md
```
