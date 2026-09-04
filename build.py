#!/usr/bin/env python3
"""Builds misket.app in Turkish and English.

Output layout (language-neutral paths are redirected by nginx to the
visitor's language, so App Store links like /etut/privacy keep working):

    /tr/…  Turkish pages
    /en/…  English pages
    /style.css

Run: python3 build.py
"""
import hashlib
import os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT

LANGS = ("tr", "en")

# Cloudflare caches static assets for hours, so the stylesheet link
# carries a hash of its own contents: edit the CSS, get a new URL.
STYLE_VERSION = hashlib.md5(
    open(os.path.join(ROOT, "style.css"), "rb").read()
).hexdigest()[:8]

# Same trick for the icons: one version stamp over all of them, so a
# re-exported icon can never be served from a stale edge cache.
def _icon_version():
    h = hashlib.md5()
    d = os.path.join(ROOT, "icons")
    for name in sorted(os.listdir(d)):
        h.update(name.encode())
        h.update(open(os.path.join(d, name), "rb").read())
    return h.hexdigest()[:8]

ICON_VERSION = _icon_version()

# ---------------------------------------------------------------- content

UI = {
    "tr": {
        "apps": "Uygulamalar", "support": "Destek", "privacy": "Gizlilik",
        "home_title": "Misket",
        "home_h1": "Misket",
        "home_tagline": "",
        "home_desc": "Misket uygulamaları: Findle, Fence ve OpSix.",
        "principles": "Ortak ilkeler",
        "p1": "<strong>Cihazında kalır.</strong> Verilerin iPhone'undan çıkmaz; hesap ya da bulut gerekmez.",
        "p2": "<strong>Takip yok.</strong> Analitik, reklam kimliği ve üçüncü taraf izleyici kullanmıyoruz.",
        "p3": "<strong>Dürüst fiyat.</strong> Çoğu uygulama ücretsiz ya da tek seferlik ödemeli; sessizce ücretliye dönen deneme yok.",
        "contact": "İletişim",
        "contact_line": "Soru, öneri ya da hata bildirimi:",
        "badge_live": "App Store'da", "badge_soon": "Çok yakında",
        "features": "Özellikler",
        "privacy_short": "Gizlilik",
        "privacy_link": "gizlilik politikası →",
        "support_h": "Destek",
        "support_line": "Sorunun mu var? Şu adrese yaz — genelde aynı gün dönüyorum:",
        "footer_1": "Hesap yok, takip yok; her uygulamanın ne sakladığı kendi gizlilik sayfasında yazar.",
        "updated": "Son güncelleme: 16 Ağustos 2026",
        "privacy_short_version": "Kısa versiyon: {app} hiçbir veri toplamaz.",
        "where_data": "Verileriniz nerede durur?",
        "not_collected": "Toplamadıklarımız",
        "nc1": "Hesap, e-posta ya da telefon numarası istemiyoruz.",
        "nc2": "Analitik, çökme raporu ya da reklam kimliği toplamıyoruz.",
        "nc3": "Üçüncü taraf izleyici (SDK) kullanmıyoruz.",
        "nc4": "Sunucumuz yok; verileriniz gidecek bir yer yok.",
        "purchases": "Satın almalar",
        "purchases_body": 'Uygulama içi satın alma varsa Apple tarafından App Store üzerinden işlenir; ödeme bilgilerinizi görmeyiz. Ayrıntı için <a href="https://www.apple.com/legal/privacy/">Apple Gizlilik Politikası</a>.',
        "children": "Çocuklar",
        "children_body": "Hiç kimseden veri toplamadığımız için çocuklardan da veri toplamıyoruz.",
        "changes": "Değişiklikler",
        "changes_body": "Bu politika değişirse yeni sürüm bu sayfada, güncel tarihle yayımlanır.",
        "lang_other": "English",
    },
    "en": {
        "apps": "Apps", "support": "Support", "privacy": "Privacy",
        "home_title": "Misket",
        "home_h1": "Misket",
        "home_tagline": "",
        "home_desc": "Misket apps: Findle, Fence and OpSix.",
        "principles": "What they share",
        "p1": "<strong>Stays on your device.</strong> Your data never leaves your iPhone — no account, no cloud.",
        "p2": "<strong>No tracking.</strong> No analytics, no advertising identifiers, no third-party trackers.",
        "p3": "<strong>Honest pricing.</strong> Most apps are free or a single one-time purchase; no trial that quietly converts.",
        "contact": "Contact",
        "contact_line": "Questions, ideas or bug reports:",
        "badge_live": "On the App Store", "badge_soon": "Coming soon",
        "features": "Features",
        "privacy_short": "Privacy",
        "privacy_link": "privacy policy →",
        "support_h": "Support",
        "support_line": "Something wrong? Write to — usually answered the same day:",
        "footer_1": "No accounts, no tracking; what each app stores is spelled out on its own privacy page.",
        "updated": "Last updated: 16 August 2026",
        "privacy_short_version": "The short version: {app} collects no data.",
        "where_data": "Where your data lives",
        "not_collected": "What we don't collect",
        "nc1": "No account, email address or phone number.",
        "nc2": "No analytics, crash reporting or advertising identifiers.",
        "nc3": "No third-party tracking SDKs.",
        "nc4": "We have no server; there is nowhere for your data to go.",
        "purchases": "Purchases",
        "purchases_body": 'Any in-app purchase is handled by Apple through the App Store; we never see your payment details. See <a href="https://www.apple.com/legal/privacy/">Apple\'s Privacy Policy</a>.',
        "children": "Children",
        "children_body": "We collect no information from anyone, children included, because we collect none at all.",
        "changes": "Changes",
        "changes_body": "If this policy changes, the new version appears on this page with an updated date.",
        "lang_other": "Türkçe",
    },
}

# The home page shows only these, in this order.
HOME_SLUGS = ["findle", "fence", "opsix"]

# slug, name, emoji, gradient, status, {lang: (tagline, longdesc, [features], privacy)}
APPS = [
 ("etut", "Etüt", "🎯", "#f25c8a,#8a1e4f", "soon", {
   "tr": ("YKS çalışma takibi — planla, kronometreyi başlat, telefon sussun.",
     "Etüt; YKS'ye hazırlanırken plan yapmanı, çalıştığın süreyi ve konuları takip etmeni ve en önemlisi telefonun seni bölmemesini sağlar.",
     ["Telefon çiti: kronometre çalışırken seçtiğin uygulamalar kapanır",
      "Flip modu: telefonu ters çevir, kronometre çalışsın; kaldırınca mola",
      "TYT/AYT müfredatı gömülü konu takibi (ders → ünite → konu)",
      "Haftalık ve aylık plan, tarih bazlı tek seferlik planlar",
      "Deneme netleri, puan ve sıralama tahmini",
      "Günün karnesi: paylaşılabilir kart + veli/koç için PDF"],
     "Etüt, Apple'ın Ekran Süresi (Family Controls) altyapısını kullanır ve hangi uygulamaları engellediğini <strong>göremez</strong> — bu bilgi iOS'ta kalır. Planların, çalışma kayıtların ve deneme sonuçların yalnızca cihazında saklanır."),
   "en": ("Study tracking for exam prep — plan, start the timer, let the phone go quiet.",
     "Etüt helps you plan your study, track the time and topics you cover and — most importantly — keeps your phone from interrupting you.",
     ["Phone fence: chosen apps are blocked while the timer runs",
      "Flip mode: turn the phone face-down to run the timer, pick it up for a break",
      "Built-in curriculum tracking (subject → unit → topic)",
      "Weekly and monthly plans, plus one-off dated plans",
      "Mock-exam results with score and rank estimates",
      "Daily report card: a shareable card and a PDF for parents or coaches"],
     "Etüt uses Apple's Screen Time (Family Controls) framework and <strong>cannot see</strong> which apps you block — that stays inside iOS. Your plans, study records and exam results are stored only on your device."),
 }),
 ("fence", "Fence", "🚧", "#2e7cd6,#14335f", "soon", {
   "tr": ("Dikkat dağıtan uygulamaları engelle. Bir kez öde.",
     "Fence, seçtiğin uygulamaları programa göre ya da odak seansları boyunca engeller — tek seferlik küçük bir ücretle, sonsuza dek.",
     ["Çitler: uygulama ve kategori seçimi, program ya da odak seansı",
      "Katılık seviyeleri: Nazik, Sıkı (günde üç izin), Kilitli",
      "Günlük süre bütçesi: 30 dakika sonra çit kendiliğinden çekilir",
      "Kilitli modda uygulama silme devre dışı",
      "Acil çıkış: günde bir kez, 60 saniye bekleme ve gerekçeyle",
      "Dürüst istatistik: kaç kez çite takıldın, kaç kez geri döndün"],
     "Fence, Apple'ın Ekran Süresi altyapısını kullanır ve hangi uygulamaları engellediğini göremez. Sayaçlar yalnızca cihazında tutulur."),
   "en": ("Block distracting apps. Pay once.",
     "Fence blocks the apps you choose — on a schedule or during focus sessions — for one small one-time price, forever.",
     ["Fences: pick apps and categories, on a schedule or for focus sessions",
      "Strictness levels: Gentle, Strict (three passes a day), Locked",
      "Daily time budget: after 30 minutes the fence rises by itself",
      "App deletion disabled during Locked sessions",
      "Emergency unlock: once a day, after a 60-second wait and a written reason",
      "Honest stats: how often you hit the fence and how often you turned back"],
     "Fence uses Apple's Screen Time framework and cannot see which apps you block. Counters stay on your device."),
 }),
 ("sanita", "Sanita", "🫶", "#2e7cd6,#173f8a", "soon", {
   "tr": ("Ağrı günlüğü — doktora götürebileceğin PDF raporlarıyla.",
     "Kronik ağrıyı hafızadan anlatmak zordur. Sanita bunu kayda dönüştürür: üç dokunuşta ağrı girişi, örüntülerin ve doktorunun gerçekten kullanabileceği bir rapor.",
     ["Vücut haritasında üç dokunuşla ağrı kaydı",
      "Tetikleyici analizi: bir tetikleyiciyle ve onsuz ortalama şiddet",
      "İlaç etkisi: aldıktan sonra şiddet nasıl değişti",
      "Apple Health'ten uyku ve aktivite korelasyonu (opsiyonel, salt okunur)",
      "Hava basıncı korelasyonu (opsiyonel)",
      "Doktora hazır PDF rapor"],
     "Sağlık verilerin iPhone'undan hiç çıkmaz. Hesap, bulut ve analitik yoktur; Apple Health verisi yalnızca cihazda işlenir ve saklanmaz."),
   "en": ("A pain diary — with PDF reports you can hand to your doctor.",
     "Chronic pain is hard to describe from memory. Sanita turns it into a record: log pain in three taps, see your patterns and bring your doctor a report they can actually use.",
     ["Log pain in three taps on a body map",
      "Trigger analysis: average intensity with a trigger versus without it",
      "Medication effect: how intensity changed after you took something",
      "Sleep and activity correlation from Apple Health (optional, read-only)",
      "Barometric pressure correlation (optional)",
      "Doctor-ready PDF report"],
     "Your health data never leaves your iPhone. No account, no cloud, no analytics; Apple Health data is processed on device and never stored."),
 }),
 ("squish", "Squish", "🗜️", "#ff8f6b,#ff4a2c", "live", {
   "tr": ("HEIC'ten JPG'ye: dönüştür, boyutlandır, sıkıştır.",
     "iPhone fotoğraflarını herkesin açabileceği formata çeviren, boyutlandıran ve sıkıştıran basit araç. Hiçbir şey buluta yüklenmez.",
     ["HEIC → JPG/PNG dönüştürme", "Toplu işlem ve ZIP içe aktarma",
      "Boyutlandırma ve kalite ayarı", "Paylaşım sayfası eklentisi ve Kısayollar desteği",
      "12 dil desteği"],
     "Fotoğraflarınız cihazınızda işlenir; uygulama hiçbir ağ isteği yapmaz."),
   "en": ("HEIC to JPG: convert, resize, compress.",
     "A simple tool that converts iPhone photos into formats everyone can open, resizes and compresses them. Nothing is ever uploaded.",
     ["HEIC → JPG/PNG conversion", "Batch processing and ZIP import",
      "Resizing and quality control", "Share extension and Shortcuts support",
      "Available in 12 languages"],
     "Your photos are processed on device; the app makes no network requests."),
 }),
 ("matte", "Matte", "✂️", "#7c5cff,#2c1e6b", "soon", {
   "tr": ("Arka planı sil, şeffaf PNG ve çıkartma üret.",
     "Fotoğraftaki nesneyi arka planından ayıran, şeffaf PNG veya mesajlaşma çıkartması üreten, tamamen cihaz üstü çalışan araç.",
     ["Tek dokunuşla arka plan kaldırma (iOS 17 yerel API)",
      "Şeffaf PNG dışa aktarma", "Mesajlaşma çıkartması üretme", "Toplu işlem"],
     "Görüntüler cihazınızda işlenir; hiçbir şey yüklenmez."),
   "en": ("Remove the background, export transparent PNGs and stickers.",
     "Lifts the subject out of a photo and exports it as a transparent PNG or a messaging sticker — entirely on device.",
     ["One-tap background removal (native iOS 17 API)",
      "Transparent PNG export", "Messaging sticker creation", "Batch processing"],
     "Images are processed on your device; nothing is uploaded."),
 }),
 ("pare", "Pare", "🧹", "#1f9e6b,#0d6b4d", "soon", {
   "tr": ("Mükerrer fotoğrafları ve yer kaplayan videoları güvenle temizle.",
     "Benzer fotoğrafları, ekran görüntülerini ve büyük videoları bulup güvenle silmeni sağlayan temizlik aracı. Onayın olmadan hiçbir şey silinmez.",
     ["Benzer fotoğraf ve ekran görüntüsü tespiti",
      "Büyük videoları boyuta göre listeleme",
      "Silmeden önce her zaman onay", "Tamamen cihaz üstü tarama"],
     "Fotoğraf kitaplığınız yalnızca cihazınızda taranır; hiçbir görüntü yüklenmez ve onayınız olmadan silinmez."),
   "en": ("Clear out duplicate photos and space-hogging videos, safely.",
     "Finds similar photos, screenshots and large videos so you can delete them with confidence. Nothing is removed without your approval.",
     ["Similar-photo and screenshot detection",
      "Large videos listed by size",
      "Always asks before deleting", "Scanning happens entirely on device"],
     "Your photo library is scanned on device only; no image is uploaded and nothing is deleted without your confirmation."),
 }),
 ("archivo", "Archivo", "📄", "#4a6cf7,#1b2a6b", "soon", {
   "tr": ("Belge tara, PDF üret, aranabilir arşivde sakla.",
     "Belgeleri kameradan tarayan, fotoğraf ve metinlerden sıfırdan PDF üreten ve hepsini aranabilir tek bir arşivde tutan uygulama.",
     ["Kameradan belge tarama", "Fotoğraf ve metinden PDF üretme",
      "Aranabilir arşiv", "Tamamen cihaz üstü"],
     "Belgeleriniz cihazınızda kalır; bulut yükleme yoktur."),
   "en": ("Scan documents, build PDFs, keep them in a searchable archive.",
     "Scans documents with the camera, builds PDFs from photos and text, and keeps everything in one searchable archive.",
     ["Camera document scanning", "PDFs from photos and text",
      "Searchable archive", "Entirely on device"],
     "Your documents stay on your device; there is no cloud upload."),
 }),
 ("opsix", "OpSix", "🎯", "#f5a524,#8a5a00", "soon", {
   "tr": ("Günlük sayı bulmacası — 6 sayı, dört işlem, tek hedef.",
     "Bir Kelime Bir İşlem'in sayı turu: altı sayıyı dört işlemle hedefe ulaştır. Her gün herkese aynı bulmacalar.",
     ["Her gün 15 bulmaca (kolay/orta/zor)", "Game Center sıralaması",
      "Paylaşılabilir sonuç kartı", "Tamamen sunucusuz, çevrimdışı çalışır",
      "12 dil desteği"],
     "Oyun verileriniz cihazınızda tutulur. Sıralama için yalnızca Game Center kullanılır."),
   "en": ("A daily number puzzle — six numbers, four operations, one target.",
     "Reach the target using six numbers and the four basic operations. Everyone gets the same puzzles each day.",
     ["15 puzzles every day (easy/medium/hard)", "Game Center leaderboards",
      "Shareable result card", "Fully serverless, works offline",
      "Available in 12 languages"],
     "Your game data stays on device. Game Center is the only service used, and only for rankings."),
 }),
 ("civics", "Civics Test", "🇺🇸", "#3452b8,#1a2c6e", "soon", {
   "tr": ("ABD vatandaşlık mülakatı için resmi 128 soruluk civics testi hazırlığı.",
     "USCIS vatandaşlık mülakatının civics bölümüne hazırlık: 2025 testinin 128 resmi sorusu, 2008 testi (100 soru), İngilizce okuma-yazma kelime listeleri ve mülakat süreci kartları. Tüm cevaplar resmi USCIS kaynaklarından.",
     ["128 resmi 2025 sorusu, kabul edilen tüm cevaplarıyla, konu konu",
      "2008 testi modülü ve 65/20 muafiyet seti",
      "Gerçek formatta deneme testleri (20 soru, 12 doğru ile geçiş)",
      "Resmi İngilizce okuma/yazma kelimeleri ve dikte cümleleri",
      "Konu bazlı ilerleme takibi; içerik indikten sonra çevrimdışı çalışır"],
     "Civics Test hesap istemez. Reklam gösterir (Google AdMob) ve çalışma ilerlemeni anonim bir cihaz kimliğiyle sunucumuzla eşitler; ad, e-posta ya da kişisel bilgi toplanmaz."),
   "en": ("Prep for the U.S. naturalization interview with the official 128-question civics test.",
     "Study for the civics portion of the USCIS naturalization interview: all 128 official 2025 questions, the 2008 test (100 questions), the official English reading and writing vocabulary, and interview-process cards. Every answer is sourced from official USCIS material.",
     ["All 128 official 2025 questions with every acceptable answer, by topic",
      "2008 test module and the 65/20 exemption study set",
      "Practice tests in the real format (20 questions, pass with 12)",
      "Official English reading/writing vocabulary and dictation sentences",
      "Progress tracking by topic; works offline once content is downloaded"],
     "Civics Test needs no account. It shows ads (Google AdMob) and syncs your study progress to our server under an anonymous device identifier; no name, email or personal details are collected."),
 }),
 ("pastel", "Pastel", "🖍️", "#f9736a,#f2b134", "soon", {
   "tr": ("Çocuklar için sonsuz boyama kitabı — sadece iPad.",
     "Pastel, 2–8 yaş için bir boyama uygulaması. Sayfalar bitmez: her dokunuşta yeni bir bahçe, deniz, gökyüzü, orman ya da uzay resmi oluşur. Yaşa göre üç mod: dokun-doldur, çizgilerin dışına çıkmayan sihirli fırça ve serbest fırça. Reklam yok, abonelik yok, hesap yok.",
     ["Sonsuz sayfa: her seferinde cihazda üretilen yeni bir resim",
      "Yaş grubuna göre çizgi kalınlığı, nesne sayısı ve araçlar (Minik / Orta / Büyük)",
      "Dokun-doldur, taşırmadan boyayan sihirli fırça, serbest fırça ve silgi",
      "Apple Pencil ve parmakla; kalınlık basınca göre",
      "Ayarlar ve paylaşım ebeveyn kapısının arkasında",
      "Bitmiş resmi yazdır ya da paylaş (ebeveyn onayıyla)"],
     "Pastel hiçbir veri toplamaz. Resimler yalnızca iPad'de saklanır; hesap, sunucu, analitik ya da reklam yoktur."),
   "en": ("An endless coloring book for kids — iPad only.",
     "Pastel is a coloring app for ages 2–8. The pages never run out: every tap makes a new garden, sea, sky, forest or space picture. Three modes by age: tap to fill, a magic brush that stays inside the lines, and a free brush. No ads, no subscriptions, no accounts.",
     ["Endless pages: a new picture is generated on the device every time",
      "Line thickness, scene complexity and tools follow the age group (Little / Middle / Big)",
      "Tap to fill, a magic brush that cannot spill over the lines, free brush and eraser",
      "Apple Pencil and fingers; pressure changes the brush size",
      "Settings and sharing sit behind a parental gate",
      "Print or share the finished picture (with a grown-up's OK)"],
     "Pastel collects nothing. Pictures are stored only on the iPad; there is no account, server, analytics or advertising."),
 }),
 ("findle", "Findle", "🔎", "#2a6bfa,#5b2bd6", "soon", {
   "tr": ("Mac'te dosya adıyla anında arama — milyonlarca dosyada bile.",
     "Findle, Mac'indeki her dosya ve klasörün adını hafif bir dizinde tutar. ⌥ Boşluk ile açılan Spotlight benzeri panelde yazdıkça sonuçlar milisaniyeler içinde gelir; gizli dosyalar, sistem klasörleri ve dış diskler dahil.",
     ["⌥ Boşluk ile her uygulamanın üstünde açılan arama paneli",
      "Yazdıkça sonuç: milyonlarca dosyada bile onlarca milisaniye",
      "Joker karakter ve filtreler: serv*.json, ext:pdf, is:folder, size:>100mb, in:Downloads",
      "Uygulamalar en üstte; Return ile aç, ⌘Return ile Finder'da göster, ⌘Y ile Quick Look",
      "Diskler arka planda izlenir, dizin hep güncel kalır",
      "Hangi disklerin dahil olacağını ve hangi klasörlerin atlanacağını sen seçersin"],
     "Findle yalnızca dosya adlarını, boyutlarını ve tarihlerini okur; dosya içeriklerini hiç açmaz. Dizin yalnızca Mac'inde saklanır; ağ erişimi, hesap ve analitik yoktur."),
   "en": ("Find any file on your Mac by name, instantly — even among millions.",
     "Findle keeps a lightweight index of every file and folder name on your Mac. Press ⌥ Space, start typing, and results appear in milliseconds in a Spotlight-style panel — hidden files, system folders and external disks included.",
     ["A search panel that opens over any app with ⌥ Space",
      "Results as you type: tens of milliseconds even with millions of files",
      "Wildcards and filters: serv*.json, ext:pdf, is:folder, size:>100mb, in:Downloads",
      "Apps first; Return to open, ⌘Return to reveal in Finder, ⌘Y for Quick Look",
      "Disks are watched in the background so the index stays current",
      "You choose which disks to include and which folders to skip"],
     "Findle reads only file names, sizes and dates; it never opens file contents. The index is stored only on your Mac; there is no network access, no account and no analytics."),
 }),
]

# Apps that use a server or ads get their own privacy text instead of the
# "collects nothing" template. {lang: html body}
CUSTOM_PRIVACY = {
  "civics": {
    "en": """<p><strong>The short version: Civics Test has no accounts and never asks who you are. It shows ads through Google AdMob and syncs your study progress to our server under an anonymous device identifier.</strong></p>

<h2>What the app stores</h2>
<p>Your practice-test results, flashcard progress and favourites are saved on your device. To keep your progress if you reinstall or switch devices, the same results are also sent to our server together with a random identifier generated by iOS for this app (<em>identifierForVendor</em>). That identifier is not tied to your name, Apple Account, email address or phone number, and it resets if you delete the app.</p>
<p>Question content is downloaded from our server so it can be updated without an app update. We do not log which questions you read.</p>

<h2>Advertising</h2>
<p>The free version shows ads served by <strong>Google AdMob</strong>. AdMob may collect device information and, if you allow tracking when iOS asks, the advertising identifier (IDFA) to personalise ads. You can decline at that prompt or change your choice any time in Settings → Privacy &amp; Security → Tracking; ads then remain non-personalised. See <a href="https://policies.google.com/technologies/partner-sites">how Google uses data from partner apps</a>. Premium removes ads.</p>

<h2>Feedback</h2>
<p>If you send feedback from within the app, the message you write is delivered to us together with the app version and the same anonymous device identifier so we can reply to follow-up bug reports. No email address is required.</p>

<h2>What we don't collect</h2>
<ul><li>No account, name, email address or phone number.</li><li>No location, contacts, photos or microphone access.</li><li>No third-party analytics SDKs other than the AdMob advertising SDK described above.</li></ul>

<h2>Purchases</h2>
<p>Premium subscriptions are handled by Apple through the App Store; we never see your payment details. See <a href="https://www.apple.com/legal/privacy/">Apple's Privacy Policy</a>.</p>

<h2>Data deletion</h2>
<p>Deleting the app removes the local data and discards the device identifier, which leaves the synced results orphaned on our server. Write to us and we will delete them from the server as well.</p>

<h2>Children</h2>
<p>The app is intended for adults preparing for the naturalization interview. We do not knowingly collect information from children.</p>

<h2>Changes</h2>
<p>If this policy changes, the new version appears on this page with an updated date.</p>

<h2>Contact</h2>
<p><a href="mailto:hello@misket.app">hello@misket.app</a></p>""",
    "tr": """<p><strong>Kısa versiyon: Civics Test hesap açtırmaz, kim olduğunu sormaz. Google AdMob üzerinden reklam gösterir ve çalışma ilerlemeni anonim bir cihaz kimliğiyle sunucumuza eşitler.</strong></p>

<h2>Uygulamanın sakladıkları</h2>
<p>Deneme sonuçların, kart ilerlemen ve favorilerin cihazında saklanır. Uygulamayı yeniden yükler ya da cihaz değiştirirsen ilerlemen kaybolmasın diye aynı sonuçlar, iOS'un bu uygulama için ürettiği rastgele bir kimlikle (<em>identifierForVendor</em>) birlikte sunucumuza da gönderilir. Bu kimlik adınla, Apple hesabınla, e-postanla ya da telefon numaranla ilişkili değildir; uygulamayı silince sıfırlanır.</p>
<p>Soru içeriği, uygulama güncellemesi gerekmeden yenilenebilsin diye sunucumuzdan indirilir. Hangi soruları okuduğunu kaydetmiyoruz.</p>

<h2>Reklam</h2>
<p>Ücretsiz sürüm <strong>Google AdMob</strong> reklamları gösterir. AdMob cihaz bilgisi ve — iOS sorduğunda izin verirsen — reklamları kişiselleştirmek için reklam kimliğini (IDFA) toplayabilir. O soruda reddedebilir ya da tercihini Ayarlar → Gizlilik ve Güvenlik → İzleme'den her zaman değiştirebilirsin; reklamlar kişiselleştirilmeden gösterilmeye devam eder. Bkz. <a href="https://policies.google.com/technologies/partner-sites">Google'ın iş ortağı uygulamalardan gelen verileri nasıl kullandığı</a>. Premium reklamları kaldırır.</p>

<h2>Geri bildirim</h2>
<p>Uygulama içinden geri bildirim gönderirsen yazdığın mesaj, uygulama sürümü ve aynı anonim cihaz kimliğiyle birlikte bize ulaşır; böylece sonraki hata raporlarını eşleştirebiliriz. E-posta adresi zorunlu değildir.</p>

<h2>Toplamadıklarımız</h2>
<ul><li>Hesap, ad, e-posta ya da telefon numarası yok.</li><li>Konum, kişiler, fotoğraf ya da mikrofon erişimi yok.</li><li>Yukarıda anlatılan AdMob reklam SDK'sı dışında üçüncü taraf analitik SDK'sı yok.</li></ul>

<h2>Satın almalar</h2>
<p>Premium abonelikler Apple tarafından App Store üzerinden işlenir; ödeme bilgilerini görmeyiz. Bkz. <a href="https://www.apple.com/legal/privacy/">Apple Gizlilik Politikası</a>.</p>

<h2>Veri silme</h2>
<p>Uygulamayı silmek yerel verileri ve cihaz kimliğini kaldırır; sunucudaki eşitlenmiş sonuçlar sahipsiz kalır. Bize yazarsan onları sunucudan da sileriz.</p>

<h2>Çocuklar</h2>
<p>Uygulama vatandaşlık mülakatına hazırlanan yetişkinler içindir. Çocuklardan bilerek veri toplamıyoruz.</p>

<h2>Değişiklikler</h2>
<p>Bu politika değişirse yeni sürüm bu sayfada, güncel tarihle yayımlanır.</p>

<h2>İletişim</h2>
<p><a href="mailto:hello@misket.app">hello@misket.app</a></p>""",
  },
}

FAQ = {
    "tr": [
        ("Satın aldığım özelliği kaybettim, ne yapmalıyım?",
         "Uygulamanın Ayarlar bölümünde \"Satın alımı geri yükle\" düğmesi var. Aynı Apple hesabıyla giriş yaptığından emin ol; tek seferlik satın almalar kalıcıdır."),
        ("Verilerim yedekleniyor mu?",
         "Uygulamalar cihaz üstünde çalıştığı için verilerin iPhone yedeğine (iCloud Backup ya da bilgisayar yedeği) dahil olur. Telefon değiştirirken yedekten geri yükleme yaparsan verilerin gelir."),
        ("Uygulama engelleme neden izin istiyor?",
         "Etüt ve Fence, Apple'ın Ekran Süresi altyapısını kullanır. Bu izin olmadan iOS hiçbir uygulamanın engellenmesine izin vermez. İzni istediğin an Ayarlar → Ekran Süresi'nden geri alabilirsin."),
        ("Hata buldum ya da özellik önerim var",
         "Yaz gitsin — küçük stüdyo olmanın iyi tarafı, önerilerin gerçekten sıradaki güncellemeye girebilmesi."),
    ],
    "en": [
        ("I lost a feature I paid for — what now?",
         "Every app has a \"Restore purchase\" button in Settings. Make sure you're signed in with the same Apple Account; one-time purchases are permanent."),
        ("Are my data backed up?",
         "Because the apps run on device, your data is included in your iPhone backup (iCloud Backup or a computer backup). Restoring a backup on a new phone brings everything along."),
        ("Why does app blocking ask for permission?",
         "Etüt and Fence use Apple's Screen Time framework. Without that permission iOS won't let any app block another. You can revoke it any time in Settings → Screen Time."),
        ("I found a bug or have a feature idea",
         "Send it over — the upside of a one-person studio is that suggestions can genuinely land in the next update."),
    ],
}

# ---------------------------------------------------------------- rendering

def nav(lang, path_in_lang):
    t = UI[lang]
    other = "en" if lang == "tr" else "tr"
    return f'''<div class="nav">
  <a class="brand" href="/{lang}/"><span class="dot"></span> Misket</a>
  <span class="spacer"></span>
  <span class="links">
    <a href="/{lang}/#apps">{t["apps"]}</a>
    <a href="/{lang}/support/">{t["support"]}</a>
    <a href="/{lang}/privacy/">{t["privacy"]}</a>
    <a href="/{other}/{path_in_lang}">{t["lang_other"]}</a>
  </span>
</div>'''


def footer(lang):
    t = UI[lang]
    return f'''<footer>
  <p>{t["footer_1"]}</p>
  <p><a href="mailto:hello@misket.app">hello@misket.app</a> · <a href="/{lang}/privacy/">{t["privacy"]}</a> · <a href="/{lang}/support/">{t["support"]}</a> · © 2026 Misket</p>
</footer>'''


def page(lang, path_in_lang, title, description, body):
    """path_in_lang: '' for the language home, 'etut/' etc. otherwise."""
    canonical = f"/{lang}/{path_in_lang}"
    alt = "".join(
        f'<link rel="alternate" hreflang="{l}" href="https://misket.app/{l}/{path_in_lang}">\n'
        for l in LANGS
    )
    html = f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://misket.app{canonical}">
{alt}<link rel="alternate" hreflang="x-default" href="https://misket.app/en/{path_in_lang}">
<link rel="stylesheet" href="/style.css?v={STYLE_VERSION}">
</head>
<body>
<div class="wrap">
{nav(lang, path_in_lang)}
{body}
{footer(lang)}
</div>
</body>
</html>
'''
    full = os.path.join(OUT, lang, path_in_lang, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)


def build_lang(lang):
    t = UI[lang]

    # Home: only the apps we want front and center right now.
    # Every other app keeps its inner page and stays reachable by direct link.
    home_apps = [a for h in HOME_SLUGS for a in APPS if a[0] == h]
    cards = []
    for slug, name, emoji, grad, status, texts in home_apps:
        g1, g2 = grad.split(",")
        tagline = texts[lang][0]
        badge_class, badge_text = ("live", t["badge_live"]) if status == "live" else ("soon", t["badge_soon"])
        cards.append(f'''  <a class="app" href="/{lang}/{slug}/">
    <img class="icon" src="/icons/{slug}.png?v={ICON_VERSION}" alt="{name}" width="60" height="60" loading="lazy">
    <div class="name">{name} <span class="badge {badge_class}">{badge_text}</span></div>
    <div class="desc">{tagline}</div>
  </a>''')

    shelf = "".join(
        f'<a href="/{lang}/{s}/"><img src="/icons/{s}.png?v={ICON_VERSION}" alt="{n}" width="52" height="52" loading="lazy"></a>'
        for s, n, *_ in home_apps
    )
    hero_tagline = f'\n  <p class="tagline">{t["home_tagline"]}</p>' if t["home_tagline"] else ""
    home_body = f'''<header class="hero">
  <h1>{t["home_h1"]}</h1>{hero_tagline}
  <div class="shelf">{shelf}</div>
</header>''' + f'''

<h2 id="apps">{t["apps"]}</h2>
<div class="grid">
{chr(10).join(cards)}
</div>

<div class="card">
  <h3 style="margin-top:0">{t["principles"]}</h3>
  <ul><li>{t["p1"]}</li><li>{t["p2"]}</li><li>{t["p3"]}</li></ul>
</div>

<h2>{t["contact"]}</h2>
<p class="small">{t["contact_line"]} <a href="mailto:hello@misket.app">hello@misket.app</a></p>'''
    page(lang, "", t["home_title"], t.get("home_desc") or t["home_tagline"], home_body)

    # App pages + privacy
    for slug, name, emoji, grad, status, texts in APPS:
        g1, g2 = grad.split(",")
        tagline, longdesc, features, privacy = texts[lang]
        badge_class, badge_text = ("live", t["badge_live"]) if status == "live" else ("soon", t["badge_soon"])
        feats = "\n".join(f"  <li>{f}</li>" for f in features)
        body = f'''<header class="app-head">
  <img src="/icons/{slug}.png?v={ICON_VERSION}" alt="{name}" width="92" height="92">
  <div>
    <h1>{name}</h1>
    <p class="tagline">{tagline}</p>
    <div class="meta"><span class="badge {badge_class}">{badge_text}</span></div>
  </div>
</header>

<p>{longdesc}</p>

<h2>{t["features"]}</h2>
<ul>
{feats}
</ul>

<div class="card">
  <h3 style="margin-top:0">{t["privacy_short"]}</h3>
  <p class="small">{privacy}</p>
  <p class="small"><a href="/{lang}/{slug}/privacy/">{name} {t["privacy_link"]}</a></p>
</div>

<h2>{t["support_h"]}</h2>
<p class="small">{t["support_line"]} <a href="mailto:hello@misket.app?subject={name}">hello@misket.app</a></p>'''
        page(lang, f"{slug}/", f"{name} — Misket", tagline, body)

        priv_head = f'''<header class="hero">
  <h1>{name} — {t["privacy"]}</h1>
  <p class="small">{t["updated"]}</p>
</header>
'''
        if slug in CUSTOM_PRIVACY:
            page(lang, f"{slug}/privacy/", f"{name} — {t['privacy']} — Misket",
                 privacy, priv_head + CUSTOM_PRIVACY[slug][lang])
            continue

        priv_body = priv_head + f'''
<p><strong>{t["privacy_short_version"].format(app=name)}</strong></p>

<h2>{t["where_data"]}</h2>
<p>{privacy}</p>

<h2>{t["not_collected"]}</h2>
<ul><li>{t["nc1"]}</li><li>{t["nc2"]}</li><li>{t["nc3"]}</li><li>{t["nc4"]}</li></ul>

<h2>{t["purchases"]}</h2>
<p>{t["purchases_body"]}</p>

<h2>{t["children"]}</h2>
<p>{t["children_body"]}</p>

<h2>{t["changes"]}</h2>
<p>{t["changes_body"]}</p>

<h2>{t["contact"]}</h2>
<p><a href="mailto:hello@misket.app">hello@misket.app</a></p>'''
        page(lang, f"{slug}/privacy/", f"{name} — {t['privacy']} — Misket",
             t["privacy_short_version"].format(app=name), priv_body)

    # Shared privacy hub
    links = "\n".join(
        f'    <li><a href="/{lang}/{slug}/privacy/">{name}</a></li>'
        for slug, name, *_ in APPS
    )
    hub_intro = ("Misket çatısı altındaki uygulamaların tamamı cihaz üstünde çalışır. Hiçbirinde hesap sistemi, sunucu ya da analitik yoktur. Uygulamaların topladığı veri miktarı sıfırdır."
                 if lang == "tr" else
                 "Every app under the Misket umbrella runs on device. None of them has an account system, a server or analytics. The amount of data they collect is zero.")
    apple_h = "Apple servisleri" if lang == "tr" else "Apple services"
    apple_b = ("Bazı uygulamalar Apple'ın kendi servislerini kullanır: satın almalar için StoreKit, sıralamalar için Game Center, hava verisi için WeatherKit, uygulama engelleme için Ekran Süresi. Bu servislerin işlediği veriler Apple'ın gizlilik politikasına tabidir ve bize aktarılmaz."
               if lang == "tr" else
               "Some apps use Apple's own services: StoreKit for purchases, Game Center for leaderboards, WeatherKit for weather data and Screen Time for app blocking. Data handled by those services falls under Apple's privacy policy and is never passed to us.")
    policies_h = "Uygulama gizlilik politikaları" if lang == "tr" else "Per-app privacy policies"
    page(lang, "privacy/", f"{t['privacy']} — Misket", hub_intro, f'''<header class="hero">
  <h1>{t["privacy"]}</h1>
  <p class="tagline">{"Hepsi aynı ilkeyle yazıldı: verin sende kalır." if lang == "tr" else "All built on one principle: your data stays yours."}</p>
</header>

<p>{hub_intro}</p>

<div class="card">
  <h3 style="margin-top:0">{policies_h}</h3>
  <ul>
{links}
  </ul>
</div>

<h2>{apple_h}</h2>
<p>{apple_b}</p>

<h2>{t["contact"]}</h2>
<p class="small"><a href="mailto:hello@misket.app">hello@misket.app</a></p>''')

    # Support
    faq = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in FAQ[lang])
    studio = ("Tek kişilik bir stüdyo; yazdığın maili doğrudan ben okuyorum."
              if lang == "tr" else
              "A one-person studio — your email comes straight to me.")
    hint = ("Hangi uygulama, hangi iPhone modeli ve iOS sürümü olduğunu yazarsan çok daha hızlı çözerim. Ekran görüntüsü de işe yarar."
            if lang == "tr" else
            "Tell me which app, which iPhone and which iOS version and I can fix it much faster. A screenshot helps too.")
    faq_h = "Sık sorulanlar" if lang == "tr" else "Frequently asked"
    page(lang, "support/", f"{t['support']} — Misket", studio, f'''<header class="hero">
  <h1>{t["support"]}</h1>
  <p class="tagline">{studio}</p>
</header>

<div class="card">
  <h3 style="margin-top:0">{t["contact"]}</h3>
  <p><a href="mailto:hello@misket.app">hello@misket.app</a></p>
  <p class="small">{hint}</p>
</div>

<h2>{faq_h}</h2>
{faq}''')


for lang in LANGS:
    shutil.rmtree(os.path.join(OUT, lang), ignore_errors=True)
    build_lang(lang)

count = sum(len(files) for _, _, files in os.walk(OUT) if files)
print(f"built {len(LANGS)} languages, {len(APPS)} apps")
