import flet as ft
import requests

def main(page: ft.Page):
    # Sayfa Ayarları
    page.title = "Kelime Bulucu (Mobil Sürüm)"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 750
    
    kelime_bankasi = []

    def kelimeleri_indir():
        url = "https://raw.githubusercontent.com/mertemin/turkish-word-list/master/words.txt"
        try:
            cevap = requests.get(url, timeout=10)
            cevap.raise_for_status()
            kelimeler = cevap.text.splitlines()
            return [k.strip().lower() for k in kelimeler if k.strip() and " " not in k]
        except Exception:
            return []

    # Mobil Uyumlu Arayüz Elemanları
    entry_uzunluk = ft.TextField(label="Kelime Uzunluğu (Boş=Hepsi)", value="5", keyboard_type=ft.KeyboardType.NUMBER)
    entry_baslangic = ft.TextField(label="Başlangıç Harfi")
    entry_yasakli = ft.TextField(label="Yasaklı Harfler (Bitişik yaz)")
    entry_icinde = ft.TextField(label="İçinde Kesin Olanlar (Örn: aa, e)")
    entry_tam_sayi = ft.TextField(label="Tam Adedi Bilinenler (Örn: a:1, e:2)")
    entry_bilinen = ft.TextField(label="Yeri Bilinenler (Örn: 3:m, 4:r)")
    
    # Flet'in yeni kurallarına göre renkler büyük harfle (ft.Colors) yazıldı
    label_durum = ft.Text("İnternetten sözlük indiriliyor, bekle...", color=ft.Colors.RED, weight=ft.FontWeight.BOLD)
    liste_sonuclar = ft.ListView(expand=True, spacing=10, padding=10)

    # Telefonda dokunarak kopyalama işlemi
    def kelime_kopyala(kelime):
        page.set_clipboard(kelime)
        label_durum.value = f"'{kelime}' başarıyla kopyalandı!"
        label_durum.color = ft.Colors.ORANGE
        page.update()

    def kelime_bul(e):
        if not kelime_bankasi:
            label_durum.value = "Kelime bankası boş! İnternetini kontrol et."
            label_durum.color = ft.Colors.RED
            page.update()
            return
            
        uzunluk_girdi = entry_uzunluk.value.strip()
        uzunluk = int(uzunluk_girdi) if uzunluk_girdi.isdigit() else None
        
        baslangic = entry_baslangic.value.lower().strip()
        yasakli_harfler = list(entry_yasakli.value.lower().replace(" ", ""))
        
        icinde_olanlar_metni = entry_icinde.value.lower().replace(" ", "")
        istenen_harf_sayilari = {}
        for harf in icinde_olanlar_metni:
            istenen_harf_sayilari[harf] = istenen_harf_sayilari.get(harf, 0) + 1
            
        tam_sayi_girdi = entry_tam_sayi.value.lower()
        tam_sayilar = {}
        if tam_sayi_girdi.strip():
            for parca in tam_sayi_girdi.split(','):
                if ':' in parca:
                    harf, adet = parca.split(':')
                    if adet.strip().isdigit():
                        tam_sayilar[harf.strip()] = int(adet.strip())
        
        bilinen_girdi = entry_bilinen.value.lower()
        bilinenler = {}
        if bilinen_girdi.strip():
            for parca in bilinen_girdi.split(','):
                if ':' in parca:
                    sira, harf = parca.split(':')
                    if sira.strip().isdigit():
                        bilinenler[int(sira.strip()) - 1] = harf.strip()
                    
        liste_sonuclar.controls.clear()
        
        bulunanlar = []
        for kelime in kelime_bankasi:
            if uzunluk is not None and len(kelime) != uzunluk: continue
            if baslangic and not kelime.startswith(baslangic): continue
            if any(harf in kelime for harf in yasakli_harfler): continue
                
            yeterli_mi = True
            for harf, adet in istenen_harf_sayilari.items():
                if kelime.count(harf) < adet:
                    yeterli_mi = False
                    break
            if not yeterli_mi: continue
                
            tam_adet_uygun = True
            for harf, adet in tam_sayilar.items():
                if kelime.count(harf) != adet:
                    tam_adet_uygun = False
                    break
            if not tam_adet_uygun: continue
                
            uygun_mu = True
            for index, harf in bilinenler.items():
                if index >= len(kelime) or kelime[index] != harf:
                    uygun_mu = False
                    break
            if not uygun_mu: continue
                
            bulunanlar.append(kelime)
            
        for k in bulunanlar:
            liste_sonuclar.controls.append(
                ft.ListTile(
                    title=ft.Text(k, size=18, weight=ft.FontWeight.BOLD),
                    # İkonlar da büyük harfle (ft.Icons) güncellendi
                    leading=ft.Icon(name=ft.Icons.CONTENT_COPY, color=ft.Colors.BLUE), 
                    on_click=lambda e, word=k: kelime_kopyala(word)
                )
            )
            
        label_durum.value = f"Durum: Kriterlere uyan {len(bulunanlar)} kelime bulundu."
        label_durum.color = ft.Colors.BLUE
        page.update()

    def sifirla(e):
        entry_uzunluk.value = "5"
        entry_baslangic.value = ""
        entry_yasakli.value = ""
        entry_icinde.value = ""
        entry_tam_sayi.value = ""
        entry_bilinen.value = ""
        liste_sonuclar.controls.clear()
        label_durum.value = f"Sıfırlandı! Toplam {len(kelime_bankasi)} kelime aramaya hazır."
        label_durum.color = ft.Colors.GREEN
        page.update()

    page.add(
        ft.Text("Kelime Bulucu Pro", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        entry_uzunluk,
        entry_baslangic,
        entry_yasakli,
        entry_icinde,
        entry_tam_sayi,
        entry_bilinen,
        ft.Row([
            ft.ElevatedButton("Kelimeleri Bul", on_click=kelime_bul, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, expand=True, height=50),
            ft.ElevatedButton("Sıfırla", on_click=sifirla, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, expand=True, height=50)
        ]),
        label_durum,
        ft.Divider(),
        liste_sonuclar
    )

    kelime_bankasi.extend(kelimeleri_indir())
    if kelime_bankasi:
        label_durum.value = f"Sözlük Hazır! ({len(kelime_bankasi)} kelime yüklendi)"
        label_durum.color = ft.Colors.GREEN
    else:
        label_durum.value = "Sözlük yüklenemedi! İnternet bağlantını kontrol et."
        label_durum.color = ft.Colors.RED
    page.update()

ft.app(target=main)
