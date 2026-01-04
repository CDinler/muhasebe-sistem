"""
PDF stream içeriğini decode eder ve analiz eder.
FlateDecode (zlib) sıkıştırmasını çözer.
"""

import zlib
import base64

# Kullanıcının verdiği stream (ilk birkaç byte: xœ = zlib imzası)
compressed_data = b"""x\xce\xb5\\\xdb#\xb9
}\xef\xaf\xd4\xea.\xe4!\xc8yL2?0\xed\xeeZ h#\xd8}\xd9\xdf)'"\x94RUKQ4f[\xed\xa2xDQ$EQ\xbe\xedE\x9e\x9f\xdf\xef\xbf\xbehw\x83\xfff\xe9\x9b\xdf\xe2\xf6\xfb\xfb\xcb\xf6\xf2\xaf\x97\xdf^\xbe\xf2\xed\xe5\x97\xbf\xcb\x9b_\xec\xed\xdb-\x9e\x9e\xfc\xe9\xf1\xed\xdb\xdb\x8bX\xcc_\xc7\x9f\x84\xfa\xcf\xdf\xbe\xfb\xf2\xb7o\x91X\xdc\x9f_\xec<\xd2\x85u1\xee\xa6\xdft\xe1!+\xa4\xf6\xd8\xcb*W\x89\xef^\xadk$D\xc6~\x95\x8b\x97\xb7\xc7\x8b2(\xa9\xf9M\xb3l\xabEh\xc3\xc3R7M[\x06.\xe0\x82xDj\x94\xdb\xf3\x9ej\xea\x8c<\xe8\x84<H\xebVx\xf7\xc1\xe8(\xcfk.UC\x89}\xc0|7\xd2m\x87\xb6 O\x93=\xd3a;\xda\xad \x9e\x83EG`\x9b\xd9\xfb8`\xdd\xed\xec\x9c\xb6\xach \xcfS\x88MT""" + \
b"""kk=\xf6S4\xe9\xab\xd4\xa1\xb6Gv\x9e\xe3\x87\xca\xae\xbe\xe1\xe8\xfc
\x9f\xf1]\xe2b\xc3\xb6^\xbe\xb7(x8\xb7\x80\x8c:*\xbd\xd4\xbb\xfa\xb4\x9f\xf9\xcd\xa6\xbf!?\xab\x84oC^\xad\x9eM\x98L Z\xbf\xdf(UZ>O\xfa4~\xd1\xea\xb8O\x9a\x9aXI \xaf\xe5oS8\xcb\xa1\xc3\xe3;\xf1`a:\xf8|\x87\xbe\x89\xb7\xa5\xb6|\x9b\x9fPn\xaby\xac \xc7O\xd4\t&
\xfb\x8c\xb1\x9b\xb1J\xbb\x80I9\xc6\xbeF\xc0n\xbe\x91\x9cQF\xd4w\x87\xdd\x83\xef\xc8u\xe9\xf3\xe6\xd2{"+\xb2M\xca\xcfp\xbf\xf1Y\xbe.$y\xf1\xf78\xb8\x9f9)O\xcc\x8b\xb0\x8b4\xb1\xb9W.)<*8\xe3\x96\x9f7\x89\xb1\xe3X\xb0\xbd\xd2\xe7W\xfan\xa5\xcfk\xdf\xb9\xd5-\xf2\xbark""" + \
b"""X\xb4\xcdV\x9c\x9a\xd9\xc8b\xdb\xabllbk\xc3\xbak\x99\xb4\xac\x0b\x9e\x9a\xf3\xbfTW[\xda\xfb<\xafvKhp;\xe8\xef\xdd0\xb7k\xddb\xd5\xbb\xdd5#=t=\x84\xed\xc1B#\xa4\xf5\xb4}<\xdfmFuv.[F4\xc6\xe7\xa9\x8bMQjk`=vs3\xe9\xa9\xc7\x91\xd7Qk\xf2r\x91c\xacC\xe2\xc7\xce\x89]X\x93\x91>)\xa7\xc0\xf4t\xf7\xc7\xcb/\xff|\xc8\xdb_\xffW8\xa9\x9b\xc4\xca\x99\xc5\xba8\xecµ³\x94
\x99?4h62Uv\xdd\x99tX\xd6\x96\xcd\x99\xe9\xa6?\xa8\xc5^MY^\xadL\x88\xea\xf9\xf3\xccO|\xc9\xbe_\xe5\\\x00\xb3F=O\x86\xc9$\xa3\x85\xceF\xa2T,9A\xdb\x91\xe3\xc5\x94L\xf7\xa7\xe7\xa2\xc1#\xa7\x9fD\xe7\xa9O[G\xe6u\xa7~^\xfbF9\x89<\x99\xedddd\xd1a\xdb \xa1\x83n|PQ\x96\xed\x9b`\xb1\x9e\xa4^X\xe5\xb08\xd3\xdd""" + \
b"""xD\x91\xc3\x80\x96µ3\xf3\xe80.\x9a\xe8^(\x98\x86\xa5\xe7Zc""" + \
b"""Lu\xd9\xca%8\xc6\xd7\xd92h)\xd8b\x83\xbfh\xfc\x96\xc3+-P;J\xa2\xf7\xf6GP`j)\x8b\x86@a\x8cEB\xfc\xe6\xf507\xef%D\xb1\xf6yps\xb0\xc1f\xc6\x93v?\x85\xb2U\xc7rO\xc3\xcf\xdbw\xb6G\x88\x94\x8b\xf3Y\xb1)x\xac³\x85\x84"""

# Continuation of compressed data (bu çok uzun, sadece başlangıç kısmını gösteriyoruz)
# Gerçek PDF'ten tüm stream'i almak lazım ama prensibi göstermek için yeterli

def decode_flate_stream(compressed_bytes):
    """FlateDecode (zlib) stream'ini çözer."""
    try:
        decompressed = zlib.decompress(compressed_bytes)
        return decompressed.decode('latin-1', errors='replace')
    except Exception as e:
        return f"Decode hatası: {e}"

# Decode et
decoded_content = decode_flate_stream(compressed_data)

print("=" * 80)
print("PDF STREAM İÇERİĞİ DECODE EDİLDİ")
print("=" * 80)
print("\nORJİNAL STREAM BİLGİLERİ:")
print("- Type: XObject (Form)")
print("- BBox: [0 0 595 842] → A4 sayfa boyutu (595x842 points)")
print("- Filter: FlateDecode (zlib sıkıştırma)")
print("- Length: 3682 bytes (sıkıştırılmış)")
print("- Resources: 2 Font (F1, F2) + 1 Image (Im1)")
print("\n" + "=" * 80)
print("DECODE EDİLMİŞ İÇERİK (PDF KOMUTLARI):")
print("=" * 80)
print(decoded_content[:2000])  # İlk 2000 karakter
print("\n... (devamı var)")
print("\n" + "=" * 80)
print("İÇERİK ANALİZİ:")
print("=" * 80)

# PDF komutlarını analiz et
if decoded_content:
    # Metin komutlarını bul
    text_commands = []
    lines = decoded_content.split('\n')
    for i, line in enumerate(lines):
        if 'Tj' in line or 'TJ' in line or 'Td' in line or 'Tm' in line:
            text_commands.append((i, line.strip()))
    
    print(f"\n📝 Toplam {len(text_commands)} adet metin komutu bulundu")
    print("\nİlk 10 metin komutu:")
    for idx, cmd in text_commands[:10]:
        print(f"  Satır {idx}: {cmd}")
    
    # Sayıları bul (fatura tutarları olabilir)
    import re
    numbers = re.findall(r'\d+[.,]\d+', decoded_content)
    if numbers:
        print(f"\n💰 Bulunan sayısal değerler (ilk 20):")
        for num in numbers[:20]:
            print(f"  {num}")

print("\n" + "=" * 80)
print("AÇIKLAMA:")
print("=" * 80)
print("""
Bu stream, PDF'in bir sayfasının veya formunun görsel içeriğini tanımlayan
PostScript/PDF komutlarını içerir. Decode edildikten sonra:

- 'BT' / 'ET': Metin bloğu başlangıç/bitiş
- 'Tm': Metin matrisi (pozisyon)
- 'Tf': Font seçimi
- 'Tj' / 'TJ': Metin göster
- 'l', 'm': Çizgi çizme komutları
- 'S', 'f': Stroke/fill komutları
- Sayısal değerler: Koordinatlar, font boyutları, tutarlar

E-fatura PDF'lerinde bu stream'ler içinde:
- Fatura numarası
- ETTN
- Tarihler  
- VKN/TCKN
- Tutarlar
- Firma isimleri

gibi bilgiler metin komutları (Tj/TJ) içinde bulunur.
""")
