# TABLOLAR

-------------------------------------------
#table [personnel]
-------------------------------------------

	1	id				----->	PRIMARY (AUTO_INCREMENT)
	2	tc_kimlik_no	----->	_POST ['tc_kimlik_no']
	3	ad				----->	_POST ['ad']
	4	soyad			----->	_POST ['soyad']
	5	accounts_id		----->	table[accounts][id]
	6	iban			----->	_POST ['iban']



-------------------------------------------
# table [personnel_contracts]
-------------------------------------------

	1	id								----->	PRIMARY (AUTO_INCREMENT)
	2	personnel_id					----->	table [personnel] [id]
	3	tc_kimlik_no					----->	table [personnel] [tc_kimlik_no]
	4	bolum							----->	table [monthly_personnel_records] dan güncellenecek
	5	monthly_personnel_records_id	----->	table [monthly_personnel_records] dan güncellenecek
	6	ise_giris_tarihi				----->	table [monthly_personnel_records] dan güncellenecek
	7	isten_cikis_tarihi				----->	table [monthly_personnel_records] dan güncellenecek
	8	ucret_nevi						----->	_POST ['ucret_nevi'] enum (aylik, sabit aylik, gunluk)
	9	kanun_tipi						----->	_POST ['kanun_tipi'] 
	10	calisma_takvimi					----->	_POST ['calisma_takvimi'] enum (atipi,btipi,ctipi)
	11	maas1_tip						----->	table [monthly_personnel_records] dan güncellenecek
	12	maas1_tutar						----->	table [monthly_personnel_records] dan güncellenecek
	13	maas2_tutar						----->	_POST ['maas2_tutar']
	14	maas_hesabi						----->	otomatik atanacak aşağıdaki gibi.
	15	iban							----->	table [personnel] [iban]
	16	fm_orani						----->	_POST ['fm_orani'] varsayılan 1
	17	tatil_orani						----->	_POST ['tatil_orani'] varsayılan 1
	18	taseron							----->	_POST ['taseron'] enum (1, 0) frontendde evet(1) yada hayır(0) diye seçim yapılacak. 
	19	taseron_id						----->	_POST ['taşeron_id'] eğer taseron 1 ise select boxtan carilerin içinden seçilecek cari idsi yazılacak
	20	departman						----->	_POST ['tipi] enum('Ankraj Ekibi','Asfaltlama Ekibi','Bekçi Ekibi','Beton Kesim Ekibi','Demirci Ekibi','Döşeme Ekibi','Elektrikçi Ekibi','Fore Kazık Ekibi','İdare Ekibi','Kalıpçı Ekibi','Kalıpçı Kolon Ekibi','Kaynakçı Ekibi','Merkez Ekibi','Operatör Ekibi','Saha Beton Ekibi','Stajyer Ekibi','Şöför Ekibi','Yıkım Ekibi')
	21	cost_center_id					----->	_POST [select table [cost_centers]]		
	22	is_active						----->	table [monthly_personnel_records] dan güncellenecek

	calisma_takvimi;
		atipi- PAZAR TATİL 08:00-17:00 (ucret_nevi, aylik ve maaş2 var ise varsayılan olarak bu seçili olacak; ucret_nevi, sabit aylik ise otomatik olarak bu seçili olacak)
		btipi- HER GÜN 08:00-17:00 (ucret_nevi, günlük ise otomatik olarak bu seçili olacak; ucret_nevi, aylik ve taseron 1 ise varsayılan olarak bu seçili olacak)
		ctipi- TAKVİM YOK (ucret_nevi, aylik ve maaş2 yok ise varsayılan olarak bu seçili olacak)
	```
	def calisma_takvimi_kisa(ucret_nevi, maas2_tutar=None, taseron=None):
	
    if ucret_nevi == 'sabit aylik':
        return 'atipi'
    
    if ucret_nevi == 'gunluk':
        return 'btipi'
    
    if ucret_nevi == 'aylik':
        if maas2_tutar:
            return 'atipi'
        elif taseron == 1:
            return 'btipi'
        else:
            return 'ctipi'
    
    return 'ctipi'  # Diğer durumlar için
	
	
	
	maas_hesabi = (
    'tipa' if (ucret_nevi == 'aylik' and maas2_tutar is None) else
    'tipb' if (ucret_nevi == 'sabit aylik' and maas2_tutar is not None) else
    'tipc' if (ucret_nevi in ['aylik', 'gunluk'] and maas2_tutar is not None) else
    None
	)
	```

-------------------------------------------
# table [monthly_personnel_records]
-------------------------------------------
	1	id									----->	PRIMARY (EŞSİZ ANAHTAR) 
	2	personnel_id						----->	
	3	contract_id							----->		
	4	donem								----->
	5	yıl
	6	ay
	7	adi									----->	
	8	soyadi								----->	
	9	cinsiyeti							----->	
	10	unvan								----->	
	11	isyeri								----->	
	12	bolum								----->
	13	ssk_no								----->	
	14	tc_kimlik_no						----->	
	15	baba_adi							----->	
	16	anne_adi							----->	
	17	dogum_yeri							----->	
	18	dogum_tarihi						----->	
	19	nufus_cuzdani_no					----->	
	20	nufusa_kayitli_oldugu_il			----->	
	21	nufusa_kayitli_oldugu_ilce			----->	
	22	nufusa_kayitli_oldugu_mah			----->	
	23	cilt_no								----->	
	24	sira_no								----->	
	25	kutuk_no							----->	
	26	ise_giris_tarihi					----->	
	27	isten_cikis_tarihi					----->	
	28	isten_ayrilis_kodu					----->	
	29	isten_ayrilis_nedeni				----->	
	30	adres								----->	
	31	telefon								----->	
	32	banka_sube_adi						----->	
	33	hesap_no							----->	
	34	ucret								----->	
	35	net_brut							----->	
	36	kan_grubu							----->	
	37	meslek_kodu							----->	
	38	meslek_adi							----->	


-------------------------------------------
# table [personnel_puantaj_grid]
-------------------------------------------
	1	id									-----> PRIMARY (EŞSİZ ANAHTAR)
	2	personnel_id						-----> _POST tablo[takvimli_puantaj][personnel_id]
	3	contract_id							-----> _POST tablo[takvimli_puantaj][contract_id]
	4	cost_center_id						-----> _POST tablo[takvimli_puantaj][cost_center_id]
	5	donem								-----> _POST tablo[takvimli_puantaj][donem]
	6	yil									-----> _POST tablo[takvimli_puantaj][yil]
	7	ay									-----> _POST tablo[takvimli_puantaj][ay]
	8	ayin_toplam_gun_sayisi				-----> _POST tablo[takvimli_puantaj][ayin_toplam_gun_sayisi]
	9	gun_1								-----> _POST tablo[takvimli_puantaj][gun_1]
	10	gun_2								-----> _POST tablo[takvimli_puantaj][gun_2]
	11	gun_3								-----> _POST tablo[takvimli_puantaj][gun_3]
	12	gun_4								-----> _POST tablo[takvimli_puantaj][gun_4]
	13	gun_5								-----> _POST tablo[takvimli_puantaj][gun_5]
	14	gun_6								-----> _POST tablo[takvimli_puantaj][gun_6]
	15	gun_7								-----> _POST tablo[takvimli_puantaj][gun_7]
	16	gun_8								-----> _POST tablo[takvimli_puantaj][gun_8]
	17	gun_9								-----> _POST tablo[takvimli_puantaj][gun_9]
	18	gun_10								-----> _POST tablo[takvimli_puantaj][gun_10]
	19	gun_11								-----> _POST tablo[takvimli_puantaj][gun_11]
	20	gun_12								-----> _POST tablo[takvimli_puantaj][gun_12]
	21	gun_13								-----> _POST tablo[takvimli_puantaj][gun_13]
	22	gun_14								-----> _POST tablo[takvimli_puantaj][gun_14]
	23	gun_15								-----> _POST tablo[takvimli_puantaj][gun_15]
	24	gun_16								-----> _POST tablo[takvimli_puantaj][gun_16]
	25	gun_17								-----> _POST tablo[takvimli_puantaj][gun_17]
	26	gun_18								-----> _POST tablo[takvimli_puantaj][gun_18]
	27	gun_19								-----> _POST tablo[takvimli_puantaj][gun_19]
	28	gun_20								-----> _POST tablo[takvimli_puantaj][gun_20]
	29	gun_21								-----> _POST tablo[takvimli_puantaj][gun_21]
	30	gun_22								-----> _POST tablo[takvimli_puantaj][gun_22]
	31	gun_23								-----> _POST tablo[takvimli_puantaj][gun_23]
	32	gun_24								-----> _POST tablo[takvimli_puantaj][gun_24]
	33	gun_25								-----> _POST tablo[takvimli_puantaj][gun_25]
	34	gun_26								-----> _POST tablo[takvimli_puantaj][gun_26]
	35	gun_27								-----> _POST tablo[takvimli_puantaj][gun_27]
	36	gun_28								-----> _POST tablo[takvimli_puantaj][gun_28]
	37	gun_29								-----> _POST tablo[takvimli_puantaj][gun_29]
	38	gun_30								-----> _POST tablo[takvimli_puantaj][gun_30]
	39	gun_31								-----> _POST tablo[takvimli_puantaj][gun_31]
	40	fm_gun_1							-----> _POST tablo[takvimli_puantaj][fm_gun_1]
	41	fm_gun_2							-----> _POST tablo[takvimli_puantaj][fm_gun_2]
	42	fm_gun_3							-----> _POST tablo[takvimli_puantaj][fm_gun_3]
	43	fm_gun_4							-----> _POST tablo[takvimli_puantaj][fm_gun_4]
	44	fm_gun_5							-----> _POST tablo[takvimli_puantaj][fm_gun_5]
	45	fm_gun_6							-----> _POST tablo[takvimli_puantaj][fm_gun_6]
	46	fm_gun_7							-----> _POST tablo[takvimli_puantaj][fm_gun_7]
	47	fm_gun_8							-----> _POST tablo[takvimli_puantaj][fm_gun_8]
	48	fm_gun_9							-----> _POST tablo[takvimli_puantaj][fm_gun_9]
	49	fm_gun_10							-----> _POST tablo[takvimli_puantaj][fm_gun_10]
	50	fm_gun_11							-----> _POST tablo[takvimli_puantaj][fm_gun_11]
	51	fm_gun_12							-----> _POST tablo[takvimli_puantaj][fm_gun_12]
	52	fm_gun_13							-----> _POST tablo[takvimli_puantaj][fm_gun_13]
	53	fm_gun_14							-----> _POST tablo[takvimli_puantaj][fm_gun_14]
	54	fm_gun_15							-----> _POST tablo[takvimli_puantaj][fm_gun_15]
	55	fm_gun_16							-----> _POST tablo[takvimli_puantaj][fm_gun_16]
	56	fm_gun_17							-----> _POST tablo[takvimli_puantaj][fm_gun_17]
	57	fm_gun_18							-----> _POST tablo[takvimli_puantaj][fm_gun_18]
	58	fm_gun_19							-----> _POST tablo[takvimli_puantaj][fm_gun_19]
	59	fm_gun_20							-----> _POST tablo[takvimli_puantaj][fm_gun_20]
	60	fm_gun_21							-----> _POST tablo[takvimli_puantaj][fm_gun_21]
	61	fm_gun_22							-----> _POST tablo[takvimli_puantaj][fm_gun_22]
	62	fm_gun_23							-----> _POST tablo[takvimli_puantaj][fm_gun_23]
	63	fm_gun_24							-----> _POST tablo[takvimli_puantaj][fm_gun_24]
	64	fm_gun_25							-----> _POST tablo[takvimli_puantaj][fm_gun_25]
	65	fm_gun_26							-----> _POST tablo[takvimli_puantaj][fm_gun_26]
	66	fm_gun_27							-----> _POST tablo[takvimli_puantaj][fm_gun_27]
	67	fm_gun_28							-----> _POST tablo[takvimli_puantaj][fm_gun_28]
	68	fm_gun_29							-----> _POST tablo[takvimli_puantaj][fm_gun_29]
	69	fm_gun_30							-----> _POST tablo[takvimli_puantaj][fm_gun_30]
	70	fm_gun_31							-----> _POST tablo[takvimli_puantaj][fm_gun_31]
	72	calisilan_gun_sayisi				-----> _POST tablo[takvimli_puantaj][calisilan_gun_sayisi]
	73	ssk_gun_sayisi						-----> _POST tablo[takvimli_puantaj][ssk_gun_sayisi]
	74	yillik_izin_gun						-----> _POST tablo[takvimli_puantaj][yillik_izin_gun]
	75	izin_gun_sayisi						-----> _POST tablo[takvimli_puantaj][izin_gun_sayisi]
	76	rapor_gun_sayisi					-----> _POST tablo[takvimli_puantaj][rapor_gun_sayisi]
	77	eksik_gun_sayisi					-----> _POST tablo[takvimli_puantaj][eksik_gun_sayisi]
	78	yarim_gun_sayisi					-----> _POST tablo[takvimli_puantaj][yarim_gun_sayisi]
	79	toplam_gun_sayisi					-----> _POST tablo[takvimli_puantaj][toplam_gun_sayisi]
	80	normal_calismasi					-----> _POST tablo[takvimli_puantaj][normal_calismasi]
	81	fazla_calismasi						-----> _POST tablo[takvimli_puantaj][fazla_calismasi]
	82	gece_calismasi						-----> _POST tablo[takvimli_puantaj][gece_calismasi]
	83	tatil_calismasi						-----> _POST tablo[takvimli_puantaj][tatil_calismasi]
	84	sigorta_girmedigi					-----> _POST tablo[takvimli_puantaj][sigorta_girmedigi]
	85	ayin_toplam_gun_sayisi				-----> _POST tablo[takvimli_puantaj][ayin_toplam_gun_sayisi]
	86	hafta_tatili						-----> _POST tablo[takvimli_puantaj][hafta_tatili]
	87	resmi_tatil							-----> _POST tablo[takvimli_puantaj][resmi_tatil]
	88	yol									-----> _POST tablo[takvimli_puantaj][yol]
	89	prim								-----> _POST tablo[takvimli_puantaj][prim]
	90	ikramiye							-----> _POST tablo[takvimli_puantaj][ikramiye]
	91	bayram								-----> _POST tablo[takvimli_puantaj][bayram]
	92	kira								-----> _POST tablo[takvimli_puantaj][kira]
	92	created_at							-----> _POST tablo[takvimli_puantaj][created_at]
	94	updated_at							-----> _POST tablo[takvimli_puantaj][updated_at]
	
	ucret_nevi (aylik, sabit aylik, gunluk)
	calisma_takvimi (atipi,btipi,ctipi)
		atipi- PAZAR TATİL 08:00-17:00 (ucret_nevi, aylik ve maaş2 var ise varsayılan olarak bu seçili olacak; ucret_nevi, sabit aylik ise otomatik olarak bu seçili olacak)
		btipi- HER GÜN 08:00-17:00 (ucret_nevi, günlük ise otomatik olarak bu seçili olacak; ucret_nevi, aylik ve taseron 1 ise varsayılan olarak bu seçili olacak)
		ctipi- TAKVİM YOK (ucret_nevi, aylik ve maaş2 yok ise varsayılan olarak bu seçili olacak)
	
	``` 
	import calendar
	from datetime import datetime

	# Şu anki tarihin ayı için
	simdi = datetime.now()
	yil = simdi.year
	ay = simdi.month

	ayin_toplam_gun_sayisi = calendar.monthrange(yil, ay)[1]
	```
	
	var calisilan_gun_sayisi	= TABLO SATIRINDAKİ TOPLAM ('N') SAYISI
	var yillik_izin_gun			= TABLO SATIRINDAKİ TOPLAM ('S') SAYISI
	var izin_gun_sayisi			= TABLO SATIRINDAKİ TOPLAM ('İ') SAYISI
	var rapor_gun_sayisi		= TABLO SATIRINDAKİ TOPLAM ('R') SAYISI
	var yarim_gun_sayisi		= TABLO SATIRINDAKİ TOPLAM ('Y') SAYISI * 0,5
	var eksik_gun_sayisi		= TABLO SATIRINDAKİ TOPLAM ('E') SAYISI
	var fazla_calismasi			= toplam (fazla mesai saatleri)
	var tatil_calismasi			= TABLO SATIRINDAKİ TOPLAM ('M') SAYISI
	var sigorta_girmedigi		= TABLO SATIRINDAKİ TOPLAM ('-') SAYISI
	var hafta_tatili			= TABLO SATIRINDAKİ TOPLAM ('H') SAYISI
	var resmi_tatil				= TABLO SATIRINDAKİ TOPLAM ('T') SAYISI
	
	var pc_ucret_nevi		= table [personnel_contracts][ucret_nevi]  (aylik, sabit aylik, gunluk)
	
	```
	normal_calismasi = (
    30 if (pc_ucret_nevi == "aylik" and eksik_gun_sayisi == 0 and ayin_toplam_gun_sayisi != 30) else
    30 if (pc_ucret_nevi == "sabit aylik" and sigorta_girmedigi == 0) else
    toplam_gun_sayisi if (pc_ucret_nevi == "sabit aylik" and sigorta_girmedigi != 0) else
    calisilan_gun_sayisi + yarim_gun_sayisi  # Bu hem "gunluk" hem de diğer durumlar için
	)
	```
	var tatiller			= hafta_tatili + resmi_tatil + tatil_calismasi
	var toplam_gun_sayisi	= ayin_toplam_gun_sayisi - sigorta_girmedigi
	var ssk_gun_sayisi		= toplam_gun_sayisi - eksik_gun_sayisi




-------------------------------------------
# table [cost_centers]
-------------------------------------------

	1	id							----->	PRIMARY (AUTO_INCREMENT)
	2	code						----->	backend [BÜYÜKHARF(BOŞLUK YERİNE ALT ÇİZGİ(name))]
	3	name						----->	frontend [name]	
	4	is_active					----->	frontend [is_active]
	5	bolum_adi					----->	frontend [bolum_adi]

-------------------------------------------
# table [luca_bordro]
-------------------------------------------

	1	id					----->
	2	yil 				----->
	3	ay 					----->
	4	donem 				----->
	5	sira_no				----->
	6	adi_soyadi			----->
	7	giris_t				----->
	8	cikis_t				----->
	9	tckn				----->
	10	ssk_sicil_no		----->
	11	t_gun				----->
	12	nor_kazanc			----->
	13	dig_kazanc			----->
	14	top_kazanc			----->
	15	ssk_m				----->
	16	ssk_isci			----->
	17	iss_p_isci			----->
	18	g_v_m				----->
	19	gel_ver				----->
	20	damga_v				----->
	21	oz_kesinti			----->
	22	n_odenen			----->
	23	isveren_maliyeti	----->
	24	ssk_isveren			----->
	25	iss_p_isveren		----->
	26	kanun				----->
	27	ssk_tesviki			----->
	28	oto_kat_bes			----->
	29	icra				----->
	30	avans				----->

-------------------------------------------
# table [monthly_puantaj]
-------------------------------------------

#	Adı								Türü			Karşılaştırma	Öznitelikler	Boş		Varsayılan			Açıklamalar	Ekstra
1	id 				BirincilIndex	int(11)											Hayır	Yok								AUTO_INCREMENT
2	yil 			Index			int(11)											Hayır	Yok		
3	ay 				Index			int(11)											Hayır	Yok		
4	donem 			Index			varchar(7)		utf8mb4_unicode_ci				Hayır	Yok		
5	personnel_id 	Index			int(11)											Hayır	Yok		
6	contract_id 	Index			int(11)											Evet	NULL		
7	cost_center_id 	Index			int(11)											Evet	NULL		
8	tckn 			Index			varchar(11)		utf8mb4_unicode_ci				Hayır	Yok		
9	adi_soyadi						varchar(200)	utf8mb4_unicode_ci				Hayır	Yok				
10	normal_gun						decimal(5,2)									Evet	NULL		
11	fazla_mesai_saat				decimal(7,2)									Evet	NULL		
12	tatil_mesai_gun					decimal(5,2)									Evet	NULL		
13	yillik_izin_gun					decimal(5,2)									Evet	NULL		
14	rapor_gun						decimal(5,2)									Evet	NULL		
15	hafta_tatili_gun				decimal(5,2)									Evet	NULL		
16	toplam_gun						decimal(5,2)									Evet	NULL		
17	upload_date						timestamp										Evet	current_timestamp()		
18	file_name						varchar(500)	utf8mb4_unicode_ci				Evet	NULL		
19	is_processed					int(11)											Evet	NULL		
20	notes							varchar(500)	utf8mb4_unicode_ci				Evet	NULL		
21	created_at						timestamp										Evet	current_timestamp()		
22	updated_at						timestamp										Evet	current_timestamp()		

	


# TABLO GÜNCELLELERİ

-------------------------------------------
# table [monthly_personnel_records] yükleme
-------------------------------------------

## ISLEM1 - DONEM seçilir

	var mpr_donem	----->	_POST [donem]
	var mpr_yil		-----> mpr_donem den hesaplanır
	var mpr_ay		-----> mpr_donem den hesaplanır

## ISLEM2 - EXCEL yüklemesi geçekleştirilir

## ISLEM3 - Satır bilgileri alınır
	

var mpr_adi									----->	excel [monthly_personnel_records] [Adı]
var mpr_soyadi								----->	excel [monthly_personnel_records] [Soyadı]
var mpr_cinsiyeti							----->	excel [monthly_personnel_records] [Cinsiyeti]
var mpr_unvan								----->	excel [monthly_personnel_records] [Ünvan]
var mpr_isyeri								----->	excel [monthly_personnel_records] [İşyeri]
var mpr_bolum								----->	excel [monthly_personnel_records] [Bölüm]
var mpr_ssk_no								----->	excel [monthly_personnel_records] [SSK No]
var mpr_tc_kimlik_no						----->	excel [monthly_personnel_records] [TC Kimlik No]
var mpr_baba_adi							----->	excel [monthly_personnel_records] [Baba Adı]
var mpr_anne_adi							----->	excel [monthly_personnel_records] [Anne Adı]
var mpr_dogum_yeri							----->	excel [monthly_personnel_records] [Doğum Yeri]
var mpr_dogum_tarihi						----->	excel [monthly_personnel_records] [Doğum Tarihi]
var mpr_nufus_cuzdani_no					----->	excel [monthly_personnel_records] [Nüfus Cüzdanı No]
var mpr_nufusa_kayitli_oldugu_il			----->	excel [monthly_personnel_records] [Nüfusa Kayıtlı Olduğu İl]
var mpr_nufusa_kayitli_oldugu_ilce			----->	excel [monthly_personnel_records] [Nüfusa Kayıtlı Olduğu İlçe]
var mpr_nufusa_kayitli_oldugu_mah			----->	excel [monthly_personnel_records] [Nüfusa Kayıtlı Olduğu Mah-Köy]
var mpr_cilt_no								----->	excel [monthly_personnel_records] [Cilt No]
var mpr_sira_no								----->	excel [monthly_personnel_records] [Sıra No]
var mpr_kutuk_no							----->	excel [monthly_personnel_records] [Kütük No]
var mrp_ise_giris_tarihi					----->	excel [monthly_personnel_records] [İşe Giriş Tarihi]
var mpr_isten_cikis_tarihi					----->	excel [monthly_personnel_records] [İşten Çıkış Tarihi]
var mpr_isten_ayrilis_kodu					----->	excel [monthly_personnel_records] [İşten Ayrılış Kodu]
var mpr_isten_ayrilis_nedeni				----->	excel [monthly_personnel_records] [İşten Ayrılış Nedeni]
var mpr_adres								----->	excel [monthly_personnel_records] [Adres]
var mpr_telefon								----->	excel [monthly_personnel_records] [Telefon]
var mpr_banka_sube_adi						----->	excel [monthly_personnel_records] [Banka Şube Adı]
var mpr_hesap_no							----->	excel [monthly_personnel_records] [Hesap No]
var mpr_ucret								----->	excel [monthly_personnel_records] [Ücret]
var mpr_net_brut							----->	excel [monthly_personnel_records] [Net / Brüt]
var mpr_kan_grubu							----->	excel [monthly_personnel_records] [Kan Grubu]
var mpr_meslek_kodu							----->	excel [monthly_personnel_records] [Meslek Kodu]
var mpr_meslek_adi							----->	excel [monthly_personnel_records] [Meslek Adı]

## ISLEM4 - EĞER table [personnel] [tc_kimlik_no] 'ların içinde mpr_tc_kimlik_no yoksa aşağıdaki işlemleri yap;

table [personnel] 'da yeni kayıt oluştur;
	1	table [personnel] [id]				----->	PRIMARY (AUTO_INCREMENT)
	2	table [personnel] [tc_kimlik_no]	----->	mpr_tc_kimlik_no
	3	table [personnel] [ad]				----->	mpr_adi
	4	table [personnel] [soyad]			----->	mpr_soyadi

var mpr_personnel_id = table [personnel] [id]
var acc_code = text( '335.'& mpr_tc_kimlik_no )
var acc_name = text( mpr_adi & " " & mpr_soyadi & " " & mpr_tc_kimlik_no )
	
table [accounts] 'da yeni kayıt oluştur;
	1	table [accounts] [id] 			----->	PRIMARY (AUTO_INCREMENT)
	2	table [accounts] [code] 		----->	acc_code
	3	table [accounts] [name]			----->	acc_name
	4	table [accounts] [account_type]	----->	'BALANCE_SHEET'
	5	table [accounts] [is_active]	----->	1
	6	table [accounts] [contact_id]	----->	NULL
	7	table [accounts] [personnel_id]	----->	mpr_personnel_id

var pr_accounts_id = table [accounts] [id]

table [personnel] 'e tekra git accounts_id 'i oluştur.

	1	table [personnel] [accounts_id]	----->	pr_accounts_id

table [personnel_contracts]'a git

	1	table [personnel_contracts] [id]							= PRIMARY (AUTO_INCREMENT)
	2	table [personnel_contracts] [personnel_id]					= mpr_personnel_id
	2	table [personnel_contracts] [bolum]							= mpr_bolum
	3	table [personnel_contracts] [cost_center_id]				= table [cost_centers][bolum] ile karşılaştır, eşleşen varsa id değerini buraya ata yoksa NULL.
	4	table [personnel_contracts] [ise_giris_tarihi]				= mrp_ise_giris_tarihi
	5	table [personnel_contracts] [isten_cikis_tarihi]			= mpr_isten_cikis_tarihi
	6	table [personnel_contracts] [maas1_tip]						= mpr_net_brut
	7	table [personnel_contracts] [maas1_tutar]					= mpr_ucret
	8	table [personnel_contracts] [fm_orani]						= 1
	9	table [personnel_contracts] [tatil_orani]					= 1
	10	table [personnel_contracts] [is_active]						= FORMÜL( eğer mpr_isten_cikis_tarihi NULL ise 1 değilse 0 )
	
var mpr_contract_id = table [personnel_contracts] [id]
	
monthly_personnel_records tablsosunda kayıt işlemini gerçekleştir.

	table [monthly_personnel_records] [id]								= PRIMARY (EŞSİZ ANAHTAR) 
	table [monthly_personnel_records] [personnel_id]					= mpr_personnel_id
	table [monthly_personnel_records] [donem] 							= mpr_donem	
	table [monthly_personnel_records] [contract_id]						= mpr_contract_id
	table [monthly_personnel_records] [adi]								= mpr_adi
	table [monthly_personnel_records] [soyadi]							= mpr_soyadi
	table [monthly_personnel_records] [cinsiyeti]						= mpr_cinsiyeti
	table [monthly_personnel_records] [unvan]							= mpr_unvan
	table [monthly_personnel_records] [isyeri]							= mpr_isyeri
	table [monthly_personnel_records] [bolum]							= mpr_bolum
	table [monthly_personnel_records] [sk_no]							= mpr_ssk_no
	table [monthly_personnel_records] [tc_kimlik_no]					= mpr_tc_kimlik_no
	table [monthly_personnel_records] [baba_adi]						= mpr_baba_adi
	table [monthly_personnel_records] [anne_adi]						= mpr_anne_adi
	table [monthly_personnel_records] [dogum_yeri]						= mpr_dogum_yeri
	table [monthly_personnel_records] [dogum_tarihi]					= mpr_dogum_tarihi
	table [monthly_personnel_records] [nufus_cuzdani_no]				= mpr_nufus_cuzdani_no
	table [monthly_personnel_records] [nufusa_kayitli_oldugu_il]		= mpr_nufusa_kayitli_oldugu_il
	table [monthly_personnel_records] [nufusa_kayitli_oldugu_ilce]		= mpr_nufusa_kayitli_oldugu_ilce
	table [monthly_personnel_records] [nufusa_kayitli_oldugu_mah]		= mpr_nufusa_kayitli_oldugu_mah
	table [monthly_personnel_records] [cilt_no]							= mpr_cilt_no
	table [monthly_personnel_records] [sira_no]							= mpr_sira_no
	table [monthly_personnel_records] [kutuk_no]						= mpr_kutuk_no
	table [monthly_personnel_records] [ise_giris_tarihi]				= mrp_ise_giris_tarihi
	table [monthly_personnel_records] [isten_cikis_tarihi]				= mpr_isten_cikis_tarihi
	table [monthly_personnel_records] [isten_ayrilis_kodu]				= mpr_isten_ayrilis_kodu
	table [monthly_personnel_records] [isten_ayrilis_nedeni]			= mpr_isten_ayrilis_nedeni
	table [monthly_personnel_records] [adres]							= mpr_adres
	table [monthly_personnel_records] [telefon]							= mpr_telefon
	table [monthly_personnel_records] [banka_sube_adi]					= mpr_banka_sube_adi
	table [monthly_personnel_records] [hesap_no]						= mpr_hesap_no
	table [monthly_personnel_records] [ucret]							= mpr_ucret
	table [monthly_personnel_records] [net_brut]						= mpr_net_brut
	table [monthly_personnel_records] [kan_grubu]						= mpr_kan_grubu
	table [monthly_personnel_records] [meslek_kodu]						= mpr_meslek_kodu
	table [monthly_personnel_records] [meslek_adi]						= mpr_meslek_adi
		
	var mpr_id = table [monthly_personnel_records] [id]
	
	personnel_contracts tablosuna dön ve oluşan monthly_personnel_records_id değerini gir.
	
	table [personnel_contracts] [monthly_personnel_records_id]	----->	mpr_id


	Diğer EXCEL satırını al, ISLEM3 'ye dön.



## ISLEM5  - mpr_personnel_id değeri belirlenir;

var mpr_personnel_id ----->	FORMÜL( mpr_tc_kimlik_no değerini table [personnel] [tc_kimlik_no] kolonunda sorgula ve table [personnel] [id] değerini mpr_personnel_id değişkenine ata.

## ISLEM6 - Daha önce yüklenmiş mi aynısı kontrolü yapılır;

	table [monthly_personnel_records] da ( mpr_tc_kimlik_no AND mrp_ise_giris_tarihi AND mpr_donem AND mpr_bolum ) taraması yap (table [monthly_personnel_records] [tc_kimlik_no] AND table [monthly_personnel_records] [ise_giris_tarihi] AND table [monthly_personnel_records] [donem] AND table [monthly_personnel_records] [bolum]) eşleşen varsa, 
	
	var mpr_id = FORMÜL( eşleşen satır table [monthly_personnel_records][id] değeri )
	
	tablonun o satırını EXCEL'den gelen veriler ile güncelle 
	
	table [personnel_contracts] da (mpr_tc_kimlik_no & mrp_ise_giris_tarihi & mpr_bolum) sorgulaması yap eşleşen varsa table [personnel_contracts] aşağıdaki kolonlarını güncelle.

	table [personnel_contracts] [monthly_personnel_records_id]		= mpr_id
	table [personnel_contracts] [isten_cikis_tarihi]				= mpr_isten_cikis_tarihi
	table [personnel_contracts] [maas1_tip]							= mpr_net_brut
	table [personnel_contracts] [maas1_tutar]						= mpr_ucret
	table [personnel_contracts] [is_active]							= FORMÜL( eğer mpr_isten_cikis_tarihi NULL ise 1 değilse 0 )
	
	Diğer excel satırnı incelemeye geç (ISLEM3' dön)
	
	Eşleşen yoksa tabloya yeni satırı ekle EXCEL'den alınan satır verilerini gir.
	
	table [monthly_personnel_records] [id]								= PRIMARY (EŞSİZ ANAHTAR) 
	table [monthly_personnel_records] [personnel_id]					= mpr_personnel_id
	table [monthly_personnel_records] [donem] 							= mpr_donem	
	table [monthly_personnel_records] [cost_center_id]					= mpr_cost_center_id
	table [monthly_personnel_records] [adi]								= mpr_adi
	table [monthly_personnel_records] [soyadi]							= mpr_soyadi
	table [monthly_personnel_records] [cinsiyeti]						= mpr_cinsiyeti
	table [monthly_personnel_records] [unvan]							= mpr_unvan
	table [monthly_personnel_records] [isyeri]							= mpr_isyeri
	table [monthly_personnel_records] [bolum]							= mpr_bolum
	table [monthly_personnel_records] [sk_no]							= mpr_ssk_no
	table [monthly_personnel_records] [tc_kimlik_no]					= mpr_tc_kimlik_no
	table [monthly_personnel_records] [baba_adi]						= mpr_baba_adi
	table [monthly_personnel_records] [anne_adi]						= mpr_anne_adi
	table [monthly_personnel_records] [dogum_yeri]						= mpr_dogum_yeri
	table [monthly_personnel_records] [dogum_tarihi]					= mpr_dogum_tarihi
	table [monthly_personnel_records] [nufus_cuzdani_no]				= mpr_nufus_cuzdani_no
	table [monthly_personnel_records] [nufusa_kayitli_oldugu_il]		= mpr_nufusa_kayitli_oldugu_il
	table [monthly_personnel_records] [nufusa_kayitli_oldugu_ilce]		= mpr_nufusa_kayitli_oldugu_ilce
	table [monthly_personnel_records] [nufusa_kayitli_oldugu_mah]		= mpr_nufusa_kayitli_oldugu_mah
	table [monthly_personnel_records] [cilt_no]							= mpr_cilt_no
	table [monthly_personnel_records] [sira_no]							= mpr_sira_no
	table [monthly_personnel_records] [kutuk_no]						= mpr_kutuk_no
	table [monthly_personnel_records] [ise_giris_tarihi]				= mrp_ise_giris_tarihi
	table [monthly_personnel_records] [isten_cikis_tarihi]				= mpr_isten_cikis_tarihi
	table [monthly_personnel_records] [isten_ayrilis_kodu]				= mpr_isten_ayrilis_kodu
	table [monthly_personnel_records] [isten_ayrilis_nedeni]			= mpr_isten_ayrilis_nedeni
	table [monthly_personnel_records] [adres]							= mpr_adres
	table [monthly_personnel_records] [telefon]							= mpr_telefon
	table [monthly_personnel_records] [banka_sube_adi]					= mpr_banka_sube_adi
	table [monthly_personnel_records] [hesap_no]						= mpr_hesap_no
	table [monthly_personnel_records] [ucret]							= mpr_ucret
	table [monthly_personnel_records] [net_brut]						= mpr_net_brut
	table [monthly_personnel_records] [kan_grubu]						= mpr_kan_grubu
	table [monthly_personnel_records] [meslek_kodu]						= mpr_meslek_kodu
	table [monthly_personnel_records] [meslek_adi]						= mpr_meslek_adi
		
	var mpr_id = table [monthly_personnel_records] [id]


## ISLEM7 - table [personnel_contracts] da (mpr_tc_kimlik_no & mrp_ise_giris_tarihi & mpr_bolum) sorgulaması yap eşleşen varsa table [personnel_contracts] aşağıdaki kolonlarını güncelle.

	table [personnel_contracts] [monthly_personnel_records_id]	=	mpr_id
	table [personnel_contracts] [isten_cikis_tarihi]			=	mpr_isten_cikis_tarihi
	table [personnel_contracts] [maas1_tip]						=	mpr_net_brut
	table [personnel_contracts] [maas1_tutar]					=	mpr_ucret
	table [personnel_contracts] [is_active]						=	FORMÜL( eğer mpr_isten_cikis_tarihi NULL ise 1 değilse 0 )
	
	
## ISLEM8 - table [personnel_contracts] da , mpr_tc_kimlik_no su eşleşip ise_giris_tarihi&bolum eşleşmeyen varsa;

	table [personnel_contracts]'a git yeni bir kontrat oluştur.
	
	table [personnel_contracts] [id]							=	PRIMARY (AUTO_INCREMENT)
	table [personnel_contracts] [personnel_id]					=	mpr_personnel_id
	table [personnel_contracts] [bolum]							=	mpr_bolum
	table [personnel_contracts] [monthly_personnel_records_id]	=	mpr_id
	table [personnel_contracts] [ise_giris_tarihi]				=	mrp_ise_giris_tarihi
	table [personnel_contracts] [isten_cikis_tarihi]			=	mpr_isten_cikis_tarihi
	table [personnel_contracts] [maas1_tip]						=	mpr_net_brut
	table [personnel_contracts] [maas1_tutar]					=	mpr_ucret
	table [personnel_contracts] [fm_orani]						=	1
	table [personnel_contracts] [tatil_orani]					=	1
	table [personnel_contracts] [is_active]						=	FORMÜL( eğer mpr_isten_cikis_tarihi NULL ise 1 değilse 0 )


## ISLEM9 - Excel den gelen verilerin tümü işlenmiş ise durum raporu verip yükleme işlemini bitir, işlem yapılmayan satır varsa sıraki excel satırını işlemek üzere mpr_donem hariç tüm değişkenleri temizleyip işlem 3' geç.



-------------------------------------------
# table [cost_centers] yükleme
-------------------------------------------

	table [cost_centers] [id]			= PRIMARY (AUTO_INCREMENT)
	table [cost_centers] [code]			= FORMÜL ( BÜYÜKHARF ( BOŞLUK YERİNE ALT ÇİZGİ( _POST [name] )))
	table [cost_centers] [name]			= _POST [name]	
	table [cost_centers] [is_active]	= _POST [is_active]
	table [cost_centers] [bolum_adi]	= _POST [bolum_adi]

-------------------------------------------
# table [luca_bordro] yükleme
-------------------------------------------

## ISLEM1 - DONEM seçilir

	var lb_yıl				= $_POST ['yil']	(donem bilgisini aa kısmı)
	var lb_ay				= $_POST ['ay']		(donem bilgisini yyyy kısmı)
	var lb_donem			= $_POST ['donem']	(yyyy-aa şeklinde frontendden alınacak)

## ISLEM2 - EXCEL yüklemesi geçekleştirilir

## ISLEM3 - Satır bilgileri alınır

	var lb_sira_no			= excel [luca_bordro] [#]
	var lb_adi_soyadi		= excel [luca_bordro] [Adı Soyadı]
	var lb_giris_t			= excel [luca_bordro] [Giriş T]
	var lb_cikis_t			= excel [luca_bordro] [Çıkış T]
	var lb_tckn				= excel [luca_bordro] [TCKN]
	var lb_ssk_sicil_no		= excel [luca_bordro] [SSK Sicil No]
	var lb_t_gun			= excel [luca_bordro] [T.Gün]
	var lb_nor_kazanc		= excel [luca_bordro] [Nor.Kazanç]
	var lb_dig_kazanc		= excel [luca_bordro] [Diğ.Kazanç]
	var lb_top_kazanc		= excel [luca_bordro] [Top.Kazanç]
	var lb_ssk_m			= excel [luca_bordro] [SSK M.]
	var lb_ssk_isci			= excel [luca_bordro] [SSK İşçi]
	var lb_iss_p_isci		= excel [luca_bordro] [İşs.P.İşçi]
	var lb_g_v_m			= excel [luca_bordro] [G.V.M]
	var lb_gel_ver			= excel [luca_bordro] [[Gel.Ver.]
	var lb_damga_v			= excel [luca_bordro] [Damga V]
	var lb_oz_kesinti		= excel [luca_bordro] [Öz.Kesinti]
	var lb_n_odenen			= excel [luca_bordro] [N.Ödenen]
	var lb_isveren_maliyeti	= excel [luca_bordro] [İşveren Maliyeti]
	var lb_ssk_isveren		= excel [luca_bordro] [SSK İşveren]
	var lb_iss_p_isveren	= excel [luca_bordro] [İşs.P.İşveren]
	var lb_kanun			= excel [luca_bordro] [Kanun]
	var lb_ssk_tesviki		= excel [luca_bordro] [SSK Teşviki]
	var lb_oto_kat_bes		= excel [luca_bordro] [Oto.Kat.BES]
	var lb_icra				= excel [luca_bordro] [icra]
	var lb_avans			= excel [luca_bordro] [Avans]

## ISLEM4 - Daha önce yüklenmiş mi kontrol edilir;

	table [luca_bordro] ' (lb_yıl & lb_ay & lb_donem & lb_tckn & lb_giris_t & lb_cikis_t) sorgulanır eşleşme varsa excel verileri güncellenir, excel verilerinin tüm satıları işlenmişse yükleme bitirilir, işlenmemiş satırlar varsa ISLEM2'ye dönülür, 
		
	Eşeleşme yoksa;
		
	table [luca_bordro] tablosuna yeni satır işlenir;
		
	1	id					----->PRIMARY (AUTO_INCREMENT)
	2	yil 				----->lb_yıl
	3	ay 					----->lb_ay
	4	donem 				----->lb_donem
	5	sira_no				----->lb_sira_no
	6	adi_soyadi			----->lb_adi_soyadi
	7	giris_t				----->lb_giris_t
	8	cikis_t				----->lb_cikis_t
	9	tckn				----->lb_tckn
	10	ssk_sicil_no		----->lb_ssk_sicil_no
	11	t_gun				----->lb_t_gun
	12	nor_kazanc			----->lb_nor_kazanc
	13	dig_kazanc			----->lb_dig_kazanc
	14	top_kazanc			----->lb_top_kazanc
	15	ssk_m				----->lb_ssk_m
	16	ssk_isci			----->lb_ssk_isci
	17	iss_p_isci			----->lb_iss_p_isci
	18	g_v_m				----->lb_g_v_m
	19	gel_ver				----->lb_gel_ver
	20	damga_v				----->lb_damga_v
	21	oz_kesinti			----->lb_oz_kesinti
	22	n_odenen			----->lb_n_odenen
	23	isveren_maliyeti	----->lb_isveren_maliyeti
	24	ssk_isveren			----->lb_ssk_isveren
	25	iss_p_isveren		----->lb_iss_p_isveren
	26	kanun				----->lb_kanun
	27	ssk_tesviki			----->lb_ssk_tesviki
	28	oto_kat_bes			----->lb_oto_kat_bes
	29	icra				----->lb_icra
	30	avans				----->lb_avans
	
	
	excel verilerinin tüm satıları işlenmişse yükleme bitirilir, işlenmemiş satırlar varsa ISLEM2'ye dönülür, 
	
	

# BORDRO HESAPLAMA

- Değişkenleri belirleme
	
	*table [luca_bordro] değişkenleri atama
	
	var lc_id					=table [luca_bordro] [id]
	var lc_yil					=table [luca_bordro] [yil]
	var lc_ay					=table [luca_bordro] [ay]
	var lc_donem				=table [luca_bordro] [donem]
	var lc_sira_no				=table [luca_bordro] [sira_no]
	var lc_adi_soyadi			=table [luca_bordro] [adi_soyadi]
	var lc_giris_t				=table [luca_bordro] [giris_t]
	var lc_cikis_t				=table [luca_bordro] [cikis_t]
	var lc_tckn					=table [luca_bordro] [tckn]
	var lc_ssk_sicil_no			=table [luca_bordro] [ssk_sicil_no]
	var lc_t_gun				=table [luca_bordro] [t_gun]
	var lc_nor_kazanc			=table [luca_bordro] [nor_kazanc]
	var lc_dig_kazanc			=table [luca_bordro] [dig_kazanc]
	var lc_top_kazanc			=table [luca_bordro] [top_kazanc]
	var lc_ssk_m				=table [luca_bordro] [ssk_m]
	var lc_ssk_isci				=table [luca_bordro] [ssk_isci]
	var lc_iss_p_isci			=table [luca_bordro] [iss_p_isci]
	var lc_g_v_m				=table [luca_bordro] [g_v_m]
	var lc_gel_ver				=table [luca_bordro] [gel_ver]
	var lc_damga_v				=table [luca_bordro] [damga_v]
	var lc_oz_kesinti			=table [luca_bordro] [oz_kesinti]
	var lc_n_odenen				=table [luca_bordro] [n_odenen]
	var lc_isveren_maliyeti		=table [luca_bordro] [isveren_maliyeti]
	var lc_ssk_isveren			=table [luca_bordro] [ssk_isveren]
	var lc_iss_p_isveren		=table [luca_bordro] [iss_p_isveren]
	var lc_kanun				=table [luca_bordro] [kanun]
	var lc_ssk_tesviki			=table [luca_bordro] [ssk_tesviki]
	var lc_oto_kat_bes			=table [luca_bordro] [oto_kat_bes]
	var lc_icra					=table [luca_bordro] [icra]
	var lc_avans				=table [luca_bordro] [avans]
	
	*table [personnel_puantaj_grid] değişkenleri atama
	
	lc_donem ve tr_contracts_id değerleri personnel_puantaj_grid tablosunda 'contract_id' ve 'donem' ile eşleşen satırdan aşağıdaki değerler çekilir.
	
	var ppg_calisilan_gun_sayisi	=table [personnel_puantaj_grid] [calisilan_gun_sayisi]
	var ppg_yillik_izin_gun			=table [personnel_puantaj_grid] [yillik_izin_gun]
	var ppg_izin_gun_sayisi			=table [personnel_puantaj_grid] [izin_gun_sayisi]
	var ppg_rapor_gun_sayisi		=table [personnel_puantaj_grid] [rapor_gun_sayisi]
	var ppg_yarim_gun_sayisi		=table [personnel_puantaj_grid] [yarim_gun_sayisi]
	var ppg_eksik_gun_sayisi		=table [personnel_puantaj_grid] [eksik_gun_sayisi]
	var ppg_fazla_calismasi			=table [personnel_puantaj_grid] [fazla_calismasi]
	var ppg_tatil_calismasi			=table [personnel_puantaj_grid] [tatil_calismasi]
	var ppg_sigorta_girmedigi		=table [personnel_puantaj_grid] [sigorta_girmedigi]
	var ppg_hafta_tatili			=table [personnel_puantaj_grid] [hafta_tatili]
	var ppg_resmi_tatil				=table [personnel_puantaj_grid] [resmi_tatil]
	var ppg_pc_ucret_nevi			=table [personnel_puantaj_grid] [pc_ucret_nevi]
	var ppg_normal_calismasi		=table [personnel_puantaj_grid] [normal_calismasi]
	var ppg_tatiller				=table [personnel_puantaj_grid] [tatiller]
	var ppg_toplam_gun_sayisi		=table [personnel_puantaj_grid] [toplam_gun_sayisi]
	var ppg_ssk_gun_sayisi			=table [personnel_puantaj_grid] [ssk_gun_sayisi]
	var ppg_yol						=table [personnel_puantaj_grid] [yol]
	var ppg_prim					=table [personnel_puantaj_grid] [prim]
	var ppg_ikramiye				=table [personnel_puantaj_grid] [ikramiye]
	var ppg_bayram					=table [personnel_puantaj_grid] [bayram]
	var ppg_kira					=table [personnel_puantaj_grid] [kira]
	
	```
	tr_gunluk_ucret = (tr_maas2_tutar / 30 if tr_ucret_nevi in ['aylik', 'sabit aylik'] 
                   else tr_maas2_tutar if tr_ucret_nevi == 'gunluk' 
                   else 0)
				   
	tr_normal_calisma_tutar	= tr_gunluk_ucret * ppg_normal_calismasi
	tr_fazla_calisma_tutar	= tr_gunluk_ucret / 8 * ppg_fazla_calismasi
	tr_resmi_tatil_tutar	= tr_gunluk_ucret * ppg_resmi_tatil
	tr_hafta_tatili_tutar	= tr_gunluk_ucret * ppg_hafta_tatili
	tr_tatil_calismasi_tutar= tr_gunluk_ucret * ppg_tatil_calismasi
	tr_yillik_izin_gun_tutar= tr_gunluk_ucret * ppg_yillik_izin_gun
	
	
	```
	
	
	
	
	
	* transaction değerleri
	var tr_no 					= transaction_number değerini üretin motordan yeni değeri alır
	
	var tr_date					= (lc_yıl ve lc_ay değikkenlerinden üertilen ayın on günü örn. 30.11.2025 gibi)
	
	lc_tckn değeri table[personnel][tc_kimlik_no] sütununda aranıp eşleşen satırdan table[personnel][id], [personnel][accounts_id] ,[personnel][ad], [personnel][soyad]
	
	var tr_per_id				= table[personnel][id]
	var tr_per_ad				= table[personnel][ad]
	var tr_per_soyad			= table[personnel][soyad]
	var tr_per_acc_id			= table [personnel][accounts_id]
	
	pc_id & lc_giris_t arihleri ,table[personnel_contracts] tablosunda [personnel_id] ve [ise_giris_tarihi] sütünlarında eşleşen satırdan,
	
	var tr_contracts_id			= table[personnel_contracts][id]
	var tr_cc_id				= table[personnel_contracts][cost_center_id]
	var tr_maas_hesabi			= table[personnel_contracts][maas_hesabi]
	var tr_maas2_tutar			= table[personnel_contracts][maas2_tutar]
	var tr_ucret_nevi			= table[personnel_contracts][ucret_nevi] 'enum (aylik, sabit aylik, gunluk)
	
	tr_cost_center_id değişkeni, table [cost_centers][id] tablosunda aratılıp eşleşen satırda [name] değeri , tr_cost_center_name değişkenine atanır.
	
	var tr_cc_name	= table [cost_centers][name]
	
	var tr_des_text				= text ( lc_donem & " " & tr_per_ad & " " & tr_per_soyad & " " & tr_cc_name & " bordrosu" )
	
	* transaction_lines hesap kodlarını değişkene atama
	
	var maliyet_acc_id			= ( eğer pc_cost_center_id = 31 ise 5556 değilse 5535 )
	var g_vergi_acc_id			= 728
	var d_vergi_acc_id			= 729
	var sgk_isci_prim_acc_id	= 731
	var sgk_isveren_prim_acc_id = 732
	var sgk_isci_isz_acc_id 	= 733
	var sgk_isveren_isz_acc_id 	= 734
	var bes_kesinti_acc_id 		= 735
	var icra_kesinti_acc_id 	= 736
	var haz_kat_payi_acc_id		= 744

	
	* transaction_lines diğer bordro hesaplamaları
	
	var od_ssk_isveren = lc_ssk_isveren - lc_ssk_tesviki



	# table [transactions] tablosu'na verinin işlenmesi
	
	table [transactions]
		
	1	id							----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_number			----->	tr_no
	3	transaction_date			----->	tr_date	
	4	accounting_period			----->	lc_donem	
	5	cost_center_id				----->	tr_cc_id
	6	description	text			----->	tr_des_text
	7	document_type				----->	"MAAŞ BORDROSU" 
	8	document_subtype			----->	"Aylık Maaş"
	9	document_number				----->	"BORDRO " & dönem
	10	related_invoice_number		----->	NULL
	
	var tr_id = table [transactions][id]

	# table [transaction_lines] tablosuna verinin işlenmesi

	## Seçenek 1 eğer tr_maas_hesabi = 'tipa' ise aşağıdaki gibi satırlar eklenir; (aylık ve maaş2 yok)
	
	Eğer lc_n_odenen > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Net Ödenen"
	6	debit				----->	lc_n_odenen
	7	credit				----->	0
	
	Eğer lc_icra > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0
	
	Eğer lc_oto_kat_bes > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0
	
	Eğer lc_avans > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Avans Kesintisi"
	6	debit				----->	lc_avans
	7	credit				----->	0
	
	Eğer lc_gel_ver > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	lc_gel_ver
	7	credit				----->	0
	
	Eğer lc_damga_v > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	lc_damga_v
	7	credit				----->	0	
	
	Eğer lc_ssk_isci > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk İşçi Payı"
	6	debit				----->	lc_ssk_isci
	7	credit				----->	0
	
	Eğer lc_iss_p_isci > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşçi Payı"
	6	debit				----->	lc_iss_p_isci
	7	credit				----->	0	
	
	Eğer lc_ssk_isveren > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk İşveren Payı"
	6	debit				----->	lc_ssk_isveren
	7	credit				----->	0
	
	Eğer lc_iss_p_isveren > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşveren Payı"
	6	debit				----->	lc_iss_p_isveren
	7	credit				----->	0
	
	Eğer lc_oto_kat_bes > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0
	
	Eğer lc_icra > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0
	
	Eğer lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Net Kazanç"
	6	debit				----->	0
	7	credit				----->	lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans
	
	Eğer lc_ssk_isci > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_prim_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşçi Payı"
	6	debit				----->	0
	7	credit				----->	lc_ssk_isci
	
	Eğer od_ssk_isveren > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_prim_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşveren Payı"
	6	debit				----->	0
	7	credit				----->	od_ssk_isveren
	
	Eğer lc_iss_p_isci > 0 ise ;
		
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_isz_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşçi İşsizlik Sigortası Payı"
	6	debit				----->	0
	7	credit				----->	lc_iss_p_isci
	
	Eğer iss_p_isveren > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_isz_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşveren İşsizlik sigortası Payı"
	6	debit				----->	0
	7	credit				----->	iss_p_isveren
	
	Eğer lc_damga_v > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	d_vergi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_damga_v
	
	Eğer lc_gel_ver > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	g_vergi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_gel_ver
	
	Eğer lc_ssk_tesviki > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	haz_kat_payi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Hazine Katkı Payı"
	6	debit				----->	0
	7	credit				----->	lc_ssk_tesviki

	Eğer lc_oto_kat_bes > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	bes_kesinti_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_oto_kat_bes
	
	Eğer lc_icra > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	icra_kesinti_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_icra
	
	
	## Seçenek 2 eğer tr_maas_hesabi = 'tipb' ise aşağıdaki gibi satırlar eklenir; (sabit aylık ve maaş2 var)
	
	lc_tckn & lc_donem; table [luca_bordro] [id] eşit değildir lc_id olan table [luca_bordro] tablosunda (lc_tckn & lc_donem) = (table [luca_bordro] [tckn]  & table [luca_bordro] [donem] )eşleşmesini sağlayan tüm satırların; ([n_odenen] + [oto_kat_bes] + [icra] + [avans]) toplamları alınır, tr_bordro_net_toplamı değişkenine atanır.
	
	var tr_bordro_net_toplamı = toplam	([n_odenen] + [oto_kat_bes] + [icra] + [avans]) - (lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans)
	
	var tr_kalan_net = tr_maas2_tutar - tr_bordro_net_toplamı
	
	var tr_elden_kalan = tr_kalan_net - (lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans)
	
	var tr_elden_kalan_yuvarlanmis = tr_elden_kalan 'ın 100 'e yuvarlanması ile elde edilir.
	
	var tr_elden_yuvarlamasi = tr_elden_kalan - tr_elden_kalan_yuvarlanmis

	
	Eğer tr_elden_yuvarlamasi > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Elden Yuvarlama"
	6	debit				----->	tr_elden_yuvarlamasi
	7	credit				----->	0

	Eğer tr_elden_yuvarlamasi < 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Elden Yuvarlama"
	6	debit				----->	0
	7	credit				----->	|tr_elden_yuvarlamasi|

	Eğer tr_elden_kalan_yuvarlanmis > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Elden Ödenen"
	6	debit				----->	tr_elden_kalan_yuvarlanmis
	7	credit				----->	0

	Eğer lc_n_odenen > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Net Ödenen"
	6	debit				----->	lc_n_odenen
	7	credit				----->	0
	
	Eğer lc_icra > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0
	
	Eğer lc_oto_kat_bes > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0
	
	Eğer lc_avans > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Avans Kesintisi"
	6	debit				----->	lc_avans
	7	credit				----->	0
	
	Eğer lc_gel_vers > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	lc_gel_ver
	7	credit				----->	0

	Eğer lc_damga_v > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	lc_damga_v
	7	credit				----->	0	
	
	Eğer lc_ssk_isci > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk İşçi Payı"
	6	debit				----->	lc_ssk_isci
	7	credit				----->	0	
	
	Eğer lc_iss_p_isci > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşçi Payı"
	6	debit				----->	lc_iss_p_isci
	7	credit				----->	0	

	Eğer lc_ssk_isveren > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk İşveren Payı"
	6	debit				----->	lc_ssk_isveren
	7	credit				----->	0
	
	Eğer lc_iss_p_isveren > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşveren Payı"
	6	debit				----->	lc_iss_p_isveren
	7	credit				----->	0

	Eğer lc_oto_kat_bes > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0

	Eğer lc_icra > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0

	Eğer tr_kalan_net > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Net Kazanç"
	6	debit				----->	0
	7	credit				----->	tr_kalan_net

	Eğer lc_ssk_isci > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_prim_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşçi Payı"
	6	debit				----->	0
	7	credit				----->	lc_ssk_isci

	Eğer od_ssk_isveren > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_prim_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşveren Payı"
	6	debit				----->	0
	7	credit				----->	od_ssk_isveren

	Eğer lc_iss_p_isci > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_isz_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşçi İşsizlik Sigortası Payı"
	6	debit				----->	0
	7	credit				----->	lc_iss_p_isci

	Eğer iss_p_isveren > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_isz_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşveren İşsizlik sigortası Payı"
	6	debit				----->	0
	7	credit				----->	iss_p_isveren

	Eğer lc_damga_v > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	d_vergi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_damga_v

	Eğer lc_gel_ver > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	g_vergi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_gel_ver

	Eğer ssk_tesviki > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	haz_kat_payi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Hazine Katkı Payı"
	6	debit				----->	0
	7	credit				----->	ssk_tesviki

	Eğer lc_oto_kat_bes > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	bes_kesinti_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_oto_kat_bes

	Eğer lc_icra > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	icra_kesinti_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_icra
	
	
## Seçenek 3 eğer tr_maas_hesabi = 'tipc' ise aşağıdaki gibi satırlar eklenir; (aylık yada günlük ve maaş2 var)

	lc_tckn & lc_donem; table [luca_bordro] [id] eşit değildir lc_id olan table [luca_bordro] tablosunda (lc_tckn & lc_donem) = (table [luca_bordro] [tckn]  & table [luca_bordro] [donem] )eşleşmesini sağlayan tüm satırların; ([n_odenen] + [oto_kat_bes] + [icra] + [avans]) toplamları alınır, tr_bordro_net_toplamı değişkenine atanır.
	
	var tr_bordro_net_toplamı = lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans
	
	var tr_net_maas_tutar = ppg_yol + ppg_prim + ppg_ikramiye + ppg_bayram + ppg_kira + tr_normal_calisma_tutar + tr_fazla_calisma_tutar + tr_resmi_tatil_tutar + tr_hafta_tatili_tutar + tr_tatil_calismasi_tutar + tr_yillik_izin_gun_tutar
	
	var tr_elden_kalan = tr_net_maas_tutar - tr_bordro_net_toplamı
	
	var tr_elden_kalan_yuvarlanmis = tr_elden_kalan 'ın 100 'e yuvarlanması ile elde edilir.
	
	var tr_elden_yuvarlamasi = tr_elden_kalan - tr_elden_kalan_yuvarlanmis
	
		Eğer tr_elden_yuvarlamasi > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Elden Yuvarlama"
	6	debit				----->	tr_elden_yuvarlamasi
	7	credit				----->	0

	Eğer tr_elden_yuvarlamasi < 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Elden Yuvarlama"
	6	debit				----->	0
	7	credit				----->	|tr_elden_yuvarlamasi|

	Eğer tr_elden_kalan_yuvarlanmis > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Elden Ödenen"
	6	debit				----->	tr_elden_kalan_yuvarlanmis
	7	credit				----->	0

	Eğer lc_n_odenen > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Net Ödenen"
	6	debit				----->	lc_n_odenen
	7	credit				----->	0
	
	Eğer lc_icra > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0
	
	Eğer lc_oto_kat_bes > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0
	
	Eğer lc_avans > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Avans Kesintisi"
	6	debit				----->	lc_avans
	7	credit				----->	0
	
	Eğer lc_gel_vers > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	lc_gel_ver
	7	credit				----->	0

	Eğer lc_damga_v > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	lc_damga_v
	7	credit				----->	0	
	
	Eğer lc_ssk_isci > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk İşçi Payı"
	6	debit				----->	lc_ssk_isci
	7	credit				----->	0	
	
	Eğer lc_iss_p_isci > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşçi Payı"
	6	debit				----->	lc_iss_p_isci
	7	credit				----->	0	

	Eğer lc_ssk_isveren > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk İşveren Payı"
	6	debit				----->	lc_ssk_isveren
	7	credit				----->	0
	
	Eğer lc_iss_p_isveren > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşveren Payı"
	6	debit				----->	lc_iss_p_isveren
	7	credit				----->	0

	Eğer lc_oto_kat_bes > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0

	Eğer lc_icra > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0

	Eğer tr_normal_calisma_tutar > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Normal Çalışması"
	6	debit				----->	0
	7	credit				----->	tr_normal_calisma_tutar
	
	Eğer tr_fazla_calisma_tutar > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Fazla Çalışması"
	6	debit				----->	0
	7	credit				----->	tr_fazla_calisma_tutar
	
	Eğer tr_resmi_tatil_tutar > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Resmi Tatili"
	6	debit				----->	0
	7	credit				----->	tr_resmi_tatil_tutar
	
	Eğer tr_hafta_tatili_tutar > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Hafta Tatili"
	6	debit				----->	0
	7	credit				----->	tr_hafta_tatili_tutar
	
	Eğer tr_tatil_calismasi_tutar > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Tatil Çalışması"
	6	debit				----->	0
	7	credit				----->	tr_tatil_calismasi_tutar
	
	Eğer tr_yillik_izin_gun_tutar > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Yıllık İzin"
	6	debit				----->	0
	7	credit				----->	tr_yillik_izin_gun_tutar
	
	Eğer ppg_kira > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Kira Ödemesi"
	6	debit				----->	0
	7	credit				----->	ppg_kira
	
	Eğer ppg_bayram > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bayram Ödemesi"
	6	debit				----->	0
	7	credit				----->	ppg_bayram
	
	Eğer ppg_ikramiye > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İkramiye"
	6	debit				----->	0
	7	credit				----->	ppg_ikramiye
	
	Eğer ppg_prim > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Prim"
	6	debit				----->	0
	7	credit				----->	ppg_prim
	
	Eğer ppg_yol > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Yol Ödemesi"
	6	debit				----->	0
	7	credit				----->	ppg_yol
	

	Eğer lc_ssk_isci > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_prim_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşçi Payı"
	6	debit				----->	0
	7	credit				----->	lc_ssk_isci

	Eğer od_ssk_isveren > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_prim_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşveren Payı"
	6	debit				----->	0
	7	credit				----->	od_ssk_isveren

	Eğer lc_iss_p_isci > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_isz_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşçi İşsizlik Sigortası Payı"
	6	debit				----->	0
	7	credit				----->	lc_iss_p_isci

	Eğer iss_p_isveren > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_isz_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İşveren İşsizlik sigortası Payı"
	6	debit				----->	0
	7	credit				----->	iss_p_isveren

	Eğer lc_damga_v > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	d_vergi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_damga_v

	Eğer lc_gel_ver > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	g_vergi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_gel_ver

	Eğer ssk_tesviki > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	haz_kat_payi_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Hazine Katkı Payı"
	6	debit				----->	0
	7	credit				----->	ssk_tesviki

	Eğer lc_oto_kat_bes > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	bes_kesinti_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"Bes Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_oto_kat_bes

	Eğer lc_icra > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	icra_kesinti_acc_id
	4	contact_id			----->	tr_per_id
	5	description	text	----->	"İcra Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_icra
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	5535 740.00100
	5556 770.00100

	      BORÇ: 740.00100 - İşçi Ücret ve Giderleri
        - Net Ödenen
        - İcra, BES, Avans
        - Gelir Vergisi, Damga Vergisi
        - SSK İşçi, İşsizlik İşçi
        - SSK İşveren, İşsizlik İşveren
      102.00001 - Kuveytturk Hesap No:8934435,Ek No:1
      ALACAK:
        - 335.XXXXX BES
		- 335.XXXXX İcra
		- 335.XXXXX Net Ödenen)
		- 335.XXXXX Avans
		- 196.00001 Bankadan Ödenen Avans
        - 361.00001 (SSK İşçi)
        - 361.00002 (SSK İşveren)
        - 361.00003 (İşsizlik İşçi)
        - 361.00004 (İşsizlik İşveren)
        - 369.00001 (BES)
        - 369.00002 (İcra)
        - 196 (Avans)
        - 360.00004 (Gelir Vergisi)
        - 360.00005 (Damga Vergisi)
        - 602.00003 (SSK Teşviki - varsa)
		
		Net Ödenen
		İcra	
		Bes	
		Avans
		Gelir Vergisi	
		Damga Vergisi	
		Ssk İşçi Payı	
		İşsizlik Sigortası İşçi Payı
		Ssk İşveren Payı	
		İşsizlik Sigortası İşveren Payı	
		Elden Ücretler
		
		ssk_m				----->excel [luca_bordro] [[SSK M.]
ssk_isci			----->excel [luca_bordro] [[SSK İşçi]
iss_p_isci			----->excel [luca_bordro] [[İşs.P.İşçi]
g_v_m				----->excel [luca_bordro] [[G.V.M]
gel_ver				----->excel [luca_bordro] [[Gel.Ver.]
damga_v				----->excel [luca_bordro] [[Damga V]
oz_kesinti			----->excel [luca_bordro] [[Öz.Kesinti]
n_odenen			----->excel [luca_bordro] [[N.Ödenen]
isveren_maliyeti	----->excel [luca_bordro] [[İşveren Maliyeti]
ssk_isveren			----->excel [luca_bordro] [[SSK İşveren]
iss_p_isveren		----->excel [luca_bordro] [[İşs.P.İşveren]
kanun				----->excel [luca_bordro] [[Kanun]
ssk_tesviki			----->excel [luca_bordro] [[SSK Teşviki]
oto_kat_bes			----->excel [luca_bordro] [[Oto.Kat.BES]
icra				----->excel [luca_bordro] [[icra]
avans				----->excel [luca_bordro] [[Avans]
imza	




728 360.00004 Gelir Vergisi
729 360.00005 Damga Vergisi
731 361.00001 İşçi SSK Payı
732 361.00002 İşveren SSK Payı
733 361.00003 İşçi İşsizlik Sigortası Payı
734 361.00004 İşveren İşsizlik Sigortası Payı
735 369.00001 BES Kesintileri

var g_vergi_acc_id = 728
var d_vergi_acc_id = 729
var sgk_isci_prim_acc_id = 731
var sgk_isveren_prim_acc_id = 732
var sgk_isci_isz_acc_id = 733
var sgk_isveren_isz_acc_id = 734
var bes_kesinti_acc_id = 735
var icra_kesinti_acc_id = 736
