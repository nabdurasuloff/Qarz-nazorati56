# -*- coding: utf-8 -*-
"""
Qarz Nazorat Dastur — Bosh oyna (Tkinter GUI)

Ishga tushirish:  python main.py
"""
import os
import sys

# PyInstaller --windowed (konsolsiz) rejimida ishga tushirilganda sys.stdout/
# sys.stderr None bo'lib qoladi. Bu holat docx2pdf kabi ba'zi kutubxonalarni
# ("'NoneType' object has no attribute 'write'" xatosi bilan) buzadi.
# Shuning uchun bularni eng boshida, zararsiz "null" oqimga almashtiramiz.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

import threading
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import database as db
import importer
import letters
import util

def _app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = _app_dir()
XATLAR_DIR = os.path.join(APP_DIR, 'yaratilgan_xatlar')
MIB_HUJJATLAR_DIR = os.path.join(APP_DIR, 'mib_hujjatlar')
YIGMA_JILD_DIR = os.path.join(APP_DIR, 'Yigma_jildlar')


def yigma_jild_papka_yarat(mijoz_ism, anketa_raqami, mib_ish_raqami):
    """
    Bitta ijro ishi uchun HAQIQIY, doimiy yig'ma jild papkasini yaratadi
    (sana bo'yicha emas — ish bo'yicha), unga tegishli barcha hujjatlar
    (titul, ijro varaqasi, dalolatnoma, sotuv hujjatlari) to'planib boradi.
    """
    papka_nomi = f"{letters.safe_filename(mijoz_ism)}_{letters.safe_filename(anketa_raqami)}_" \
                 f"{letters.safe_filename(mib_ish_raqami)}"
    papka = os.path.join(YIGMA_JILD_DIR, papka_nomi)
    os.makedirs(papka, exist_ok=True)
    return papka


def bugungi_papka(tur=None):
    """
    Bugungi sana bo'yicha papka (masalan yaratilgan_xatlar/14.08.2026) — mavjud
    bo'lmasa yaratadi. 'tur' berilsa, hujjat turi bo'yicha ichki papka ham
    yaratiladi (masalan yaratilgan_xatlar/14.08.2026/Xatlar).
    """
    sana_papka = datetime.date.today().strftime('%d.%m.%Y')
    path = os.path.join(XATLAR_DIR, sana_papka)
    if tur:
        path = os.path.join(path, tur)
    os.makedirs(path, exist_ok=True)
    return path


def mib_bugungi_papka(tur=None):
    """
    MIB hujjatlari (dalolatnoma, auksion rasmlari) uchun sana bo'yicha papka.
    'Ijro varaqa' kabi asosiy hujjat turlari endi bugungi_papka() orqali
    yaratilgan_xatlar ichida saqlanadi — bu funksiya faqat dalolatnoma/
    rasmlar kabi qo'shimcha MIB fayllari uchun ishlatiladi.
    """
    sana_papka = datetime.date.today().strftime('%d.%m.%Y')
    path = os.path.join(MIB_HUJJATLAR_DIR, sana_papka)
    if tur:
        path = os.path.join(path, tur)
    os.makedirs(path, exist_ok=True)
    return path


def fayl_nusxala(manba_yol, maqsad_papka, prefiks='', mijoz_nomi=''):
    """Tanlangan faylni maqsad papkaga nusxalab, yangi yo'lni qaytaradi."""
    import shutil
    if not manba_yol:
        return None
    ext = os.path.splitext(manba_yol)[1]
    mijoz_qismi = f"_{letters.safe_filename(mijoz_nomi)}" if mijoz_nomi else ''
    fname = f"{prefiks}{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}{mijoz_qismi}{ext}"
    dest = os.path.join(maqsad_papka, fname)
    shutil.copy2(manba_yol, dest)
    return dest


def yigma_jild_toldirish(jild_papka, xat):
    """
    Yig'ma jild yaratilganda (yoki keyinchalik yangilanganda), shu ishga
    tegishli AVVAL yaratilgan barcha hujjatlarni (Ogohlantirish/Talabnoma
    xati, Davo ariza, Sud buyrug'i, Ijro varaqasi) — qaysi biri mavjud
    bo'lsa — avtomatik ravishda jildga nusxalab qo'yadi. Bu funksiya
    "backfill" sifatida ham (jild birinchi marta ochilganda, undan oldin
    yaratilgan hujjatlarni yig'ish uchun), ham keyingi yangilanishlarda
    ishlatilishi mumkin. Fayl mavjud bo'lmasa yoki topilmasa, sekin
    o'tkazib yuboriladi (xato bermaydi).
    """
    if not jild_papka or not os.path.isdir(jild_papka):
        return
    hujjatlar = [
        ('fayl_yoli', '02_Xat_'),
        ('davo_ariza_fayl_yoli', '03_Davo_ariza_'),
        ('sud_buyrugi_fayl', '04_Sud_buyrugi_'),
        ('ijro_varaqasi_fayl', '01_Ijro_varaqasi_'),
    ]
    for maydon, prefiks in hujjatlar:
        manba = xat.get(maydon)
        if manba and os.path.exists(manba):
            # Bir xil fayl ikki marta qo'shilib qolmasligi uchun, shu prefiks
            # bilan boshlangan fayl allaqachon jildda bor-yo'qligini tekshiramiz
            allaqachon_bor = any(f.startswith(prefiks) for f in os.listdir(jild_papka))
            if not allaqachon_bor:
                fayl_nusxala(manba, jild_papka, prefiks=prefiks)

BG = '#F4F6FB'
INK = '#1B2033'
STAMP = '#1E2761'
KRAFT = '#B7862C'
WHITE = '#FFFFFF'
ERR = '#C0392B'
NAVY_DARK = '#141B4D'
NAVY_HOVER = '#232C63'
ICE = '#CADCFC'
GOLD = '#C9A227'
LINE = '#E3E7F0'
MUTED = '#6B7280'


resolve_mijoz = util.resolve_mijoz  # qulaylik uchun shu modulda ham mavjud


class Sidebar(tk.Frame):
    """Chap tomondagi zamonaviy navigatsiya paneli (yuqoridagi tab qatorini almashtiradi)."""
    def __init__(self, parent, on_select, items):
        super().__init__(parent, bg=NAVY_DARK, width=232)
        self.pack_propagate(False)
        self.on_select = on_select
        self.active_key = None
        self.entries = {}

        title = tk.Frame(self, bg=NAVY_DARK, height=76)
        title.pack(fill='x')
        title.pack_propagate(False)
        tk.Label(title, text="🏦  Qarz Nazorat", bg=NAVY_DARK, fg=WHITE,
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', padx=20, pady=(16, 0))
        tk.Label(title, text="Talabnoma Tizimi", bg=NAVY_DARK, fg=GOLD,
                 font=('Segoe UI', 9)).pack(anchor='w', padx=20, pady=(1, 0))

        tk.Frame(self, bg='#2E3B7A', height=1).pack(fill='x')

        canvas = tk.Canvas(self, bg=NAVY_DARK, highlightthickness=0, width=232)
        vscroll = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas, bg=NAVY_DARK)
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inner, anchor='nw', width=232)
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side='left', fill='both', expand=True)
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        for item in items:
            if item[0] == 'sep':
                tk.Frame(inner, bg='#2E3B7A', height=1).pack(fill='x', padx=18, pady=8)
                continue
            key, icon, label = item
            self._add_entry(inner, key, icon, label)

        footer = tk.Frame(self, bg=NAVY_DARK)
        footer.pack(side='bottom', fill='x', pady=14)
        tk.Label(footer, text="Agrobank ATB — Boyovut", bg=NAVY_DARK, fg='#5B6BA8',
                 font=('Segoe UI', 8)).pack(anchor='w', padx=20)

    def _add_entry(self, parent, key, icon, label):
        row = tk.Frame(parent, bg=NAVY_DARK, cursor='hand2')
        row.pack(fill='x')
        indicator = tk.Frame(row, bg=NAVY_DARK, width=4)
        indicator.pack(side='left', fill='y')
        body = tk.Frame(row, bg=NAVY_DARK)
        body.pack(side='left', fill='both', expand=True)
        icon_lbl = tk.Label(body, text=icon, bg=NAVY_DARK, fg=ICE, font=('Segoe UI', 12), width=2)
        icon_lbl.pack(side='left', padx=(16, 8), pady=10)
        text_lbl = tk.Label(body, text=label, bg=NAVY_DARK, fg=ICE, font=('Segoe UI', 10, 'bold'),
                             anchor='w')
        text_lbl.pack(side='left', fill='x', expand=True, pady=10)

        widgets = [row, body, icon_lbl, text_lbl]
        for w in widgets:
            w.bind('<Button-1>', lambda e, k=key: self.on_select(k))
            w.bind('<Enter>', lambda e, k=key: self._hover(k, True))
            w.bind('<Leave>', lambda e, k=key: self._hover(k, False))
        self.entries[key] = {'row': row, 'body': body, 'icon': icon_lbl, 'text': text_lbl,
                              'indicator': indicator}

    def _hover(self, key, entering):
        if key == self.active_key:
            return
        e = self.entries[key]
        color = NAVY_HOVER if entering else NAVY_DARK
        e['row'].configure(bg=color)
        e['body'].configure(bg=color)
        e['icon'].configure(bg=color)
        e['text'].configure(bg=color)

    def set_active(self, key):
        if self.active_key and self.active_key in self.entries:
            old = self.entries[self.active_key]
            for w in (old['row'], old['body'], old['icon'], old['text']):
                w.configure(bg=NAVY_DARK)
            old['indicator'].configure(bg=NAVY_DARK)
            old['icon'].configure(fg=ICE)
            old['text'].configure(fg=ICE, font=('Segoe UI', 10, 'bold'))
        self.active_key = key
        new = self.entries[key]
        for w in (new['row'], new['body'], new['icon'], new['text']):
            w.configure(bg=NAVY_HOVER)
        new['indicator'].configure(bg=GOLD)
        new['icon'].configure(fg=GOLD)
        new['text'].configure(fg=WHITE)


SIDEBAR_ITEMS = [
    ('bosh_sahifa', '🏠', 'Bosh sahifa'),
    ('portfel', '🗂', 'Portfel'),
    ('mijozlar', '👥', 'Mijozlar bazasi'),
    ('sep',),
    ('tahlil', '📊', 'Tahlil'),
    ('reja', '🗓', 'Reja Grafik'),
    ('sep',),
    ('talabnoma', '✉', 'Talabnoma'),
    ('davo', '📄', 'Davo Ariza'),
    ('sud', '⚖', 'SUD Ishlari'),
    ('mib', '🚔', 'MIB ijro harakatlari'),
    ('vafot', '🕊', 'Vafot etganlar'),
    ('sep',),
    ('nazorat95413', '🗃', '95413'),
    ('chora', '🎯', "Chora ko'rish"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Qarz Nazorat va Talabnoma Tizimi")
        self.geometry("1360x790")
        self.configure(bg=BG)

        self._setup_style()

        root_frame = tk.Frame(self, bg=BG)
        root_frame.pack(fill='both', expand=True)

        self.sidebar = Sidebar(root_frame, self.show_page, SIDEBAR_ITEMS)
        self.sidebar.pack(side='left', fill='y')

        content_outer = tk.Frame(root_frame, bg=BG)
        content_outer.pack(side='left', fill='both', expand=True)
        self.container = tk.Frame(content_outer, bg=BG)
        self.container.pack(fill='both', expand=True, padx=14, pady=14)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.page_refresh = {}

        def register(key, frame, refresh_fn=None):
            frame.grid(row=0, column=0, sticky='nsew', in_=self.container)
            self.pages[key] = frame
            if refresh_fn:
                self.page_refresh[key] = refresh_fn

        # ---- Mustaqil (standalone) bo'limlar ----
        self.tab_dashboard = DashboardTab(self.container, self)
        self.tab_portfel = PortfelTab(self.container, self)
        self.tab_mijozlar = MijozlarTab(self.container, self)
        self.tab_analitika = AnalitikaTab(self.container, self)
        self.tab_reja = RejaGrafikTab(self.container, self)
        register('bosh_sahifa', self.tab_dashboard, self.tab_dashboard.refresh)
        register('portfel', self.tab_portfel)
        register('mijozlar', self.tab_mijozlar)
        register('tahlil', self.tab_analitika, self.tab_analitika.refresh)
        register('reja', self.tab_reja, self.tab_reja.refresh)

        # ---- Talabnoma (Yuborilishi kerak / Yuborilgan hisoboti / Sozlamalar) ----
        talabnoma_frame, self.talabnoma_inner = build_module(self.container)
        self.tab_talabnoma_xat = TahlilTab(self.talabnoma_inner, self)
        self.tab_talabnoma_hisobot = XatlarTab(self.talabnoma_inner, self)
        self.tab_talabnoma_sozlamalar = SozlamalarGuruh(
            self.talabnoma_inner, self, "Talabnoma sozlamalari",
            TALABNOMA_SOZLAMA_FIELDS, sections=['xat_shablon'])
        self.talabnoma_inner.add(self.tab_talabnoma_xat, text="  Yuborilishi kerak bo'lgan xatlar  ")
        self.talabnoma_inner.add(self.tab_talabnoma_hisobot, text='  Yuborilgan xatlar hisoboti  ')
        self.talabnoma_inner.add(self.tab_talabnoma_sozlamalar, text='  Sozlamalar  ')
        self.talabnoma_inner.bind('<<NotebookTabChanged>>', self._on_subtab_changed)
        register('talabnoma', talabnoma_frame, self.tab_talabnoma_xat.refresh_stats)

        # ---- Davo Ariza (Tayyorlash+SSP / Sozlamalar) ----
        davo_frame, self.davo_inner = build_module(self.container)
        self.tab_davo = DavoArizaTab(self.davo_inner, self)
        self.tab_davo_sozlamalar = SozlamalarGuruh(
            self.davo_inner, self, "Davo ariza sozlamalari",
            DAVO_ARIZA_SOZLAMA_FIELDS, sections=['davo_shablon'])
        self.davo_inner.add(self.tab_davo, text="  Tayyorlash / SSPga yuborish / Tasdiqlash  ")
        self.davo_inner.add(self.tab_davo_sozlamalar, text='  Sozlamalar  ')
        self.davo_inner.bind('<<NotebookTabChanged>>', self._on_subtab_changed)
        register('davo', davo_frame, self.tab_davo.refresh)

        # ---- SUD Ishlari (SSPdan sudga / Sud->MIB jarayonida / Hisobot) ----
        sud_frame, self.sud_inner = build_module(self.container)
        self.tab_sud = SudBazaTab(self.sud_inner, self)
        self.tab_sud_mib_jarayon = SudMibJarayonidaTab(self.sud_inner, self)
        self.tab_davo_hisobot = DavoHisobotTab(self.sud_inner, self)
        self.sud_inner.add(self.tab_sud, text='  SSPdan o\'tib sudga jo\'natiladiganlar  ')
        self.sud_inner.add(self.tab_sud_mib_jarayon, text='  Suddan o\'tkazilgan / MIB jarayonida  ')
        self.sud_inner.add(self.tab_davo_hisobot, text='  Hisobot  ')
        self.sud_inner.bind('<<NotebookTabChanged>>', self._on_subtab_changed)
        register('sud', sud_frame, self.tab_sud.refresh)

        # ---- MIB ijro harakatlari (Jarayondagilar / Harakatsizlar / Yakunlangan / Sozlamalar) ----
        mib_frame, self.mib_inner = build_module(self.container)
        self.tab_mib = MibBazaTab(self.mib_inner, self)
        self.tab_mib_harakatsiz = MibHarakatsizlarTab(self.mib_inner, self)
        self.tab_mib_yakunlangan = MibYakunlanganTab(self.mib_inner, self)
        self.tab_mib_sozlamalar = SozlamalarGuruh(
            self.mib_inner, self, "MIB sozlamalari", MIB_SOZLAMA_FIELDS, sections=['yigma_jild_shablon'])
        self.mib_inner.add(self.tab_mib, text='  MIBda jarayondagi hujjatlar  ')
        self.mib_inner.add(self.tab_mib_harakatsiz, text='  Harakatsiz qolganlar  ')
        self.mib_inner.add(self.tab_mib_yakunlangan, text='  Yakunlangan ishlar  ')
        self.mib_inner.add(self.tab_mib_sozlamalar, text='  MIB Sozlamalari  ')
        self.mib_inner.bind('<<NotebookTabChanged>>', self._on_subtab_changed)
        register('mib', mib_frame, self.tab_mib.refresh)

        # ---- Vafot etganlar (Qilingan ishlar / Sozlamalar) ----
        vafot_frame, self.vafot_inner = build_module(self.container)
        self.tab_vafot = VafotEtganlarTab(self.vafot_inner, self)
        self.tab_vafot_sozlamalar = SozlamalarGuruh(
            self.vafot_inner, self, "Vafot etganlar sozlamalari",
            VAFOT_SOZLAMA_FIELDS, sections=['sugurta_shablon'])
        self.vafot_inner.add(self.tab_vafot, text='  Qilingan ishlar  ')
        self.vafot_inner.add(self.tab_vafot_sozlamalar, text='  Sozlamalar  ')
        self.vafot_inner.bind('<<NotebookTabChanged>>', self._on_subtab_changed)
        register('vafot', vafot_frame, self.tab_vafot.refresh)

        # ---- Mustaqil qolgan bo'limlar ----
        self.tab_95413 = Nazorat95413Tab(self.container, self)
        self.tab_chora = ChoraKorishTab(self.container, self)
        register('nazorat95413', self.tab_95413, self.tab_95413.refresh)
        register('chora', self.tab_chora, self.tab_chora.refresh)

        self.show_page('bosh_sahifa')
        self._check_muddat_otganlar()

    def show_page(self, key):
        frame = self.pages.get(key)
        if not frame:
            return
        frame.tkraise()
        self.sidebar.set_active(key)
        fn = self.page_refresh.get(key)
        if fn:
            try:
                fn()
            except Exception:
                pass

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[16, 10],
                         background='#E9ECF5', foreground=INK)
        style.map('TNotebook.Tab', background=[('selected', STAMP)], foreground=[('selected', WHITE)])
        style.configure('TFrame', background=BG)
        style.configure('TLabel', background=BG, foreground=INK, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 17, 'bold'), foreground=INK)
        style.configure('Sub.TLabel', font=('Segoe UI', 9), foreground=MUTED)
        style.configure('Stat.TLabel', font=('Consolas', 22, 'bold'), foreground=STAMP)
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.configure('Accent.TButton', background=STAMP, foreground=WHITE)
        style.map('Accent.TButton', background=[('active', '#2B3676')])
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=28, fieldbackground=WHITE,
                         background=WHITE, borderwidth=0)
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'), background='#EEF1F8',
                         foreground=INK, relief='flat')
        style.map('Treeview', background=[('selected', '#D7DEF5')], foreground=[('selected', INK)])
        style.map('Treeview.Heading', background=[('active', '#E4E9F5')])

    def _on_subtab_changed(self, event):
        current = event.widget.tab(event.widget.select(), 'text').strip()
        refresh_map = {
            "Yuborilishi kerak bo'lgan xatlar": self.tab_talabnoma_xat.refresh_stats,
            'Yuborilgan xatlar hisoboti': self.tab_talabnoma_hisobot.refresh,
            'Tayyorlash / SSPga yuborish / Tasdiqlash': self.tab_davo.refresh,
            "SSPdan o'tib sudga jo'natiladiganlar": self.tab_sud.refresh,
            "Suddan o'tkazilgan / MIB jarayonida": self.tab_sud_mib_jarayon.refresh,
            'Hisobot': self.tab_davo_hisobot.refresh,
            'MIBda jarayondagi hujjatlar': self.tab_mib.refresh,
            'Harakatsiz qolganlar': self.tab_mib_harakatsiz.refresh,
            'Yakunlangan ishlar': self.tab_mib_yakunlangan.refresh,
            'Qilingan ishlar': self.tab_vafot.refresh,
        }
        fn = refresh_map.get(current)
        if fn:
            fn()

    def _check_muddat_otganlar(self):
        n = db.update_muddati_otganlar()
        n_davo = len(db.get_davo_ariza_muddati_otganlar())
        n_sud = len(db.get_sud_topshirish_muddati_otganlar())
        n_mib = len(db.get_mib_harakatsizlar())
        n_sugurta = len(db.get_sugurta_javob_kutilayotganlar())
        if n > 0 or n_davo > 0 or n_sud > 0 or n_mib > 0 or n_sugurta > 0:
            xabar = []
            if n > 0:
                xabar.append(f"• {n} ta xat yuborish muddati tugagan! 'Talabnoma' bo'limini tekshiring.")
            if n_davo > 0:
                xabar.append(f"• {n_davo} ta Davo ariza tayyorlangan, lekin belgilangan muddat (5 kun) "
                              f"ichida 'Olib kelindi' deb belgilanmagan! 'Davo Ariza' bo'limini tekshiring.")
            if n_sud > 0:
                xabar.append(f"• {n_sud} ta hujjat Palatadan qaytgan, lekin belgilangan muddat (5 kun) "
                              f"ichida sudga topshirilmagan! 'SUD Ishlari' bo'limini tekshiring.")
            if n_mib > 0:
                xabar.append(f"• {n_mib} ta mijoz bo'yicha MIBda 15 kundan ortiq hech qanday harakat "
                              f"kuzatilmadi — ijro harakati to'xtab qolgan bo'lishi mumkin! "
                              f"'MIB ijro harakatlari' bo'limini tekshirib, ijro harakatini boshlang.")
            if n_sugurta > 0:
                xabar.append(f"• {n_sugurta} ta vafot etgan mijoz bo'yicha sug'urta kompaniyasidan "
                              f"belgilangan muddatda (40 ish kuni) javob kelmadi! "
                              f"'Vafot etganlar' bo'limini tekshiring.")
            messagebox.showwarning("Eslatma", "\n\n".join(xabar))
        self.after(60 * 60 * 1000, self._check_muddat_otganlar)  # har soatda tekshirish


class ScrollableFrame(ttk.Frame):
    """Vertikal scroll qila oladigan konteyner."""
    def __init__(self, parent):
        super().__init__(parent)
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.body = ttk.Frame(canvas)

        self.body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas_window = canvas.create_window((0, 0), window=self.body, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        canvas.bind_all('<MouseWheel>', _on_mousewheel)


def _fmt_summa_qisqa(v):
    v = v or 0
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f} mlrd"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f} mln"
    return f"{v:,.0f}".replace(',', ' ')


class DashboardTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        scroll = ScrollableFrame(self)
        scroll.pack(fill='both', expand=True)
        body = scroll.body

        ttk.Label(body, text="Qarz Nazorat va Talabnoma Tizimi", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(body, text="Portfelni tahlil qiling, muddati o'tgan mijozlarga xat tayyorlang.",
                  style='Sub.TLabel').pack(anchor='w', padx=20, pady=(0, 16))

        cards = ttk.Frame(body)
        cards.pack(fill='x', padx=20)
        self.card_portfel = self._card(cards, "Portfeldagi kreditlar")
        self.card_45kun = self._card(cards, "45+ kun muddati o'tgan")
        self.card_tayyor = self._card(cards, "Yuborilmagan xatlar")
        self.card_otgan = self._card(cards, "Muddati o'tgan xatlar")

        # ---- Bugungi harakatlar ----
        ttk.Label(body, text="Bugungi harakatlar", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(24, 8))
        today_cards = ttk.Frame(body)
        today_cards.pack(fill='x', padx=20)
        self.card_bugun_yaratildi = self._card(today_cards, "Bugun yaratilgan xatlar", small=True)
        self.card_bugun_yuborildi = self._card(today_cards, "Bugun yuborilgan xatlar", small=True)
        self.card_davo_muddati = self._card(today_cards, "Davo ariza muddati o'tgan", small=True)
        self.card_sud_muddati = self._card(today_cards, "Sudga topshirish muddati o'tgan", small=True)
        self.card_mib_harakatsiz = self._card(today_cards, "MIBda harakatsiz (15+ kun)", small=True)
        self.card_chora = self._card(today_cards, "Chora ko'rish kerak", small=True)
        self.card_sugurta = self._card(today_cards, "Sug'urta javobi kechikkan", small=True)

        # ---- Statistika (grafik) ----
        ttk.Label(body, text="Statistika", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(24, 8))
        charts_row = ttk.Frame(body)
        charts_row.pack(fill='x', padx=20)

        viloyat_box = tk.Frame(charts_row, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        viloyat_box.pack(side='left', fill='both', expand=True, padx=(0, 8), ipady=10)
        tk.Label(viloyat_box, text="Tarmoq bo'yicha Stage 3 kreditlar",
                 bg=WHITE, fg=INK, font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=12, pady=(4, 8))
        self.viloyat_canvas = tk.Canvas(viloyat_box, bg=WHITE, height=200, highlightthickness=0)
        self.viloyat_canvas.pack(fill='x', padx=12, pady=(0, 8))

        reja_box = tk.Frame(charts_row, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        reja_box.pack(side='left', fill='both', expand=True, padx=(8, 0), ipady=10)
        tk.Label(reja_box, text="Bugungi ish kuni rejasi",
                 bg=WHITE, fg=INK, font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=12, pady=(4, 8))
        self.reja_content = tk.Frame(reja_box, bg=WHITE)
        self.reja_content.pack(fill='x', padx=12, pady=(0, 8))

        # ---- So'nggi harakatlar ----
        ttk.Label(body, text="So'nggi harakatlar", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(24, 4))

        search_frame = ttk.Frame(body)
        search_frame.pack(fill='x', padx=20, pady=(0, 8))
        ttk.Label(search_frame, text="Mijozni anketa raqami bo'yicha qidirish "
                                      "(butun portfel bo'yicha, qaysi bosqichda ekanini ko'rish uchun):",
                  style='Sub.TLabel', wraplength=700, justify='left').pack(anchor='w')
        search_row = ttk.Frame(body)
        search_row.pack(fill='x', padx=20, pady=(4, 10))
        self.anketa_search_var = tk.StringVar()
        entry = ttk.Entry(search_row, textvariable=self.anketa_search_var, width=20)
        entry.pack(side='left')
        entry.bind('<Return>', lambda e: self.qidirish_anketa())
        ttk.Button(search_row, text="🔍 Qidirish", style='Accent.TButton',
                   command=self.qidirish_anketa).pack(side='left', padx=8)

        cols = ('sana', 'mijoz', 'xat_turi', 'holat')
        self.recent_tree = ttk.Treeview(body, columns=cols, show='headings', height=8)
        headings = {'sana': 'Sana', 'mijoz': 'Mijoz', 'xat_turi': 'Xat turi', 'holat': 'Holat'}
        widths = {'sana': 140, 'mijoz': 320, 'xat_turi': 110, 'holat': 130}
        for c in cols:
            self.recent_tree.heading(c, text=headings[c])
            self.recent_tree.column(c, width=widths[c])
        self.recent_tree.pack(fill='x', padx=20, pady=(0, 10))

        # ---- Ishlash tartibi ----
        info = ttk.Frame(body)
        info.pack(fill='x', padx=20, pady=(14, 30))
        ttk.Label(info, text="Ishlash tartibi:", style='Header.TLabel').pack(anchor='w')
        steps = [
            "1. 'Portfel' bo'limida .xlsb faylni yuklang.",
            "2. 'Mijozlar bazasi' bo'limida jismoniy/yuridik shaxslar ma'lumotini import qiling.",
            "3. 'Tahlil / Talabnoma' bo'limida 45 kundan o'tgan mijozlarni ko'ring, xat yarating.",
            "4. 'Xatlar holati' bo'limida yuborilganlarni belgilang — 3 kun ichida yuborilmasa, eslatma chiqadi.",
        ]
        for s in steps:
            ttk.Label(info, text=s, font=('Segoe UI', 10)).pack(anchor='w', pady=3)

        self.refresh()

    def _card(self, parent, title, small=False):
        f = tk.Frame(parent, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        f.pack(side='left', expand=True, fill='both', padx=6, ipady=14 if not small else 10)
        num = tk.Label(f, text='0', bg=WHITE, fg=STAMP, font=('Consolas', 22 if small else 26, 'bold'))
        num.pack(pady=(10, 0))
        tk.Label(f, text=title, bg=WHITE, fg='#6B7280', font=('Segoe UI', 9),
                 wraplength=220, justify='center').pack(pady=(0, 8))
        return num

    def _draw_ish_kuni_rejasi(self):
        for w in self.reja_content.winfo_children():
            w.destroy()

        reja = db.get_ish_kuni_rejasi()

        def qator(parent, matn, qiymat, rang=INK, katta=False):
            row = tk.Frame(parent, bg=WHITE)
            row.pack(fill='x', pady=1)
            tk.Label(row, text=matn, bg=WHITE, fg='#6B7280',
                     font=('Segoe UI', 9)).pack(side='left')
            tk.Label(row, text=str(qiymat), bg=WHITE, fg=rang,
                     font=('Consolas', 13 if katta else 10, 'bold')).pack(side='right')

        def mini_bar(parent, bajarildi, reja_soni):
            bar_frame = tk.Frame(parent, bg='#E3E7F0', height=8)
            bar_frame.pack(fill='x', pady=(2, 8))
            bar_frame.pack_propagate(False)
            foiz = 0
            if reja_soni > 0:
                foiz = min(bajarildi / reja_soni, 1.0)
            fill_w = int(foiz * 300)
            tk.Frame(bar_frame, bg=STAMP, width=fill_w, height=8).place(x=0, y=0)

        # --- Har bir tur bo'yicha alohida blok ---
        for turk in reja['turkumlar']:
            blok = tk.Frame(self.reja_content, bg=WHITE)
            blok.pack(fill='x', pady=(0, 4))
            tk.Label(blok, text=turk['nomi'], bg=WHITE, fg=INK,
                     font=('Segoe UI', 9, 'bold')).pack(anchor='w')
            qator(blok, "Kerak:", f"{turk['reja']} ta")
            qator(blok, "Bajarildi:", f"{turk['bajarildi']} ta", rang=STAMP)
            qator(blok, "Qolib ketyapti:", f"{turk['qoldi']} ta",
                  rang=ERR if turk['qoldi'] > 0 else STAMP)
            mini_bar(blok, turk['bajarildi'], turk['reja'])

        sep = tk.Frame(self.reja_content, bg='#E3E7F0', height=1)
        sep.pack(fill='x', pady=(2, 8))

        qator(self.reja_content, "Kunlik ish rejasi umumiy bajarilishi:",
              f"{reja['foiz']}%", rang=(STAMP if reja['foiz'] >= 70 else
                                        ('#B7862C' if reja['foiz'] >= 30 else ERR)), katta=True)
        mini_bar(self.reja_content, reja['umumiy_bajarildi'], reja['umumiy_reja'])

        qator(self.reja_content, "Jami (oy oxirigacha) ish:", f"{reja['jami_ish']} ta")
        qator(self.reja_content, "Muddat (har oy 20-sanagacha):", reja['deadline'])
        qator(self.reja_content, "Qolgan ish kunlari:", f"{reja['ish_kunlari_qolgan']} kun")

        if reja['ish_vaqti_tugadimi']:
            tk.Label(self.reja_content, text="⚠ Bugungi ish vaqti (18:00) tugagan — bajarilmagan "
                                              "ishlar ertangi rejaga o'tkaziladi",
                     bg=WHITE, fg=ERR, font=('Segoe UI', 8, 'bold'),
                     wraplength=320, justify='left').pack(anchor='w', pady=(6, 0))
        else:
            tk.Label(self.reja_content, text="Ish vaqti: 18:00 gacha",
                     bg=WHITE, fg='#6B7280', font=('Segoe UI', 8)).pack(anchor='w', pady=(6, 0))

    def _draw_hbar_chart(self, canvas, items, label_key, value_key, value_fmt=str, color=STAMP):
        """items: list of dict; oddiy tk.Canvas'da gorizontal ustunli diagramma chizadi."""
        canvas.delete('all')
        canvas.update_idletasks()
        width = canvas.winfo_width() or 380
        if not items:
            canvas.create_text(width // 2, 90, text="Ma'lumot yo'q", fill='#6B7280', font=('Segoe UI', 9))
            return
        max_val = max((it[value_key] or 0) for it in items) or 1
        row_h = 22
        label_w = 150
        bar_max_w = max(width - label_w - 130, 40)
        y = 8
        for it in items:
            label = str(it[label_key])[:22]
            val = it[value_key] or 0
            bar_w = int((val / max_val) * bar_max_w)
            canvas.create_text(4, y + row_h // 2, text=label, anchor='w',
                                font=('Segoe UI', 8), fill=INK)
            canvas.create_rectangle(label_w, y + 3, label_w + bar_w, y + row_h - 3,
                                     fill=color, outline='')
            canvas.create_text(label_w + bar_w + 6, y + row_h // 2,
                                text=value_fmt(val), anchor='w',
                                font=('Segoe UI', 8), fill='#6B7280')
            y += row_h
        canvas.configure(height=max(y + 6, 60))

    def qidirish_anketa(self):
        anketa = self.anketa_search_var.get().strip()
        if not anketa:
            messagebox.showinfo("Diqqat", "Anketa raqamini kiriting.")
            return
        natija = db.get_mijoz_holati_anketa_boyicha(anketa)
        if not natija:
            messagebox.showinfo("Topilmadi", f"Anketa №{anketa} bo'yicha portfelda hech narsa topilmadi.")
            return
        MijozHolatiDialog(self, anketa, natija)

    def refresh(self):
        def xavfsiz(fn, nomi, standart=0):
            """Bitta statistik hisoblash xato bersa, butun Bosh sahifa qulamasin —
            o'sha kartochka 0/bo'sh ko'rsatiladi, xato konsolga chiqadi."""
            try:
                return fn()
            except Exception as e:
                print(f"Bosh sahifa: '{nomi}' hisoblanmadi — {e}")
                return standart

        conn = db.get_conn()
        portfel_n = conn.execute('SELECT COUNT(*) c FROM portfel WHERE faol=1').fetchone()['c']
        conn.close()
        chegara = int(db.get_setting('dpd_chegara_kun', 45))
        kun45 = xavfsiz(lambda: len(db.get_portfel_45_kun(chegara)), '45+ kun')
        tayyor = xavfsiz(lambda: len(db.get_xatlar('tayyor')), 'tayyor xatlar')
        otgan = xavfsiz(lambda: len(db.get_xatlar('muddati_otgan')), 'muddati o\'tgan xatlar')

        self.card_portfel.config(text=str(portfel_n))
        self.card_45kun.config(text=str(kun45))
        self.card_tayyor.config(text=str(tayyor))
        self.card_otgan.config(text=str(otgan))
        self.card_otgan.config(fg=ERR if otgan > 0 else STAMP)

        bugungi = xavfsiz(db.get_bugungi_harakatlar, 'bugungi harakatlar', {'yaratildi': 0, 'yuborildi': 0})
        self.card_bugun_yaratildi.config(text=str(bugungi['yaratildi']))
        self.card_bugun_yuborildi.config(text=str(bugungi['yuborildi']))
        n_davo_otgan = xavfsiz(lambda: len(db.get_davo_ariza_muddati_otganlar()), 'davo ariza muddati')
        self.card_davo_muddati.config(text=str(n_davo_otgan), fg=ERR if n_davo_otgan > 0 else STAMP)
        n_sud_otgan = xavfsiz(lambda: len(db.get_sud_topshirish_muddati_otganlar()), 'sud topshirish muddati')
        self.card_sud_muddati.config(text=str(n_sud_otgan), fg=ERR if n_sud_otgan > 0 else STAMP)
        n_mib_harakatsiz = xavfsiz(lambda: len(db.get_mib_harakatsizlar()), 'MIB harakatsizlar')
        self.card_mib_harakatsiz.config(text=str(n_mib_harakatsiz), fg=ERR if n_mib_harakatsiz > 0 else STAMP)
        n_chora = xavfsiz(lambda: len(db.get_chora_korish_royxati()), 'chora ko\'rish')
        self.card_chora.config(text=str(n_chora), fg=ERR if n_chora > 0 else STAMP)
        n_sugurta = xavfsiz(lambda: len(db.get_sugurta_javob_kutilayotganlar()), 'sug\'urta javobi')
        self.card_sugurta.config(text=str(n_sugurta), fg=ERR if n_sugurta > 0 else STAMP)

        tarmoq_data = xavfsiz(lambda: db.get_tarmoq_stage3_breakdown(limit=8), 'tarmoq statistikasi', [])
        self._draw_hbar_chart(
            self.viloyat_canvas, tarmoq_data, 'tarmoq', 'jami',
            value_fmt=_fmt_summa_qisqa, color=STAMP
        )

        try:
            self._draw_ish_kuni_rejasi()
        except Exception as e:
            print(f"Bosh sahifa: ish kuni rejasi chizilmadi — {e}")

        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        recent = db.get_xatlar()[:10]
        status_labels = {'tayyor': 'Tayyor', 'yuborildi': '✓ Yuborildi', 'muddati_otgan': "⚠ Muddati o'tgan"}
        for r in recent:
            try:
                sana = datetime.datetime.fromisoformat(r['yaratilgan_sana']).strftime('%d.%m.%Y %H:%M')
            except Exception:
                sana = r['yaratilgan_sana'] or ''
            self.recent_tree.insert('', 'end', values=(
                sana, r['mijoz_nomi'], r['xat_turi'], status_labels.get(r['holat'], r['holat'])
            ))


class PortfelTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Portfel ma'lumotlarini import qilish", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="IFRS portfel hisobotini (.xlsb) yuklang. Mavjud kreditlar "
                              "yangilanadi, yangilari qo'shiladi — avval yaratilgan xatlar/Davo "
                              "arizalar bilan bog'lanish saqlanib qoladi.", style='Sub.TLabel',
                  wraplength=900, justify='left').pack(
            anchor='w', padx=20, pady=(0, 16))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(anchor='w', padx=20)
        ttk.Button(btn_frame, text="📂 .xlsb faylni tanlash va import qilish",
                   style='Accent.TButton', command=self.import_file).pack(side='left')

        self.status_label = ttk.Label(self, text='', style='Sub.TLabel', wraplength=900, justify='left')
        self.status_label.pack(anchor='w', padx=20, pady=10)

        self.progress = ttk.Progressbar(self, mode='determinate', length=400)
        self.progress.pack(anchor='w', padx=20, pady=(0, 10))

        cols = ('anketa', 'mijoz', 'turi', 'dpd', 'jami_qarz')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz nomi', 'turi': 'Turi',
                    'dpd': 'DPD (kun)', 'jami_qarz': "Muddati o'tgan qarz"}
        widths = {'anketa': 100, 'mijoz': 350, 'turi': 90, 'dpd': 90, 'jami_qarz': 160}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self.refresh_table()

    def import_file(self):
        filepath = filedialog.askopenfilename(
            title="Portfel faylini tanlang",
            filetypes=[("Excel Binary", "*.xlsb"), ("Barcha fayllar", "*.*")]
        )
        if not filepath:
            return
        self.status_label.config(text="Import qilinmoqda...")
        self.progress['value'] = 0

        def worker():
            try:
                def cb(i, total):
                    pct = int(i / max(total, 1) * 100)
                    self.progress['value'] = pct

                result = importer.import_portfel_xlsb(filepath, progress_cb=cb)
                self.progress['value'] = 100
                conn = db.get_conn()
                faol_soni = conn.execute('SELECT COUNT(*) c FROM portfel WHERE faol=1').fetchone()['c']
                faolsiz_soni = conn.execute('SELECT COUNT(*) c FROM portfel WHERE faol=0').fetchone()['c']
                conn.close()
                msg = (f"Tayyor! {result['jami_qator']} ta qator yangilandi (varaq: {result['sheet']}).\n"
                       f"Joriy faol portfel: {faol_soni} ta kredit.")
                if faolsiz_soni:
                    msg += (f"\n{faolsiz_soni} ta eski kredit (bu faylda endi yo'q — to'langan yoki "
                             f"chiqarib tashlangan) 'faol emas' deb belgilandi va Tahlil/Chora "
                             f"ko'rish statistikasidan chiqarib tashlandi.")
                if result['topilmagan_ustunlar']:
                    msg += f"\nOgohlantirish: {len(result['topilmagan_ustunlar'])} ta ustun faylda topilmadi."
                self.status_label.config(text=msg)
                self.refresh_table()
                self.app.tab_dashboard.refresh()
            except Exception as e:
                messagebox.showerror("Xato", f"Import vaqtida xato: {e}")
                self.status_label.config(text="Xato yuz berdi.")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = db.get_conn()
        rows = conn.execute('SELECT * FROM portfel WHERE faol=1 ORDER BY dpd_max DESC LIMIT 500').fetchall()
        conn.close()
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['anketa_raqami'], r['mijoz_nomi'], r['mijoz_turi'], r['dpd_max'],
                f"{r['jami_qarz']:,.0f}".replace(',', ' ') if r['jami_qarz'] else '0'
            ))


class MijozlarTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Mijozlar bazasini import qilish", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))

        # ---- Tavsiya etilgan usul: xom matn (.txt / .zip) ----
        ttk.Label(self, text="Tavsiya etiladi: bank tizimidan olingan xom matn fayli",
                  style='Header.TLabel').pack(anchor='w', padx=20, pady=(10, 2))
        ttk.Label(self, text="Bank tizimidan '|' bilan ajratilgan xom (.txt yoki uni ichiga olgan "
                              ".zip) faylni to'g'ridan-to'g'ri yuklang — Excel orqali o'tmagani "
                              "uchun hech qanday ma'lumot buzilmaydi, ustunlarni moslashtirish "
                              "shart emas.",
                  style='Sub.TLabel', wraplength=900, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))
        ttk.Button(self, text="📄 Xom matn (.txt / .zip) faylni import qilish",
                   style='Accent.TButton',
                   command=self.import_txt_file).pack(anchor='w', padx=20)

        self.txt_status_label = ttk.Label(self, text='', style='Sub.TLabel')
        self.txt_status_label.pack(anchor='w', padx=20, pady=(8, 0))
        self.txt_progress = ttk.Progressbar(self, mode='determinate', length=400)
        self.txt_progress.pack(anchor='w', padx=20, pady=(6, 4))

        # ---- Muqobil usul: Excel (ustunlarni qo'lda moslashtirish) ----
        sep = ttk.Frame(self, height=2)
        sep.pack(fill='x', padx=20, pady=(18, 14))
        ttk.Label(self, text="Muqobil usul: Excel fayl (ustunlarni o'zingiz moslashtirasiz)",
                  style='Header.TLabel').pack(anchor='w', padx=20, pady=(0, 4))
        ttk.Label(self, text="Agar xom matn fayli mavjud bo'lmasa, Excel (.xlsx) faylni "
                              "yuklab, ustunlarni qo'lda moslashtirishingiz mumkin.",
                  style='Sub.TLabel').pack(anchor='w', padx=20, pady=(0, 10))

        btns = ttk.Frame(self)
        btns.pack(anchor='w', padx=20)
        ttk.Button(btns, text="👤 Jismoniy shaxslar Excel faylini import qilish",
                   command=lambda: self.import_file('jismoniy')).pack(side='left', padx=(0, 10))
        ttk.Button(btns, text="🏢 Yuridik shaxslar Excel faylini import qilish",
                   command=lambda: self.import_file('yuridik')).pack(side='left')

        self.status_label = ttk.Label(self, text='', style='Sub.TLabel')
        self.status_label.pack(anchor='w', padx=20, pady=14)

        stats = ttk.Frame(self)
        stats.pack(anchor='w', padx=20)
        self.lbl_jis = ttk.Label(stats, text="Jismoniy shaxslar: 0")
        self.lbl_jis.pack(anchor='w', pady=2)
        self.lbl_yur = ttk.Label(stats, text="Yuridik shaxslar: 0")
        self.lbl_yur.pack(anchor='w', pady=2)
        self.refresh_stats()

    def import_txt_file(self):
        filepath = filedialog.askopenfilename(
            title="Xom matn (.txt) yoki .zip faylni tanlang",
            filetypes=[("Matn / Zip", "*.txt *.zip"), ("Barcha fayllar", "*.*")]
        )
        if not filepath:
            return
        self.txt_status_label.config(text="Import qilinmoqda... (katta fayllar 20-30 sekund olishi mumkin)")
        self.txt_progress['value'] = 0

        def worker():
            try:
                def cb(i, total):
                    pct = int(i / max(total, 1) * 100)
                    self.txt_progress['value'] = pct

                result = importer.import_clients_txt(filepath, progress_cb=cb)
                self.txt_progress['value'] = 100
                msg = (f"Tayyor! {result['import_qilingan']} / {result['jami_qator']} "
                       f"yozuv import qilindi.")
                if result['otkazib_yuborildi']:
                    msg += f" ({result['otkazib_yuborildi']} ta qator o'tkazib yuborildi.)"
                self.txt_status_label.config(text=msg)
                self.refresh_stats()
            except Exception as e:
                messagebox.showerror("Xato", f"Import vaqtida xato: {e}")
                self.txt_status_label.config(text="Xato yuz berdi.")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_stats(self):
        conn = db.get_conn()
        jis = conn.execute("SELECT COUNT(*) c FROM mijozlar WHERE turi='jismoniy'").fetchone()['c']
        yur = conn.execute("SELECT COUNT(*) c FROM mijozlar WHERE turi='yuridik'").fetchone()['c']
        conn.close()
        self.lbl_jis.config(text=f"Jismoniy shaxslar: {jis}")
        self.lbl_yur.config(text=f"Yuridik shaxslar: {yur}")

    def import_file(self, turi):
        filepath = filedialog.askopenfilename(
            title="Mijozlar faylini tanlang",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Barcha fayllar", "*.*")]
        )
        if not filepath:
            return
        try:
            cols, preview_df = importer.preview_mijozlar_columns(filepath)
        except Exception as e:
            messagebox.showerror("Xato", f"Fayl o'qilmadi: {e}")
            return

        dialog = ColumnMapDialog(self, cols, preview_df, turi)
        self.wait_window(dialog)
        if not dialog.result:
            return

        self.status_label.config(text="Import qilinmoqda...")

        def worker():
            try:
                result = importer.import_mijozlar_xlsx(filepath, turi, dialog.result)
                self.status_label.config(
                    text=f"Tayyor! {result['import_qilingan']} / {result['jami_qator']} qator import qilindi.")
                self.refresh_stats()
            except Exception as e:
                messagebox.showerror("Xato", f"Import vaqtida xato: {e}")

        threading.Thread(target=worker, daemon=True).start()


class ColumnMapDialog(tk.Toplevel):
    """Excel ustunlarini bazadagi maydonlarga moslashtirish oynasi."""
    FIELDS = [
        ('kalit', "Bog'lovchi ID (STIR / PINFL / Уникал) *", True),
        ('ism', "Ism-familiya / Tashkilot nomi *", True),
        ('manzil', "Manzil", False),
        ('telefon', "Telefon", False),
        ('hujjat_raqami', "Passport / STIR raqami", False),
        ('rahbar_ism', "Rahbar F.I.Sh (yuridik shaxs uchun)", False),
    ]

    def __init__(self, parent, columns, preview_df, turi):
        super().__init__(parent)
        self.title(f"Ustunlarni moslashtirish — {turi}")
        self.geometry("560x480")
        self.configure(bg=BG)
        self.result = None
        self.columns = [''] + list(columns)

        ttk.Label(self, text="Har bir maydon uchun mos Excel ustunini tanlang:",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 10))

        self.vars = {}
        form = ttk.Frame(self)
        form.pack(fill='x', padx=16)
        for field, label, required in self.FIELDS:
            row = ttk.Frame(form)
            row.pack(fill='x', pady=4)
            ttk.Label(row, text=label, width=38).pack(side='left')
            var = tk.StringVar(value='')
            combo = ttk.Combobox(row, textvariable=var, values=self.columns, state='readonly', width=28)
            combo.pack(side='left')
            self.vars[field] = var

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="Import qilish", style='Accent.TButton',
                   command=self.on_confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def on_confirm(self):
        mapping = {f: v.get() for f, v in self.vars.items() if v.get()}
        if not mapping.get('kalit') or not mapping.get('ism'):
            messagebox.showerror("Xato", "Bog'lovchi ID va Ism ustunlari majburiy.")
            return
        self.result = mapping
        self.destroy()


class AnalitikaTab(ttk.Frame):
    """'Tahlil' bo'limi — butun portfel bo'yicha umumiy statistik tahlil."""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        scroll = ScrollableFrame(self)
        scroll.pack(fill='both', expand=True)
        body = scroll.body

        ttk.Label(body, text="Tahlil", style='Header.TLabel').pack(anchor='w', padx=20, pady=(20, 4))
        ttk.Label(body, text="Butun portfel bo'yicha umumiy holat: jismoniy/yuridik taqsimoti, "
                              "tarmoqlar kesimida va Stage 1/2/3 bo'yicha tahlil.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(body)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", style='Accent.TButton', command=self.refresh).pack(side='left')
        ttk.Label(toolbar, text="Format:").pack(side='left', padx=(16, 4))
        self.format_var = tk.StringVar(value='Word (.docx)')
        ttk.Combobox(toolbar, textvariable=self.format_var, values=['Word (.docx)', 'PDF (.pdf)'],
                     state='readonly', width=14).pack(side='left')
        ttk.Button(toolbar, text="📄 Hisobotni yuklab olish", command=self.export_hisobot).pack(side='left', padx=8)

        self.cards_frame = ttk.Frame(body)
        self.cards_frame.pack(fill='x', padx=20, pady=(16, 10))

        self.stage_frame = ttk.Frame(body)
        self.stage_frame.pack(fill='x', padx=20, pady=(0, 10))

        ttk.Label(body, text="Tarmoq (soha) kesimida — EAD summasi bo'yicha",
                  style='Header.TLabel').pack(anchor='w', padx=20, pady=(10, 8))
        self.tarmoq_canvas = tk.Canvas(body, bg=WHITE, height=340, highlightthickness=1,
                                        highlightbackground='#E3E7F0')
        self.tarmoq_canvas.pack(fill='x', padx=20, pady=(0, 20))

        self._tahlil = None
        self.refresh()

    def _card(self, parent, value, label, color=None):
        f = tk.Frame(parent, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        f.pack(side='left', expand=True, fill='both', padx=6, ipady=10)
        tk.Label(f, text=value, bg=WHITE, fg=color or INK, font=('Consolas', 18, 'bold')).pack(pady=(6, 0))
        tk.Label(f, text=label, bg=WHITE, fg='#6B7280', font=('Segoe UI', 9),
                 wraplength=200, justify='center').pack(pady=(0, 6))
        return f

    def refresh(self):
        self._tahlil = db.get_umumiy_tahlil()
        t = self._tahlil

        for w in self.cards_frame.winfo_children():
            w.destroy()
        self._card(self.cards_frame, f"{t['jami_soni']:,}".replace(',', ' '), "Jami portfeldagi mijozlar")
        self._card(self.cards_frame, _fmt_summa_qisqa(t['jami_ead']), "Jami EAD qoldiq")
        self._card(self.cards_frame,
                    f"{t['jismoniy']['soni']:,}".replace(',', ' '),
                    f"Jismoniy shaxslar\n({_fmt_summa_qisqa(t['jismoniy']['ead'])})", color=STAMP)
        self._card(self.cards_frame,
                    f"{t['yuridik']['soni']:,}".replace(',', ' '),
                    f"Yuridik shaxslar\n({_fmt_summa_qisqa(t['yuridik']['ead'])})", color=KRAFT)

        for w in self.stage_frame.winfo_children():
            w.destroy()
        stage_colors = {'1': STAMP, '2': KRAFT, '3': ERR}
        for st in t['stage']:
            f = tk.Frame(self.stage_frame, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
            f.pack(side='left', expand=True, fill='both', padx=6, ipady=8)
            color = stage_colors.get(str(st['stage']), INK)
            tk.Label(f, text=f"Stage {st['stage']}", bg=WHITE, fg=color,
                     font=('Segoe UI', 11, 'bold')).pack(pady=(8, 2))
            tk.Label(f, text=f"{st['soni']:,} ta".replace(',', ' '), bg=WHITE, fg=INK,
                     font=('Consolas', 15, 'bold')).pack()
            tk.Label(f, text=_fmt_summa_qisqa(st['ead']), bg=WHITE, fg='#6B7280',
                     font=('Segoe UI', 9)).pack()
            bar_bg = tk.Frame(f, bg='#E3E7F0', height=10)
            bar_bg.pack(fill='x', padx=16, pady=(6, 4))
            bar_bg.pack_propagate(False)
            tk.Frame(bar_bg, bg=color, width=0, height=10).place(relwidth=min(st['ulush'] / 100, 1.0), relheight=1)
            tk.Label(f, text=f"Portfeldagi ulushi: {st['ulush']}%", bg=WHITE, fg='#6B7280',
                     font=('Segoe UI', 9, 'bold')).pack(pady=(0, 8))

        self._draw_tarmoq_chart(t['tarmoq'][:8])

    def _draw_tarmoq_chart(self, items):
        c = self.tarmoq_canvas
        c.delete('all')
        c.update_idletasks()
        w = c.winfo_width() or 1000
        h = 340
        if not items:
            return
        max_val = max((i['ead'] or 0) for i in items) or 1
        row_h = h / len(items)
        label_w = 260
        for idx, item in enumerate(items):
            y0 = idx * row_h + 6
            bar_h = row_h * 0.5
            label = item['tarmoq']
            if len(label) > 34:
                label = label[:34] + '…'
            c.create_text(label_w - 10, y0 + bar_h / 2, text=label, anchor='e',
                           font=('Segoe UI', 9), fill=INK)
            bar_len = (item['ead'] / max_val) * (w - label_w - 110)
            c.create_rectangle(label_w, y0, label_w + bar_len, y0 + bar_h, fill=STAMP, outline='')
            c.create_text(label_w + bar_len + 8, y0 + bar_h / 2,
                           text=_fmt_summa_qisqa(item['ead']), anchor='w', font=('Segoe UI', 9), fill='#6B7280')

    def export_hisobot(self):
        if not self._tahlil:
            self.refresh()
        out_path = filedialog.asksaveasfilename(
            title="Hisobotni saqlash", defaultextension=".docx",
            initialfile="tahlil_hisoboti.docx", filetypes=[("Word", "*.docx")]
        )
        if not out_path:
            return
        settings = db.get_all_settings()
        try:
            letters.generate_tahlil_hisoboti(out_path, self._tahlil, settings)
            if self.format_var.get().startswith('PDF'):
                out_path = letters.convert_docx_to_pdf(out_path, delete_docx=True)
        except Exception as e:
            messagebox.showerror("Xato", f"Hisobot yaratishda xato: {e}")
            return
        messagebox.showinfo("Tayyor", f"Hisobot tayyorlandi:\n{out_path}")
        webbrowser.open(out_path)


class RejaGrafikTab(ttk.Frame):
    """'Reja Grafik' bo'limi — bugungi kunlik ish rejasi va tarmoq kesimida bajarilish."""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        scroll = ScrollableFrame(self)
        scroll.pack(fill='both', expand=True)
        body = scroll.body

        ttk.Label(body, text="Reja Grafik", style='Header.TLabel').pack(anchor='w', padx=20, pady=(20, 4))
        ttk.Label(body, text="Bugungi kunda qilinishi kerak bo'lgan ishlar rejasi (xat, Davo ariza, "
                              "MIB) va tarmoqlar kesimida bajarilgan ishlar hisoboti.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(body)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", style='Accent.TButton', command=self.refresh).pack(side='left')
        ttk.Label(toolbar, text="Format:").pack(side='left', padx=(16, 4))
        self.format_var = tk.StringVar(value='Word (.docx)')
        ttk.Combobox(toolbar, textvariable=self.format_var, values=['Word (.docx)', 'PDF (.pdf)'],
                     state='readonly', width=14).pack(side='left')
        ttk.Button(toolbar, text="📄 Hisobotni yuklab olish", command=self.export_hisobot).pack(side='left', padx=8)

        ttk.Label(body, text="Bugungi ish rejasi", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 8))
        self.reja_cards = ttk.Frame(body)
        self.reja_cards.pack(fill='x', padx=20, pady=(0, 10))

        self.umumiy_frame = tk.Frame(body, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        self.umumiy_frame.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Label(body, text="Tarmoq kesimida bajarilgan ishlar", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(0, 8))
        cols = ('tarmoq', 'xat', 'yuborilgan', 'davo', 'sud', 'mib')
        self.tree = ttk.Treeview(body, columns=cols, show='headings', height=12)
        headings = {'tarmoq': 'Tarmoq', 'xat': 'Jami xat', 'yuborilgan': 'Yuborilgan',
                    'davo': 'Davo ariza', 'sud': 'Sudga o\'tkazilgan', 'mib': 'MIBga o\'tkazilgan'}
        widths = {'tarmoq': 340, 'xat': 90, 'yuborilgan': 100, 'davo': 100, 'sud': 130, 'mib': 130}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.pack(fill='x', padx=20, pady=(0, 20))

        self._reja = None
        self._tarmoq_reja = None
        self.refresh()

    def _mini_bar(self, parent, bajarildi, reja_soni, color):
        bar_frame = tk.Frame(parent, bg='#E3E7F0', height=8)
        bar_frame.pack(fill='x', pady=(4, 0))
        bar_frame.pack_propagate(False)
        foiz = min(bajarildi / reja_soni, 1.0) if reja_soni > 0 else 0
        fill_w = int(foiz * 260)
        tk.Frame(bar_frame, bg=color, width=fill_w, height=8).place(x=0, y=0)

    def refresh(self):
        self._reja = db.get_ish_kuni_rejasi()
        self._tarmoq_reja = db.get_reja_tarmoq_kesimida()
        reja = self._reja

        for w in self.reja_cards.winfo_children():
            w.destroy()
        for turk in reja['turkumlar']:
            f = tk.Frame(self.reja_cards, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
            f.pack(side='left', expand=True, fill='both', padx=6, ipady=10)
            tk.Label(f, text=turk['nomi'], bg=WHITE, fg=INK, font=('Segoe UI', 11, 'bold')).pack(
                anchor='w', padx=14, pady=(8, 6))
            row = tk.Frame(f, bg=WHITE)
            row.pack(fill='x', padx=14)
            tk.Label(row, text="Kerak:", bg=WHITE, fg='#6B7280', font=('Segoe UI', 9)).pack(side='left')
            tk.Label(row, text=f"{turk['reja']} ta", bg=WHITE, fg=INK, font=('Consolas', 11, 'bold')).pack(side='right')
            row2 = tk.Frame(f, bg=WHITE)
            row2.pack(fill='x', padx=14)
            tk.Label(row2, text="Bajarildi:", bg=WHITE, fg='#6B7280', font=('Segoe UI', 9)).pack(side='left')
            tk.Label(row2, text=f"{turk['bajarildi']} ta", bg=WHITE, fg=STAMP, font=('Consolas', 11, 'bold')).pack(side='right')
            row3 = tk.Frame(f, bg=WHITE)
            row3.pack(fill='x', padx=14, pady=(0, 8))
            tk.Label(row3, text="Qolib ketyapti:", bg=WHITE, fg='#6B7280', font=('Segoe UI', 9)).pack(side='left')
            tk.Label(row3, text=f"{turk['qoldi']} ta", bg=WHITE,
                     fg=ERR if turk['qoldi'] > 0 else STAMP, font=('Consolas', 11, 'bold')).pack(side='right')
            self._mini_bar(f, turk['bajarildi'], turk['reja'], STAMP)
            tk.Frame(f, bg=WHITE, height=6).pack()

        for w in self.umumiy_frame.winfo_children():
            w.destroy()
        tk.Label(self.umumiy_frame, text="Kunlik ish rejasi umumiy bajarilishi", bg=WHITE, fg=INK,
                 font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=16, pady=(12, 4))
        foiz_color = STAMP if reja['foiz'] >= 70 else (KRAFT if reja['foiz'] >= 30 else ERR)
        tk.Label(self.umumiy_frame, text=f"{reja['foiz']}%", bg=WHITE, fg=foiz_color,
                 font=('Consolas', 26, 'bold')).pack(anchor='w', padx=16)
        self._mini_bar(self.umumiy_frame, reja['umumiy_bajarildi'], reja['umumiy_reja'], foiz_color)
        info = tk.Frame(self.umumiy_frame, bg=WHITE)
        info.pack(fill='x', padx=16, pady=(10, 14))
        for label, val in [("Jami ish:", f"{reja['jami_ish']} ta"), ("Muddat:", reja['deadline']),
                            ("Qolgan ish kunlari:", f"{reja['ish_kunlari_qolgan']} kun")]:
            row = tk.Frame(info, bg=WHITE)
            row.pack(side='left', padx=(0, 30))
            tk.Label(row, text=label, bg=WHITE, fg='#6B7280', font=('Segoe UI', 9)).pack(anchor='w')
            tk.Label(row, text=val, bg=WHITE, fg=INK, font=('Segoe UI', 11, 'bold')).pack(anchor='w')

        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self._tarmoq_reja:
            self.tree.insert('', 'end', values=(
                t['tarmoq'], t['xat_soni'], t['yuborilgan_soni'], t['davo_soni'], t['sud_soni'], t['mib_soni']
            ))

        self.app.tab_dashboard.refresh()

    def export_hisobot(self):
        if not self._reja:
            self.refresh()
        out_path = filedialog.asksaveasfilename(
            title="Hisobotni saqlash", defaultextension=".docx",
            initialfile="reja_grafik_hisoboti.docx", filetypes=[("Word", "*.docx")]
        )
        if not out_path:
            return
        settings = db.get_all_settings()
        try:
            letters.generate_reja_hisoboti(out_path, self._reja, self._tarmoq_reja, settings)
            if self.format_var.get().startswith('PDF'):
                out_path = letters.convert_docx_to_pdf(out_path, delete_docx=True)
        except Exception as e:
            messagebox.showerror("Xato", f"Hisobot yaratishda xato: {e}")
            return
        messagebox.showinfo("Tayyor", f"Hisobot tayyorlandi:\n{out_path}")
        webbrowser.open(out_path)


class TahlilTab(ttk.Frame):
    PAKET_OPTIONS = ['10', '30', '50', '100', 'Barchasi']

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Tahlil va Talabnoma", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        self.sub_label = ttk.Label(self, text='', style='Sub.TLabel')
        self.sub_label.pack(anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔍 Tahlil qilish (yangilash)",
                   command=self.refresh_stats).pack(side='left')

        self.only_new_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Faqat xat yaratilmagan / muddati o'tganlar",
                         variable=self.only_new_var,
                         command=self.refresh_stats).pack(side='left', padx=14)

        paket_frame = ttk.Frame(self)
        paket_frame.pack(fill='x', padx=20, pady=(10, 6))
        ttk.Label(paket_frame, text="Paket hajmi:").pack(side='left')
        self.paket_var = tk.StringVar(value='30')
        ttk.Combobox(paket_frame, textvariable=self.paket_var, values=self.PAKET_OPTIONS,
                     state='readonly', width=10).pack(side='left', padx=8)
        ttk.Button(paket_frame, text="① Birinchi paketni belgilash",
                   command=self.select_paket).pack(side='left', padx=6)
        ttk.Button(paket_frame, text="📊 Excel'ga eksport qilish (tanlanganlar)",
                   command=self.export_excel).pack(side='left', padx=6)
        ttk.Button(paket_frame, text="📥 Tahrirlangan Excel'ni yuklash",
                   command=self.import_excel_updates).pack(side='left', padx=6)

        format_frame = ttk.Frame(self)
        format_frame.pack(fill='x', padx=20, pady=(0, 6))
        ttk.Label(format_frame, text="Xat fayl formati:").pack(side='left')
        self.format_var = tk.StringVar(value='Word (.docx)')
        ttk.Combobox(format_frame, textvariable=self.format_var,
                     values=['Word (.docx)', 'PDF (.pdf)'],
                     state='readonly', width=14).pack(side='left', padx=8)
        ttk.Label(format_frame, text="(PDF uchun kompyuterda Microsoft Word o'rnatilgan bo'lishi kerak)",
                  style='Sub.TLabel').pack(side='left', padx=6)

        gen_frame = ttk.Frame(self)
        gen_frame.pack(fill='x', padx=20, pady=(0, 6))
        ttk.Button(gen_frame, text="✉ Tanlanganlar uchun xat yaratish (ommaviy)",
                   style='Accent.TButton', command=self.generate_bulk).pack(side='left')

        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=20, pady=(14, 6))
        ttk.Label(search_frame, text="Bitta mijozga: Anketa raqami").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side='left', padx=8)
        ttk.Button(search_frame, text="Qidirish", command=self.search_single).pack(side='left')
        ttk.Button(search_frame, text="✉ Xatni yuborish (shu mijozga)",
                   command=self.generate_single).pack(side='left', padx=8)

        cols = ('anketa', 'mijoz', 'turi', 'dpd', 'jami_qarz', 'mijoz_topildi', 'holat')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=14, selectmode='extended')
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz nomi', 'turi': 'Turi',
                    'dpd': 'DPD (kun)', 'jami_qarz': "Muddati o'tgan qarz",
                    'mijoz_topildi': "Bazada mavjud?", 'holat': 'Oldingi xat holati'}
        widths = {'anketa': 90, 'mijoz': 280, 'turi': 80, 'dpd': 80, 'jami_qarz': 140,
                  'mijoz_topildi': 100, 'holat': 130}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        ttk.Label(self, text="Ctrl / Shift bosib bir nechta mijozni tanlashingiz mumkin.",
                  style='Sub.TLabel').pack(anchor='w', padx=20, pady=(0, 10))

        self._rows_cache = []
        self.refresh_stats()

    def refresh_stats(self):
        chegara = int(db.get_setting('dpd_chegara_kun', 45))
        rows = db.get_portfel_45_kun(chegara)
        status_map = db.get_latest_xat_status_by_portfel()

        # Vafot etgan mijozlarga hech qanday chora ko'rilmaydi — ro'yxatdan chiqarib tashlaymiz
        vafot_anketalar = {v['anketa_raqami'] for v in db.get_vafot_etganlar_royxati()}
        rows = [r for r in rows if r.get('anketa_raqami') not in vafot_anketalar]

        if self.only_new_var.get():
            rows = [r for r in rows if status_map.get(r['id']) not in ('tayyor', 'yuborildi')]

        self._rows_cache = rows
        self._status_map = status_map
        self.sub_label.config(
            text=f"{chegara}+ kun muddati o'tgan mijozlar: {len(rows)} ta "
                 f"(jami tahlil qilingan {len(db.get_portfel_45_kun(chegara))} tadan, "
                 f"vafot etganlar chiqarib tashlangan)")
        self._fill_tree(rows)

    def _fill_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        status_labels = {'tayyor': 'Tayyor', 'yuborildi': 'Yuborilgan',
                          'muddati_otgan': "⚠ Muddati o'tgan"}
        for r in rows:
            turi, mijoz = resolve_mijoz(r)
            holat = status_labels.get(self._status_map.get(r['id']), '—') if hasattr(self, '_status_map') else '—'
            self.tree.insert('', 'end', iid=str(r['id']), values=(
                r['anketa_raqami'], r['mijoz_nomi'], turi, r['dpd_max'],
                f"{r['jami_qarz']:,.0f}".replace(',', ' ') if r['jami_qarz'] else '0',
                "Ha" if mijoz else "Yo'q", holat
            ))

    def select_paket(self):
        paket = self.paket_var.get()
        all_items = self.tree.get_children()
        if not all_items:
            messagebox.showinfo("Diqqat", "Ro'yxat bo'sh.")
            return
        n = len(all_items) if paket == 'Barchasi' else int(paket)
        to_select = all_items[:n]
        self.tree.selection_set(to_select)
        if to_select:
            self.tree.see(to_select[0])
        messagebox.showinfo("Tanlandi", f"{len(to_select)} ta mijoz tanlandi (paket hajmi: {paket}).")

    def _selected_rows(self):
        selected = self.tree.selection()
        if not selected:
            return []
        ids = [int(i) for i in selected]
        return [r for r in self._rows_cache if r['id'] in ids]

    def _rows_for_excel(self, portfel_rows):
        out = []
        for r in portfel_rows:
            turi, mijoz = resolve_mijoz(r)
            xat_turi = 'Talabnoma' if turi in ('yuridik', 'yatt') else 'Ogohlantirish'
            out.append({
                'anketa_raqami': r.get('anketa_raqami', ''),
                'mijoz_nomi': mijoz['ism'] if mijoz else r.get('mijoz_nomi', ''),
                'turi': turi,
                'manzil': mijoz['manzil'] if mijoz else '',
                'telefon': mijoz['telefon'] if mijoz else '',
                'dpd_max': r.get('dpd_max', 0),
                'jami_qarz': r.get('jami_qarz', 0),
                'xat_turi': xat_turi,
            })
        return out

    def export_excel(self):
        rows = self._selected_rows()
        if not rows:
            messagebox.showinfo("Diqqat", "Avval ro'yxatdan mijozlarni tanlang "
                                           "('Birinchi paketni belgilash' yordam beradi).")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="talabnoma_royxati.xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        try:
            excel_rows = self._rows_for_excel(rows)
            importer.export_tahlil_excel(excel_rows, out_path)
            messagebox.showinfo(
                "Tayyor",
                f"{len(excel_rows)} ta qator eksport qilindi:\n{out_path}\n\n"
                "Manzil / Telefon ustunlarini tahrirlab, so'ng "
                "'Tahrirlangan Excel'ni yuklash' orqali qaytaring."
            )
            webbrowser.open(out_path)
        except Exception as e:
            messagebox.showerror("Xato", str(e))

    def import_excel_updates(self):
        filepath = filedialog.askopenfilename(
            title="Tahrirlangan Excel faylni tanlang",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
        if not filepath:
            return
        try:
            result = importer.import_manzil_updates(filepath)
            msg = f"{result['yangilandi']} ta mijoz manzili/ma'lumoti yangilandi."
            if result['otkazib_yuborildi']:
                msg += f"\n{result['otkazib_yuborildi']} ta qator o'tkazib yuborildi " \
                       f"(anketa raqami portfelda topilmadi)."
            messagebox.showinfo("Tayyor", msg)
            self.refresh_stats()
        except Exception as e:
            messagebox.showerror("Xato", str(e))

    def search_single(self):
        anketa = self.search_var.get().strip()
        if not anketa:
            return
        rows = db.get_portfel_by_anketa(anketa)
        self._status_map = db.get_latest_xat_status_by_portfel()
        self._rows_cache = rows
        self._fill_tree(rows)

    def _generate_for_row(self, portfel_row, skip_if_exists=True):
        anketa = portfel_row.get('anketa_raqami', 'noma_lum')

        if skip_if_exists and db.xat_mavjudmi(anketa):
            # Bitta anketaga faqat bitta xat — bu anketa uchun allaqachon
            # (istalgan holatda) xat mavjud, qayta yaratilmaydi.
            return None, None, True

        turi, mijoz = resolve_mijoz(portfel_row)
        xat_turi = 'Talabnoma' if turi in ('yuridik', 'yatt') else 'Ogohlantirish'

        mijoz_ism = mijoz['ism'] if mijoz else portfel_row.get('mijoz_nomi', '')
        mijoz_manzil = mijoz['manzil'] if mijoz else ''
        rahbar_ism = mijoz.get('rahbar_ism') if mijoz else ''

        settings = db.get_all_settings()
        fname = f"{xat_turi}_{letters.safe_filename(anketa)}_{letters.safe_filename(mijoz_ism)}.docx"
        out_path = os.path.join(bugungi_papka('Xatlar'), fname)

        letters.generate_letter(
            output_path=out_path,
            xat_turi=xat_turi,
            mijoz_ism=mijoz_ism,
            mijoz_manzil=mijoz_manzil,
            portfel_row=portfel_row,
            settings=settings,
            anketa_raqami=anketa,
            rahbar_ism=rahbar_ism,
        )

        want_pdf = self.format_var.get().startswith('PDF')
        pdf_xato = None
        if want_pdf:
            # PDF konvertatsiyasi (ayniqsa ommaviy rejimda) ba'zan beqaror ishlashi
            # mumkin — muvaffaqiyatsiz bo'lsa, xat butunlay yo'qolib ketmasin, .docx
            # holida saqlanib qolsin va bazaga baribir yozilsin.
            try:
                out_path = letters.convert_docx_to_pdf(out_path, delete_docx=True)
            except Exception as e:
                pdf_xato = str(e)

        muddat_kun = int(settings.get('eslatma_muddati_kun', 3))
        db.create_xat(
            portfel_id=portfel_row['id'],
            anketa_raqami=anketa,
            mijoz_nomi=mijoz_ism,
            mijoz_turi=turi,
            xat_turi=xat_turi,
            fayl_yoli=out_path,
            muddat_kun=muddat_kun,
        )
        return out_path, pdf_xato, False

    def generate_bulk(self):
        rows = self._selected_rows()
        if not rows:
            messagebox.showinfo("Diqqat", "Iltimos, kamida bitta mijozni tanlang "
                                           "('Birinchi paketni belgilash' yordam beradi).")
            return

        os.makedirs(XATLAR_DIR, exist_ok=True)
        created = []
        pdf_muvaffaqiyatsiz = []
        otkazib_yuborildi = []
        errors = []
        for r in rows:
            try:
                path, pdf_xato, skipped = self._generate_for_row(r)
                if skipped:
                    otkazib_yuborildi.append(r.get('anketa_raqami'))
                    continue
                created.append(path)
                if pdf_xato:
                    pdf_muvaffaqiyatsiz.append(r.get('anketa_raqami'))
            except Exception as e:
                errors.append(f"{r.get('anketa_raqami')}: {e}")

        out_dir = bugungi_papka('Xatlar')
        msg = f"{len(created)} ta xat yaratildi.\nJoylashuv: {out_dir}"
        if otkazib_yuborildi:
            msg += (f"\n\nℹ {len(otkazib_yuborildi)} ta anketa uchun xat allaqachon mavjud edi "
                    f"— takroriy yaratilmadi (bitta anketaga bitta xat).")
        if pdf_muvaffaqiyatsiz:
            msg += (f"\n\n⚠ {len(pdf_muvaffaqiyatsiz)} ta xat PDF'ga aylantirilmadi (Word "
                    f"bilan bog'liq vaqtinchalik muammo) — ular Word (.docx) holida saqlandi, "
                    f"lekin baribir ro'yxatga to'g'ri qo'shildi. Ularni qayta PDF qilish shart "
                    f"emas — Word holida ham yuborsangiz bo'laveradi.")
        if errors:
            msg += f"\n\n{len(errors)} ta xatoda:\n" + '\n'.join(errors[:5])
        messagebox.showinfo("Tayyor", msg)
        if created:
            webbrowser.open(out_dir)
        self.app.tab_dashboard.refresh()
        self.app.tab_xatlar.refresh()
        self.refresh_stats()

    def generate_single(self):
        anketa = self.search_var.get().strip()
        if not anketa:
            messagebox.showinfo("Diqqat", "Anketa raqamini kiriting.")
            return
        if db.xat_mavjudmi(anketa):
            messagebox.showinfo(
                "Diqqat",
                f"Anketa {anketa} uchun allaqachon xat mavjud — bitta anketaga bitta xat "
                "yaratiladi. Agar qayta yaratish kerak bo'lsa, avval 'Yuborilgan xatlar "
                "hisoboti' bo'limida eskisini o'chiring (nolga tushiring)."
            )
            return
        rows = db.get_portfel_by_anketa(anketa)
        if not rows:
            messagebox.showinfo("Topilmadi", "Bu anketa raqami bo'yicha ma'lumot topilmadi.")
            return
        row = rows[0]
        os.makedirs(XATLAR_DIR, exist_ok=True)
        try:
            path, pdf_xato, skipped = self._generate_for_row(row)
            msg = f"Xat yaratildi:\n{path}"
            if pdf_xato:
                msg += ("\n\n⚠ PDF'ga aylantirishda vaqtinchalik muammo bo'ldi — Word (.docx) "
                        "holida saqlandi, lekin ro'yxatga to'g'ri qo'shildi.")
            messagebox.showinfo("Tayyor", msg)
            webbrowser.open(path)
        except Exception as e:
            messagebox.showerror("Xato", str(e))
        self.app.tab_dashboard.refresh()
        self.app.tab_xatlar.refresh()


class XatlarTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Xatlar holati", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Tayyorlangan xat 3 kun ichida yuborilmasa, 'muddati o'tgan' deb belgilanadi.",
                  style='Sub.TLabel').pack(anchor='w', padx=20, pady=(0, 14))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="✓ Yuborildi deb belgilash", style='Accent.TButton',
                   command=self.mark_sent).pack(side='left', padx=10)
        ttk.Button(toolbar, text="📂 Faylni ochish", command=self.open_file).pack(side='left')

        toolbar_check = ttk.Frame(self)
        toolbar_check.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Label(toolbar_check, text="Anketa raqami bo'yicha topib belgilash:").pack(side='left')
        self.qidiruv_var = tk.StringVar()
        qidiruv_entry = ttk.Entry(toolbar_check, textvariable=self.qidiruv_var, width=16)
        qidiruv_entry.pack(side='left', padx=6)
        qidiruv_entry.bind('<Return>', lambda e: self.qidirib_belgilash())
        ttk.Button(toolbar_check, text="🔍 Topib belgilash", command=self.qidirib_belgilash).pack(side='left')
        ttk.Button(toolbar_check, text="☑ Hammasini belgilash", command=self.hammasini_belgilash).pack(
            side='left', padx=(16, 0))
        ttk.Button(toolbar_check, text="☐ Belgilarni bekor qilish", command=self.belgilarni_bekor_qilish).pack(
            side='left', padx=6)

        toolbar2 = ttk.Frame(self)
        toolbar2.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Button(toolbar2, text="🗑 Tanlangan xatlarni o'chirish (nolga tushirish)",
                   command=self.delete_selected).pack(side='left')
        ttk.Button(toolbar2, text="🗑 Barcha 'Tayyor' xatlarni tozalash",
                   command=self.delete_all_tayyor).pack(side='left', padx=10)
        ttk.Button(toolbar2, text="🧹 Dublikat (bir anketaga bir nechta) xatlarni tozalash",
                   command=self.clean_duplicates).pack(side='left', padx=10)

        ttk.Label(self, text="Xat 'Yuborildi' deb belgilangach, 'Davo ariza' bo'limida davo ariza "
                              "tayyorlashingiz mumkin bo'ladi. Katakchani (☐) bosib bir nechta "
                              "xatni belgilashingiz mumkin — 'Yuborildi deb belgilash' o'shalarga qo'llanadi.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(anchor='w', padx=20, pady=(4, 8))

        cols = ('check', 'anketa', 'mijoz', 'turi', 'xat_turi', 'yaratilgan', 'muddat', 'holat', 'davo_ariza')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'check': '', 'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'xat_turi': 'Xat turi',
                    'yaratilgan': 'Yaratilgan', 'muddat': 'Yuborish muddati', 'holat': 'Holat',
                    'davo_ariza': 'Davo ariza'}
        widths = {'check': 34, 'anketa': 90, 'mijoz': 220, 'turi': 75, 'xat_turi': 95,
                  'yaratilgan': 110, 'muddat': 110, 'holat': 105, 'davo_ariza': 100}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor='center' if c == 'check' else 'w')
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.tag_configure('yuborildi', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree.bind('<Button-1>', self._on_tree_click)

        self._id_map = {}
        self.checked = set()
        self.refresh()

    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row:
            return
        if col == '#1':  # 'check' ustuni
            if row in self.checked:
                self.checked.discard(row)
            else:
                self.checked.add(row)
            self._qayta_chiz_belgi(row)

    def _qayta_chiz_belgi(self, iid):
        belgi = '☑' if iid in self.checked else '☐'
        vals = list(self.tree.item(iid, 'values'))
        vals[0] = belgi
        self.tree.item(iid, values=vals)

    def qidirib_belgilash(self):
        anketa = self.qidiruv_var.get().strip()
        if not anketa:
            return
        topildi = None
        for iid, r in self._id_map.items():
            if str(r.get('anketa_raqami', '')) == anketa:
                topildi = iid
                break
        if not topildi:
            messagebox.showinfo("Topilmadi", f"Anketa {anketa} bo'yicha xat topilmadi.")
            return
        self.checked.add(topildi)
        self._qayta_chiz_belgi(topildi)
        self.tree.selection_set(topildi)
        self.tree.see(topildi)
        self.qidiruv_var.set('')

    def hammasini_belgilash(self):
        for iid in self._id_map:
            self.checked.add(iid)
            self._qayta_chiz_belgi(iid)

    def belgilarni_bekor_qilish(self):
        for iid in list(self.checked):
            self.checked.discard(iid)
            self._qayta_chiz_belgi(iid)

    def refresh(self):
        db.update_muddati_otganlar()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.checked = set()
        rows = db.get_xatlar()
        for r in rows:
            tag = ''
            holat_label = r['holat']
            if r['holat'] == 'muddati_otgan':
                tag = 'otgan'
                holat_label = "⚠ Muddati o'tgan"
            elif r['holat'] == 'yuborildi':
                tag = 'yuborildi'
                holat_label = "✓ Yuborildi"
            else:
                holat_label = "Tayyor"

            def fmt_date(s):
                try:
                    return datetime.datetime.fromisoformat(s).strftime('%d.%m.%Y')
                except Exception:
                    return s or ''

            davo_label = "✓ Tayyor" if r.get('davo_ariza_fayl_yoli') else "—"

            iid = str(r['id'])
            self.tree.insert('', 'end', iid=iid, values=(
                '☐', r['anketa_raqami'], r['mijoz_nomi'], r['mijoz_turi'], r['xat_turi'],
                fmt_date(r['yaratilgan_sana']), fmt_date(r['muddat_sana']), holat_label, davo_label
            ), tags=(tag,))
            self._id_map[iid] = r

        self.app.tab_dashboard.refresh()

    def _effective_selection(self):
        """Katakcha (☐) bilan belgilanganlar bo'lsa — o'shalar, aks holda odatiy
        (Ctrl/Shift bosib) tanlangan qatorlar ishlatiladi."""
        if self.checked:
            return list(self.checked)
        return list(self.tree.selection())

    def mark_sent(self):
        selected = self._effective_selection()
        if not selected:
            messagebox.showinfo("Diqqat", "Xatni tanlang (katakchani belgilang yoki qatorni bosing).")
            return
        for iid in selected:
            db.mark_xat_yuborildi(int(iid))
        self.refresh()

    def open_file(self):
        selected = self.tree.selection()
        if not selected:
            return
        r = self._id_map.get(selected[0])
        if r and r['fayl_yoli'] and os.path.exists(r['fayl_yoli']):
            webbrowser.open(r['fayl_yoli'])
        else:
            messagebox.showinfo("Topilmadi", "Fayl topilmadi.")

    def delete_selected(self):
        selected = self._effective_selection()
        if not selected:
            messagebox.showinfo("Diqqat", "O'chirish uchun kamida bitta xatni tanlang "
                                           "(katakchani belgilang yoki qatorni bosing).")
            return
        rows = [self._id_map.get(iid) for iid in selected if self._id_map.get(iid)]
        yuborilgan = [r for r in rows if r.get('holat') == 'yuborildi']
        if yuborilgan:
            messagebox.showwarning(
                "Diqqat",
                f"Tanlanganlar orasida {len(yuborilgan)} ta allaqachon 'Yuborildi' deb "
                "belgilangan xat bor — bunday xatlar o'chirilmaydi (Davo ariza/Sud/MIB "
                "bosqichiga bog'liq bo'lishi mumkin). Faqat 'Tayyor'/'Muddati o'tgan' "
                "holatidagi xatlar o'chiriladi."
            )
        ochiriladigan = [r for r in rows if r.get('holat') != 'yuborildi']
        if not ochiriladigan:
            return
        javob = messagebox.askyesno(
            "Tasdiqlash",
            f"{len(ochiriladigan)} ta xat bazadan butunlay o'chiriladi (nolga tushiriladi). "
            "Fayllar diskda qoladi, ularni qo'lda o'chirishingiz mumkin. Davom etaymi?"
        )
        if not javob:
            return
        n = db.delete_xatlar([r['id'] for r in ochiriladigan])
        messagebox.showinfo("Bajarildi", f"{n} ta xat yozuvi o'chirildi.")
        self.refresh()
        self.app.tab_dashboard.refresh()

    def delete_all_tayyor(self):
        ids = db.get_xatlar_ids_by_holat('tayyor')
        ids += db.get_xatlar_ids_by_holat('muddati_otgan')
        if not ids:
            messagebox.showinfo("Diqqat", "'Tayyor' yoki 'Muddati o'tgan' holatidagi xatlar yo'q.")
            return
        javob = messagebox.askyesno(
            "Tasdiqlash",
            f"Hali yuborilmagan (Tayyor + Muddati o'tgan) jami {len(ids)} ta xat bazadan "
            "BUTUNLAY o'chiriladi va hisoblagichlar nolga tushiriladi. Yuborilgan xatlarga "
            "tegilmaydi. Fayllar diskda qoladi. Davom etaymi?"
        )
        if not javob:
            return
        n = db.delete_xatlar(ids)
        messagebox.showinfo("Bajarildi", f"{n} ta xat yozuvi o'chirildi, hisoblagichlar nolga tushdi.")
        self.refresh()
        self.app.tab_dashboard.refresh()

    def clean_duplicates(self):
        dup = db.get_duplicate_xat_anketalar()
        if not dup:
            messagebox.showinfo("Diqqat", "Dublikat (bir anketaga bir nechta) xat topilmadi.")
            return
        jami_ortiqcha = sum(d['soni'] - 1 for d in dup)
        javob = messagebox.askyesno(
            "Tasdiqlash",
            f"{len(dup)} ta anketa uchun bir nechtadan xat yaratilgan holat topildi "
            f"(jami {jami_ortiqcha} ta ortiqcha yozuv). Har bir anketa uchun eng "
            "muhim (Davo ariza/Sud/MIBga bog'langan yoki eng oxirgi yuborilgan) bitta "
            "yozuv saqlanib qoladi, qolganlari o'chiriladi. Davom etaymi?"
        )
        if not javob:
            return
        n = db.tozala_duplikat_xatlar()
        messagebox.showinfo("Bajarildi", f"{n} ta dublikat yozuv o'chirildi. Endi har bir "
                                          "anketada faqat bitta xat qoldi.")
        self.refresh()
        self.app.tab_dashboard.refresh()


class TaminotDialog(tk.Toplevel):
    """Bitta mijoz uchun kafil/garov ma'lumotlarini qo'lda kiritish oynasi."""
    FIELDS = [
        ('taminot_turi', "Ta'minot turi", 'combo',
         ['yoq', 'kafillik', 'garov', 'kafillik_garov']),
        ('kafil_ism', 'Kafil F.I.Sh', 'text', None),
        ('kafil_manzil', 'Kafil manzili', 'text', None),
        ('kafil_pinfl', 'Kafil PINFL', 'text', None),
        ('kafil_passport', 'Kafil passport (seriya-raqam)', 'text', None),
        ('kafil_passport_sana', 'Kafil passport berilgan sana', 'text', None),
        ('kafil_passport_organ', 'Kafil passport bergan organ', 'text', None),
        ('kafil_tel', 'Kafil telefon', 'text', None),
        ('garov_tavsifi', 'Garov mulki tavsifi', 'multitext', None),
        ('garov_bahosi', "Garov bahosi (so'm)", 'text', None),
        ('pochta_xarajati', "Pochta xarajati (so'm)", 'text', None),
    ]

    def __init__(self, parent, anketa_raqami, mijoz_nomi):
        super().__init__(parent)
        self.title(f"Ta'minot ma'lumotlari — {mijoz_nomi}")
        self.geometry("560x620")
        self.configure(bg=BG)
        self.anketa_raqami = anketa_raqami
        self.result_saved = False

        ttk.Label(self, text=f"Anketa №{anketa_raqami} — {mijoz_nomi}",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 10))

        current = db.get_taminot(anketa_raqami) or {}

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        body = ttk.Frame(canvas)
        body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=body, anchor='nw', width=520)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True, padx=(16, 0))
        scrollbar.pack(side='right', fill='y')

        self.vars = {}
        self.text_widgets = {}
        for field, label, kind, options in self.FIELDS:
            row = ttk.Frame(body)
            row.pack(fill='x', pady=5, padx=(0, 16))
            ttk.Label(row, text=label, width=28, wraplength=170).pack(side='left', anchor='n')
            val = current.get(field, '') or ''
            if kind == 'combo':
                var = tk.StringVar(value=str(val) or 'yoq')
                ttk.Combobox(row, textvariable=var, values=options, state='readonly', width=28).pack(side='left')
                self.vars[field] = var
            elif kind == 'multitext':
                txt = tk.Text(row, width=32, height=4, font=('Segoe UI', 9))
                txt.insert('1.0', str(val))
                txt.pack(side='left')
                self.text_widgets[field] = txt
            else:
                var = tk.StringVar(value=str(val))
                ttk.Entry(row, textvariable=var, width=32).pack(side='left')
                self.vars[field] = var

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=14, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="💾 Saqlash", style='Accent.TButton', command=self.save).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def save(self):
        fields = {}
        for field, var in self.vars.items():
            fields[field] = var.get().strip()
        for field, txt in self.text_widgets.items():
            fields[field] = txt.get('1.0', 'end').strip()
        db.upsert_taminot(self.anketa_raqami, **fields)
        self.result_saved = True
        self.destroy()


class OlibKelindiDialog(tk.Toplevel):
    """Davo ariza Palata/suddan ish raqami va sana bilan qaytganini tasdiqlash oynasi."""
    def __init__(self, parent, mijoz_nomi):
        super().__init__(parent)
        self.title(f"Olib kelindi — {mijoz_nomi}")
        self.geometry("460x380")
        self.configure(bg=BG)
        self.result = None
        self.skan_yoli = None

        ttk.Label(self, text="Davo ariza olib kelinganini tasdiqlash",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mijoz_nomi, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 14))

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Ish raqami:", width=16).pack(side='left')
        self.ish_raqami_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.ish_raqami_var, width=24).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="Imzo/kelgan sana:", width=16).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row2, textvariable=self.sana_var, width=24).pack(side='left')
        ttk.Label(self, text="(format: kun.oy.yil, masalan 14.08.2026)",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 10))

        ttk.Label(self, text="SSPdan olib kelingan hujjat skani (PDF) — majburiy:",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(4, 4))
        file_row = ttk.Frame(self)
        file_row.pack(fill='x', padx=16)
        self.skan_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.skan_label.pack(side='left')
        ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_skan).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Tasdiqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def tanlash_skan(self):
        filepath = filedialog.askopenfilename(
            title="SSPdan olib kelingan hujjat skanini (PDF) tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.skan_yoli = filepath
            self.skan_label.config(text=os.path.basename(filepath))

    def confirm(self):
        ish_raqami = self.ish_raqami_var.get().strip()
        sana = self.sana_var.get().strip()
        if not ish_raqami or not sana:
            messagebox.showerror("Xato", "Ish raqami va sanani kiriting.")
            return
        if not self.skan_yoli:
            messagebox.showerror("Xato", "SSPdan olib kelingan hujjat skanini (PDF) yuklang — bu majburiy.")
            return
        self.result = (ish_raqami, sana, self.skan_yoli)
        self.destroy()


class SudTopshirishDialog(tk.Toplevel):
    """Davo ariza sudga (Fuqarolik/Iqtisodiy) topshirilganini tasdiqlash oynasi."""
    def __init__(self, parent, mijoz_nomi, sud_nomi):
        super().__init__(parent)
        self.title(f"Sudga topshirildi — {mijoz_nomi}")
        self.geometry("480x400")
        self.configure(bg=BG)
        self.result = None
        self.buyruq_yol = None

        ttk.Label(self, text="Sudga topshirilganini tasdiqlash",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mijoz_nomi, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 2))
        ttk.Label(self, text=f"Sud: {sud_nomi}", style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 14))

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Sud ish raqami:", width=16).pack(side='left')
        self.ish_raqami_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.ish_raqami_var, width=24).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="Topshirilgan sana:", width=16).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row2, textvariable=self.sana_var, width=24).pack(side='left')
        ttk.Label(self, text="(format: kun.oy.yil, masalan 14.08.2026)",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 10))

        ttk.Label(self, text="Sud buyrug'i (agar mavjud bo'lsa, PDF):",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(4, 4))
        file_row = ttk.Frame(self)
        file_row.pack(fill='x', padx=16)
        self.fayl_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.fayl_label.pack(side='left')
        ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_fayl).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Tasdiqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def tanlash_fayl(self):
        filepath = filedialog.askopenfilename(
            title="Sud buyrug'i (PDF) faylini tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.buyruq_yol = filepath
            self.fayl_label.config(text=os.path.basename(filepath))

    def confirm(self):
        ish_raqami = self.ish_raqami_var.get().strip()
        sana = self.sana_var.get().strip()
        if not ish_raqami or not sana:
            messagebox.showerror("Xato", "Sud ish raqami va sanani kiriting.")
            return
        self.result = (ish_raqami, sana, self.buyruq_yol)
        self.destroy()


class MibToxtatishDialog(tk.Toplevel):
    """MIB ijro ishini to'xtatish/yakunlashni tasdiqlash oynasi."""
    def __init__(self, parent, mijoz_nomi, tavsiya_xabari=''):
        super().__init__(parent)
        self.title(f"To'xtatish / Yakunlash — {mijoz_nomi}")
        self.geometry("500x460")
        self.configure(bg=BG)
        self.result = None
        self.asos_hujjat_yoli = None

        ttk.Label(self, text="MIB ijro ishini to'xtatish / yakunlash",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mijoz_nomi, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 8))

        if tavsiya_xabari:
            box = tk.Frame(self, bg='#FDF3E7', highlightbackground=KRAFT, highlightthickness=1)
            box.pack(fill='x', padx=16, pady=(0, 10))
            tk.Label(box, text=f"Tizim tavsiyasi: {tavsiya_xabari}", bg='#FDF3E7', fg=INK,
                     font=('Segoe UI', 9), wraplength=440, justify='left').pack(
                anchor='w', padx=10, pady=8)

        ttk.Label(self, text="Sabab / izoh:").pack(anchor='w', padx=16, pady=(4, 2))
        self.sabab_text = tk.Text(self, height=5, width=54, font=('Segoe UI', 10))
        self.sabab_text.pack(padx=16, pady=(0, 8))
        if tavsiya_xabari:
            self.sabab_text.insert('1.0', tavsiya_xabari)

        row = ttk.Frame(self)
        row.pack(fill='x', padx=16, pady=(0, 8))
        ttk.Label(row, text="Sana:", width=10).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row, textvariable=self.sana_var, width=20).pack(side='left')

        ttk.Label(self, text="Yakunlash asosi hujjati (PDF) — majburiy:",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(4, 4))
        ttk.Label(self, text="(masalan: MIBning ishni tugatish to'g'risidagi qarori, to'liq "
                              "undirilganlik dalolatnomasi va h.k.)",
                  style='Sub.TLabel', wraplength=440, justify='left').pack(anchor='w', padx=16, pady=(0, 4))
        file_row = ttk.Frame(self)
        file_row.pack(fill='x', padx=16)
        self.asos_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.asos_label.pack(side='left')
        ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_asos).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Tasdiqlash", style='Accent.TButton', command=self.confirm).pack(
            side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def tanlash_asos(self):
        filepath = filedialog.askopenfilename(
            title="Yakunlash asosi hujjatini (PDF) tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.asos_hujjat_yoli = filepath
            self.asos_label.config(text=os.path.basename(filepath))

    def confirm(self):
        sabab = self.sabab_text.get('1.0', 'end').strip()
        sana = self.sana_var.get().strip()
        if not sabab:
            messagebox.showerror("Xato", "Sabab/izohni kiriting.")
            return
        if not sana:
            messagebox.showerror("Xato", "Sanani kiriting.")
            return
        if not self.asos_hujjat_yoli:
            messagebox.showerror("Xato", "Yakunlash asosi hujjatini (PDF) yuklang — bu majburiy.")
            return
        self.result = (sabab, sana, self.asos_hujjat_yoli)
        self.destroy()


class MibTransferDialog(tk.Toplevel):
    """Hujjat MIBga (Ijro byurosiga) o'tkazilganini tasdiqlash oynasi."""
    def __init__(self, parent, mijoz_nomi, sud_ish_raqami):
        super().__init__(parent)
        self.title(f"MIBga o'tkazish — {mijoz_nomi}")
        self.geometry("500x460")
        self.configure(bg=BG)
        self.result = None
        self.ijro_varaqasi_yol = None
        self.sud_buyrugi_yol = None

        ttk.Label(self, text="MIBga o'tkazilganini tasdiqlash",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mijoz_nomi, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 2))
        ttk.Label(self, text=f"Sud ish raqami (solishtirish uchun): {sud_ish_raqami}",
                  style='Sub.TLabel', wraplength=460).pack(anchor='w', padx=16, pady=(0, 14))

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="MIB ish raqami:", width=16).pack(side='left')
        self.ish_raqami_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.ish_raqami_var, width=26).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="O'tkazilgan sana:", width=16).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row2, textvariable=self.sana_var, width=26).pack(side='left')

        ttk.Label(self, text="Sud buyrug'i / hal qiluv qarori (PDF) — majburiy:",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(14, 4))
        file_row0 = ttk.Frame(self)
        file_row0.pack(fill='x', padx=16)
        self.sud_fayl_label = ttk.Label(file_row0, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.sud_fayl_label.pack(side='left')
        ttk.Button(file_row0, text="📎 PDF tanlash", command=self.tanlash_sud_fayl).pack(side='left', padx=8)

        ttk.Label(self, text="Ijro varaqasi (PDF) — majburiy:", style='Sub.TLabel').pack(
            anchor='w', padx=16, pady=(14, 4))
        file_row = ttk.Frame(self)
        file_row.pack(fill='x', padx=16)
        self.fayl_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.fayl_label.pack(side='left')
        ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_fayl).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=20, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Tasdiqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def tanlash_fayl(self):
        filepath = filedialog.askopenfilename(
            title="Ijro varaqasi (PDF) faylini tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.ijro_varaqasi_yol = filepath
            self.fayl_label.config(text=os.path.basename(filepath))

    def tanlash_sud_fayl(self):
        filepath = filedialog.askopenfilename(
            title="Sud buyrug'i / hal qiluv qarori (PDF) faylini tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.sud_buyrugi_yol = filepath
            self.sud_fayl_label.config(text=os.path.basename(filepath))

    def confirm(self):
        ish_raqami = self.ish_raqami_var.get().strip()
        sana = self.sana_var.get().strip()
        if not ish_raqami or not sana:
            messagebox.showerror("Xato", "MIB ish raqami va sanani kiriting.")
            return
        if not self.sud_buyrugi_yol:
            messagebox.showerror("Xato", "Sud buyrug'i / hal qiluv qarori (PDF) faylini tanlang — bu majburiy.")
            return
        if not self.ijro_varaqasi_yol:
            messagebox.showerror("Xato", "Ijro varaqasi (PDF) faylini tanlang — bu majburiy.")
            return
        self.result = (ish_raqami, sana, self.ijro_varaqasi_yol, self.sud_buyrugi_yol)
        self.destroy()


class MibAmalDialog(tk.Toplevel):
    """MIBda amalga oshirilgan yangi harakatni (jurnal yozuvini) kiritish oynasi."""
    AMAL_TURLARI = [
        ('oylik_ish_haqqi', "Oylik ish haqqiga qaratildi"),
        ('avto_taqiq', "Avto transportga taqiq qo'yildi"),
        ('avto_qidiruv', "Avto transport qidiruvga berildi"),
        ('chetga_chiqish_taqiq', "Chetga chiqishga taqiq qo'yilgan"),
        ('majburiy_xatlov', "Majburiy xatlov o'tkazildi"),
        ('sotish_togridan', "To'g'ridan-to'g'ri sotildi"),
        ('sotish_auksion', "Auksion yo'li bilan sotildi"),
        ('kafil_ish', "Kafil bo'yicha ish qilindi"),
        ('garov_xatlov', "Garov mulkiga xatlov o'tkazildi"),
        ('garov_sotish', "Garov mulki sotildi"),
    ]

    def __init__(self, parent, mijoz_nomi):
        super().__init__(parent)
        self.title(f"Yangi MIB harakati — {mijoz_nomi}")
        self.geometry("520x620")
        self.configure(bg=BG)
        self.result = None
        self.dalolatnoma_yol = None
        self.auksion_rasm_yollari = []

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        body = ttk.Frame(canvas)
        body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=body, anchor='nw', width=490)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side='right', fill='y')

        ttk.Label(body, text=f"Mijoz: {mijoz_nomi}", style='Header.TLabel').pack(anchor='w', pady=(0, 10))

        ttk.Label(body, text="Harakat turi:").pack(anchor='w')
        self.turi_var = tk.StringVar(value=self.AMAL_TURLARI[0][1])
        turi_combo = ttk.Combobox(body, textvariable=self.turi_var,
                                   values=[v for k, v in self.AMAL_TURLARI],
                                   state='readonly', width=42)
        turi_combo.pack(anchor='w', pady=(2, 10))
        turi_combo.bind('<<ComboboxSelected>>', lambda e: self._update_fields())

        row_sana = ttk.Frame(body)
        row_sana.pack(fill='x', pady=4)
        ttk.Label(row_sana, text="Sana:", width=16).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row_sana, textvariable=self.sana_var, width=24).pack(side='left')

        # ---- Oddiy tavsif (kafilsiz turlar uchun) ----
        self.frame_oddiy = ttk.Frame(body)
        ttk.Label(self.frame_oddiy, text="Qo'shimcha izoh (ixtiyoriy):").pack(anchor='w', pady=(6, 2))
        self.tavsif_text = tk.Text(self.frame_oddiy, width=52, height=3, font=('Segoe UI', 9))
        self.tavsif_text.pack(anchor='w')

        # ---- Oylik ish haqqiga qaratish maydonlari ----
        self.frame_oylik = ttk.Frame(body)
        row_oylik = ttk.Frame(self.frame_oylik)
        row_oylik.pack(fill='x', pady=3)
        ttk.Label(row_oylik, text="Ushbu safar undirilgan summa (so'm):", width=32).pack(side='left')
        self.undirilgan_summa_var = tk.StringVar()
        ttk.Entry(row_oylik, textvariable=self.undirilgan_summa_var, width=20).pack(side='left')
        ttk.Label(self.frame_oylik, text="Qo'shimcha izoh (ixtiyoriy):").pack(anchor='w', pady=(8, 2))
        self.tavsif_oylik_text = tk.Text(self.frame_oylik, width=52, height=3, font=('Segoe UI', 9))
        self.tavsif_oylik_text.pack(anchor='w')

        # ---- Majburiy xatlov maydonlari ----
        self.frame_xatlov = ttk.Frame(body)
        for label, attr in [("Mulk nomi:", 'mulk_nomi_var'), ("Mulk soni:", 'mulk_soni_var'),
                             ("Mulk summasi (so'm):", 'mulk_summasi_var')]:
            row = ttk.Frame(self.frame_xatlov)
            row.pack(fill='x', pady=3)
            ttk.Label(row, text=label, width=20).pack(side='left')
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(row, textvariable=var, width=28).pack(side='left')
        ttk.Label(self.frame_xatlov, text="Dalolatnoma nusxasi (PDF):",
                  style='Sub.TLabel').pack(anchor='w', pady=(8, 4))
        dal_row = ttk.Frame(self.frame_xatlov)
        dal_row.pack(fill='x')
        self.dalolatnoma_label = ttk.Label(dal_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.dalolatnoma_label.pack(side='left')
        ttk.Button(dal_row, text="📎 PDF tanlash", command=self.tanlash_dalolatnoma).pack(side='left', padx=8)

        # ---- To'g'ridan-to'g'ri sotish maydonlari ----
        self.frame_togridan = ttk.Frame(body)
        for label, attr in [("Sotilgan mulk nomi:", 'sotilgan_nomi_var'),
                             ("Soni:", 'sotilgan_soni_var'),
                             ("Sotilgan summa (so'm):", 'sotilgan_summasi_var')]:
            row = ttk.Frame(self.frame_togridan)
            row.pack(fill='x', pady=3)
            ttk.Label(row, text=label, width=20).pack(side='left')
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(row, textvariable=var, width=28).pack(side='left')

        # ---- Auksion maydonlari ----
        self.frame_auksion = ttk.Frame(body)
        for label, attr in [("Auksion sanasi:", 'auksion_sana_var'),
                             ("Auksion narxi (so'm):", 'auksion_narxi_var'),
                             ("Lot raqami:", 'auksion_lot_var')]:
            row = ttk.Frame(self.frame_auksion)
            row.pack(fill='x', pady=3)
            ttk.Label(row, text=label, width=20).pack(side='left')
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(row, textvariable=var, width=28).pack(side='left')
        ttk.Label(self.frame_auksion, text="Lot rasmlari (.jpg/.png, bir nechta tanlash mumkin):",
                  style='Sub.TLabel', wraplength=440).pack(anchor='w', pady=(8, 4))
        rasm_row = ttk.Frame(self.frame_auksion)
        rasm_row.pack(fill='x')
        self.rasm_label = ttk.Label(rasm_row, text="(rasm tanlanmagan)", style='Sub.TLabel')
        self.rasm_label.pack(side='left')
        ttk.Button(rasm_row, text="🖼 Rasmlar tanlash", command=self.tanlash_rasmlar).pack(side='left', padx=8)

        self._update_fields()

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Saqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def _turi_kaliti(self):
        for k, v in self.AMAL_TURLARI:
            if v == self.turi_var.get():
                return k
        return self.AMAL_TURLARI[0][0]

    def _update_fields(self):
        for f in (self.frame_oddiy, self.frame_xatlov, self.frame_togridan, self.frame_auksion,
                  self.frame_oylik):
            f.pack_forget()
        turi = self._turi_kaliti()
        if turi in ('majburiy_xatlov', 'garov_xatlov'):
            self.frame_xatlov.pack(fill='x', pady=(6, 0))
        elif turi in ('sotish_togridan', 'garov_sotish'):
            self.frame_togridan.pack(fill='x', pady=(6, 0))
        elif turi == 'sotish_auksion':
            self.frame_auksion.pack(fill='x', pady=(6, 0))
        elif turi == 'oylik_ish_haqqi':
            self.frame_oylik.pack(fill='x', pady=(6, 0))
        else:
            self.frame_oddiy.pack(fill='x', pady=(6, 0))

    def tanlash_dalolatnoma(self):
        filepath = filedialog.askopenfilename(
            title="Dalolatnoma (PDF) faylini tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.dalolatnoma_yol = filepath
            self.dalolatnoma_label.config(text=os.path.basename(filepath))

    def tanlash_rasmlar(self):
        filepaths = filedialog.askopenfilenames(
            title="Lot rasmlarini tanlang", filetypes=[("Rasmlar", "*.jpg *.jpeg *.png")]
        )
        if filepaths:
            self.auksion_rasm_yollari = list(filepaths)
            self.rasm_label.config(text=f"{len(filepaths)} ta rasm tanlandi")

    def confirm(self):
        turi = self._turi_kaliti()
        sana = self.sana_var.get().strip()
        if not sana:
            messagebox.showerror("Xato", "Sanani kiriting.")
            return

        data = {'amal_turi': turi, 'amal_sanasi': sana, 'tavsif': ''}

        if turi in ('majburiy_xatlov', 'garov_xatlov'):
            if not self.dalolatnoma_yol:
                messagebox.showerror("Xato", "Dalolatnoma (PDF) faylini tanlang.")
                return
            data['tavsif'] = self.tavsif_text.get('1.0', 'end').strip() if hasattr(self, 'tavsif_text') else ''
            data['mulk_nomi'] = self.mulk_nomi_var.get().strip()
            data['mulk_soni'] = self.mulk_soni_var.get().strip()
            try:
                data['mulk_summasi'] = float(self.mulk_summasi_var.get().strip() or 0)
            except ValueError:
                data['mulk_summasi'] = 0
            data['_dalolatnoma_src'] = self.dalolatnoma_yol
        elif turi in ('sotish_togridan', 'garov_sotish'):
            data['sotilgan_nomi'] = self.sotilgan_nomi_var.get().strip()
            data['sotilgan_soni'] = self.sotilgan_soni_var.get().strip()
            try:
                data['sotilgan_summasi'] = float(self.sotilgan_summasi_var.get().strip() or 0)
            except ValueError:
                data['sotilgan_summasi'] = 0
        elif turi == 'sotish_auksion':
            if not self.auksion_rasm_yollari:
                messagebox.showerror("Xato", "Kamida bitta lot rasmini tanlang.")
                return
            data['auksion_sana'] = self.auksion_sana_var.get().strip()
            try:
                data['auksion_narxi'] = float(self.auksion_narxi_var.get().strip() or 0)
            except ValueError:
                data['auksion_narxi'] = 0
            data['auksion_lot_raqami'] = self.auksion_lot_var.get().strip()
            data['_auksion_rasm_src'] = self.auksion_rasm_yollari
        elif turi == 'oylik_ish_haqqi':
            try:
                data['undirilgan_summa'] = float(self.undirilgan_summa_var.get().strip() or 0)
            except ValueError:
                data['undirilgan_summa'] = 0
            data['tavsif'] = self.tavsif_oylik_text.get('1.0', 'end').strip()
        else:
            data['tavsif'] = self.tavsif_text.get('1.0', 'end').strip()

        self.result = data
        self.destroy()


class MibTarixDialog(tk.Toplevel):
    """Bitta mijoz uchun barcha MIB harakatlari tarixini ko'rsatadi."""
    AMAL_NOMLARI = dict(MibAmalDialog.AMAL_TURLARI)

    def __init__(self, parent, mijoz_nomi, xat_id):
        super().__init__(parent)
        self.title(f"MIB harakatlari tarixi — {mijoz_nomi}")
        self.geometry("760x480")
        self.configure(bg=BG)

        ttk.Label(self, text=f"MIB harakatlari — {mijoz_nomi}",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 10))

        cols = ('sana', 'turi', 'tafsilot', 'fayl')
        tree = ttk.Treeview(self, columns=cols, show='headings', height=16)
        headings = {'sana': 'Sana', 'turi': 'Harakat turi', 'tafsilot': 'Tafsilot', 'fayl': 'Fayl'}
        widths = {'sana': 100, 'turi': 190, 'tafsilot': 320, 'fayl': 100}
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, width=widths[c])
        tree.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        amallar = db.get_mib_amallar(xat_id)
        self._fayl_map = {}
        for a in amallar:
            turi_nomi = self.AMAL_NOMLARI.get(a['amal_turi'], a['amal_turi'])
            tafsilot = a.get('tavsif', '') or ''
            fayl = ''
            if a['amal_turi'] in ('majburiy_xatlov', 'garov_xatlov'):
                tafsilot = f"{a.get('mulk_nomi','')} — {a.get('mulk_soni','')} dona, " \
                           f"{a.get('mulk_summasi',0):,.0f} so'm".replace(',', ' ')
                fayl = a.get('dalolatnoma_fayl', '') or ''
            elif a['amal_turi'] in ('sotish_togridan', 'garov_sotish'):
                tafsilot = f"{a.get('sotilgan_nomi','')} — {a.get('sotilgan_soni','')} dona, " \
                           f"{a.get('sotilgan_summasi',0):,.0f} so'm".replace(',', ' ')
            elif a['amal_turi'] == 'sotish_auksion':
                tafsilot = f"Lot №{a.get('auksion_lot_raqami','')} — " \
                           f"{a.get('auksion_narxi',0):,.0f} so'm".replace(',', ' ')
                fayl = a.get('auksion_rasmlar', '') or ''
            elif a['amal_turi'] == 'oylik_ish_haqqi':
                summa = a.get('undirilgan_summa') or 0
                tafsilot = f"Undirilgan summa: {summa:,.0f} so'm".replace(',', ' ')
                if a.get('tavsif'):
                    tafsilot += f" — {a['tavsif']}"

            iid = str(a['id'])
            tree.insert('', 'end', iid=iid, values=(a['amal_sanasi'], turi_nomi, tafsilot,
                                                       "📎 ochish" if fayl else ''))
            self._fayl_map[iid] = fayl

        def on_double_click(event):
            sel = tree.selection()
            if sel and self._fayl_map.get(sel[0]):
                fayl = self._fayl_map[sel[0]]
                birinchi = fayl.split(',')[0]
                if os.path.exists(birinchi):
                    webbrowser.open(birinchi)

        tree.bind('<Double-1>', on_double_click)

        ttk.Button(self, text="Yopish", command=self.destroy).pack(pady=(0, 16))
        self.transient(parent)
        self.grab_set()


class MijozHolatiDialog(tk.Toplevel):
    """Anketa raqami bo'yicha qidirilgan mijoz(lar)ning to'liq bosqich holatini ko'rsatadi."""
    XAT_HOLAT_NOMLARI = {'tayyor': 'Tayyor', 'yuborildi': "✓ Yuborildi",
                          'muddati_otgan': "⚠ Muddati o'tgan"}
    DAVO_HOLAT_NOMLARI = {'tayyor': 'Tayyor (Palataga topshirilgan)', 'olib_kelindi': "✓ Olib kelindi"}
    SUD_HOLAT_NOMLARI = {'topshirildi': "✓ Topshirilgan"}
    MIB_HOLAT_NOMLARI = {'otkazildi': "✓ O'tkazilgan"}
    MIB_AMAL_NOMLARI = dict(MibAmalDialog.AMAL_TURLARI)

    def __init__(self, parent, anketa, natija_royxati):
        super().__init__(parent)
        self.title(f"Mijoz holati — Anketa №{anketa}")
        self.geometry("620x600")
        self.configure(bg=BG)

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        body = ttk.Frame(canvas)
        body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=body, anchor='nw', width=590)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side='right', fill='y')

        if len(natija_royxati) > 1:
            ttk.Label(body, text=f"Diqqat: bu anketa raqami {len(natija_royxati)} ta turli "
                                  f"kredit/mijozga tegishli ekan — barchasi quyida ko'rsatilgan.",
                      style='Sub.TLabel', wraplength=560, justify='left').pack(anchor='w', pady=(0, 14))

        for idx, item in enumerate(natija_royxati):
            self._build_kartochka(body, item, idx, len(natija_royxati))

        ttk.Button(self, text="Yopish", command=self.destroy).pack(pady=(0, 16))
        self.transient(parent)
        self.grab_set()

    def _bosqich_qatori(self, parent, nomi, holat_matni, tag=None, fayl_yoli=None):
        row = tk.Frame(parent, bg=WHITE)
        row.pack(fill='x', pady=2)
        tk.Label(row, text=nomi, bg=WHITE, fg=INK, font=('Segoe UI', 9, 'bold'),
                 width=22, anchor='w').pack(side='left', padx=(10, 4), pady=4)
        color = ERR if tag == 'otgan' else (STAMP if tag == 'ok' else INK)
        clickable = bool(fayl_yoli and os.path.exists(fayl_yoli))
        matn = holat_matni + ("  📎 (ochish uchun bosing)" if clickable else "")
        lbl = tk.Label(row, text=matn, bg=WHITE, fg=(STAMP if clickable else color),
                       font=('Segoe UI', 9, 'underline') if clickable else ('Segoe UI', 9),
                       anchor='w', wraplength=380, justify='left',
                       cursor='hand2' if clickable else 'arrow')
        lbl.pack(side='left', pady=4)
        if clickable:
            lbl.bind('<Button-1>', lambda e, f=fayl_yoli: webbrowser.open(f))

    def _build_kartochka(self, parent, item, idx, jami):
        prow = item['portfel']
        xat = item['xat']
        oxirgi_mib = item['oxirgi_mib_amal']

        card = tk.Frame(parent, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        card.pack(fill='x', pady=(0, 14))

        jami_qarz = (prow.get('asosiy_qarz') or 0) + (prow.get('foiz_qarz') or 0) + (prow.get('jarima') or 0)
        header = tk.Frame(card, bg=WHITE)
        header.pack(fill='x', padx=10, pady=(10, 6))
        tk.Label(header, text=prow.get('mijoz_nomi', ''), bg=WHITE, fg=INK,
                 font=('Segoe UI', 11, 'bold'), anchor='w').pack(anchor='w')
        tk.Label(header, text=f"Filial kodi: {prow.get('filial_kodi','')} | "
                               f"DPD: {prow.get('dpd_max',0)} kun | "
                               f"Muddati o'tgan qarz: {jami_qarz:,.0f} so'm".replace(',', ' '),
                 bg=WHITE, fg='#6B7280', font=('Segoe UI', 9), anchor='w').pack(anchor='w', pady=(2, 0))

        if not xat:
            self._bosqich_qatori(card, "Joriy bosqich:", "Hali xat (Ogohlantirish/Talabnoma) yaratilmagan")
            tk.Frame(card, bg=WHITE, height=6).pack()
            return

        # Xat bosqichi
        xat_holat = self.XAT_HOLAT_NOMLARI.get(xat['holat'], xat['holat'])
        self._bosqich_qatori(card, "1) Xat:",
                              f"{xat['xat_turi']} — {xat_holat} ({self._fmt(xat.get('yaratilgan_sana'))})",
                              tag='otgan' if xat['holat'] == 'muddati_otgan' else None,
                              fayl_yoli=xat.get('fayl_yoli'))

        # Davo ariza bosqichi
        if xat.get('davo_ariza_fayl_yoli'):
            davo_holat = self.DAVO_HOLAT_NOMLARI.get(xat.get('davo_ariza_holati'), xat.get('davo_ariza_holati') or '')
            davo_turi_nomi = letters.DAVO_ARIZA_NOMLARI.get(xat.get('davo_ariza_turi'), xat.get('davo_ariza_turi') or '')
            self._bosqich_qatori(card, "2) Davo ariza:",
                                  f"{davo_turi_nomi} — {davo_holat} ({self._fmt(xat.get('davo_ariza_sana'))})",
                                  tag='ok' if xat.get('davo_ariza_holati') == 'olib_kelindi' else None,
                                  fayl_yoli=xat.get('davo_ariza_fayl_yoli'))
        else:
            self._bosqich_qatori(card, "2) Davo ariza:", "Hali tayyorlanmagan")
            tk.Frame(card, bg=WHITE, height=6).pack()
            return

        # Sud bosqichi
        if xat.get('davo_ariza_holati') == 'olib_kelindi':
            if xat.get('sud_holati') == 'topshirildi':
                self._bosqich_qatori(card, "3) Sud:",
                                      f"✓ Topshirilgan — ish raqami: {xat.get('sud_ish_raqami','')} "
                                      f"({xat.get('sud_topshirilgan_sana','')})", tag='ok',
                                      fayl_yoli=xat.get('sud_buyrugi_fayl'))
            else:
                self._bosqich_qatori(card, "3) Sud:", "Hali sudga topshirilmagan (Palatadan qaytgan)")
                tk.Frame(card, bg=WHITE, height=6).pack()
                return
        else:
            tk.Frame(card, bg=WHITE, height=6).pack()
            return

        # MIB bosqichi
        if xat.get('mib_holati') == 'otkazildi':
            mib_matn = f"✓ O'tkazilgan — ish raqami: {xat.get('mib_ish_raqami','')} " \
                       f"({xat.get('mib_otkazilgan_sana','')})"
            mib_fayl = xat.get('yigma_jild_papka') or xat.get('ijro_varaqasi_fayl')
            self._bosqich_qatori(card, "4) MIB:", mib_matn, tag='ok', fayl_yoli=mib_fayl)
            if oxirgi_mib:
                turi_nomi = self.MIB_AMAL_NOMLARI.get(oxirgi_mib['amal_turi'], oxirgi_mib['amal_turi'])
                self._bosqich_qatori(card, "    So'nggi MIB ishi:",
                                      f"{turi_nomi} ({oxirgi_mib['amal_sanasi']})")
            else:
                self._bosqich_qatori(card, "    So'nggi MIB ishi:", "Hali birorta harakat qayd qilinmagan")
        else:
            self._bosqich_qatori(card, "4) MIB:", "Hali MIBga o'tkazilmagan (sudga topshirilgan)")

        tk.Frame(card, bg=WHITE, height=6).pack()

    @staticmethod
    def _fmt(sana_str):
        if not sana_str:
            return ''
        try:
            return datetime.datetime.fromisoformat(sana_str).strftime('%d.%m.%Y')
        except Exception:
            return sana_str


class SudBazaTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Sud bazasi", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Palatadan (SSPdan) imzolanib qaytgan Davo arizalar shu yerda "
                              "ko'rinadi. Fuqarolik sudiga ham, Iqtisodiy sudiga ham topshirish "
                              "muddati — 5 kun.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="✓ Sudga topshirildi deb belgilash", style='Accent.TButton',
                   command=self.mark_topshirildi).pack(side='left', padx=8)
        ttk.Button(toolbar, text="📁 Eski sud ishini kiritish", command=self.add_legacy).pack(
            side='left', padx=8)
        ttk.Button(toolbar, text="📊 Excel'ga eksport qilish", command=self.export_excel).pack(
            side='left', padx=8)

        toolbar2 = ttk.Frame(self)
        toolbar2.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Label(toolbar2, text="Anketa raqami bo'yicha qidirish:").pack(side='left')
        self.anketa_qidiruv_var = tk.StringVar()
        qidiruv_entry = ttk.Entry(toolbar2, textvariable=self.anketa_qidiruv_var, width=16)
        qidiruv_entry.pack(side='left', padx=6)
        qidiruv_entry.bind('<Return>', lambda e: self.anketa_boyicha_topish())
        ttk.Button(toolbar2, text="🔍 Topish", command=self.anketa_boyicha_topish).pack(side='left')

        cols = ('anketa', 'mijoz', 'turi', 'sud_nomi', 'jami_qarz', 'asosiy', 'foiz', 'penya',
                'kafil_garov', 'olib_kelingan', 'muddat_holati')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'sud_nomi': 'Sud turi',
                    'jami_qarz': 'Jami qarzdorlik', 'asosiy': 'Asosiy qarz', 'foiz': 'Foiz', 'penya': 'Penya',
                    'kafil_garov': "Kafil / Garov",
                    'olib_kelingan': 'Palatadan kelgan', 'muddat_holati': 'Sudga topshirish muddati'}
        widths = {'anketa': 80, 'mijoz': 160, 'turi': 60, 'sud_nomi': 85, 'jami_qarz': 100,
                  'asosiy': 90, 'foiz': 80, 'penya': 80, 'kafil_garov': 160,
                  'olib_kelingan': 100, 'muddat_holati': 140}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.tag_configure('kutilmoqda_sud', foreground=KRAFT)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self._rows_cache = {}
        self.refresh()

    @staticmethod
    def _sud_nomi(mijoz_turi, settings):
        # YaTT — huquqiy jihatdan yuridik shaxs kabi, iqtisodiy sudga yo'naltiriladi
        if mijoz_turi in ('yuridik', 'yatt'):
            return settings.get('sud_iqtisodiy_nomi', '')
        return settings.get('sud_fuqarolik_nomi', '')

    @staticmethod
    def _kafil_garov_label(anketa_raqami):
        taminot = db.get_taminot(anketa_raqami)
        if not taminot:
            return "—"
        turi = taminot.get('taminot_turi') or 'yoq'
        qismlar = []
        if turi in ('kafillik', 'kafillik_garov') and taminot.get('kafil_ism'):
            qismlar.append(f"Kafil: {taminot['kafil_ism']}")
        if turi in ('garov', 'kafillik_garov') and taminot.get('garov_tavsifi'):
            qisqa = taminot['garov_tavsifi'][:30]
            qismlar.append(f"Garov: {qisqa}{'...' if len(taminot['garov_tavsifi']) > 30 else ''}")
        return " | ".join(qismlar) if qismlar else "—"

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        settings = db.get_all_settings()
        muddat_kun = int(settings.get('sud_topshirish_muddati_kun', 5))
        xatlar = db.get_sud_topshirish_kerak()
        for x in xatlar:
            prow = db.get_portfel_by_id(x['portfel_id'])
            asosiy = foiz = penya = 0
            if prow:
                asosiy = prow.get('asosiy_qarz') or 0
                foiz = prow.get('foiz_qarz') or 0
                penya = prow.get('jarima') or 0
            jami = asosiy + foiz + penya
            sud_nomi = self._sud_nomi(x['mijoz_turi'], settings)
            kafil_garov_label = self._kafil_garov_label(x['anketa_raqami'])

            tag = ''
            try:
                imzo_dt = datetime.datetime.strptime(x['davo_ariza_imzo_sana'], '%d.%m.%Y')
                olib_kelingan = imzo_dt.strftime('%d.%m.%Y')
                qolgan = muddat_kun - (datetime.datetime.now() - imzo_dt).days
                if qolgan < 0:
                    muddat_label = f"⚠ {abs(qolgan)} kun o'tib ketdi"
                    tag = 'otgan'
                else:
                    muddat_label = f"{qolgan} kun qoldi"
            except Exception:
                olib_kelingan = x.get('davo_ariza_imzo_sana', '') or ''
                muddat_label = ''

            iid = str(x['id'])
            self.tree.insert('', 'end', iid=iid, values=(
                x['anketa_raqami'], x['mijoz_nomi'], x['mijoz_turi'], sud_nomi,
                f"{jami:,.0f}".replace(',', ' '), f"{asosiy:,.0f}".replace(',', ' '),
                f"{foiz:,.0f}".replace(',', ' '), f"{penya:,.0f}".replace(',', ' '),
                kafil_garov_label, olib_kelingan, muddat_label
            ), tags=(tag,))
            self._rows_cache[iid] = {'xat': x, 'portfel': prow, 'sud_nomi': sud_nomi,
                                      'asosiy': asosiy, 'foiz': foiz, 'penya': penya, 'jami': jami}

        self.app.tab_dashboard.refresh()

    def anketa_boyicha_topish(self):
        anketa = self.anketa_qidiruv_var.get().strip()
        if not anketa:
            return
        topildi = None
        for iid, item in self._rows_cache.items():
            if str(item['xat'].get('anketa_raqami', '')) == anketa:
                topildi = iid
                break
        if topildi:
            self.tree.selection_set(topildi)
            self.tree.see(topildi)
            self.tree.focus(topildi)
            item = self._rows_cache[topildi]
            messagebox.showinfo(
                "Topildi",
                f"{item['xat']['mijoz_nomi']} — Anketa {anketa}\n\n"
                f"Jami qarzdorlik: {item['jami']:,.0f} so'm\n"
                f"  - Asosiy qarz: {item['asosiy']:,.0f} so'm\n"
                f"  - Foiz: {item['foiz']:,.0f} so'm\n"
                f"  - Penya: {item['penya']:,.0f} so'm".replace(',', ' ')
            )
            return
        # Ushbu ro'yxatda topilmasa, sudga ALLAQACHON topshirilgan yoki MIB
        # jarayonidagi tarixiy yozuvlarni ham tekshiramiz
        conn = db.get_conn()
        row = conn.execute(
            "SELECT * FROM xatlar WHERE anketa_raqami=? AND sud_holati='topshirildi'", (anketa,)
        ).fetchone()
        conn.close()
        if row:
            rd = dict(row)
            prow = db.get_portfel_by_id(rd['portfel_id'])
            asosiy = (prow.get('asosiy_qarz') or 0) if prow else 0
            foiz = (prow.get('foiz_qarz') or 0) if prow else 0
            penya = (prow.get('jarima') or 0) if prow else 0
            messagebox.showinfo(
                "Topildi (allaqachon sudga topshirilgan)",
                f"{rd['mijoz_nomi']} — Anketa {anketa}\n"
                f"Sud ish raqami: {rd.get('sud_ish_raqami','') or '—'}\n"
                f"Sudga topshirilgan: {rd.get('sud_topshirilgan_sana','') or '—'}\n\n"
                f"Sudga berilgan (topshirish paytidagi) qarz taqsimoti:\n"
                f"  - Asosiy qarz: {asosiy:,.0f} so'm\n"
                f"  - Foiz: {foiz:,.0f} so'm\n"
                f"  - Penya: {penya:,.0f} so'm".replace(',', ' ')
            )
        else:
            messagebox.showinfo("Topilmadi", f"Anketa {anketa} bo'yicha Sud bazasida yozuv topilmadi.")

    def export_excel(self):
        if not self._rows_cache:
            messagebox.showinfo("Diqqat", "Eksport qilinadigan ma'lumot yo'q.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="sudga_topshirilishi_kerak.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows = []
        for item in self._rows_cache.values():
            x = item['xat']
            prow = item['portfel']
            pinfl = (prow.get('pinfl', '') if prow else '') or ''
            rows.append([
                x['anketa_raqami'], pinfl, x['mijoz_nomi'], x['mijoz_turi'], item['sud_nomi'],
                item['jami'], item['asosiy'], item['foiz'], item['penya'],
                x.get('davo_ariza_ish_raqami', '') or '', x.get('davo_ariza_imzo_sana', '') or ''
            ])
        headers = ['Anketa raqami', 'PINFL', 'Mijoz', 'Turi', 'Sud turi', 'Jami qarzdorlik',
                   'Asosiy qarz', 'Foiz', 'Penya', 'Palata ish raqami', 'Palatadan kelgan sana']
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"{len(rows)} ta yozuv eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)

    def add_legacy(self):
        dlg = LegacySudDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            prow, ish_raqami, sana, buyruq_src = dlg.result
            existing = db.get_conn().execute(
                'SELECT id FROM xatlar WHERE portfel_id=?', (prow['id'],)
            ).fetchone()
            if existing:
                javob = messagebox.askyesno(
                    "Diqqat",
                    "Bu mijoz uchun bazada allaqachon yozuv mavjud. Baribir yangi, alohida "
                    "sud yozuvi yaratilsinmi?"
                )
                if not javob:
                    return

            dest = None
            if buyruq_src:
                dest = fayl_nusxala(buyruq_src, bugungi_papka("Sud buyrug'i"),
                                     prefiks='sud_buyrugi_', mijoz_nomi=prow['mijoz_nomi'])
            mijoz_turi = util.turi_kodidan(prow.get('mijoz_turi_kodi'), prow.get('mijoz_turi'))
            xat_id = db.create_legacy_sud_xat(
                portfel_id=prow['id'], anketa_raqami=prow['anketa_raqami'],
                mijoz_nomi=prow['mijoz_nomi'], mijoz_turi=mijoz_turi,
                sud_ish_raqami=ish_raqami, sud_sana=sana, sud_buyrugi_fayl=dest
            )
            if dest:
                msg = ("Eski sud ishi bazaga kiritildi. Sud buyrug'i mavjud bo'lgani uchun "
                       "endi bu mijozni 'MIB ijro harakatlari' bo'limida MIBga o'tkazishingiz mumkin.")
            else:
                msg = ("Eski sud ishi bazaga kiritildi. Sud buyrug'i hali yo'q — bu ish "
                       "'Suddan o'tkazilgan / MIB jarayonida' bo'limida 'Kutilmoqda' holatida "
                       "ko'rinadi, hal bo'lgach sud buyrug'ini yuklab MIBga o'tkazishingiz mumkin.")
            messagebox.showinfo("Saqlandi", msg)
            self.refresh()

    def mark_topshirildi(self):
        selected = self.tree.selection()
        if len(selected) != 1:
            messagebox.showinfo("Diqqat", "Aynan bitta mijozni tanlang.")
            return
        item = self._rows_cache[selected[0]]
        xat = item['xat']
        dlg = SudTopshirishDialog(self, xat['mijoz_nomi'], item['sud_nomi'])
        self.wait_window(dlg)
        if dlg.result:
            ish_raqami, sana, buyruq_src = dlg.result
            buyruq_dest = None
            if buyruq_src:
                buyruq_dest = fayl_nusxala(buyruq_src, bugungi_papka("Sud buyrug'i"),
                                            prefiks='sud_buyrugi_', mijoz_nomi=xat['mijoz_nomi'])
            db.mark_sud_topshirildi(xat['id'], ish_raqami, sana, buyruq_dest)
            messagebox.showinfo("Saqlandi", "Sudga topshirilgani belgilandi.")
            self.refresh()


class LegacySudDialog(tk.Toplevel):
    """
    Bu dasturdan tashqarida avvalroq sudga topshirilgan eski ishni ro'yxatga
    olish oynasi — anketa raqami bo'yicha portfeldan mijozni topib, sud
    ish raqami/sanasi bilan kiritadi. Agar ish hali hal bo'lmagan bo'lsa,
    "Sud ishi hal qilingan" katakchasini belgilamasdan qoldiring — u holda
    ish "kutilmoqda" holatida ko'rinadi.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Eski sud ishini kiritish")
        self.geometry("520x520")
        self.configure(bg=BG)
        self.result = None
        self.sud_buyrugi_yol = None
        self._tanlangan_portfel = None
        self._portfel_natijalar = []

        ttk.Label(self, text="Eski sud ishini bazaga kiritish",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text="Bu dasturdan tashqarida avvalroq sudga topshirilgan ish uchun — "
                              "anketa raqamini kiritib mijozni portfeldan topasiz, so'ng sud "
                              "ma'lumotlarini kiritasiz.",
                  style='Sub.TLabel', wraplength=470, justify='left').pack(anchor='w', padx=16, pady=(0, 14))

        search_row = ttk.Frame(self)
        search_row.pack(fill='x', padx=16, pady=4)
        ttk.Label(search_row, text="Anketa raqami:", width=16).pack(side='left')
        self.anketa_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.anketa_var, width=20).pack(side='left')
        ttk.Button(search_row, text="🔍 Qidirish", command=self.qidirish).pack(side='left', padx=8)

        self.natija_var = tk.StringVar(value="Hali qidirilmagan")
        ttk.Label(self, textvariable=self.natija_var, style='Sub.TLabel',
                  wraplength=470, justify='left').pack(anchor='w', padx=16, pady=(8, 4))

        self.tanlov_combo = ttk.Combobox(self, state='readonly', width=60)
        self.tanlov_combo.pack(anchor='w', padx=16, pady=(0, 10))
        self.tanlov_combo.bind('<<ComboboxSelected>>', self._on_tanlov)

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Sud ish raqami:", width=16).pack(side='left')
        self.ish_raqami_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.ish_raqami_var, width=24).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="Sudga topshirilgan sana:", width=16).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row2, textvariable=self.sana_var, width=24).pack(side='left')

        self.hal_bolgan_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Sud ishi hal qilingan (sud buyrug'i/qarori mavjud)",
                         variable=self.hal_bolgan_var, command=self._toggle_fayl).pack(
            anchor='w', padx=16, pady=(10, 4))
        ttk.Label(self, text="(belgilanmasa — ish 'kutilmoqda' holatida ko'rinadi, hali "
                              "MIBga o'tkazib bo'lmaydi)", style='Sub.TLabel').pack(
            anchor='w', padx=16, pady=(0, 8))

        self.fayl_frame = ttk.Frame(self)
        self.fayl_frame.pack(fill='x', padx=16)
        ttk.Label(self.fayl_frame, text="Sud buyrug'i / hal qiluv qarori (PDF):",
                  style='Sub.TLabel').pack(anchor='w', pady=(0, 4))
        file_row = ttk.Frame(self.fayl_frame)
        file_row.pack(fill='x')
        self.fayl_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.fayl_label.pack(side='left')
        self.fayl_btn = ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_fayl,
                                    state='disabled')
        self.fayl_btn.pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Saqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def _toggle_fayl(self):
        self.fayl_btn.config(state='normal' if self.hal_bolgan_var.get() else 'disabled')

    def qidirish(self):
        anketa = self.anketa_var.get().strip()
        if not anketa:
            messagebox.showinfo("Diqqat", "Anketa raqamini kiriting.")
            return
        rows = db.get_portfel_by_anketa(anketa)
        if not rows:
            self.natija_var.set("Topilmadi — bu anketa raqami portfelda yo'q.")
            self.tanlov_combo['values'] = []
            self._portfel_natijalar = []
            return
        self._portfel_natijalar = rows
        labels = [f"{r['mijoz_nomi']} — filial {r.get('filial_kodi','')} — "
                  f"DPD {r.get('dpd_max',0)} kun" for r in rows]
        self.tanlov_combo['values'] = labels
        self.tanlov_combo.current(0)
        self._on_tanlov()
        self.natija_var.set(f"{len(rows)} ta natija topildi. Kerakli mijozni tanlang:")

    def _on_tanlov(self, event=None):
        idx = self.tanlov_combo.current()
        if 0 <= idx < len(self._portfel_natijalar):
            self._tanlangan_portfel = self._portfel_natijalar[idx]

    def tanlash_fayl(self):
        filepath = filedialog.askopenfilename(
            title="Sud buyrug'i / hal qiluv qarori (PDF) faylini tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.sud_buyrugi_yol = filepath
            self.fayl_label.config(text=os.path.basename(filepath))

    def confirm(self):
        if not self._tanlangan_portfel:
            messagebox.showerror("Xato", "Avval anketa raqami bo'yicha qidirib, mijozni tanlang.")
            return
        ish_raqami = self.ish_raqami_var.get().strip()
        sana = self.sana_var.get().strip()
        if not ish_raqami or not sana:
            messagebox.showerror("Xato", "Sud ish raqami va sanani kiriting.")
            return
        if self.hal_bolgan_var.get() and not self.sud_buyrugi_yol:
            messagebox.showerror("Xato", "Sud ishi hal qilingan deb belgilangan — sud buyrug'i "
                                          "(PDF) faylini yuklang.")
            return
        self.result = (self._tanlangan_portfel, ish_raqami, sana,
                        self.sud_buyrugi_yol if self.hal_bolgan_var.get() else None)
        self.destroy()


class LegacyMibDialog(tk.Toplevel):
    """
    Bu dasturdan tashqarida avvalroq MIBga chiqarilgan eski ishni
    ro'yxatga olish oynasi — anketa raqami bo'yicha portfeldan mijozni
    topib, MIB ish raqami/sanasi bilan to'g'ridan-to'g'ri MIB bosqichiga kiritadi.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Eski MIB ishini kiritish")
        self.geometry("520x480")
        self.configure(bg=BG)
        self.result = None
        self.ijro_varaqasi_yol = None
        self._tanlangan_portfel = None

        ttk.Label(self, text="Eski MIB ishini bazaga kiritish",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text="Bu dasturdan tashqarida avvalroq MIBga topshirilgan ish uchun — "
                              "anketa raqamini kiritib mijozni portfeldan topasiz, so'ng MIB "
                              "ma'lumotlarini kiritasiz.",
                  style='Sub.TLabel', wraplength=470, justify='left').pack(anchor='w', padx=16, pady=(0, 14))

        search_row = ttk.Frame(self)
        search_row.pack(fill='x', padx=16, pady=4)
        ttk.Label(search_row, text="Anketa raqami:", width=16).pack(side='left')
        self.anketa_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.anketa_var, width=20).pack(side='left')
        ttk.Button(search_row, text="🔍 Qidirish", command=self.qidirish).pack(side='left', padx=8)

        self.natija_var = tk.StringVar(value="Hali qidirilmagan")
        ttk.Label(self, textvariable=self.natija_var, style='Sub.TLabel',
                  wraplength=470, justify='left').pack(anchor='w', padx=16, pady=(8, 4))

        self.tanlov_combo = ttk.Combobox(self, state='readonly', width=60)
        self.tanlov_combo.pack(anchor='w', padx=16, pady=(0, 10))
        self.tanlov_combo.bind('<<ComboboxSelected>>', self._on_tanlov)
        self._portfel_natijalar = []

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="MIB ish raqami:", width=16).pack(side='left')
        self.ish_raqami_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.ish_raqami_var, width=24).pack(side='left')

        row1b = ttk.Frame(self)
        row1b.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1b, text="Sud ish raqami:", width=16).pack(side='left')
        self.sud_ish_raqami_var = tk.StringVar()
        ttk.Entry(row1b, textvariable=self.sud_ish_raqami_var, width=24).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="MIBga o'tkazilgan sana:", width=16).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row2, textvariable=self.sana_var, width=24).pack(side='left')

        row3 = ttk.Frame(self)
        row3.pack(fill='x', padx=16, pady=6)
        ttk.Label(row3, text="Hozirgi qarzdorlik (so'm):", width=16).pack(side='left')
        self.qarz_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.qarz_var, width=24).pack(side='left')
        ttk.Label(self, text="(bo'sh qoldirilsa, portfeldagi joriy summa olinadi)",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 4))

        ttk.Label(self, text="Ijro varaqasi (agar mavjud bo'lsa, PDF):",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(10, 4))
        file_row = ttk.Frame(self)
        file_row.pack(fill='x', padx=16)
        self.fayl_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.fayl_label.pack(side='left')
        ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_fayl).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Saqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def qidirish(self):
        anketa = self.anketa_var.get().strip()
        if not anketa:
            messagebox.showinfo("Diqqat", "Anketa raqamini kiriting.")
            return
        rows = db.get_portfel_by_anketa(anketa)
        if not rows:
            self.natija_var.set("Topilmadi — bu anketa raqami portfelda yo'q.")
            self.tanlov_combo['values'] = []
            self._portfel_natijalar = []
            return
        self._portfel_natijalar = rows
        labels = [f"{r['mijoz_nomi']} — filial {r.get('filial_kodi','')} — "
                  f"DPD {r.get('dpd_max',0)} kun" for r in rows]
        self.tanlov_combo['values'] = labels
        self.tanlov_combo.current(0)
        self._on_tanlov()
        self.natija_var.set(f"{len(rows)} ta natija topildi. Kerakli mijozni tanlang:")

    def _on_tanlov(self, event=None):
        idx = self.tanlov_combo.current()
        if 0 <= idx < len(self._portfel_natijalar):
            self._tanlangan_portfel = self._portfel_natijalar[idx]

    def tanlash_fayl(self):
        filepath = filedialog.askopenfilename(
            title="Ijro varaqasi (PDF) faylini tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.ijro_varaqasi_yol = filepath
            self.fayl_label.config(text=os.path.basename(filepath))

    def confirm(self):
        if not self._tanlangan_portfel:
            messagebox.showerror("Xato", "Avval anketa raqami bo'yicha qidirib, mijozni tanlang.")
            return
        ish_raqami = self.ish_raqami_var.get().strip()
        sana = self.sana_var.get().strip()
        if not ish_raqami or not sana:
            messagebox.showerror("Xato", "MIB ish raqami va sanani kiriting.")
            return

        qarz = None
        qarz_matn = self.qarz_var.get().strip().replace(' ', '')
        if qarz_matn:
            try:
                qarz = float(qarz_matn)
            except ValueError:
                messagebox.showerror("Xato", "Hozirgi qarzdorlik summasi noto'g'ri kiritildi.")
                return

        existing = db.get_conn().execute(
            'SELECT id FROM xatlar WHERE portfel_id=?', (self._tanlangan_portfel['id'],)
        ).fetchone()
        if existing:
            javob = messagebox.askyesno(
                "Diqqat",
                "Bu mijoz uchun bazada allaqachon yozuv mavjud (masalan xat/Davo ariza orqali "
                "yaratilgan bo'lishi mumkin). Baribir yangi, alohida MIB yozuvi yaratilsinmi?"
            )
            if not javob:
                return

        self.result = (self._tanlangan_portfel, ish_raqami, sana, self.ijro_varaqasi_yol,
                        self.sud_ish_raqami_var.get().strip(), qarz)
        self.destroy()


class AvtomashinaQoshishDialog(tk.Toplevel):
    """Mijozga tegishli avtomashinani ro'yxatga olish oynasi."""
    def __init__(self, parent, mijoz_nomi, mijoz_pinfl=''):
        super().__init__(parent)
        self.title(f"Avtomashina qo'shish — {mijoz_nomi}")
        self.geometry("440x300")
        self.configure(bg=BG)
        self.result = None

        ttk.Label(self, text="Yangi avtomashina", style='Header.TLabel').pack(
            anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mijoz_nomi, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 14))

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Mashina rusumi:", width=16).pack(side='left')
        self.rusumi_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.rusumi_var, width=26).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="Davlat raqami:", width=16).pack(side='left')
        self.davlat_raqami_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.davlat_raqami_var, width=26).pack(side='left')

        row3 = ttk.Frame(self)
        row3.pack(fill='x', padx=16, pady=6)
        ttk.Label(row3, text="Mijoz PINFL:", width=16).pack(side='left')
        self.pinfl_var = tk.StringVar(value=mijoz_pinfl)
        ttk.Entry(row3, textvariable=self.pinfl_var, width=26).pack(side='left')

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=20, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Qo'shish", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def confirm(self):
        rusumi = self.rusumi_var.get().strip()
        davlat_raqami = self.davlat_raqami_var.get().strip()
        if not rusumi or not davlat_raqami:
            messagebox.showerror("Xato", "Mashina rusumi va davlat raqamini kiriting.")
            return
        self.result = (rusumi, davlat_raqami, self.pinfl_var.get().strip())
        self.destroy()


class AvtomashinaHolatDialog(tk.Toplevel):
    """Avtomashina holatini (taqiq/qidiruv/xatlangan) o'zgartirish oynasi."""
    HOLATLAR = [('taqiq', "Taqiq qo'yilgan"), ('qidiruv', "Qidiruvda"),
                ('xatlangan', "Xatlangan (topilgan)")]

    def __init__(self, parent, mashina_label, joriy_holati):
        super().__init__(parent)
        self.title(f"Holatni o'zgartirish — {mashina_label}")
        self.geometry("460x360")
        self.configure(bg=BG)
        self.result = None
        self.hujjat_yol = None

        ttk.Label(self, text="Avtomashina holatini yangilash",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mashina_label, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 14))

        ttk.Label(self, text="Yangi holat:").pack(anchor='w', padx=16)
        self.holat_var = tk.StringVar(value=self.HOLATLAR[0][1])
        holat_combo = ttk.Combobox(self, textvariable=self.holat_var,
                                    values=[v for k, v in self.HOLATLAR], state='readonly', width=30)
        holat_combo.pack(anchor='w', padx=16, pady=(2, 12))
        holat_combo.bind('<<ComboboxSelected>>', lambda e: self._update_fields())

        self.qoshimcha_frame = ttk.Frame(self)
        self.qoshimcha_frame.pack(fill='x', padx=16)

        row1 = ttk.Frame(self.qoshimcha_frame)
        row1.pack(fill='x', pady=6)
        ttk.Label(row1, text="Modda:", width=14).pack(side='left')
        self.modda_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.modda_var, width=28).pack(side='left')

        ttk.Label(self.qoshimcha_frame, text="Asoslovchi hujjat (PDF):",
                  style='Sub.TLabel').pack(anchor='w', pady=(6, 4))
        file_row = ttk.Frame(self.qoshimcha_frame)
        file_row.pack(fill='x')
        self.fayl_label = ttk.Label(file_row, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.fayl_label.pack(side='left')
        ttk.Button(file_row, text="📎 PDF tanlash", command=self.tanlash_fayl).pack(side='left', padx=8)

        self._update_fields()

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=20, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Saqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def _holat_kaliti(self):
        for k, v in self.HOLATLAR:
            if v == self.holat_var.get():
                return k
        return self.HOLATLAR[0][0]

    def _update_fields(self):
        if self._holat_kaliti() == 'xatlangan':
            self.qoshimcha_frame.pack_forget()
        else:
            self.qoshimcha_frame.pack(fill='x', padx=16)

    def tanlash_fayl(self):
        filepath = filedialog.askopenfilename(
            title="Asoslovchi hujjatni (PDF) tanlang", filetypes=[("PDF", "*.pdf")]
        )
        if filepath:
            self.hujjat_yol = filepath
            self.fayl_label.config(text=os.path.basename(filepath))

    def confirm(self):
        holati = self._holat_kaliti()
        if holati in ('taqiq', 'qidiruv') and not self.hujjat_yol:
            messagebox.showerror("Xato", "Bu holat uchun asoslovchi hujjat (PDF) yuklanishi shart.")
            return
        if holati in ('taqiq', 'qidiruv') and not self.modda_var.get().strip():
            messagebox.showerror("Xato", "Qaysi modda asosida ekanini kiriting.")
            return
        self.result = (holati, self.hujjat_yol, self.modda_var.get().strip())
        self.destroy()


class AvtomashinalarRoyxatiDialog(tk.Toplevel):
    """Bitta mijoz uchun barcha avtomashinalar ro'yxati va holatini boshqarish oynasi."""
    def __init__(self, parent, mijoz_nomi, xat_id, mijoz_pinfl=''):
        super().__init__(parent)
        self.title(f"Avtomashinalar — {mijoz_nomi}")
        self.geometry("760x460")
        self.configure(bg=BG)
        self.xat_id = xat_id
        self.mijoz_nomi = mijoz_nomi
        self.mijoz_pinfl = mijoz_pinfl

        ttk.Label(self, text=f"Avtomashinalar — {mijoz_nomi}",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=16)
        ttk.Button(toolbar, text="➕ Avtomashina qo'shish", style='Accent.TButton',
                   command=self.qoshish).pack(side='left')
        ttk.Button(toolbar, text="✏ Holatni o'zgartirish", command=self.holat_ozgartirish).pack(
            side='left', padx=8)
        ttk.Button(toolbar, text="📎 Hujjatni ochish", command=self.hujjat_ochish).pack(side='left')

        cols = ('rusumi', 'davlat_raqami', 'holati', 'modda', 'sana')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=14)
        headings = {'rusumi': 'Mashina rusumi', 'davlat_raqami': 'Davlat raqami',
                    'holati': 'Holati', 'modda': 'Modda', 'sana': 'Sana'}
        widths = {'rusumi': 160, 'davlat_raqami': 130, 'holati': 150, 'modda': 130, 'sana': 100}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('qidiruv', foreground='#B7862C')
        self.tree.tag_configure('taqiq', foreground=STAMP)
        self.tree.tag_configure('xatlangan', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=16, pady=(10, 16))

        self._rows_cache = {}
        self.refresh()

        ttk.Button(self, text="Yopish", command=self.destroy).pack(pady=(0, 16))
        self.transient(parent)
        self.grab_set()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        for m in db.get_avtomashinalar(self.xat_id):
            iid = str(m['id'])
            tag = m['holati'] if m['holati'] in ('qidiruv', 'taqiq', 'xatlangan') else ''
            self.tree.insert('', 'end', iid=iid, values=(
                m['mashina_rusumi'], m['davlat_raqami'], db.AVTO_HOLAT_NOMLARI.get(m['holati'], m['holati']),
                m.get('modda', '') or '', m.get('holat_sanasi', '') or ''
            ), tags=(tag,))
            self._rows_cache[iid] = m

    def _selected(self):
        sel = self.tree.selection()
        if len(sel) != 1:
            messagebox.showinfo("Diqqat", "Bitta mashinani tanlang.")
            return None
        return self._rows_cache.get(sel[0])

    def qoshish(self):
        dlg = AvtomashinaQoshishDialog(self, self.mijoz_nomi, self.mijoz_pinfl)
        self.wait_window(dlg)
        if dlg.result:
            rusumi, davlat_raqami, pinfl = dlg.result
            db.add_avtomashina(self.xat_id, rusumi, davlat_raqami, pinfl)
            self.refresh()

    def holat_ozgartirish(self):
        m = self._selected()
        if not m:
            return
        label = f"{m['mashina_rusumi']} ({m['davlat_raqami']})"
        dlg = AvtomashinaHolatDialog(self, label, m['holati'])
        self.wait_window(dlg)
        if dlg.result:
            holati, hujjat_src, modda = dlg.result
            dest = None
            if hujjat_src:
                dest = fayl_nusxala(hujjat_src, mib_bugungi_papka(),
                                     prefiks=f'Avto_{holati}_', mijoz_nomi=self.mijoz_nomi)
            db.update_avtomashina_holati(m['id'], holati, asoslovchi_hujjat_fayl=dest, modda=modda)
            self.refresh()

    def hujjat_ochish(self):
        m = self._selected()
        if not m:
            return
        fayl = m.get('asoslovchi_hujjat_fayl')
        if fayl and os.path.exists(fayl):
            webbrowser.open(fayl)
        else:
            messagebox.showinfo("Diqqat", "Bu mashina uchun hujjat yuklanmagan.")


class MibBazaTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="MIB (Ijro byurosi) bazasi", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Sudga topshirilgan hujjatlarni MIBga o'tkazishni tasdiqlaysiz, "
                              "so'ng undirish jarayonidagi har bir harakatni (ish haqiga qaratish, "
                              "xatlov, sotish va h.k.) shu yerda kuzatib borasiz.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="📤 MIBga o'tkazildi deb belgilash", style='Accent.TButton',
                   command=self.mark_otkazildi).pack(side='left', padx=8)
        ttk.Button(toolbar, text="➕ Yangi harakat qo'shish", command=self.add_amal).pack(side='left', padx=8)
        ttk.Button(toolbar, text="📋 Harakatlar tarixini ko'rish", command=self.view_tarix).pack(side='left', padx=8)
        ttk.Button(toolbar, text="📁 Eski MIB ishini kiritish", command=self.add_legacy).pack(side='left', padx=8)
        ttk.Button(toolbar, text="🗂 Yig'ma jildni ochish", command=self.open_jild).pack(side='left', padx=8)

        toolbar2 = ttk.Frame(self)
        toolbar2.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Button(toolbar2, text="🚗 Avtomashinalar ro'yxati", style='Accent.TButton',
                   command=self.avtomashinalar_royxati).pack(side='left')
        ttk.Button(toolbar2, text="📥 Excel orqali mashinalarni yuklash",
                   command=self.import_avtomashinalar_excel).pack(side='left', padx=8)
        ttk.Button(toolbar2, text="📊 Xatlanmagan mashinalarni Excel'ga eksport qilish",
                   command=self.export_xatlanmagan_excel).pack(side='left', padx=8)

        toolbar3 = ttk.Frame(self)
        toolbar3.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Button(toolbar3, text="📊 Jarayondagi hujjatlarni Excel'ga eksport qilish",
                   style='Accent.TButton', command=self.export_jarayondagilar_excel).pack(side='left')
        ttk.Button(toolbar3, text="🏁 To'xtatish / Yakunlash", command=self.toxtatish_yakunlash).pack(
            side='left', padx=8)
        self.qidiruv_label = ttk.Label(toolbar2, text='', style='Sub.TLabel')
        self.qidiruv_label.pack(side='left', padx=12)

        toolbar4 = ttk.Frame(self)
        toolbar4.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Label(toolbar4, text="Anketa raqami bo'yicha qidirish:").pack(side='left')
        self.anketa_qidiruv_var = tk.StringVar()
        qidiruv_entry = ttk.Entry(toolbar4, textvariable=self.anketa_qidiruv_var, width=16)
        qidiruv_entry.pack(side='left', padx=6)
        qidiruv_entry.bind('<Return>', lambda e: self.anketa_boyicha_topish())
        ttk.Button(toolbar4, text="🔍 Topish", command=self.anketa_boyicha_topish).pack(side='left')

        cols = ('anketa', 'mijoz', 'turi', 'jami_qarz', 'mib_holati', 'mib_ish_raqami',
                'oxirgi_harakat', 'harakat_holati', 'yigma_jild', 'farq', 'nazorat')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'jami_qarz': 'Qarzdorlik',
                    'mib_holati': 'MIB holati', 'mib_ish_raqami': 'MIB ish raqami',
                    'oxirgi_harakat': "So'nggi harakat", 'harakat_holati': 'Harakat holati',
                    'yigma_jild': "Yig'ma jild", 'farq': "Bugungi-Ijro farqi", 'nazorat': 'Nazorat holati'}
        widths = {'anketa': 80, 'mijoz': 150, 'turi': 55, 'jami_qarz': 95, 'mib_holati': 85,
                  'mib_ish_raqami': 85, 'oxirgi_harakat': 95, 'harakat_holati': 110, 'yigma_jild': 70,
                  'farq': 130, 'nazorat': 190}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.tag_configure('otkazilmagan', foreground=KRAFT)
        self.tree.tag_configure('nazorat_toxtatish', foreground=ERR)
        self.tree.tag_configure('nazorat_qoshimcha', foreground='#B7862C')
        self.tree.tag_configure('farq_bor', foreground=ERR)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self._rows_cache = {}
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        muddat_kun = int(db.get_setting('mib_harakatsizlik_muddati_kun', 15))

        # 1) Sudga topshirilgan, MIBga hali o'tkazilmagan mijozlar
        kutilmoqda = db.get_mib_otkazish_kerak()
        for x in kutilmoqda:
            try:
                prow = db.get_portfel_by_id(x['portfel_id'])
                jami = 0
                if prow:
                    jami = (prow.get('asosiy_qarz') or 0) + (prow.get('foiz_qarz') or 0) + (prow.get('jarima') or 0)
                iid = str(x['id'])
                self.tree.insert('', 'end', iid=iid, values=(
                    x['anketa_raqami'], x['mijoz_nomi'], x['mijoz_turi'],
                    f"{jami:,.0f}".replace(',', ' '), "Kutilmoqda", '—', '—', '—', '—', '—', '—'
                ), tags=('otkazilmagan',))
                self._rows_cache[iid] = {'xat': x, 'portfel': prow}
            except Exception as e:
                print(f"MIB qator o'tkazib yuborildi (xat_id={x.get('id')}): {e}")
                continue

        # 2) MIBga o'tkazilgan, undirish jarayonidagi mijozlar
        faol = db.get_mib_faol_royxat()
        for x in faol:
            try:
                prow = db.get_portfel_by_id(x['portfel_id'])
                jami = 0
                if prow:
                    jami = (prow.get('asosiy_qarz') or 0) + (prow.get('foiz_qarz') or 0) + (prow.get('jarima') or 0)

                oxirgi_sana = db.get_mib_oxirgi_amal_sanasi(x['id'], x.get('mib_otkazilgan_sana'))
                tag = ''
                harakat_holati = '—'
                if oxirgi_sana:
                    try:
                        oxirgi_dt = datetime.datetime.strptime(str(oxirgi_sana), '%d.%m.%Y')
                        kun_otdi = (datetime.datetime.now() - oxirgi_dt).days
                        if kun_otdi > muddat_kun:
                            harakat_holati = f"⚠ {kun_otdi} kun harakatsiz"
                            tag = 'otgan'
                        else:
                            harakat_holati = f"Faol ({kun_otdi} kun oldin)"
                    except Exception:
                        pass

                iid = str(x['id'])
                jild_label = "✓ Mavjud" if x.get('yigma_jild_holati') == 'mavjud' else "—"

                nazorat_label = '—'
                farq_label = '—'
                if prow:
                    settings = db.get_all_settings()
                    nazorat = db.get_mib_monitoring_holati(x['id'], prow, x, settings)
                    farq_summa = nazorat.get('jami_qarz', 0) - nazorat.get('mib_summasi', 0)
                    if farq_summa > 0:
                        farq_label = f"+{farq_summa:,.0f}".replace(',', ' ')
                        if tag == '':
                            tag = 'farq_bor'
                    if nazorat['holat'] == 'toxtatish':
                        nazorat_label = "⚠ To'xtatish/yakunlash kerak"
                        tag = 'nazorat_toxtatish'
                    elif nazorat['holat'] == 'qoshimcha':
                        nazorat_label = "⚠ Farq qo'shish kerak"
                        if tag != 'nazorat_toxtatish':
                            tag = 'nazorat_qoshimcha'

                self.tree.insert('', 'end', iid=iid, values=(
                    x['anketa_raqami'], x['mijoz_nomi'], x['mijoz_turi'],
                    f"{jami:,.0f}".replace(',', ' '), "✓ O'tkazilgan", x.get('mib_ish_raqami', '') or '',
                    oxirgi_sana or '', harakat_holati, jild_label, farq_label, nazorat_label
                ), tags=(tag,))
                self._rows_cache[iid] = {'xat': x, 'portfel': prow}
            except Exception as e:
                print(f"MIB faol qator o'tkazib yuborildi (xat_id={x.get('id')}): {e}")
                continue

        # Qidiruvda turgan avtomashinalar bo'yicha eslatma
        qidiruv = db.get_qidiruv_avtomashinalar()
        if qidiruv:
            self.qidiruv_label.config(
                text=f"⚠ {len(qidiruv)} ta avtomashina qidiruvda — topilsa xatlash (majburiy "
                     f"xatlov) buyrug'i berilishi kerak",
                foreground=ERR)
        else:
            self.qidiruv_label.config(text='')

        self.app.tab_dashboard.refresh()

    def _selected_item(self):
        sel = self.tree.selection()
        if len(sel) != 1:
            messagebox.showinfo("Diqqat", "Aynan bitta mijozni tanlang.")
            return None
        return self._rows_cache.get(sel[0])

    def anketa_boyicha_topish(self):
        anketa = self.anketa_qidiruv_var.get().strip()
        if not anketa:
            return
        topildi = None
        for iid, item in self._rows_cache.items():
            if str(item['xat'].get('anketa_raqami', '')) == anketa:
                topildi = iid
                break
        if not topildi:
            messagebox.showinfo("Topilmadi", f"Anketa {anketa} bo'yicha MIB ro'yxatida yozuv topilmadi.")
            return
        self.tree.selection_set(topildi)
        self.tree.see(topildi)
        self.tree.focus(topildi)

    def toxtatish_yakunlash(self):
        item = self._selected_item()
        if not item:
            return
        xat = item['xat']
        if xat.get('mib_holati') != 'otkazildi':
            messagebox.showwarning("Diqqat", "Bu mijoz hali MIBga o'tkazilmagan.")
            return
        if xat.get('mib_yakunlangan'):
            javob = messagebox.askyesno(
                "Diqqat",
                "Bu ish allaqachon to'xtatilgan/yakunlangan deb belgilangan. "
                "Uni qaytadan FAOL holatga qaytarishni xohlaysizmi?"
            )
            if javob:
                db.mib_ishni_qayta_ochish(xat['id'])
                messagebox.showinfo("Saqlandi", "Ish qaytadan faol holatga qaytarildi.")
                self.refresh()
            return

        prow = item['portfel'] or db.get_portfel_by_id(xat['portfel_id'])
        tavsiya_xabari = ''
        if prow:
            settings = db.get_all_settings()
            nazorat = db.get_mib_monitoring_holati(xat['id'], prow, xat, settings)
            if nazorat.get('holat') == 'toxtatish':
                tavsiya_xabari = nazorat.get('xabar', '')

        dlg = MibToxtatishDialog(self, xat['mijoz_nomi'], tavsiya_xabari)
        self.wait_window(dlg)
        if dlg.result:
            sabab, sana, asos_pdf_src = dlg.result
            db.mark_mib_yakunlandi(xat['id'], sabab, sana)

            # Yakunlash asosi hujjatini kunlik papkaga saqlaymiz, bazaga
            # bog'laymiz va yig'ma jildga ham avtomatik qo'shamiz
            asos_dest = fayl_nusxala(asos_pdf_src, mib_bugungi_papka('Yakunlash asosi'),
                                      prefiks='yakunlash_asosi_', mijoz_nomi=xat['mijoz_nomi'])
            db.set_mib_yakunlash_hujjati(xat['id'], asos_dest)
            if xat.get('yigma_jild_papka') and os.path.isdir(xat['yigma_jild_papka']):
                fayl_nusxala(asos_pdf_src, xat['yigma_jild_papka'], prefiks='05_Yakunlash_asosi_')

            messagebox.showinfo(
                "Saqlandi",
                "MIB ijro ishi to'xtatilgan/yakunlangan deb belgilandi, yakunlash asosi "
                "hujjati saqlandi va yig'ma jildga qo'shildi. Endi bu mijoz 'MIBda "
                "jarayondagi hujjatlar' ro'yxatidan chiqarilib, 'Yakunlangan ishlar' "
                "bo'limida ko'rinadi."
            )
            self.refresh()
            if hasattr(self.app, 'tab_mib_yakunlangan'):
                self.app.tab_mib_yakunlangan.refresh()

    def mark_otkazildi(self):
        item = self._selected_item()
        if not item:
            return
        xat = item['xat']
        if xat.get('mib_holati') == 'otkazildi':
            messagebox.showinfo("Diqqat", "Bu mijoz hujjati allaqachon MIBga o'tkazilgan.")
            return
        dlg = MibTransferDialog(self, xat['mijoz_nomi'], xat.get('sud_ish_raqami', '') or '—')
        self.wait_window(dlg)
        if dlg.result:
            ish_raqami, sana, ijro_pdf_src, sud_pdf_src = dlg.result

            # 0) MIBga o'tkazish paytidagi qarz summasini "surat" sifatida saqlaymiz —
            #    keyinchalik qarz o'sishini kuzatish uchun kerak bo'ladi
            prow0 = item['portfel'] or db.get_portfel_by_id(xat['portfel_id'])
            mib_summasi = 0
            if prow0:
                mib_summasi = (prow0.get('asosiy_qarz') or 0) + (prow0.get('foiz_qarz') or 0) + \
                    (prow0.get('jarima') or 0)

            # 1) Ijro varaqasi va sud buyrug'ini kunlik papkaga saqlaymiz
            dest_ijro = fayl_nusxala(ijro_pdf_src, bugungi_papka('Ijro varaqa'),
                                      prefiks='ijro_varaqasi_', mijoz_nomi=xat['mijoz_nomi'])
            dest_sud = fayl_nusxala(sud_pdf_src, bugungi_papka('Sud buyrug\'i'),
                                     prefiks='sud_buyrugi_', mijoz_nomi=xat['mijoz_nomi'])
            db.mark_mib_otkazildi(xat['id'], ish_raqami, sana, dest_ijro,
                                   mib_ijro_summasi=mib_summasi, sud_buyrugi_fayl=dest_sud)

            # 2) Ish uchun HAQIQIY yig'ma jild papkasini ochamiz
            jild_papka = yigma_jild_papka_yarat(xat['mijoz_nomi'], xat['anketa_raqami'], ish_raqami)

            # 3) Titul (muqova) hujjatini avtomatik yaratamiz
            prow = prow0
            mijoz_turi_m, mijoz = util.resolve_mijoz(prow) if prow else (None, None)
            settings = db.get_all_settings()
            xat_yangilangan = db.get_xat_by_id(xat['id'])
            titul_path = os.path.join(jild_papka, '00_Titul.docx')
            letters.generate_yigma_jild_titul(titul_path, xat_yangilangan, prow, mijoz, settings)
            db.mark_yigma_jild_yaratildi(xat['id'], jild_papka, titul_path)

            # 4) MUHIM: shu ishga tegishli AVVAL yaratilgan barcha hujjatlarni
            #    (Ogohlantirish/Talabnoma xati, Davo ariza, Sud buyrug'i, Ijro
            #    varaqasi) yig'ma jildga avtomatik nusxalaymiz — foydalanuvchi
            #    qo'lda hech narsa qo'shmasa ham, jild to'liq bo'ladi.
            xat_toliq = db.get_xat_by_id(xat['id'])
            yigma_jild_toldirish(jild_papka, xat_toliq)

            # 5) Agar kafil/garov mavjud bo'lsa, ular bo'yicha ham MIB harakati
            #    kiritish zarurligini eslatamiz
            taminot = db.get_taminot(xat['anketa_raqami'])
            eslatma = ""
            if taminot and taminot.get('taminot_turi') not in (None, '', 'yoq'):
                turi_t = taminot['taminot_turi']
                if turi_t in ('kafillik', 'kafillik_garov'):
                    eslatma += (f"\n\n⚠ Diqqat: bu mijozda KAFIL bor ({taminot.get('kafil_ism','')}). "
                                "Kafil bo'yicha ham MIB ishi (masalan ish haqiga qaratish, mol-mulkini "
                                "aniqlash va h.k.) 'Yangi harakat qo'shish' orqali kiritilib borilishi kerak.")
                if turi_t in ('garov', 'kafillik_garov'):
                    eslatma += ("\n\n⚠ Diqqat: bu mijozda GAROV mulki bor. Garov mulkini xatlash "
                                "(majburiy xatlov) yoki sotish jarayoni 'Yangi harakat qo'shish' "
                                "orqali kiritilib borilishi kerak.")

            messagebox.showinfo(
                "Saqlandi",
                "MIBga o'tkazilgani tasdiqlandi.\n\n"
                f"Ish uchun yig'ma jild ochildi, titul hujjati tayyorlandi va mavjud "
                f"barcha hujjatlar (xat, Davo ariza, sud buyrug'i, ijro varaqasi) "
                f"avtomatik jildga qo'shildi:\n{jild_papka}"
                f"{eslatma}"
            )
            webbrowser.open(titul_path)
            self.refresh()

    def add_amal(self):
        item = self._selected_item()
        if not item:
            return
        xat = item['xat']
        if xat.get('mib_holati') != 'otkazildi':
            messagebox.showwarning("Ruxsat berilmagan",
                                    "Avval hujjat MIBga o'tkazilganini tasdiqlang.")
            return
        dlg = MibAmalDialog(self, xat['mijoz_nomi'])
        self.wait_window(dlg)
        if dlg.result:
            data = dlg.result
            # Hujjatlar, agar mavjud bo'lsa, doimiy yig'ma jild papkasiga
            # qo'shilib boradi — shu bilan barcha ish hujjatlari bir joyda
            # to'planadi. Agar biror sababdan jild yo'q bo'lsa, ehtiyot
            # chorasi sifatida kunlik MIB papkasiga saqlanadi.
            papka = xat.get('yigma_jild_papka') or mib_bugungi_papka()
            if '_dalolatnoma_src' in data:
                data['dalolatnoma_fayl'] = fayl_nusxala(data.pop('_dalolatnoma_src'), papka,
                                                          prefiks='Dalolatnoma_', mijoz_nomi=xat['mijoz_nomi'])
            if '_auksion_rasm_src' in data:
                rasm_yollari = [fayl_nusxala(p, papka, prefiks='Lot_rasm_', mijoz_nomi=xat['mijoz_nomi'])
                                 for p in data.pop('_auksion_rasm_src')]
                data['auksion_rasmlar'] = ','.join(r for r in rasm_yollari if r)
            db.add_mib_amal(xat['id'], **data)
            messagebox.showinfo("Saqlandi", "Yangi harakat qo'shildi.")
            self.refresh()

    def view_tarix(self):
        item = self._selected_item()
        if not item:
            return
        xat = item['xat']
        MibTarixDialog(self, xat['mijoz_nomi'], xat['id'])

    def open_jild(self):
        item = self._selected_item()
        if not item:
            return
        xat = item['xat']
        papka = xat.get('yigma_jild_papka')
        if not papka or not os.path.exists(papka):
            messagebox.showinfo("Diqqat", "Bu mijoz uchun hali yig'ma jild ochilmagan "
                                           "(avval MIBga o'tkazilganini tasdiqlash kerak).")
            return
        webbrowser.open(papka)

    def avtomashinalar_royxati(self):
        item = self._selected_item()
        if not item:
            return
        xat = item['xat']
        if xat.get('mib_holati') != 'otkazildi':
            messagebox.showwarning("Ruxsat berilmagan",
                                    "Avval hujjat MIBga o'tkazilganini tasdiqlang.")
            return
        prow = item.get('portfel')
        pinfl = (prow.get('pinfl') if prow else '') or ''
        dlg = AvtomashinalarRoyxatiDialog(self, xat['mijoz_nomi'], xat['id'], pinfl)
        self.wait_window(dlg)
        self.refresh()

    def import_avtomashinalar_excel(self):
        filepath = filedialog.askopenfilename(
            title="Avtomashinalar Excel faylini tanlang",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
        if not filepath:
            return
        try:
            natija = importer.import_avtomashinalar_excel(filepath)
        except Exception as e:
            messagebox.showerror("Xato", str(e))
            return

        msg = f"{natija['qoshildi']} ta avtomashina muvaffaqiyatli qo'shildi va tegishli " \
              f"mijozga (MIB ishiga) avtomatik bog'landi."
        if natija['topilmadi']:
            msg += f"\n\n⚠ {len(natija['topilmadi'])} ta qator uchun mos MIB ishi topilmadi " \
                   f"(anketa raqami/PINFL noto'g'ri, yoki bu mijoz hali MIBga o'tkazilmagan):\n"
            for t in natija['topilmadi'][:5]:
                msg += f"  • {t['rusumi']} ({t['davlat_raqami']}) — anketa: {t['anketa'] or '—'}\n"
            if len(natija['topilmadi']) > 5:
                msg += f"  ... va yana {len(natija['topilmadi']) - 5} ta"
        messagebox.showinfo("Natija", msg)
        self.refresh()

    def export_xatlanmagan_excel(self):
        xatlanmagan = db.get_xatlanmagan_avtomashinalar()
        if not xatlanmagan:
            messagebox.showinfo("Diqqat", "Xatlanmagan avtomashinalar yo'q.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="xatlanmagan_avtomashinalar.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows = [[m['mashina_rusumi'], m['davlat_raqami'], m.get('mijoz_pinfl', ''),
                 m['anketa_raqami'], m['mijoz_nomi']] for m in xatlanmagan]
        headers = ['Mashina rusumi', 'Davlat raqami', 'Mijoz PINFL', 'Anketa raqami', 'Mijoz nomi']
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"{len(rows)} ta xatlanmagan mashina eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)

    def export_jarayondagilar_excel(self):
        royxat = db.get_mib_faol_royxat_toliq()
        if not royxat:
            messagebox.showinfo("Diqqat", "MIBda jarayondagi hujjatlar yo'q.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="mib_jarayondagi_hujjatlar.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows = []
        for item in royxat:
            xat = item['xat']
            amal = item['amal']
            amal_turi_nomi = dict(MibAmalDialog.AMAL_TURLARI).get(amal['amal_turi'], amal['amal_turi']) if amal else ''
            oylik_ish_haqqi_summa = ''
            if amal and amal['amal_turi'] == 'oylik_ish_haqqi':
                oylik_ish_haqqi_summa = amal.get('undirilgan_summa', '') or ''
            rows.append([
                xat['anketa_raqami'], item['pinfl'], xat['mijoz_nomi'], xat['mijoz_turi'],
                f"{item['jami_qarz']:,.0f}".replace(',', ' '),
                xat.get('mib_ish_raqami', '') or '', xat.get('mib_otkazilgan_sana', '') or '',
                amal_turi_nomi, amal.get('amal_sanasi', '') if amal else '',
                amal.get('tavsif', '') if amal else '', oylik_ish_haqqi_summa,
                amal.get('undirilgan_summa', '') if amal else '',
            ])
        headers = ['Anketa raqami', 'PINFL', 'F.I.Sh / Nomi', 'Turi', 'Qarzdorlik (so\'m)',
                   'MIB ish raqami', 'MIBga o\'tkazilgan sana', 'Harakat turi', 'Harakat sanasi',
                   'Tavsif', "Oylik ish haqqidan undirilgan summa", "Undirilgan summa (umumiy)"]
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"{len(rows)} ta qator (harakat) eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)

    def add_legacy(self):
        dlg = LegacyMibDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            prow, ish_raqami, sana, pdf_src, sud_ish_raqami, qarz = dlg.result
            dest = None
            if pdf_src:
                dest = fayl_nusxala(pdf_src, bugungi_papka('Ijro varaqa'),
                                     prefiks='ijro_varaqasi_', mijoz_nomi=prow['mijoz_nomi'])
            mijoz_turi = util.turi_kodidan(prow.get('mijoz_turi_kodi'), prow.get('mijoz_turi'))
            xat_id = db.create_legacy_mib_xat(
                portfel_id=prow['id'], anketa_raqami=prow['anketa_raqami'],
                mijoz_nomi=prow['mijoz_nomi'], mijoz_turi=mijoz_turi,
                mib_ish_raqami=ish_raqami, mib_sana=sana, ijro_varaqasi_fayl=dest,
                sud_ish_raqami=sud_ish_raqami or None, joriy_qarzdorlik=qarz
            )

            jild_papka = yigma_jild_papka_yarat(prow['mijoz_nomi'], prow['anketa_raqami'], ish_raqami)
            turi_m, mijoz = util.resolve_mijoz(prow)
            settings = db.get_all_settings()
            xat_yangilangan = db.get_xat_by_id(xat_id)
            titul_path = os.path.join(jild_papka, '00_Titul.docx')
            letters.generate_yigma_jild_titul(titul_path, xat_yangilangan, prow, mijoz, settings)
            db.mark_yigma_jild_yaratildi(xat_id, jild_papka, titul_path)

            # Mavjud bo'lsa (masalan keyinroq xat/Davo ariza qo'lda bog'langan
            # bo'lsa) — barcha tegishli hujjatlarni ham jildga qo'shamiz
            xat_toliq = db.get_xat_by_id(xat_id)
            yigma_jild_toldirish(jild_papka, xat_toliq)

            messagebox.showinfo(
                "Saqlandi",
                "Eski MIB ishi bazaga kiritildi va nazorat ostiga olindi.\n\n"
                f"Ish uchun yig'ma jild ochildi va titul hujjati tayyorlandi:\n{jild_papka}"
            )
            webbrowser.open(titul_path)
            self.refresh()


class DavoArizaTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Davo ariza tayyorlash", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Faqat xati 'Yuborildi' deb belgilangan mijozlar ro'yxatda ko'rinadi.",
                  style='Sub.TLabel').pack(anchor='w', padx=20, pady=(0, 10))

        turi_frame = ttk.Frame(self)
        turi_frame.pack(fill='x', padx=20, pady=(0, 6))
        ttk.Label(turi_frame, text="Ariza turi:").pack(side='left')
        self.turi_var = tk.StringVar(value=list(letters.DAVO_ARIZA_NOMLARI.values())[0])
        self._turi_kalitlar = list(letters.DAVO_ARIZA_NOMLARI.keys())
        ttk.Combobox(turi_frame, textvariable=self.turi_var,
                     values=list(letters.DAVO_ARIZA_NOMLARI.values()),
                     state='readonly', width=48).pack(side='left', padx=8)

        format_frame = ttk.Frame(self)
        format_frame.pack(fill='x', padx=20, pady=(0, 8))
        ttk.Label(format_frame, text="Fayl formati:").pack(side='left')
        self.format_var = tk.StringVar(value='Word (.docx)')
        ttk.Combobox(format_frame, textvariable=self.format_var,
                     values=['Word (.docx)', 'PDF (.pdf)'], state='readonly', width=14).pack(side='left', padx=8)
        ttk.Label(format_frame, text="(PDF uchun Microsoft Word o'rnatilgan bo'lishi kerak)",
                  style='Sub.TLabel').pack(side='left', padx=6)

        taminot_frame = ttk.Frame(self)
        taminot_frame.pack(fill='x', padx=20, pady=(4, 6))
        ttk.Button(taminot_frame, text="✏ Kafil/garov ma'lumotini kiritish (tanlangan mijoz)",
                   command=self.open_taminot_dialog).pack(side='left')
        ttk.Button(taminot_frame, text="📊 Ta'minot Excel'ini eksport qilish",
                   command=self.export_taminot).pack(side='left', padx=8)
        ttk.Button(taminot_frame, text="📥 Tahrirlangan Excel'ni yuklash",
                   command=self.import_taminot).pack(side='left', padx=8)

        gen_frame = ttk.Frame(self)
        gen_frame.pack(fill='x', padx=20, pady=(4, 10))
        ttk.Button(gen_frame, text="⚖ Tanlanganlar uchun Davo ariza tayyorlash",
                   style='Accent.TButton', command=self.generate_bulk).pack(side='left')
        ttk.Button(gen_frame, text="✓ Olib kelindi deb belgilash (ish raqami bilan)",
                   command=self.mark_olib_kelindi).pack(side='left', padx=8)
        ttk.Button(gen_frame, text="📥 Imzodan kelganlarni Excel'ga eksport qilish",
                   command=self.export_olib_kelinganlar).pack(side='left', padx=8)

        toolbar_check = ttk.Frame(self)
        toolbar_check.pack(fill='x', padx=20, pady=(0, 8))
        ttk.Label(toolbar_check, text="Anketa raqami bo'yicha topib belgilash:").pack(side='left')
        self.qidiruv_var = tk.StringVar()
        qidiruv_entry = ttk.Entry(toolbar_check, textvariable=self.qidiruv_var, width=16)
        qidiruv_entry.pack(side='left', padx=6)
        qidiruv_entry.bind('<Return>', lambda e: self.qidirib_belgilash())
        ttk.Button(toolbar_check, text="🔍 Topib belgilash", command=self.qidirib_belgilash).pack(side='left')
        ttk.Button(toolbar_check, text="☑ Hammasini belgilash", command=self.hammasini_belgilash).pack(
            side='left', padx=(16, 0))
        ttk.Button(toolbar_check, text="☐ Belgilarni bekor qilish", command=self.belgilarni_bekor_qilish).pack(
            side='left', padx=6)

        cols = ('check', 'anketa', 'mijoz', 'turi', 'jami_qarz', 'davo_summasi', 'yuborilgan', 'davo_holati',
                'ish_raqami', 'taminot', 'tavsiya', 'farq_holati')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=16, selectmode='extended')
        headings = {'check': '', 'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'jami_qarz': "Jami qarz",
                    'davo_summasi': "Davo summasi", 'yuborilgan': 'Xat yuborilgan', 'davo_holati': 'Davo ariza holati',
                    'ish_raqami': 'Ish raqami', 'taminot': "Ta'minot", 'tavsiya': "Tavsiya etilgan turi",
                    'farq_holati': "Summa farqi"}
        widths = {'check': 34, 'anketa': 80, 'mijoz': 150, 'turi': 55, 'jami_qarz': 90,
                  'davo_summasi': 100, 'yuborilgan': 80, 'davo_holati': 110, 'ish_raqami': 75, 'taminot': 45,
                  'tavsiya': 140, 'farq_holati': 130}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor='center' if c == 'check' else 'w')
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.tag_configure('tayyor', foreground=STAMP)
        self.tree.tag_configure('farq_bor', foreground=ERR)
        self.tree.pack(fill='both', expand=True, padx=20, pady=6)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Button-1>', self._on_tree_click, add='+')

        self.tavsiya_label = ttk.Label(self, text='', style='Sub.TLabel')
        self.tavsiya_label.pack(anchor='w', padx=20, pady=(0, 8))

        self._rows_cache = {}
        self.checked = set()
        self.refresh()

    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row:
            return
        if col == '#1':  # 'check' ustuni
            if row in self.checked:
                self.checked.discard(row)
            else:
                self.checked.add(row)
            self._qayta_chiz_belgi(row)

    def _qayta_chiz_belgi(self, iid):
        belgi = '☑' if iid in self.checked else '☐'
        vals = list(self.tree.item(iid, 'values'))
        vals[0] = belgi
        self.tree.item(iid, values=vals)

    def qidirib_belgilash(self):
        anketa = self.qidiruv_var.get().strip()
        if not anketa:
            return
        topildi = None
        for iid, item in self._rows_cache.items():
            if str(item['xat'].get('anketa_raqami', '')) == anketa:
                topildi = iid
                break
        if not topildi:
            messagebox.showinfo("Topilmadi", f"Anketa {anketa} bo'yicha ro'yxatda yozuv topilmadi.")
            return
        self.checked.add(topildi)
        self._qayta_chiz_belgi(topildi)
        self.tree.selection_set(topildi)
        self.tree.see(topildi)
        self.qidiruv_var.set('')

    def hammasini_belgilash(self):
        for iid in self._rows_cache:
            self.checked.add(iid)
            self._qayta_chiz_belgi(iid)

    def belgilarni_bekor_qilish(self):
        for iid in list(self.checked):
            self.checked.discard(iid)
            self._qayta_chiz_belgi(iid)

    def _turi_kaliti(self):
        label = self.turi_var.get()
        for k, v in letters.DAVO_ARIZA_NOMLARI.items():
            if v == label:
                return k
        return self._turi_kalitlar[0]

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        self.checked = set()
        muddat_kun = int(db.get_setting('davo_ariza_muddati_kun', 5))
        xatlar = db.get_xatlar_yuborilgan_davo_kerak()
        for x in xatlar:
            prow = db.get_portfel_by_id(x['portfel_id'])
            if not prow:
                continue
            taminot = db.get_taminot(x['anketa_raqami'])
            taminot_label = "✓" if taminot and taminot.get('taminot_turi') not in (None, '', 'yoq') else "—"
            tavsiya_kaliti = letters.tavsiya_ariza_turi(x['mijoz_turi'], taminot)
            tavsiya_nomi = letters.DAVO_ARIZA_NOMLARI.get(tavsiya_kaliti, '')
            has_davo = bool(x.get('davo_ariza_fayl_yoli'))
            olib_kelindi = x.get('davo_ariza_holati') == 'olib_kelindi'
            jami = (prow.get('asosiy_qarz') or 0) + (prow.get('foiz_qarz') or 0) + (prow.get('jarima') or 0)
            try:
                yuborilgan = datetime.datetime.fromisoformat(x['yuborilgan_sana']).strftime('%d.%m.%Y')
            except Exception:
                yuborilgan = x.get('yuborilgan_sana', '') or ''

            tag = ''
            if olib_kelindi:
                davo_holati = "✓ Olib kelindi"
                tag = 'tayyor'
            elif has_davo:
                try:
                    davo_dt = datetime.datetime.fromisoformat(x['davo_ariza_sana'])
                    qolgan = muddat_kun - (datetime.datetime.now() - davo_dt).days
                    if qolgan < 0:
                        davo_holati = f"⚠ {abs(qolgan)} kun o'tib ketdi"
                        tag = 'otgan'
                    else:
                        davo_holati = f"Tayyor — {qolgan} kun qoldi"
                except Exception:
                    davo_holati = "Tayyor"
            else:
                davo_holati = "—"

            ish_raqami = x.get('davo_ariza_ish_raqami', '') or ''

            davo_summasi_label = '—'
            if has_davo:
                davo_summasi = (x.get('davo_summasi_asosiy') or 0) + (x.get('davo_summasi_foiz') or 0) + \
                    (x.get('davo_summasi_jarima') or 0)
                if davo_summasi:
                    davo_summasi_label = f"{davo_summasi:,.0f}".replace(',', ' ')

            farq_label = '—'
            if olib_kelindi:
                if x.get('qoshimcha_davo_kerak'):
                    farq_label = "⚠ Farq bor — qo'shimcha ariza kerak"
                    tag = 'farq_bor'
                else:
                    farq_label = "OK"

            iid = str(x['id'])
            self.tree.insert('', 'end', iid=iid, values=(
                '☐', x['anketa_raqami'], x['mijoz_nomi'], x['mijoz_turi'],
                f"{jami:,.0f}".replace(',', ' '), davo_summasi_label, yuborilgan, davo_holati, ish_raqami,
                taminot_label, tavsiya_nomi, farq_label
            ), tags=(tag,))
            self._rows_cache[iid] = {'xat': x, 'portfel': prow, 'tavsiya': tavsiya_kaliti}

    def _on_select(self, event=None):
        selected = self.tree.selection()
        if len(selected) == 1:
            item = self._rows_cache.get(selected[0])
            if item and item.get('tavsiya'):
                tavsiya_nomi = letters.DAVO_ARIZA_NOMLARI.get(item['tavsiya'], '')
                self.turi_var.set(tavsiya_nomi)
                self.tavsiya_label.config(
                    text=f"✓ Ta'minot ma'lumotiga asosan avtomatik tanlandi: {tavsiya_nomi}",
                    foreground=STAMP)
        else:
            self.tavsiya_label.config(text='')

    def _selected(self):
        if self.checked:
            return [self._rows_cache[i] for i in self.checked if i in self._rows_cache]
        return [self._rows_cache[i] for i in self.tree.selection() if i in self._rows_cache]

    def mark_olib_kelindi(self):
        selected = self._selected()
        if len(selected) != 1:
            messagebox.showinfo("Diqqat", "Aynan bitta mijozni tanlang.")
            return
        item = selected[0]
        xat = item['xat']
        if not xat.get('davo_ariza_fayl_yoli'):
            messagebox.showwarning("Diqqat", "Bu mijoz uchun hali Davo ariza tayyorlanmagan.")
            return
        dlg = OlibKelindiDialog(self, xat['mijoz_nomi'])
        self.wait_window(dlg)
        if dlg.result:
            ish_raqami, sana, skan_src = dlg.result
            # SSPdan olib kelingan hujjat skanini (imzo/muhr bilan tasdiqlangan
            # rasmiy nusxa) kunlik papkaga saqlab, Davo ariza faylini SHU
            # skan bilan almashtiramiz — bu yig'ma jildga ham avtomatik
            # to'g'ri (rasmiy, tasdiqlangan) nusxa bo'lib tushishini ta'minlaydi.
            skan_dest = fayl_nusxala(skan_src, bugungi_papka('Davo ariza'),
                                      prefiks='SSP_tasdiqlangan_', mijoz_nomi=xat['mijoz_nomi'])
            db.update_davo_ariza_fayl(xat['id'], skan_dest)

            # Joriy (eng so'nggi) qarzdorlikni olib, davo summasi bilan solishtiramiz
            joriy_prow = db.get_portfel_by_id(xat['portfel_id']) or item.get('portfel')
            settings = db.get_all_settings()
            qoshimcha_kerak = db.mark_davo_ariza_olib_kelindi(
                xat['id'], ish_raqami, sana, portfel_row=joriy_prow, settings=settings)
            if qoshimcha_kerak:
                xat_yangi = db.get_xat_by_id(xat['id'])
                farqi = db.get_davo_ariza_farqi(xat_yangi, joriy_prow, settings)
                messagebox.showwarning(
                    "Diqqat — qo'shimcha Davo ariza kerak",
                    "Davo ariza 'Olib kelindi' deb belgilandi (SSP tasdiqlagan skan saqlandi).\n\n"
                    f"⚠ Joriy qarzdorlik Davo ariza yaratilgan paytdagi summadan "
                    f"{farqi['farq']:,.0f} so'mga oshib ketgan (BXMning bir barobaridan ko'p).\n\n"
                    f"Davo ariza yaratilgandagi summa: {farqi['davo_summasi']:,.0f} so'm\n"
                    f"Joriy qarzdorlik: {farqi['joriy_qarz']:,.0f} so'm\n\n"
                    "Farq summasiga YANGI (qo'shimcha) SSP davo ariza kiritish va uni sudga "
                    "yo'naltirish talab qilinadi.".replace(',', ' ')
                )
            else:
                messagebox.showinfo("Saqlandi", "Davo ariza 'Olib kelindi' deb belgilandi "
                                                  "(SSP tasdiqlagan skan saqlandi).")
            self.refresh()

    def export_olib_kelinganlar(self):
        royxat = db.get_olib_kelinganlar_royxati()
        if not royxat:
            messagebox.showinfo("Diqqat", "Hali Palatadan/imzodan qaytgan Davo arizalar yo'q.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="imzodan_kelganlar.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows = []
        for item in royxat:
            xat = item['xat']
            rows.append([
                xat['anketa_raqami'], xat['mijoz_nomi'], item['pinfl'],
                xat.get('davo_ariza_ish_raqami', '') or '',
                xat.get('davo_ariza_imzo_sana', '') or '',
                item['davo_summasi_asosiy'], item['davo_summasi_foiz'], item['davo_summasi_jarima'],
                item['davo_summasi'], item['joriy_qarz'], item['farq'],
                "✓ Ha" if item['qoshimcha_kerak'] else "Yo'q",
            ])
        headers = ['Anketa raqami', 'Mijoz', 'PINFL', 'Ish raqami', 'Chiqqan sana',
                   'Davo summasi (asosiy)', 'Davo summasi (foiz)', 'Davo summasi (jarima)',
                   'Jami davo summasi', 'Joriy qarzdorlik', 'Farq',
                   "Qo'shimcha ariza kerakmi"]
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"{len(rows)} ta yozuv eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)

    def open_taminot_dialog(self):
        selected = self._selected()
        if len(selected) != 1:
            messagebox.showinfo("Diqqat", "Kafil/garov kiritish uchun aynan bitta mijozni tanlang.")
            return
        item = selected[0]
        dlg = TaminotDialog(self, item['xat']['anketa_raqami'], item['xat']['mijoz_nomi'])
        self.wait_window(dlg)
        self.refresh()

    def export_taminot(self):
        selected = self._selected()
        if not selected:
            messagebox.showinfo("Diqqat", "Avval ro'yxatdan mijozlarni tanlang.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="taminot_royxati.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        rows = []
        for item in selected:
            anketa = item['xat']['anketa_raqami']
            existing = db.get_taminot(anketa) or {}
            row = {'anketa_raqami': anketa, 'mijoz_nomi': item['xat']['mijoz_nomi']}
            row.update(existing)
            rows.append(row)
        try:
            importer.export_taminot_excel(rows, out_path)
            messagebox.showinfo("Tayyor", f"{len(rows)} ta qator eksport qilindi:\n{out_path}")
            webbrowser.open(out_path)
        except Exception as e:
            messagebox.showerror("Xato", str(e))

    def import_taminot(self):
        filepath = filedialog.askopenfilename(
            title="Tahrirlangan ta'minot Excel faylini tanlang",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
        if not filepath:
            return
        try:
            result = importer.import_taminot_excel(filepath)
            messagebox.showinfo("Tayyor", f"{result['yangilandi']} ta mijoz ta'minot ma'lumoti saqlandi.\n\n"
                                           "Bu ma'lumotlar endi eslab qolindi — keyingi safar ham ishlatiladi.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Xato", str(e))

    def generate_bulk(self):
        selected = self._selected()
        if not selected:
            messagebox.showinfo("Diqqat", "Iltimos, kamida bitta mijozni tanlang.")
            return

        dropdown_turi = self._turi_kaliti()
        want_pdf = self.format_var.get().startswith('PDF')
        settings = db.get_all_settings()
        out_dir = bugungi_papka('Davo ariza')

        created, errors = [], []
        pdf_muvaffaqiyatsiz = []
        otkazib_yuborildi = []
        turlar_soni = {}
        for item in selected:
            xat = item['xat']
            prow = item['portfel']
            if db.davo_ariza_mavjudmi(xat['anketa_raqami']):
                # Bitta anketaga faqat bitta Davo ariza — allaqachon mavjud, o'tkazib yuboriladi.
                otkazib_yuborildi.append(xat.get('anketa_raqami'))
                continue
            try:
                mijoz_turi, mijoz = resolve_mijoz(prow)
                taminot = db.get_taminot(xat['anketa_raqami'])
                # MUHIM: har bir mijoz uchun o'zining kafillik/garov ma'lumotiga
                # qarab TO'G'RI turini alohida hisoblaymiz — agar bir nechta
                # mijoz birga tanlangan bo'lsa (ular orasida kafili bor va
                # yo'qlari aralash bo'lishi mumkin), tepadagi oynachadagi
                # bitta tanlov BARCHASIGA bir xilda qo'llanmaydi. Faqat
                # aniq ta'minot ma'lumoti topilmasa (masalan kafil/garov
                # hali kiritilmagan bo'lsa), oynachadagi tanlovga tayanamiz.
                if taminot and taminot.get('taminot_turi') not in (None, '', 'yoq'):
                    turi = letters.tavsiya_ariza_turi(mijoz_turi, taminot)
                else:
                    turi = dropdown_turi
                turlar_soni[turi] = turlar_soni.get(turi, 0) + 1

                mijoz_ism_fayl = letters.safe_filename(mijoz.get('ism') if mijoz else xat['mijoz_nomi'])
                fname = f"Davo_{turi}_{letters.safe_filename(xat['anketa_raqami'])}_{mijoz_ism_fayl}.docx"
                out_path = os.path.join(out_dir, fname)
                letters.generate_davo_ariza_v2(
                    turi, out_path, prow, mijoz, taminot, settings,
                    xat_sanasi=self._fmt_sana(xat.get('yaratilgan_sana')),
                    xat_turi_nomi=('Талабнома' if xat['xat_turi'] == 'Talabnoma' else 'Огохлантириш хати'),
                )
                if want_pdf:
                    try:
                        out_path = letters.convert_docx_to_pdf(out_path, delete_docx=True)
                    except Exception as pdf_e:
                        pdf_muvaffaqiyatsiz.append(xat.get('anketa_raqami'))
                db.mark_davo_ariza_yaratildi(xat['id'], out_path, turi=turi, portfel_row=prow)
                created.append(out_path)
            except Exception as e:
                errors.append(f"{xat.get('anketa_raqami')}: {e}")

        msg = f"{len(created)} ta Davo ariza yaratildi.\nJoylashuv: {out_dir}"
        if len(turlar_soni) > 1:
            taqsimot = ', '.join(f"{letters.DAVO_ARIZA_NOMLARI.get(t, t)}: {n} ta"
                                  for t, n in turlar_soni.items())
            msg += f"\n\nHar biri o'z ta'minot ma'lumotiga qarab turlicha yaratildi:\n{taqsimot}"
        if otkazib_yuborildi:
            msg += (f"\n\nℹ {len(otkazib_yuborildi)} ta anketa uchun Davo ariza allaqachon "
                    f"mavjud edi — takroriy yaratilmadi.")
        if pdf_muvaffaqiyatsiz:
            msg += (f"\n\n⚠ {len(pdf_muvaffaqiyatsiz)} ta hujjat PDF'ga aylantirilmadi (Word "
                    f"bilan bog'liq vaqtinchalik muammo) — ular Word (.docx) holida saqlandi, "
                    f"lekin baribir ro'yxatga to'g'ri qo'shildi.")
        if errors:
            msg += f"\n\n{len(errors)} ta xatoda:\n" + '\n'.join(errors[:5])
        messagebox.showinfo("Tayyor", msg)
        if created:
            webbrowser.open(out_dir)
        self.refresh()

    @staticmethod
    def _fmt_sana(iso_str):
        try:
            return datetime.datetime.fromisoformat(iso_str).strftime('%d.%m.%Y')
        except Exception:
            return iso_str or ''


class VafotQoshishDialog(tk.Toplevel):
    """Yangi vafot etgan mijozni ro'yxatga olish oynasi."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Vafot etgan mijozni kiritish")
        self.geometry("520x480")
        self.configure(bg=BG)
        self.result = None
        self.olimlik_yol = None
        self.pasport_yol = None
        self._tanlangan_portfel = None
        self._portfel_natijalar = []

        ttk.Label(self, text="Vafot etgan mijozni ro'yxatga olish",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text="Anketa raqami bo'yicha portfeldan mijozni topib tanlaysiz.",
                  style='Sub.TLabel', wraplength=470).pack(anchor='w', padx=16, pady=(0, 12))

        search_row = ttk.Frame(self)
        search_row.pack(fill='x', padx=16, pady=4)
        ttk.Label(search_row, text="Anketa raqami:", width=16).pack(side='left')
        self.anketa_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.anketa_var, width=20).pack(side='left')
        ttk.Button(search_row, text="🔍 Qidirish", command=self.qidirish).pack(side='left', padx=8)

        self.natija_var = tk.StringVar(value="Hali qidirilmagan")
        ttk.Label(self, textvariable=self.natija_var, style='Sub.TLabel',
                  wraplength=470, justify='left').pack(anchor='w', padx=16, pady=(8, 4))

        self.tanlov_combo = ttk.Combobox(self, state='readonly', width=60)
        self.tanlov_combo.pack(anchor='w', padx=16, pady=(0, 10))
        self.tanlov_combo.bind('<<ComboboxSelected>>', self._on_tanlov)

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Vafot sanasi:", width=16).pack(side='left')
        self.sana_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.sana_var, width=20).pack(side='left')
        ttk.Label(self, text="(format: kun.oy.yil, masalan 01.06.2026)",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 10))

        ttk.Label(self, text="O'limlik guvohnomasi (.pdf/.jpg/.png):",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(4, 4))
        f1 = ttk.Frame(self)
        f1.pack(fill='x', padx=16)
        self.olimlik_label = ttk.Label(f1, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.olimlik_label.pack(side='left')
        ttk.Button(f1, text="📎 Tanlash", command=self.tanlash_olimlik).pack(side='left', padx=8)

        ttk.Label(self, text="Pasport nusxasi (.pdf/.jpg/.png):",
                  style='Sub.TLabel').pack(anchor='w', padx=16, pady=(10, 4))
        f2 = ttk.Frame(self)
        f2.pack(fill='x', padx=16)
        self.pasport_label = ttk.Label(f2, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.pasport_label.pack(side='left')
        ttk.Button(f2, text="📎 Tanlash", command=self.tanlash_pasport).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=16, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Saqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def qidirish(self):
        anketa = self.anketa_var.get().strip()
        if not anketa:
            messagebox.showinfo("Diqqat", "Anketa raqamini kiriting.")
            return
        rows = db.get_portfel_by_anketa(anketa)
        if not rows:
            self.natija_var.set("Topilmadi — bu anketa raqami portfelda yo'q.")
            self.tanlov_combo['values'] = []
            self._portfel_natijalar = []
            return
        self._portfel_natijalar = rows
        labels = [f"{r['mijoz_nomi']} — filial {r.get('filial_kodi','')} — "
                  f"kredit tugash: {r.get('shartnoma_tugash_sanasi','—')}" for r in rows]
        self.tanlov_combo['values'] = labels
        self.tanlov_combo.current(0)
        self._on_tanlov()
        self.natija_var.set(f"{len(rows)} ta natija topildi. Kerakli mijozni tanlang:")

    def _on_tanlov(self, event=None):
        idx = self.tanlov_combo.current()
        if 0 <= idx < len(self._portfel_natijalar):
            self._tanlangan_portfel = self._portfel_natijalar[idx]

    def tanlash_olimlik(self):
        filepath = filedialog.askopenfilename(
            title="O'limlik guvohnomasini tanlang",
            filetypes=[("Hujjatlar", "*.pdf *.jpg *.jpeg *.png")]
        )
        if filepath:
            self.olimlik_yol = filepath
            self.olimlik_label.config(text=os.path.basename(filepath))

    def tanlash_pasport(self):
        filepath = filedialog.askopenfilename(
            title="Pasport nusxasini tanlang",
            filetypes=[("Hujjatlar", "*.pdf *.jpg *.jpeg *.png")]
        )
        if filepath:
            self.pasport_yol = filepath
            self.pasport_label.config(text=os.path.basename(filepath))

    def confirm(self):
        if not self._tanlangan_portfel:
            messagebox.showerror("Xato", "Avval anketa raqami bo'yicha qidirib, mijozni tanlang.")
            return
        sana = self.sana_var.get().strip()
        if not sana:
            messagebox.showerror("Xato", "Vafot sanasini kiriting.")
            return
        if not self.olimlik_yol or not self.pasport_yol:
            messagebox.showerror("Xato", "O'limlik guvohnomasi va pasport nusxasini yuklang.")
            return
        self.result = (self._tanlangan_portfel, sana, self.olimlik_yol, self.pasport_yol)
        self.destroy()


class SugurtaMalumotDialog(tk.Toplevel):
    """Sug'urta kompaniya nomi, polis raqami va faylini kiritish oynasi."""
    def __init__(self, parent, mijoz_nomi):
        super().__init__(parent)
        self.title(f"Sug'urta ma'lumoti — {mijoz_nomi}")
        self.geometry("460x300")
        self.configure(bg=BG)
        self.result = None
        self.polis_yol = None

        ttk.Label(self, text="Sug'urta ma'lumotini kiritish",
                  style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 4))
        ttk.Label(self, text=mijoz_nomi, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(0, 14))

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Sug'urta kompaniya:", width=18).pack(side='left')
        self.kompaniya_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.kompaniya_var, width=24).pack(side='left')

        row2 = ttk.Frame(self)
        row2.pack(fill='x', padx=16, pady=6)
        ttk.Label(row2, text="Polis raqami:", width=18).pack(side='left')
        self.raqam_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.raqam_var, width=24).pack(side='left')

        ttk.Label(self, text="Polis nusxasi (PDF):", style='Sub.TLabel').pack(
            anchor='w', padx=16, pady=(10, 4))
        f1 = ttk.Frame(self)
        f1.pack(fill='x', padx=16)
        self.polis_label = ttk.Label(f1, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.polis_label.pack(side='left')
        ttk.Button(f1, text="📎 Tanlash", command=self.tanlash).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=20, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Saqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def tanlash(self):
        filepath = filedialog.askopenfilename(title="Polis nusxasini tanlang", filetypes=[("PDF", "*.pdf")])
        if filepath:
            self.polis_yol = filepath
            self.polis_label.config(text=os.path.basename(filepath))

    def confirm(self):
        kompaniya = self.kompaniya_var.get().strip()
        if not kompaniya:
            messagebox.showerror("Xato", "Sug'urta kompaniya nomini kiriting.")
            return
        self.result = (kompaniya, self.raqam_var.get().strip(), self.polis_yol)
        self.destroy()


class SanaKiritishDialog(tk.Toplevel):
    """Oddiy sana (va ixtiyoriy fayl) kiritish uchun umumiy oyna."""
    def __init__(self, parent, sarlavha, fayl_talab=False, fayl_label_matni="Fayl (PDF):"):
        super().__init__(parent)
        self.title(sarlavha)
        self.geometry("420x260")
        self.configure(bg=BG)
        self.result = None
        self.fayl_yol = None
        self.fayl_talab = fayl_talab

        ttk.Label(self, text=sarlavha, style='Header.TLabel').pack(anchor='w', padx=16, pady=(16, 14))

        row1 = ttk.Frame(self)
        row1.pack(fill='x', padx=16, pady=6)
        ttk.Label(row1, text="Sana:", width=12).pack(side='left')
        self.sana_var = tk.StringVar(value=datetime.date.today().strftime('%d.%m.%Y'))
        ttk.Entry(row1, textvariable=self.sana_var, width=22).pack(side='left')

        ttk.Label(self, text=fayl_label_matni, style='Sub.TLabel').pack(anchor='w', padx=16, pady=(10, 4))
        f1 = ttk.Frame(self)
        f1.pack(fill='x', padx=16)
        self.fayl_label = ttk.Label(f1, text="(fayl tanlanmagan)", style='Sub.TLabel')
        self.fayl_label.pack(side='left')
        ttk.Button(f1, text="📎 Tanlash", command=self.tanlash).pack(side='left', padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=16, pady=20, side='bottom')
        ttk.Button(btns, text="Bekor qilish", command=self.destroy).pack(side='right', padx=4)
        ttk.Button(btns, text="✓ Tasdiqlash", style='Accent.TButton', command=self.confirm).pack(side='right', padx=4)

        self.transient(parent)
        self.grab_set()

    def tanlash(self):
        filepath = filedialog.askopenfilename(title="Faylni tanlang",
                                               filetypes=[("Hujjatlar", "*.pdf *.jpg *.jpeg *.png")])
        if filepath:
            self.fayl_yol = filepath
            self.fayl_label.config(text=os.path.basename(filepath))

    def confirm(self):
        sana = self.sana_var.get().strip()
        if not sana:
            messagebox.showerror("Xato", "Sanani kiriting.")
            return
        if self.fayl_talab and not self.fayl_yol:
            messagebox.showerror("Xato", "Faylni yuklang.")
            return
        self.result = (sana, self.fayl_yol)
        self.destroy()


class Nazorat95413Tab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="95413 nazorati (balansdan chiqarilgan kreditlar)",
                  style='Header.TLabel').pack(anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Bu bo'limda \"Колдик 95413\" balansiga ega (maxsus nazoratga "
                              "o'tkazilgan) barcha kreditlar, DPD kunidan qat'i nazar, ko'rsatiladi. "
                              "Bunday kreditlar odatda asosiy balansdan chiqarilgani uchun boshqa "
                              "DPD-asoslangan bo'limlarda (Tahlil, Chora ko'rish) ko'rinmasligi "
                              "mumkin edi — shu bois bu yerda alohida, to'liq bosqichma-bosqich "
                              "nazorat ostida ushlab turiladi.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))

        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill='x', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", style='Accent.TButton',
                   command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="📊 Excel'ga eksport qilish", command=self.export_excel).pack(
            side='left', padx=8)

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=20, pady=(8, 6))
        ttk.Label(filter_frame, text="Bosqich bo'yicha filtrlash:").pack(side='left')
        self.filter_var = tk.StringVar(value="Barchasi")
        filter_values = ["Barchasi"] + list(db.BOSQICH_NOMLARI_95413.values())
        ttk.Combobox(filter_frame, textvariable=self.filter_var, values=filter_values,
                     state='readonly', width=48).pack(side='left', padx=8)
        ttk.Button(filter_frame, text="Filtrlash", command=self.refresh_table).pack(side='left')

        cols = ('anketa', 'mijoz', 'turi', 'balans', 'bosqich', 'tafsilot', 'yigma_jild', 'nazorat')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi',
                    'balans': "Balans 95413", 'bosqich': 'Bosqich', 'tafsilot': 'Tafsilot',
                    'yigma_jild': "Yig'ma jild", 'nazorat': 'Nazorat'}
        widths = {'anketa': 80, 'mijoz': 170, 'turi': 60, 'balans': 110, 'bosqich': 170,
                  'tafsilot': 230, 'yigma_jild': 75, 'nazorat': 140}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('kerak', foreground=ERR)
        self.tree.tag_configure('kutilmoqda', foreground='#B7862C')
        self.tree.tag_configure('jarayonda', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self._royxat_cache = []
        self.refresh()

    def refresh(self):
        self._royxat_cache = db.get_95413_royxati()

        for w in self.summary_frame.winfo_children():
            w.destroy()
        from collections import Counter
        soni = Counter(r['bosqich'] for r in self._royxat_cache)
        jami_balans = sum((r['portfel'].get('balans_95413') or 0) for r in self._royxat_cache)

        f0 = tk.Frame(self.summary_frame, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
        f0.pack(side='left', expand=True, fill='both', padx=6, ipady=10)
        tk.Label(f0, text=f"{len(self._royxat_cache)} ta", bg=WHITE, fg=INK,
                 font=('Consolas', 18, 'bold')).pack(pady=(6, 0))
        tk.Label(f0, text=f"Jami kredit ({jami_balans:,.0f} so'm)".replace(',', ' '),
                 bg=WHITE, fg='#6B7280', font=('Segoe UI', 8), wraplength=180,
                 justify='center').pack(pady=(0, 6))

        for bosqich, nomi in db.BOSQICH_NOMLARI_95413.items():
            f = tk.Frame(self.summary_frame, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
            f.pack(side='left', expand=True, fill='both', padx=6, ipady=10)
            tk.Label(f, text=str(soni.get(bosqich, 0)), bg=WHITE, fg=STAMP,
                     font=('Consolas', 16, 'bold')).pack(pady=(6, 0))
            tk.Label(f, text=nomi, bg=WHITE, fg='#6B7280', font=('Segoe UI', 8),
                     wraplength=140, justify='center').pack(pady=(0, 6))

        self.refresh_table()
        self.app.tab_dashboard.refresh()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        filtr = self.filter_var.get()
        for r in self._royxat_cache:
            bosqich_nomi = db.BOSQICH_NOMLARI_95413.get(r['bosqich'], r['bosqich'])
            if filtr != "Barchasi" and bosqich_nomi != filtr:
                continue
            balans = r['portfel'].get('balans_95413') or 0
            turi = util.turi_kodidan(r['portfel'].get('mijoz_turi_kodi'), r['portfel'].get('mijoz_turi'))

            jild_label = '—'
            nazorat_label = '—'
            tag = ''
            if r['bosqich'] == 'mib_jarayonida':
                jild_label = "✓ Mavjud" if r.get('yigma_jild') else "—"
                if r.get('nazorat_holati') == 'toxtatish':
                    nazorat_label = "⚠ To'xtatish kerak"
                    tag = 'kerak'
                elif r.get('nazorat_holati') == 'qoshimcha':
                    nazorat_label = "⚠ Farq qo'shish kerak"
                    tag = 'kutilmoqda'
                else:
                    nazorat_label = "OK"
                    tag = 'jarayonda'
            elif r['bosqich'] in ('xat_kerak', 'xat_yuborish_kerak', 'davo_ariza_kerak', 'sud_kerak', 'mib_kerak'):
                tag = 'kerak'
            elif r['bosqich'] == 'palata_kutilmoqda':
                tag = 'kutilmoqda'

            self.tree.insert('', 'end', values=(
                r['portfel']['anketa_raqami'], r['portfel']['mijoz_nomi'], turi,
                f"{balans:,.0f}".replace(',', ' '), bosqich_nomi, r['tafsilot'],
                jild_label, nazorat_label
            ), tags=(tag,))

    def export_excel(self):
        if not self._royxat_cache:
            messagebox.showinfo("Diqqat", "Ro'yxat bo'sh.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="95413_nazorati.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows = []
        for r in self._royxat_cache:
            balans = r['portfel'].get('balans_95413') or 0
            turi = util.turi_kodidan(r['portfel'].get('mijoz_turi_kodi'), r['portfel'].get('mijoz_turi'))
            rows.append([r['portfel']['anketa_raqami'], r['portfel']['mijoz_nomi'], turi, balans,
                         db.BOSQICH_NOMLARI_95413.get(r['bosqich'], r['bosqich']), r['tafsilot']])
        headers = ['Anketa raqami', 'Mijoz', 'Turi', 'Balans 95413', 'Bosqich', 'Tafsilot']
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"Ro'yxat eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)


class VafotEtganlarTab(ttk.Frame):
    POLIS_HOLAT_NOMLARI = {'tekshirilmagan': "Tekshirilmagan", 'amalda': "✓ Amalda",
                            'muddati_otgan': "⚠ Muddati o'tgan"}
    XABARNOMA_HOLAT_NOMLARI = {'kerak': "Yuborish kerak", 'yuborildi': "Yuborildi, javob kutilmoqda",
                                'javob_keldi': "✓ Javob keldi"}

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Vafot etgan mijozlar", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Vafot etgan mijozlarga nisbatan hech qanday undirish chorasi "
                              "(xat, Davo ariza, MIB) ko'rilmaydi — ular avtomatik ravishda "
                              "boshqa bo'limlar ro'yxatidan chiqarib tashlanadi. Faqat sug'urta "
                              "polisi mavjud va muddati o'tmagan bo'lsa, sug'urta kompaniyasidan "
                              "kreditni qoplashni so'rash jarayoni shu yerda yuritiladi.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="➕ Yangi vafot etgan mijoz", style='Accent.TButton',
                   command=self.qoshish).pack(side='left', padx=8)
        ttk.Button(toolbar, text="💼 Sug'urta ma'lumotini kiritish",
                   command=self.sugurta_kiritish).pack(side='left', padx=8)

        toolbar2 = ttk.Frame(self)
        toolbar2.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Button(toolbar2, text="✉ Xabarnoma tayyorlash",
                   command=self.xabarnoma_tayyorlash).pack(side='left')
        ttk.Label(toolbar2, text="Format:").pack(side='left', padx=(12, 4))
        self.format_var = tk.StringVar(value='Word (.docx)')
        ttk.Combobox(toolbar2, textvariable=self.format_var,
                     values=['Word (.docx)', 'PDF (.pdf)'], state='readonly', width=14).pack(side='left')
        ttk.Button(toolbar2, text="✓ Yuborildi deb belgilash",
                   command=self.xabarnoma_yuborildi).pack(side='left', padx=8)
        ttk.Button(toolbar2, text="✓ Javob keldi deb belgilash",
                   command=self.javob_keldi).pack(side='left', padx=8)
        ttk.Button(toolbar2, text="📎 Hujjatlarni ko'rish",
                   command=self.hujjatlar_korish).pack(side='left', padx=8)

        cols = ('anketa', 'mijoz', 'vafot_sanasi', 'polis_holati', 'sugurta', 'xabarnoma_holati', 'muddat')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=16)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'vafot_sanasi': 'Vafot sanasi',
                    'polis_holati': 'Polis holati', 'sugurta': "Sug'urta kompaniya",
                    'xabarnoma_holati': 'Xabarnoma holati', 'muddat': 'Javob muddati'}
        widths = {'anketa': 80, 'mijoz': 190, 'vafot_sanasi': 95, 'polis_holati': 110,
                  'sugurta': 140, 'xabarnoma_holati': 160, 'muddat': 130}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.tag_configure('muddati_otgan', foreground=ERR)
        self.tree.tag_configure('amalda', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self._rows_cache = {}
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        muddat_kun = int(db.get_setting('sugurta_javob_muddati_ish_kun', 40))
        bugun = datetime.datetime.now()

        for v in db.get_vafot_etganlar_royxati():
            prow = db.get_portfel_by_id(v['portfel_id']) if v.get('portfel_id') else None
            polis_label = self.POLIS_HOLAT_NOMLARI.get(v['polis_holati'], v['polis_holati'])
            xabarnoma_label = self.XABARNOMA_HOLAT_NOMLARI.get(v['xabarnoma_holati'], v['xabarnoma_holati'])

            tag = 'amalda' if v['polis_holati'] == 'amalda' else (
                  'muddati_otgan' if v['polis_holati'] == 'muddati_otgan' else '')

            muddat_label = '—'
            if v['xabarnoma_holati'] == 'yuborildi' and v.get('xabarnoma_yuborilgan_sana'):
                try:
                    yub_dt = datetime.datetime.strptime(v['xabarnoma_yuborilgan_sana'], '%d.%m.%Y')
                    ish_kun_otdi = db._ish_kunlari_orasida(yub_dt, bugun)
                    qolgan = muddat_kun - ish_kun_otdi
                    if qolgan < 0:
                        muddat_label = f"⚠ {abs(qolgan)} ish kuni o'tib ketdi"
                        tag = 'otgan'
                    else:
                        muddat_label = f"{qolgan} ish kuni qoldi"
                except Exception:
                    pass

            iid = str(v['id'])
            self.tree.insert('', 'end', iid=iid, values=(
                v['anketa_raqami'], v['mijoz_nomi'], v['vafot_sanasi'], polis_label,
                v.get('sugurta_kompaniya', '') or '—', xabarnoma_label, muddat_label
            ), tags=(tag,))
            self._rows_cache[iid] = {'vafot': v, 'portfel': prow}

        self.app.tab_dashboard.refresh()

    def _selected(self):
        sel = self.tree.selection()
        if len(sel) != 1:
            messagebox.showinfo("Diqqat", "Bitta mijozni tanlang.")
            return None
        return self._rows_cache.get(sel[0])

    def qoshish(self):
        dlg = VafotQoshishDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            prow, sana, olimlik_src, pasport_src = dlg.result
            papka = mib_bugungi_papka("Vafot etganlar")
            olimlik_dest = fayl_nusxala(olimlik_src, papka, prefiks='Olimlik_', mijoz_nomi=prow['mijoz_nomi'])
            pasport_dest = fayl_nusxala(pasport_src, papka, prefiks='Pasport_', mijoz_nomi=prow['mijoz_nomi'])
            vid, holat = db.mark_vafot_etgan(prow['id'], prow['anketa_raqami'], prow['mijoz_nomi'],
                                              sana, olimlik_dest, pasport_dest)
            if holat == 'amalda':
                messagebox.showinfo(
                    "Saqlandi",
                    "Mijoz vafot etgan deb ro'yxatga olindi.\n\n"
                    "✓ Sug'urta polisi muddati hali o'tmagan (kredit tugash sanasi asosida "
                    "avtomatik aniqlandi) — sug'urta ma'lumotini kiritib, xabarnoma "
                    "tayyorlashingiz mumkin."
                )
            elif holat == 'muddati_otgan':
                messagebox.showwarning(
                    "Saqlandi",
                    "Mijoz vafot etgan deb ro'yxatga olindi.\n\n"
                    "⚠ Diqqat: sug'urta polisi muddati allaqachon o'tgan (kredit tugash "
                    "sanasidan keyin vafot etgan) — sug'urta orqali qoplash imkoni yo'q."
                )
            else:
                messagebox.showinfo(
                    "Saqlandi",
                    "Mijoz vafot etgan deb ro'yxatga olindi.\n\n"
                    "Kredit tugash sanasi topilmagani uchun polis muddati avtomatik "
                    "aniqlanmadi — qo'lda tekshirib ko'ring."
                )
            self.refresh()

    def sugurta_kiritish(self):
        item = self._selected()
        if not item:
            return
        v = item['vafot']
        if v['polis_holati'] != 'amalda':
            messagebox.showwarning("Diqqat", "Sug'urta polisi muddati o'tgan yoki tekshirilmagan — "
                                              "sug'urta ma'lumoti kiritilmaydi.")
            return
        dlg = SugurtaMalumotDialog(self, v['mijoz_nomi'])
        self.wait_window(dlg)
        if dlg.result:
            kompaniya, raqam, polis_src = dlg.result
            polis_dest = None
            if polis_src:
                papka = mib_bugungi_papka("Vafot etganlar")
                polis_dest = fayl_nusxala(polis_src, papka, prefiks='Polis_', mijoz_nomi=v['mijoz_nomi'])
            db.update_sugurta_malumot(v['id'], kompaniya, raqam, polis_dest)
            messagebox.showinfo("Saqlandi", "Sug'urta ma'lumoti saqlandi.")
            self.refresh()

    def xabarnoma_tayyorlash(self):
        item = self._selected()
        if not item:
            return
        v = item['vafot']
        prow = item['portfel']
        if v['polis_holati'] != 'amalda':
            messagebox.showwarning("Diqqat", "Sug'urta polisi amalda bo'lmagan mijoz uchun "
                                              "xabarnoma tayyorlanmaydi.")
            return
        if not v.get('sugurta_kompaniya'):
            messagebox.showwarning("Diqqat", "Avval sug'urta ma'lumotini kiriting.")
            return
        if not prow:
            messagebox.showerror("Xato", "Bog'liq portfel yozuvi topilmadi.")
            return
        turi_m, mijoz = util.resolve_mijoz(prow)
        settings = db.get_all_settings()
        papka = mib_bugungi_papka("Vafot etganlar")
        fname = f"Xabarnoma_{letters.safe_filename(v['anketa_raqami'])}_{letters.safe_filename(v['mijoz_nomi'])}.docx"
        out_path = os.path.join(papka, fname)
        try:
            letters.generate_sugurta_xabarnoma(out_path, v, prow, mijoz, settings)
            if self.format_var.get().startswith('PDF'):
                out_path = letters.convert_docx_to_pdf(out_path, delete_docx=True)
        except Exception as e:
            messagebox.showerror("Xato", f"Xabarnoma yaratishda xato: {e}")
            return
        messagebox.showinfo("Tayyor", f"Xabarnoma tayyorlandi:\n{out_path}\n\n"
                                       "Yuborilgach, \"✓ Yuborildi deb belgilash\" tugmasini bosing.")
        webbrowser.open(out_path)

    def xabarnoma_yuborildi(self):
        item = self._selected()
        if not item:
            return
        v = item['vafot']
        dlg = SanaKiritishDialog(self, f"Xabarnoma yuborilgan sana — {v['mijoz_nomi']}")
        self.wait_window(dlg)
        if dlg.result:
            sana, _ = dlg.result
            db.mark_xabarnoma_yuborildi(v['id'], sana)
            messagebox.showinfo("Saqlandi", "Xabarnoma yuborilgani belgilandi. "
                                             f"Javob {db.get_setting('sugurta_javob_muddati_ish_kun', 40)} "
                                             "ish kuni ichida kutiladi.")
            self.refresh()

    def javob_keldi(self):
        item = self._selected()
        if not item:
            return
        v = item['vafot']
        if v['xabarnoma_holati'] != 'yuborildi':
            messagebox.showwarning("Diqqat", "Avval xabarnoma yuborilgani belgilanishi kerak.")
            return
        dlg = SanaKiritishDialog(self, f"Sug'urta javobi kelgan sana — {v['mijoz_nomi']}",
                                  fayl_label_matni="Javob xati (ixtiyoriy):")
        self.wait_window(dlg)
        if dlg.result:
            sana, fayl_src = dlg.result
            fayl_dest = None
            if fayl_src:
                papka = mib_bugungi_papka("Vafot etganlar")
                fayl_dest = fayl_nusxala(fayl_src, papka, prefiks='Javob_', mijoz_nomi=v['mijoz_nomi'])
            db.mark_sugurta_javob_keldi(v['id'], sana, fayl_dest)
            messagebox.showinfo("Saqlandi", "Sug'urta javobi kelgani belgilandi.")
            self.refresh()

    def hujjatlar_korish(self):
        item = self._selected()
        if not item:
            return
        v = item['vafot']
        fayllar = {
            "O'limlik guvohnomasi": v.get('olimlik_guvohnomasi_fayl'),
            "Pasport nusxasi": v.get('pasport_fayl'),
            "Sug'urta polisi": v.get('sugurta_polis_fayl'),
            "Sug'urta javobi": v.get('javob_fayl'),
        }
        mavjud = [(nomi, yol) for nomi, yol in fayllar.items() if yol and os.path.exists(yol)]
        if not mavjud:
            messagebox.showinfo("Diqqat", "Bu mijoz uchun hali hech qanday hujjat yuklanmagan.")
            return
        win = tk.Toplevel(self)
        win.title(f"Hujjatlar — {v['mijoz_nomi']}")
        win.geometry("400x260")
        win.configure(bg=BG)
        ttk.Label(win, text=f"Hujjatlar — {v['mijoz_nomi']}", style='Header.TLabel').pack(
            anchor='w', padx=16, pady=(16, 10))
        for nomi, yol in mavjud:
            row = ttk.Frame(win)
            row.pack(fill='x', padx=16, pady=4)
            ttk.Label(row, text=nomi, width=22).pack(side='left')
            ttk.Button(row, text="📎 Ochish", command=lambda p=yol: webbrowser.open(p)).pack(side='left')
        ttk.Button(win, text="Yopish", command=win.destroy).pack(pady=16)


class SudMibJarayonidaTab(ttk.Frame):
    """Suddan o'tkazilgan, hozir MIBga o'tkazish jarayonidagi (kutilmoqda yoki allaqachon
    o'tkazilgan) mijozlar holatini ko'rsatuvchi (asosan ma'lumot uchun) ro'yxat."""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._rows_cache = {}
        ttk.Label(self, text="Suddan o'tkazilgan va MIB o'tkazish jarayonidagilar",
                  style='Header.TLabel').pack(anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Sudga topshirilgan barcha ishlar — MIBga hali o'tkazilmaganlar "
                              "('MIB ijro harakatlari' bo'limida amalga oshiriladi) va allaqachon "
                              "o'tkazilganlar shu yerda ko'rinadi. 'Sud summasi' — Davo ariza "
                              "yaratilgan paytda qayd qilingan qarzdorlik (asosiy/foiz/penya).",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", style='Accent.TButton', command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="📊 Excel'ga eksport qilish", command=self.export_excel).pack(
            side='left', padx=8)

        toolbar2 = ttk.Frame(self)
        toolbar2.pack(fill='x', padx=20, pady=(8, 0))
        ttk.Label(toolbar2, text="Anketa raqami bo'yicha qidirish:").pack(side='left')
        self.qidiruv_var = tk.StringVar()
        qidiruv_entry = ttk.Entry(toolbar2, textvariable=self.qidiruv_var, width=16)
        qidiruv_entry.pack(side='left', padx=6)
        qidiruv_entry.bind('<Return>', lambda e: self.anketa_boyicha_topish())
        ttk.Button(toolbar2, text="🔍 Topish", command=self.anketa_boyicha_topish).pack(side='left')

        cols = ('anketa', 'mijoz', 'turi', 'pinfl', 'jami_qarz', 'sud_asosiy', 'sud_foiz', 'sud_jarima',
                'sud_ish_raqami', 'sud_sana', 'mib_holati')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'pinfl': 'PINFL',
                    'jami_qarz': "Jami sud summasi", 'sud_asosiy': 'Asosiy qarz', 'sud_foiz': 'Foiz',
                    'sud_jarima': 'Penya (jarima)', 'sud_ish_raqami': 'Sud ish raqami',
                    'sud_sana': 'Sudga topshirilgan', 'mib_holati': 'MIB holati'}
        widths = {'anketa': 75, 'mijoz': 170, 'turi': 60, 'pinfl': 110, 'jami_qarz': 110,
                  'sud_asosiy': 95, 'sud_foiz': 85, 'sud_jarima': 95, 'sud_ish_raqami': 95,
                  'sud_sana': 105, 'mib_holati': 110}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('kutilmoqda', foreground=KRAFT)
        self.tree.tag_configure('otkazilgan', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        conn = db.get_conn()
        rows = conn.execute("SELECT * FROM xatlar WHERE sud_holati='topshirildi' ORDER BY id DESC").fetchall()
        conn.close()
        for x in rows:
            xd = dict(x)
            prow = db.get_portfel_by_id(xd['portfel_id'])
            pinfl = prow.get('pinfl', '') if prow else ''

            sud_asosiy = xd.get('davo_summasi_asosiy') or 0
            sud_foiz = xd.get('davo_summasi_foiz') or 0
            sud_jarima = xd.get('davo_summasi_jarima') or 0
            sud_jami = sud_asosiy + sud_foiz + sud_jarima
            if not sud_jami and prow:
                # Agar davo summasi surati yo'q bo'lsa (masalan eski/legacy yozuv),
                # portfeldagi joriy summani zaxira sifatida ko'rsatamiz
                sud_asosiy = prow.get('asosiy_qarz') or 0
                sud_foiz = prow.get('foiz_qarz') or 0
                sud_jarima = prow.get('jarima') or 0
                sud_jami = sud_asosiy + sud_foiz + sud_jarima

            mib_otkazilgan = xd.get('mib_holati') == 'otkazildi'
            iid = str(xd['id'])
            self.tree.insert('', 'end', iid=iid, values=(
                xd['anketa_raqami'], xd['mijoz_nomi'], xd['mijoz_turi'], pinfl,
                f"{sud_jami:,.0f}".replace(',', ' '),
                f"{sud_asosiy:,.0f}".replace(',', ' '),
                f"{sud_foiz:,.0f}".replace(',', ' '),
                f"{sud_jarima:,.0f}".replace(',', ' '),
                xd.get('sud_ish_raqami', '') or '',
                xd.get('sud_topshirilgan_sana', '') or '',
                "✓ O'tkazilgan" if mib_otkazilgan else "Kutilmoqda"
            ), tags=('otkazilgan' if mib_otkazilgan else 'kutilmoqda',))
            self._rows_cache[iid] = xd
        self.app.tab_dashboard.refresh()

    def anketa_boyicha_topish(self):
        anketa = self.qidiruv_var.get().strip()
        if not anketa:
            return
        topildi = None
        for iid, xd in self._rows_cache.items():
            if str(xd.get('anketa_raqami', '')) == anketa:
                topildi = iid
                break
        if not topildi:
            messagebox.showinfo("Topilmadi", f"Anketa {anketa} bo'yicha sudga topshirilgan yozuv topilmadi.")
            return
        self.tree.selection_set(topildi)
        self.tree.see(topildi)
        self.tree.focus(topildi)

    def export_excel(self):
        if not self._rows_cache:
            messagebox.showinfo("Diqqat", "Sudga topshirilgan yozuvlar yo'q.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="sudga_topshirilganlar.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows_out = []
        for xd in self._rows_cache.values():
            prow = db.get_portfel_by_id(xd['portfel_id'])
            pinfl = prow.get('pinfl', '') if prow else ''
            sud_asosiy = xd.get('davo_summasi_asosiy') or 0
            sud_foiz = xd.get('davo_summasi_foiz') or 0
            sud_jarima = xd.get('davo_summasi_jarima') or 0
            sud_jami = sud_asosiy + sud_foiz + sud_jarima
            mib_otkazilgan = xd.get('mib_holati') == 'otkazildi'
            rows_out.append([
                xd['anketa_raqami'], xd['mijoz_nomi'], pinfl, xd['mijoz_turi'],
                sud_asosiy, sud_foiz, sud_jarima, sud_jami,
                xd.get('sud_ish_raqami', '') or '', xd.get('sud_topshirilgan_sana', '') or '',
                "O'tkazilgan" if mib_otkazilgan else "Kutilmoqda"
            ])
        headers = ['Anketa raqami', 'Mijoz', 'PINFL', 'Turi', 'Asosiy qarz', 'Foiz', 'Penya (jarima)',
                   'Jami sud summasi', 'Sud ish raqami', 'Sudga topshirilgan sana', 'MIB holati']
        df = pd.DataFrame(rows_out, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"{len(rows_out)} ta yozuv eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)


class MibHarakatsizlarTab(ttk.Frame):
    """MIBda belgilangan muddat ichida hech qanday harakat qilinmagan mijozlar ro'yxati."""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="MIBda harakatsiz qolib ketayotganlar", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="MIBga o'tkazilgandan (yoki oxirgi harakatdan) keyin belgilangan muddat "
                              "ichida hech qanday yangi harakat qayd qilinmagan mijozlar — bularga "
                              "ijro harakatini boshlash/davom ettirish talab qilinadi.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(anchor='w', padx=20, pady=(0, 10))
        ttk.Button(self, text="🔄 Yangilash", style='Accent.TButton', command=self.refresh).pack(
            anchor='w', padx=20)

        cols = ('anketa', 'mijoz', 'turi', 'jami_qarz', 'mib_ish_raqami', 'harakatsizlik_kun')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'jami_qarz': 'Qarzdorlik',
                    'mib_ish_raqami': 'MIB ish raqami', 'harakatsizlik_kun': 'Necha kun harakatsiz'}
        widths = {'anketa': 85, 'mijoz': 240, 'turi': 70, 'jami_qarz': 120, 'mib_ish_raqami': 120,
                  'harakatsizlik_kun': 160}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for x in db.get_mib_harakatsizlar():
            prow = db.get_portfel_by_id(x['portfel_id'])
            jami = 0
            if prow:
                jami = (prow.get('asosiy_qarz') or 0) + (prow.get('foiz_qarz') or 0) + (prow.get('jarima') or 0)
            self.tree.insert('', 'end', values=(
                x['anketa_raqami'], x['mijoz_nomi'], x['mijoz_turi'],
                f"{jami:,.0f}".replace(',', ' '), x.get('mib_ish_raqami', '') or '',
                x.get('harakatsizlik_kun', '')
            ), tags=('otgan',))
        self.app.tab_dashboard.refresh()


class MibYakunlanganTab(ttk.Frame):
    """To'xtatilgan/yakunlangan MIB ijro ishlari ro'yxati (tarixiy)."""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._rows_cache = {}
        ttk.Label(self, text="Yakunlangan MIB ishlari", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Ijro harakati to'xtatilgan/yakunlangan deb belgilangan ishlar. "
                              "Bu yerdagilar 'MIBda jarayondagi hujjatlar' faol ro'yxatida "
                              "endi ko'rinmaydi.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", style='Accent.TButton', command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="↩ Qayta faol qilish (tanlangan)", command=self.qayta_ochish).pack(
            side='left', padx=8)

        cols = ('anketa', 'mijoz', 'turi', 'mib_ish_raqami', 'yakunlangan_sana', 'sabab')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi',
                    'mib_ish_raqami': 'MIB ish raqami', 'yakunlangan_sana': 'Yakunlangan sana',
                    'sabab': 'Sabab / izoh'}
        widths = {'anketa': 85, 'mijoz': 220, 'turi': 70, 'mib_ish_raqami': 110,
                  'yakunlangan_sana': 120, 'sabab': 380}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('yakunlangan', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = {}
        for x in db.get_mib_yakunlangan_royxati():
            iid = str(x['id'])
            self.tree.insert('', 'end', iid=iid, values=(
                x['anketa_raqami'], x['mijoz_nomi'], x['mijoz_turi'],
                x.get('mib_ish_raqami', '') or '', x.get('mib_yakunlangan_sana', '') or '',
                x.get('mib_yakunlash_sababi', '') or ''
            ), tags=('yakunlangan',))
            self._rows_cache[iid] = x
        self.app.tab_dashboard.refresh()

    def qayta_ochish(self):
        sel = self.tree.selection()
        if len(sel) != 1:
            messagebox.showinfo("Diqqat", "Aynan bitta ishni tanlang.")
            return
        x = self._rows_cache.get(sel[0])
        if not x:
            return
        javob = messagebox.askyesno(
            "Tasdiqlash",
            f"{x['mijoz_nomi']} bo'yicha ishni qaytadan FAOL holatga qaytarasizmi? "
            "U 'MIBda jarayondagi hujjatlar' ro'yxatiga qaytadi."
        )
        if not javob:
            return
        db.mib_ishni_qayta_ochish(x['id'])
        messagebox.showinfo("Saqlandi", "Ish qaytadan faol holatga qaytarildi.")
        self.refresh()
        if hasattr(self.app, 'tab_mib'):
            self.app.tab_mib.refresh()


def build_module(notebook_parent):
    """
    Bir nechta kichik bo'limdan tashkil topgan modul uchun tashqi ttk.Frame
    va ichki ttk.Notebook yaratadi. Sub-tab widget'lari SHU qaytarilgan
    ichki notebook'ni ota (parent) sifatida olib yaratilishi, so'ng
    inner.add(widget, text=...) orqali qo'shilishi kerak.
    """
    frame = ttk.Frame(notebook_parent)
    inner = ttk.Notebook(frame)
    inner.pack(fill='both', expand=True, padx=6, pady=6)
    return frame, inner


class ChoraKorishTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Chora ko'rish", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Portfel avtomatik tahlil qilinib, muddati o'tgan (DPD) kuni va joriy "
                              "bosqichiga qarab har bir qoniqarsiz mijoz uchun qanday chora zarurligi "
                              "ko'rsatiladi.",
                  style='Sub.TLabel', wraplength=1000, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))

        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill='x', padx=20, pady=(0, 10))
        self.summary_cards = {}

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Tahlil qilish (yangilash)", style='Accent.TButton',
                   command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="📊 Excel'ga eksport qilish", command=self.export_excel).pack(side='left', padx=8)

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=20, pady=(8, 6))
        ttk.Label(filter_frame, text="Chora bo'yicha filtrlash:").pack(side='left')
        self.filter_var = tk.StringVar(value="Barchasi")
        filter_values = ["Barchasi"] + list(db.CHORA_NOMLARI.values())
        ttk.Combobox(filter_frame, textvariable=self.filter_var, values=filter_values,
                     state='readonly', width=48).pack(side='left', padx=8)
        ttk.Button(filter_frame, text="Filtrlash", command=self.refresh_table).pack(side='left')

        cols = ('anketa', 'mijoz', 'turi', 'dpd', 'jami_qarz', 'chora', 'tafsilot')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=16)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'dpd': 'DPD (kun)',
                    'jami_qarz': 'Qarzdorlik', 'chora': "Talab qilinayotgan chora", 'tafsilot': 'Tafsilot'}
        widths = {'anketa': 85, 'mijoz': 190, 'turi': 70, 'dpd': 70, 'jami_qarz': 110,
                  'chora': 220, 'tafsilot': 260}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('mib', foreground=ERR)
        self.tree.tag_configure('davo', foreground='#B7862C')
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self._royxat_cache = []
        self.refresh()

    def refresh(self):
        self._royxat_cache = db.get_chora_korish_royxati()

        for w in self.summary_frame.winfo_children():
            w.destroy()
        self.summary_cards = {}
        from collections import Counter
        soni = Counter(r['chora'] for r in self._royxat_cache)
        for chora, nomi in db.CHORA_NOMLARI.items():
            f = tk.Frame(self.summary_frame, bg=WHITE, highlightbackground='#E3E7F0', highlightthickness=1)
            f.pack(side='left', expand=True, fill='both', padx=6, ipady=10)
            num = tk.Label(f, text=str(soni.get(chora, 0)), bg=WHITE, fg=STAMP,
                            font=('Consolas', 20, 'bold'))
            num.pack(pady=(6, 0))
            tk.Label(f, text=nomi, bg=WHITE, fg='#6B7280', font=('Segoe UI', 8),
                     wraplength=180, justify='center').pack(pady=(0, 6))

        self.refresh_table()
        self.app.tab_dashboard.refresh()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        filtr = self.filter_var.get()
        for r in self._royxat_cache:
            if filtr != "Barchasi" and r['chora_nomi'] != filtr:
                continue
            jami = (r['portfel'].get('asosiy_qarz') or 0) + (r['portfel'].get('foiz_qarz') or 0) + \
                   (r['portfel'].get('jarima') or 0)
            tag = 'mib' if r['chora'] == 'mib_harakat_boshlash' else (
                  'davo' if r['chora'] == 'davo_ariza_tayyorlash' else '')
            self.tree.insert('', 'end', values=(
                r['portfel']['anketa_raqami'], r['portfel']['mijoz_nomi'], r['turi'], r['dpd'],
                f"{jami:,.0f}".replace(',', ' '), r['chora_nomi'], r['tafsilot']
            ), tags=(tag,))

    def export_excel(self):
        if not self._royxat_cache:
            messagebox.showinfo("Diqqat", "Ro'yxat bo'sh.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="chora_korish_royxati.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        rows = []
        for r in self._royxat_cache:
            jami = (r['portfel'].get('asosiy_qarz') or 0) + (r['portfel'].get('foiz_qarz') or 0) + \
                   (r['portfel'].get('jarima') or 0)
            rows.append([r['portfel']['anketa_raqami'], r['portfel']['mijoz_nomi'], r['turi'],
                         r['dpd'], jami, r['chora_nomi'], r['tafsilot']])
        headers = ['Anketa raqami', 'Mijoz', 'Turi', 'DPD (kun)', 'Qarzdorlik',
                   'Talab qilinayotgan chora', 'Tafsilot']
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"Ro'yxat eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)


class DavoHisobotTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Davo ariza hisoboti", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(20, 4))
        ttk.Label(self, text="Barcha tayyorlangan Davo arizalar — qachon yaratilgani, qancha vaqtda "
                              "olib kelingani, ish raqami va mijoz qarzdorligi.",
                  style='Sub.TLabel', wraplength=1000).pack(anchor='w', padx=20, pady=(0, 10))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=20)
        ttk.Button(toolbar, text="🔄 Yangilash", command=self.refresh).pack(side='left')
        ttk.Button(toolbar, text="📊 Excel'ga eksport qilish", command=self.export_excel).pack(side='left', padx=8)

        cols = ('anketa', 'mijoz', 'turi', 'jami_qarz', 'yaratilgan', 'kutilgan_kun',
                'ish_raqami', 'imzo_sana', 'holati', 'sud_ish_raqami', 'sud_sana', 'sud_holati')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=18)
        headings = {'anketa': 'Anketa №', 'mijoz': 'Mijoz', 'turi': 'Turi', 'jami_qarz': "Qarzdorlik",
                    'yaratilgan': 'Ariza yaratilgan', 'kutilgan_kun': 'Necha kun kutildi',
                    'ish_raqami': 'Palata ish raqami', 'imzo_sana': 'Palatadan kelgan',
                    'holati': 'Holati', 'sud_ish_raqami': 'Sud ish raqami',
                    'sud_sana': 'Sudga topshirilgan', 'sud_holati': 'Sud holati'}
        widths = {'anketa': 85, 'mijoz': 190, 'turi': 70, 'jami_qarz': 100, 'yaratilgan': 100,
                  'kutilgan_kun': 90, 'ish_raqami': 100, 'imzo_sana': 100, 'holati': 120,
                  'sud_ish_raqami': 100, 'sud_sana': 110, 'sud_holati': 110}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c])
        self.tree.tag_configure('otgan', foreground=ERR)
        self.tree.tag_configure('tayyor', foreground=STAMP)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        self._rows_cache = []
        self.refresh()

    def _build_rows(self):
        muddat_kun = int(db.get_setting('davo_ariza_muddati_kun', 5))
        out = []
        for x in db.get_davo_ariza_hisoboti():
            prow = db.get_portfel_by_id(x['portfel_id'])
            jami = 0
            if prow:
                jami = (prow.get('asosiy_qarz') or 0) + (prow.get('foiz_qarz') or 0) + (prow.get('jarima') or 0)

            olib_kelindi = x.get('davo_ariza_holati') == 'olib_kelindi'
            try:
                davo_dt = datetime.datetime.fromisoformat(x['davo_ariza_sana'])
                yaratilgan = davo_dt.strftime('%d.%m.%Y')
            except Exception:
                davo_dt = None
                yaratilgan = x.get('davo_ariza_sana', '') or ''

            if olib_kelindi and davo_dt:
                try:
                    imzo_dt = datetime.datetime.strptime(x['davo_ariza_imzo_sana'], '%d.%m.%Y')
                    kutilgan_kun = max((imzo_dt.date() - davo_dt.date()).days, 0)
                except Exception:
                    kutilgan_kun = ''
                holati = "✓ Olib kelindi"
                tag = 'tayyor'
            elif davo_dt:
                kutilgan_kun = (datetime.datetime.now() - davo_dt).days
                if kutilgan_kun > muddat_kun:
                    holati = f"⚠ Muddati o'tgan ({kutilgan_kun} kun)"
                    tag = 'otgan'
                else:
                    holati = f"Kutilmoqda ({muddat_kun - kutilgan_kun} kun qoldi)"
                    tag = ''
            else:
                kutilgan_kun = ''
                holati = ''
                tag = ''

            sud_topshirildi = x.get('sud_holati') == 'topshirildi'
            out.append({
                'anketa_raqami': x['anketa_raqami'],
                'mijoz_nomi': x['mijoz_nomi'],
                'mijoz_turi': x['mijoz_turi'],
                'jami_qarz': jami,
                'yaratilgan': yaratilgan,
                'kutilgan_kun': kutilgan_kun,
                'ish_raqami': x.get('davo_ariza_ish_raqami', '') or '',
                'imzo_sana': x.get('davo_ariza_imzo_sana', '') or '',
                'holati': holati,
                'sud_ish_raqami': x.get('sud_ish_raqami', '') or '',
                'sud_sana': x.get('sud_topshirilgan_sana', '') or '',
                'sud_holati': ("✓ Topshirildi" if sud_topshirildi
                               else ("Kutilmoqda" if olib_kelindi else "—")),
                'tag': tag,
            })
        return out

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows_cache = self._build_rows()
        for r in self._rows_cache:
            self.tree.insert('', 'end', values=(
                r['anketa_raqami'], r['mijoz_nomi'], r['mijoz_turi'],
                f"{r['jami_qarz']:,.0f}".replace(',', ' '), r['yaratilgan'],
                r['kutilgan_kun'], r['ish_raqami'], r['imzo_sana'], r['holati'],
                r['sud_ish_raqami'], r['sud_sana'], r['sud_holati']
            ), tags=(r['tag'],))

    def export_excel(self):
        if not self._rows_cache:
            messagebox.showinfo("Diqqat", "Hisobotda ma'lumot yo'q.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash", defaultextension=".xlsx",
            initialfile="davo_ariza_hisoboti.xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return
        import pandas as pd
        cols = ['anketa_raqami', 'mijoz_nomi', 'mijoz_turi', 'jami_qarz', 'yaratilgan',
                'kutilgan_kun', 'ish_raqami', 'imzo_sana', 'holati',
                'sud_ish_raqami', 'sud_sana', 'sud_holati']
        headers = ['Anketa raqami', 'Mijoz', 'Turi', 'Qarzdorlik', 'Ariza yaratilgan',
                   'Necha kun', 'Palata ish raqami', 'Palatadan kelgan', 'Holati',
                   'Sud ish raqami', 'Sudga topshirilgan', 'Sud holati']
        df = pd.DataFrame([[r.get(c, '') for c in cols] for r in self._rows_cache], columns=headers)
        df.to_excel(out_path, index=False)
        messagebox.showinfo("Tayyor", f"Hisobot eksport qilindi:\n{out_path}")
        webbrowser.open(out_path)


class SozlamalarGuruh(ttk.Frame):
    """
    Sozlamalarning bir guruhini (masalan faqat Davo arizaga oid) ko'rsatadigan
    umumiy (qayta ishlatiladigan) panel. Har bir modulning o'z ichida
    "Sozlamalar" kichik bo'limi shu klass orqali quriladi.
    """
    def __init__(self, parent, app, sarlavha, fields, sections=None):
        super().__init__(parent)
        self.app = app
        self.fields = fields
        self.sections = sections or []

        scroll = ScrollableFrame(self)
        scroll.pack(fill='both', expand=True)
        body = scroll.body

        ttk.Label(body, text=sarlavha, style='Header.TLabel').pack(anchor='w', padx=20, pady=(20, 14))

        canvas_frame = ttk.Frame(body)
        canvas_frame.pack(fill='both', expand=True, padx=20)

        self.vars = {}
        current = db.get_all_settings()
        for key, label in self.fields:
            row = ttk.Frame(canvas_frame)
            row.pack(fill='x', pady=5)
            ttk.Label(row, text=label, width=46).pack(side='left')
            var = tk.StringVar(value=current.get(key, ''))
            ttk.Entry(row, textvariable=var, width=50).pack(side='left')
            self.vars[key] = var

        if self.fields:
            ttk.Button(body, text="💾 Saqlash", style='Accent.TButton',
                       command=self.save).pack(anchor='w', padx=20, pady=16)

        if 'xat_shablon' in self.sections:
            self._build_xat_shablon_section(body)
        if 'davo_shablon' in self.sections:
            self._build_davo_shablon_section(body)
        if 'sugurta_shablon' in self.sections:
            self._build_sugurta_shablon_section(body)
        if 'yigma_jild_shablon' in self.sections:
            self._build_yigma_jild_shablon_section(body)

    def save(self):
        for key, var in self.vars.items():
            db.set_setting(key, var.get())
        messagebox.showinfo("Saqlandi", "Sozlamalar saqlandi.")

    # ---- Xat (Ogohlantirish/Talabnoma) shabloni ----
    def _build_xat_shablon_section(self, body):
        sep = ttk.Frame(body, height=2)
        sep.pack(fill='x', padx=20, pady=(4, 14))
        ttk.Label(body, text="Xat shabloni (Word)", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(0, 4))
        ttk.Label(body, text="Yangi shablon yuklasangiz, hali yuborilmagan ('Tayyor' holatidagi) "
                              "xatlar avtomatik shu yangi shablon bilan qayta tayyorlanadi.",
                  style='Sub.TLabel', wraplength=800, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))
        tpl_frame = ttk.Frame(body)
        tpl_frame.pack(anchor='w', padx=20, pady=(0, 30))
        ttk.Button(tpl_frame, text="📄 Joriy shablonni ochish", command=self.open_template).pack(side='left')
        ttk.Button(tpl_frame, text="📤 Yangi shablon yuklash (.docx)", style='Accent.TButton',
                   command=self.upload_template).pack(side='left', padx=10)

    def open_template(self):
        if os.path.exists(letters.TEMPLATE_PATH):
            webbrowser.open(letters.TEMPLATE_PATH)
        else:
            messagebox.showerror("Topilmadi", "Shablon fayli topilmadi.")

    def upload_template(self):
        filepath = filedialog.askopenfilename(
            title="Yangi shablon faylini tanlang", filetypes=[("Word hujjati", "*.docx")]
        )
        if not filepath:
            return
        try:
            import shutil
            os.makedirs(os.path.dirname(letters.TEMPLATE_PATH), exist_ok=True)
            if os.path.exists(letters.TEMPLATE_PATH):
                backup = letters.TEMPLATE_PATH + '.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.bak'
                shutil.copy2(letters.TEMPLATE_PATH, backup)
            shutil.copy2(filepath, letters.TEMPLATE_PATH)
        except Exception as e:
            messagebox.showerror("Xato", f"Shablonni saqlashda xato: {e}")
            return
        javob = messagebox.askyesno(
            "Qayta tayyorlash",
            "Shablon yangilandi.\n\nHali yuborilmagan ('Tayyor' holatidagi) xatlarni "
            "yangi shablon bilan hozir qayta tayyorlaymi?"
        )
        if javob:
            self._regenerate_pending()

    def _regenerate_pending(self):
        pending = db.get_xatlar('tayyor')
        settings = db.get_all_settings()
        updated, errors = 0, []
        for xat in pending:
            try:
                prow = db.get_portfel_by_id(xat['portfel_id'])
                if not prow:
                    continue
                turi, mijoz = util.resolve_mijoz(prow)
                mijoz_ism = mijoz['ism'] if mijoz else prow.get('mijoz_nomi', '')
                mijoz_manzil = mijoz['manzil'] if mijoz else ''
                rahbar_ism = mijoz.get('rahbar_ism') if mijoz else ''
                letters.generate_letter(
                    output_path=xat['fayl_yoli'], xat_turi=xat['xat_turi'], mijoz_ism=mijoz_ism,
                    mijoz_manzil=mijoz_manzil, portfel_row=prow, settings=settings,
                    anketa_raqami=xat['anketa_raqami'], rahbar_ism=rahbar_ism,
                )
                updated += 1
            except Exception as e:
                errors.append(f"{xat.get('anketa_raqami')}: {e}")
        msg = f"{updated} ta xat yangi shablon bilan qayta tayyorlandi."
        if errors:
            msg += f"\n\n{len(errors)} ta xatoda:\n" + '\n'.join(errors[:5])
        messagebox.showinfo("Tayyor", msg)

    # ---- Davo ariza shablonlari ----
    def _build_davo_shablon_section(self, body):
        sep2 = ttk.Frame(body, height=2)
        sep2.pack(fill='x', padx=20, pady=(4, 14))
        ttk.Label(body, text="Davo ariza shablonlari (Word)", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(0, 4))
        ttk.Label(body, text="6 xil Davo ariza turidan birini tanlab, uning shablonini yangilashingiz "
                              "mumkin. Yangilagach, shu turdagi, hali 'Olib kelindi' deb belgilanmagan "
                              "arizalarni yangi shablon bilan qayta tayyorlash so'raladi.",
                  style='Sub.TLabel', wraplength=800, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))
        davo_tpl_frame = ttk.Frame(body)
        davo_tpl_frame.pack(anchor='w', padx=20, pady=(0, 10))
        ttk.Label(davo_tpl_frame, text="Ariza turi:").pack(side='left')
        self.davo_turi_var = tk.StringVar(value=list(letters.DAVO_ARIZA_NOMLARI.values())[0])
        ttk.Combobox(davo_tpl_frame, textvariable=self.davo_turi_var,
                     values=list(letters.DAVO_ARIZA_NOMLARI.values()), state='readonly', width=44).pack(
            side='left', padx=8)
        davo_tpl_btns = ttk.Frame(body)
        davo_tpl_btns.pack(anchor='w', padx=20, pady=(0, 30))
        ttk.Button(davo_tpl_btns, text="📄 Joriy shablonni ochish", command=self.open_davo_template).pack(side='left')
        ttk.Button(davo_tpl_btns, text="📤 Yangi shablon yuklash (.docx)", style='Accent.TButton',
                   command=self.upload_davo_template).pack(side='left', padx=10)

    def _davo_turi_kaliti(self):
        label = self.davo_turi_var.get()
        for k, v in letters.DAVO_ARIZA_NOMLARI.items():
            if v == label:
                return k
        return list(letters.DAVO_ARIZA_NOMLARI.keys())[0]

    def open_davo_template(self):
        turi = self._davo_turi_kaliti()
        tpl_path = os.path.join(os.path.dirname(letters.TEMPLATE_PATH), letters.DAVO_ARIZA_TEMPLATES[turi])
        if os.path.exists(tpl_path):
            webbrowser.open(tpl_path)
        else:
            messagebox.showerror("Topilmadi", "Shablon fayli topilmadi.")

    def upload_davo_template(self):
        turi = self._davo_turi_kaliti()
        tpl_path = os.path.join(os.path.dirname(letters.TEMPLATE_PATH), letters.DAVO_ARIZA_TEMPLATES[turi])
        filepath = filedialog.askopenfilename(
            title=f"Yangi shablon faylini tanlang — {self.davo_turi_var.get()}",
            filetypes=[("Word hujjati", "*.docx")]
        )
        if not filepath:
            return
        try:
            import shutil
            os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
            if os.path.exists(tpl_path):
                backup = tpl_path + '.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.bak'
                shutil.copy2(tpl_path, backup)
            shutil.copy2(filepath, tpl_path)
        except Exception as e:
            messagebox.showerror("Xato", f"Shablonni saqlashda xato: {e}")
            return
        javob = messagebox.askyesno(
            "Qayta tayyorlash",
            f"Shablon yangilandi ({self.davo_turi_var.get()}).\n\n"
            "Shu turdagi, hali 'Olib kelindi' deb belgilanmagan Davo arizalarni "
            "hozir yangi shablon bilan qayta tayyorlaymi?"
        )
        if javob:
            self._regenerate_davo_pending(turi)

    def _regenerate_davo_pending(self, turi):
        pending = db.get_davo_ariza_pending_by_turi(turi)
        settings = db.get_all_settings()
        updated, errors = 0, []
        for xat in pending:
            try:
                prow = db.get_portfel_by_id(xat['portfel_id'])
                if not prow:
                    continue
                mijoz_turi, mijoz = util.resolve_mijoz(prow)
                taminot = db.get_taminot(xat['anketa_raqami'])
                try:
                    xat_sanasi = datetime.datetime.fromisoformat(xat['yaratilgan_sana']).strftime('%d.%m.%Y')
                except Exception:
                    xat_sanasi = ''
                letters.generate_davo_ariza_v2(
                    turi, xat['davo_ariza_fayl_yoli'], prow, mijoz, taminot, settings,
                    xat_sanasi=xat_sanasi,
                    xat_turi_nomi=('Талабнома' if xat['xat_turi'] == 'Talabnoma' else 'Огохлантириш хати'),
                )
                updated += 1
            except Exception as e:
                errors.append(f"{xat.get('anketa_raqami')}: {e}")
        msg = f"{updated} ta Davo ariza yangi shablon bilan qayta tayyorlandi."
        if errors:
            msg += f"\n\n{len(errors)} ta xatoda:\n" + '\n'.join(errors[:5])
        messagebox.showinfo("Tayyor", msg)

    # ---- Sug'urta xabarnomasi shabloni ----
    def _build_sugurta_shablon_section(self, body):
        sep3 = ttk.Frame(body, height=2)
        sep3.pack(fill='x', padx=20, pady=(4, 14))
        ttk.Label(body, text="Sug'urta xabarnomasi shabloni (Word)", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(0, 4))
        ttk.Label(body, text="Vafot etgan mijozlar bo'yicha sug'urta kompaniyasiga yuboriladigan "
                              "xabarnoma shablonini shu yerdan yangilashingiz mumkin.",
                  style='Sub.TLabel', wraplength=800, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))
        sugurta_tpl_btns = ttk.Frame(body)
        sugurta_tpl_btns.pack(anchor='w', padx=20, pady=(0, 30))
        ttk.Button(sugurta_tpl_btns, text="📄 Joriy shablonni ochish", command=self.open_sugurta_template).pack(side='left')
        ttk.Button(sugurta_tpl_btns, text="📤 Yangi shablon yuklash (.docx)", style='Accent.TButton',
                   command=self.upload_sugurta_template).pack(side='left', padx=10)

    def open_sugurta_template(self):
        if os.path.exists(letters.SUGURTA_XABARNOMA_TEMPLATE_PATH):
            webbrowser.open(letters.SUGURTA_XABARNOMA_TEMPLATE_PATH)
        else:
            messagebox.showerror("Topilmadi", "Shablon fayli topilmadi.")

    def upload_sugurta_template(self):
        filepath = filedialog.askopenfilename(
            title="Yangi sug'urta xabarnomasi shablonini tanlang", filetypes=[("Word hujjati", "*.docx")]
        )
        if not filepath:
            return
        tpl_path = letters.SUGURTA_XABARNOMA_TEMPLATE_PATH
        try:
            import shutil
            os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
            if os.path.exists(tpl_path):
                backup = tpl_path + '.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.bak'
                shutil.copy2(tpl_path, backup)
            shutil.copy2(filepath, tpl_path)
        except Exception as e:
            messagebox.showerror("Xato", f"Shablonni saqlashda xato: {e}")
            return
        messagebox.showinfo(
            "Saqlandi",
            "Sug'urta xabarnomasi shabloni yangilandi.\n\n"
            "Shablonda quyidagi {{PLACEHOLDER}}lardan foydalanish mumkin:\n"
            "{{BANK_NOMI}}, {{FILIAL_NOMI}}, {{RAHBAR_ISM}}, {{MIJOZ_ISM}}, {{MIJOZ_PINFL}}, "
            "{{ANKETA_RAQAM}}, {{SHARTNOMA_SANA}}, {{KREDIT_SUMMA}}, {{KREDIT_TUGASH_SANASI}}, "
            "{{JAMI_QARZ}}, {{VAFOT_SANASI}}, {{SUGURTA_KOMPANIYA}}, {{SUGURTA_POLIS_RAQAM}}, "
            "{{XABARNOMA_SANA}}."
        )

    # ---- Yig'ma jild tituli shabloni ----
    def _build_yigma_jild_shablon_section(self, body):
        sep4 = ttk.Frame(body, height=2)
        sep4.pack(fill='x', padx=20, pady=(4, 14))
        ttk.Label(body, text="Yig'ma jild tituli shabloni (Word)", style='Header.TLabel').pack(
            anchor='w', padx=20, pady=(0, 4))
        ttk.Label(body, text="MIBga o'tkazish tasdiqlanganda avtomatik yaratiladigan yig'ma jild "
                              "muqova (titul) hujjati shablonini shu yerdan yangilashingiz mumkin.",
                  style='Sub.TLabel', wraplength=800, justify='left').pack(
            anchor='w', padx=20, pady=(0, 10))
        yj_tpl_btns = ttk.Frame(body)
        yj_tpl_btns.pack(anchor='w', padx=20, pady=(0, 30))
        ttk.Button(yj_tpl_btns, text="📄 Joriy shablonni ochish", command=self.open_yigma_jild_template).pack(side='left')
        ttk.Button(yj_tpl_btns, text="📤 Yangi shablon yuklash (.docx)", style='Accent.TButton',
                   command=self.upload_yigma_jild_template).pack(side='left', padx=10)

    def open_yigma_jild_template(self):
        if os.path.exists(letters.YIGMA_JILD_TITUL_TEMPLATE_PATH):
            webbrowser.open(letters.YIGMA_JILD_TITUL_TEMPLATE_PATH)
        else:
            messagebox.showerror("Topilmadi", "Shablon fayli topilmadi.")

    def upload_yigma_jild_template(self):
        filepath = filedialog.askopenfilename(
            title="Yangi yig'ma jild tituli shablonini tanlang", filetypes=[("Word hujjati", "*.docx")]
        )
        if not filepath:
            return
        tpl_path = letters.YIGMA_JILD_TITUL_TEMPLATE_PATH
        try:
            import shutil
            os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
            if os.path.exists(tpl_path):
                backup = tpl_path + '.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.bak'
                shutil.copy2(tpl_path, backup)
            shutil.copy2(filepath, tpl_path)
        except Exception as e:
            messagebox.showerror("Xato", f"Shablonni saqlashda xato: {e}")
            return
        messagebox.showinfo(
            "Saqlandi",
            "Yig'ma jild tituli shabloni yangilandi.\n\n"
            "Shablonda quyidagi {{PLACEHOLDER}}lardan foydalanish mumkin:\n"
            "{{BANK_NOMI}}, {{FILIAL_NOMI}}, {{MIB_ISH_RAQAMI}}, {{QARZDOR_ISM}}, {{MIJOZ_TURI}}, "
            "{{MIJOZ_MANZIL}}, {{HUJJAT_RAQAMI}}, {{ANKETA_RAQAM}}, {{JAMI_QARZ}}, {{XAT_SANASI}}, "
            "{{XAT_YUBORILGAN_SANA}}, {{DAVO_ARIZA_SANA}}, {{PALATADAN_QAYTGAN_SANA}}, "
            "{{SUDGA_TOPSHIRILGAN_SANA}}, {{SUD_ISH_RAQAMI}}, {{MIB_OTKAZILGAN_SANA}}, "
            "{{JILD_OCHILGAN_SANA}}."
        )


# ---- Har bir modul uchun sozlama maydonlari guruhlari ----
TALABNOMA_SOZLAMA_FIELDS = [
    ('bank_nomi', 'Bank nomi (to‘liq)'),
    ('bank_qisqa_nomi', 'Bank nomi (qisqa)'),
    ('bank_manzil', 'Bank manzili'),
    ('bank_email', 'Bank email'),
    ('bank_sayt', 'Bank sayti'),
    ('bank_tel', 'Bank markaziy tel'),
    ('bank_mobil_ilova', 'Mobil ilova nomi'),
    ('bank_kodi', 'Bank kodi'),
    ('aloqa_markazi_tel', 'Aloqa markazi tel'),
    ('filial_nomi', 'Filial nomi'),
    ('filial_tel', 'Filial telefon'),
    ('rahbar_ism', 'Filial rahbari F.I.Sh (standart)'),
    ('tolov_muddati_kun', "To'lov uchun beriladigan muddat (bank ish kuni)"),
    ('eslatma_muddati_kun', "Xat yuborish uchun ichki muddat (kun)"),
    ('dpd_chegara_kun', "Tahlil uchun DPD chegarasi (kun)"),
    ('chora_ogohlantirish_dpd_kun', "Chora ko'rish: xat yuborish uchun DPD chegarasi (kun)"),
    ('chora_ogohlantirish_oy', "Chora ko'rish: xat 'yangi' hisoblanadigan muddat (oy)"),
    ('chora_davo_ariza_dpd_kun', "Chora ko'rish: Davo ariza uchun DPD chegarasi (kun)"),
    ('chora_davo_ariza_oy', "Chora ko'rish: xat 'yangi' hisoblanadigan muddat, Davo ariza uchun (oy)"),
]

DAVO_ARIZA_SOZLAMA_FIELDS = [
    ('davo_ariza_muddati_kun', "Xat yuborilgandan keyin Davo ariza tayyorlash muddati (kun)"),
    ('sud_topshirish_muddati_kun', "Palatadan qaytgandan keyin sudga topshirish muddati (kun)"),
    ('viloyat_nomi', 'Viloyat nomi (davo ariza uchun)'),
    ('sud_fuqarolik_nomi', 'Fuqarolik sudi nomi (jismoniy shaxslar uchun)'),
    ('sud_iqtisodiy_nomi', 'Iqtisodiy sudi nomi (yuridik shaxslar uchun)'),
    ('palata_nomi', 'Savdo-Sanoat Palatasi bo\'limi nomi'),
    ('bank_stir', 'Bank STIR'),
    ('bank_hisob_raqami_filial', 'Bank hisob raqami (filial)'),
    ('bank_kodi_filial', 'Bank kodi (filial)'),
    ('bank_hisob_raqami_bosh', 'Bank hisob raqami (bosh ofis)'),
    ('bank_kodi_bosh', 'Bank kodi (bosh ofis)'),
    ('bank_rasmiy_manzil_filial', "Bank rasmiy manzili (filial, sud hujjatlari uchun)"),
    ('pochta_xarajati_standart', "Standart pochta xarajati (so'm)"),
    ('sud_ariza_imzo_ism', 'Davo ariza imzolovchisi F.I.Sh'),
    ('sud_ariza_imzo_lavozimi', 'Davo ariza imzolovchisi lavozimi'),
]

MIB_SOZLAMA_FIELDS = [
    ('mib_harakatsizlik_muddati_kun', "MIBda harakatsizlik ogohlantirish muddati (kun)"),
    ('bxm_miqdori', "BXM (bazaviy hisoblash miqdori), so'm"),
    ('mib_toxtatish_dpd_chegara', "MIB to'xtatish uchun DPD chegarasi (kun)"),
]

VAFOT_SOZLAMA_FIELDS = [
    ('sugurta_javob_muddati_ish_kun', "Sug'urta javobini kutish muddati (ish kuni)"),
]


def main():
    os.makedirs(XATLAR_DIR, exist_ok=True)
    db.init_db()
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
