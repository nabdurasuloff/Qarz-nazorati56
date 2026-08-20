# -*- coding: utf-8 -*-
"""
main.py va importer.py ikkalasida ham kerak bo'ladigan umumiy funksiyalar.
"""
import re
import database as db

# Bank eksport faylida mijoz F.I.Sh oldiga qo'shilib qoladigan, hujjatlarda
# ko'rinishi kerak bo'lmagan prefikslar (huquqiy-tashkiliy shakl belgilari).
_ISM_PREFIKSLARI = [
    r'^ЯТТ\s*', r'^YATT\s*', r'^YaTT\s*', r'^YTT\s*',
    r'^ЯККА ТАРТИБДАГИ ТАДБИРКОР\s*', r'^YAKKA TARTIBDAGI TADBIRKOR\s*',
]


def clean_mijoz_ism(ism):
    """
    Mijoz F.I.Sh dagi "YATT"/"ЯТТ" kabi tashkiliy-huquqiy shakl
    prefikslarini olib tashlaydi — bular hujjatlarda (xat, Davo ariza,
    yig'ma jild) F.I.Sh oldida ko'rinib qolmasligi kerak. Ba'zan ikkita
    prefiks ustma-ust yozilgan bo'ladi (masalan "YATT ЯТТ ..."), shu sabab
    hech qanday prefiks qolmaguncha takroriy tozalanadi.
    """
    if not ism:
        return ism
    natija = str(ism).strip()
    while True:
        oldingi = natija
        for pattern in _ISM_PREFIKSLARI:
            natija = re.sub(pattern, '', natija, flags=re.IGNORECASE).strip()
        if natija == oldingi:
            break
    return natija


def turi_kodidan(mijoz_turi_kodi, mijoz_turi):
    """
    Jismoniy/yuridik/YaTT ekanini aniqlaydi. Asosiy manba — portfeldagi
    "Мижоз тури" ustuni ('LE' / 'Individual'), bu eng ishonchli maydon.

    Diqqat: "Жис/юр/Ятт коди" raqamli kodi ("mijoz_turi_kodi") mustaqil
    ishonchli belgi EMAS — tekshiruv shuni ko'rsatdiki, kod=8 (asosiy
    jismoniy) va kod=11 (YaTT) Individual'ga, kod=9 esa aslida YURIDIK
    (LE) ga to'g'ri keladi (2, 3, 7, 10, 12 kodlari ham barchasi LE).
    Shu sabab bu yerda faqat 'LE' matn qiymati tekshiriladi — FAQAT
    kod=11 (YaTT) bundan mustasno: garchi bank uni "Individual" deb
    belgilagan bo'lsa-da (chunki YaTT shaxsan jismoniy shaxs), YaTT
    tadbirkorlik faoliyati yuritgani uchun huquqiy jihatdan (xat turi,
    sud turi, Davo ariza turi) YURIDIK shaxsga o'xshab ko'riladi —
    nizolari odatda iqtisodiy sudda ko'riladi, fuqarolik sudida emas.
    Shu sabab alohida 'yatt' turi qaytariladi (kerakli joylarda
    `yuridik_kabi()` orqali yuridikka teng deb hisoblanadi).
    """
    turi = str(mijoz_turi or '').strip().upper()
    if turi == 'LE':
        return 'yuridik'
    kod = str(mijoz_turi_kodi or '').strip()
    if kod == '11':
        return 'yatt'
    return 'jismoniy'


def yuridik_kabi(turi):
    """
    Xat turi, sud turi, Davo ariza turi kabi HUQUQIY qarorlar uchun —
    yuridik shaxs VA YaTT ikkalasi ham "yuridik" kabi ko'riladi (garchi
    YaTT shaxsan jismoniy shaxs bo'lsa-da). Faqat statistik hisoblarda
    (Tahlil bo'limidagi jismoniy/yuridik soni kabi) bu funksiya
    ISHLATILMAYDI — u yerda haqiqiy shaxs turi (portfeldagi LE/Individual)
    ishlatiladi, chunki YaTT baribir jismoniy shaxs sifatida sanaladi.
    """
    return turi in ('yuridik', 'yatt')


def kalit_candidates(portfel_row):
    """
    Mijozni bog'lash uchun ishlatilishi mumkin bo'lgan ID'lar ro'yxati.

    MUHIM: bank eksport faylida jismoniy shaxslarning STIR maydoni ko'pincha
    "0" (bo'sh/placeholder qiymat) bo'lib to'ldiriladi — bu esa haqiqiy
    identifikator EMAS. Agar buni filtlamasak, "0" kalitiga ega BOSHQA
    (tasodifiy) mijoz Mijozlar bazasida topilib, unga noto'g'ri bog'lanib
    qolish xavfi bor (masalan xat/yig'ma jild boshqa odamning F.I.Sh bilan
    chiqib qolishi mumkin). Shu sabab bunday "soxta" qiymatlar chiqarib
    tashlanadi.
    """
    xom = [portfel_row.get('pinfl'), portfel_row.get('stir'), portfel_row.get('unikal')]
    natija = []
    for val in xom:
        if not val:
            continue
        val_str = str(val).strip()
        # "0", "00...0", bo'sh qatorlar — haqiqiy identifikator emas
        if not val_str or val_str.strip('0') == '':
            continue
        natija.append(val_str)
    return natija


def resolve_mijoz(portfel_row):
    """Portfel qatoriga mos mijozni (agar bazada bo'lsa) topadi. Topilgan
    (yoki topilmagan holda portfeldan olingan) F.I.Sh har doim "YATT" kabi
    prefikslardan tozalangan holda qaytariladi."""
    turi = turi_kodidan(portfel_row.get('mijoz_turi_kodi'), portfel_row.get('mijoz_turi'))
    for kalit in kalit_candidates(portfel_row):
        if not kalit:
            continue
        kalit = str(kalit).strip()
        m = db.find_mijoz(turi, kalit)
        if m:
            m = dict(m)
            m['ism'] = clean_mijoz_ism(m.get('ism'))
            return turi, m
    return turi, None
