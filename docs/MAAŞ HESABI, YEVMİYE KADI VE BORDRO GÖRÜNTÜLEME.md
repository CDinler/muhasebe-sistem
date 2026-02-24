# 'YEVMİYE KAYDI ÖNİZLEME' - Personel Adı Soyadı - Kimlik nosu

##'RESMİ KAYIT' 
Fiş no
bordro id
contract_id


transaction_date
accounting_period	
cost_center_name
description	text
document_type
document_subtype
document_number

Hesap Kodu	-	Açıklama	-	Borç	-	Alacak

##'TASLAK KAYIT'
fiş no
contract_id
bolum (monthly_personnel_records tablosu contract_id sütunu eşleşmesinden çekilen 'bolum' sütunu değeri)

transaction_date
accounting_period	
cost_center_name
description	text
document_type
document_subtype
document_number

Hesap Kodu	-	Açıklama	-	Borç	-	Alacak


notlar:
1- FİŞ NUMARASı, çakışma olmaması için kaydet esnasında üretilecek. bu sebeple transaction kaydet yapıldıktan sonra gösterilmesi lazım, ön izlemede fiş numarası göstermek hatalı sonuç verir.

2- TASLAK KAYIT VARSA GÖSTERİCEK YOKSA GÖSTERİLMEYECEK

----------------------------------------------------------------------------------------

#'MAAŞ HESABI ÖNİZLEME' - Personel Adı Soyadı - Kimlik nosu

## DÖNEM BİLGİSİ

Dönem	:donem	= seçil dönem
Yıl		:yil	= seçili dönem yılı
Ay		:ay		= seçil dönem ayı


## VERİTABANI BİLGİLERİ

ID_personnel					: SELECT personnel_id FROM luca_bordro WHERE id = ID_luca_bordro;
ID_luca_bordro					: contract_id personnel_id monthly_personnel_records_id
ID_personnel_contracts			: SELECT contract_id FROM luca_bordro WHERE id = ID_luca_bordro;
ID_monthly_personnel_records	: SELECT monthly_personnel_records_id FROM luca_bordro WHERE id = ID_luca_bordro;
ID_personnel_draft_contracts	: SELECT lb.personnel_id, pdc.id AS contract_id FROM ID_luca_bordro lb INNER JOIN personnel_draft_contracts pdc ON lb.personnel_id = pdc.personnel_id WHERE pdc.is_active = 1;
ID_personnel_puantaj_grid		: 




## PERSONEL BİLGİLERİ

Personel ID			:personnel_id				= table[personnel][id]
Personel Adı		:personnel_ad				= table[personnel][ad]
Personel Soyadı		:personnel_soyad			= table[personnel][soyad]
Personel Hesap ID	:personnel_acc_id			= table [personnel][accounts_id]
Personel Hesap Kodu	:personnel_acc_kod			= table [accounts][accounts_id]
Personel iban		:personnel_iban				= table [personnel][iban]

## LUCA BORDRO BİLGİLERİ

luca_bordro_id_list 		= list(LucaBordro.objects.filter(personnel_id=personnel_id, yil=PayrollCalculation.yil, ay=PayrollCalculation.yil).values_list('id', flat=True))

id 
personnel_id
contract_id
monthly_personnel_records_id
ssk_sicil_no
giris_t
cikis_t
t_gun
nor_kazanc
dig_kazanc
top_kazanc
ssk_m
g_v_m
ssk_isci
iss_p_isci
gel_ver
damga_v
ozel_kesinti
oto_kat_bes
icra
avans
n_odenen
isveren_maliyeti
ssk_isveren
iss_p_isveren
kanun
ssk_tesviki





## TASLAK SÖZLEŞME BİLGİLERİ

Sözleşme id			:pc_contracts_id		= table[personnel_draft_contracts][id]
Maliyet Merkezi		:pc_cc_id				= table[personnel_draft_contracts][cost_center_id]
Net Ücret		:pc_net_ucret			= table[personnel_draft_contracts][net_ucret]
Ücret Nevi			:pc_ucret_nevi			= table[personnel_contracts][ucret_nevi] 'enum (aylik, sabit aylik, gunluk)
Fazla Mesai Oranı	:pc_fm_orani			= table[personnel_contracts][fm_orani]
Tatil Mesai Oranı	:pc_tatil_orani			= table[personnel_contracts][tatil_orani]
Taşeron Bilgisi		:pc_taseron_id			= table[personnel_contracts][taseron_id]

## AY BİLGİLERİ

ayin_toplam_gun_sayisi	(G)
pc_ucret_nevi

## PUANTAJ BİLGİSİ

Eğer, personelin aktif bir personnel_draft_contracts ı varsa, yani tablodaki is_active değeri 1 ise,
şişlemler select box ına, 'Puantaj Bilgileri' seçeneğini ekleyelim. (bu sorgulamayı nasıl yaptığını bana açıkla.)

puantaj bilgileri modalında,
personelin ilgili dönemdeki personnel_puantaj_grid tablosundaki;

ayin_toplam_gun_sayisi	(G)
calisilan_gun_sayisi	(N)
yillik_izin_gun			(S)
izin_gun_sayisi			(İ)
rapor_gun_sayisi		(R)
yarim_gun_sayisi		(Y)
eksik_gun_sayisi		(E)
fazla_calismasi			(FM)
tatil_calismasi			(M)
sigorta_girmedigi		(DISABLE)
hafta_tatili			(H)
resmi_tatil				(T)		
normal_calismasi		(NC)
toplam_tatiller			(TT)=(H+T+M)
toplam_gun_sayisi		(TG)=(G-DISABLE)
ssk_gun_sayisi			(SG)=(TG-E)
yol						(YOL)
prim					(PRI)
ikramiye				(IKR)
bayram					(BAY)
kira					(KIR)

	normal_calismasi = (
    30 if (ucret_nevi == "aylik" and eksik_gun_sayisi == 0 and ayin_toplam_gun_sayisi != 30) else
    30 if (ucret_nevi == "sabit aylik" and sigorta_girmedigi == 0) else
    toplam_gun_sayisi if (ucret_nevi == "sabit aylik" and sigorta_girmedigi != 0) else
    calisilan_gun_sayisi + yarim_gun_sayisi  # Bu hem "gunluk" hem de diğer durumlar için
	)
	
	
normal_calismasi = (
    30 if ((ucret_nevi == "aylik" or "sabit aylik") and eksik_gun_sayisi == 0 and ayin_toplam_gun_sayisi != 30 and sigorta_girmedigi == 0) else
    calisilan_gun_sayisi + yarim_gun_sayisi  # Bu hem "gunluk" hem de diğer durumlar için
	)


ilgilerini gösterelim.

so


## MMAŞ HESABI

Şimdi işlemlerdeki maaş hesabı kısmın kaldıralım ve aşağıdaki gibi çalışacak şekilde yeniden ekleyelim.

Eğer, personelin aktif bir personnel_draft_contracts ı varsa, yani tablodaki is_active değeri 1 ise,
şişlemler select box ına, 'Maaş Hesabı' seçeneğini ekleyelim. (bu sorgulamayı nasıl yaptığını bana açıkla.)


Taslak Sözleşme id	:draft_contracts_id		= table[personnel_draft_contracts][id]
Maliyet Merkezi		:cc_id					= table[personnel_draft_contracts][cost_center_id]
Net Ücret			:net_ucret				= table[personnel_draft_contracts][net_ucret]
Ücret Nevi			:ucret_nevi				= table[personnel_draft_contracts][ucret_nevi] 'enum (aylik, sabit aylik, gunluk)
Fazla Mesai Oranı	:fm_orani				= table[personnel_draft_contracts][fm_orani]
Tatil Mesai Oranı	:tatil_orani			= table[personnel_draft_contracts][tatil_orani]


    const normal_calismasi = 
      ((ucret_nevi === 'aylik' || ucret_nevi === 'sabit aylik') && 
       eksik_gun_sayisi === 0 && ayin_toplam_gun_sayisi !== 30 && sigorta_girmedigi === 0) ? 30-tatiller :
      calisilan_gun_sayisi + yarim_gun_sayisi;



// Günlük kazanç
gunluk_ucret = (maas2_tutar / 30 if ucret_nevi in ['aylik', 'sabit aylik'] 
                   else maas2_tutar if ucret_nevi == 'gunluk' 
                   else 0)

// Normal kazanç
normal_kazanc = normal_calismasi × gunluk_ucret

// Mesai kazancı
mesai_kazanc = (fazla_calismasi × gunluk_ucret / 8) × fm_orani

// Tatil kazancı (H + T + M)
tatiller = hafta_tatili + resmi_tatil + tatil_calismasi
tatil_kazanc = tatiller × gunluk_ucret

// Tatil mesai kazancı (sadece M günleri için)
tatil_mesai_kazanc = tatil_calismasi × gunluk_ucret × tatil_orani

// Yıllık izin kazancı (sadece S günleri için)
yillik_izin_kazanc= gunluk_ucret * yillik_izin_gun

// TOPLAM
toplam_kazanc = normal_kazanc + mesai_kazanc + tatil_kazanc + tatil_mesai_kazanc +
                yol + prim + ikramiye + bayram + kira + yillik_izin_kazanc


## RESMİ KAYIT

bordro id
contract_id

Net Ödenen	: lc_n_odenen
Oto Kat Bes	: lc_oto_kat_bes
İcra		: lc_icra

## HAKEDİŞ

Toplam Net Ödenen
Toplam Bes
Toplam İcra

tr_gunluk_ucret
tr_normal_calisma_tutar	= tr_gunluk_ucret * normal_calismasi
tr_fazla_calisma_tutar	= tr_gunluk_ucret / 8 * fazla_calismasi * tr_fm_orani
tr_tatil_tutar			= tr_gunluk_ucret * (resmi_tatil + hafta_tatili + tatil_calismasi)
tr_tatil_calismasi_tutar= tr_gunluk_ucret * tatil_calismasi * tr_tatil_orani
tr_yillik_izin_gun_tutar= tr_gunluk_ucret * yillik_izin_gun












