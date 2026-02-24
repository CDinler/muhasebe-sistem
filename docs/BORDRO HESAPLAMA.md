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
	

	

	
	var tr_gunluk_ucret = (tr_maas2_tutar / 30 if tr_ucret_nevi in ['aylik', 'sabit aylik'] 
                   else tr_maas2_tutar if tr_ucret_nevi == 'gunluk' 
                   else 0)
				   
	var tr_normal_calisma_tutar	= tr_gunluk_ucret * ppg_normal_calismasi
	var tr_fazla_calisma_tutar	= tr_gunluk_ucret / 8 * ppg_fazla_calismasi * tr_fm_orani
	var tr_tatil_tutar			= tr_gunluk_ucret * (ppg_resmi_tatil + ppg_hafta_tatili + ppg_tatil_calismasi)
	var tr_tatil_calismasi_tutar= tr_gunluk_ucret * ppg_tatil_calismasi * tr_tatil_orani
	var tr_yillik_izin_gun_tutar= tr_gunluk_ucret * ppg_yillik_izin_gun
	
	
	Aynı personnel_id lerin bordrolarındaki toplam (lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans ) toplamı tr_bordro_net_toplamı değişkenine atanır.
	
	var tr_bordro_net_toplamı = toplam (lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans ) 'personelin tüm bor
	var tr_net_maas_tutar = ppg_yol + ppg_prim + ppg_ikramiye + ppg_bayram + ppg_kira + tr_normal_calisma_tutar + tr_fazla_calisma_tutar + tr_tatili_tutar + tr_tatil_calismasi_tutar + tr_yillik_izin_gun_tutar
	
	
	var tr_elden_kalan = tr_net_maas_tutar - tr_bordro_net_toplamı
	var tr_elden_kalan_yuvarlanmis = tr_elden_kalan 'ın 100 'e yuvarlanması ile elde edilir.
	var tr_elden_yuvarlamasi = tr_elden_kalan - tr_elden_kalan_yuvarlanmis
	


	* transaction değerleri
	var tr_no 					= transaction_number değerini üretin motordan yeni değeri alır
	
	var tr_date					= (lc_yıl ve lc_ay değikkenlerinden üertilen ayın on günü örn. 30.11.2025 gibi)
	
	

	
	
	*table [personnel_contracts] değişkenleri atama
	pc_id & lc_giris_t arihleri ,table[personnel_contracts] tablosunda [personnel_id] ve [ise_giris_tarihi] sütünlarında eşleşen satırdan,
	(yada luca_bordro tablosu contract_id sütunu ile eşleşen personnel_contracts tablosundan aşağıdaki değerler çekilir.)
	
	var tr_contracts_id			= table[personnel_contracts][id]
	var tr_cc_id				= table[personnel_contracts][cost_center_id]
	var tr_maas_hesabi			= table[personnel_contracts][maas_hesabi]
	var tr_maas2_tutar			= table[personnel_contracts][maas2_tutar]
	var tr_ucret_nevi			= table[personnel_contracts][ucret_nevi] 'enum (aylik, sabit aylik, gunluk)
	var tr_fm_orani				= table[personnel_contracts][fm_orani]
	var tr_tatil_orani			= table[personnel_contracts][tatil_orani]
	var tr_taseron_id			= table[personnel_contracts][taseron_id]
	var tr_bolum				= table[personnel_contracts][bolum]
	
	
	*table [personnel] değişkenleri atama
	personnel_contracts tablosunda personnel_id sütunu ile eşleşen personnel tablosundan aşağıdaki değerler çekilir.
	
	var tr_per_id				= table[personnel][id]
	var tr_per_ad				= table[personnel][ad]
	var tr_per_soyad			= table[personnel][soyad]
	var tr_per_acc_id			= table [personnel][accounts_id]
	var tr_iban					= table [personnel][iban]
	
	
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
	var pe_accounts_id			= personel tablosu accounts_id
	
	* transaction_lines diğer bordro hesaplamaları
	
	var od_ssk_isveren = lc_ssk_isveren - lc_ssk_tesviki


# YEVMİYE KAYITLARININ İŞLENMESİ


ADIM 1 - Her luca bordro için aşağıdaki kayıtlar yapılır (RESMİ KAYITLAR);

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


## RESMİ KAYIT

her luca_bordro için oluşturulacak.

--------------------------------------------------------------------------	
------------------------------ ALACAK KAYDI ------------------------------
--------------------------------------------------------------------------


	Eğer lc_n_odenen > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Net Ödenen"
	6	debit				----->	lc_n_odenen
	7	credit				----->	0
	
	Eğer lc_icra > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0
	
	Eğer lc_oto_kat_bes > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0
	
	Eğer lc_avans > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Avans Kesintisi"
	6	debit				----->	lc_avans
	7	credit				----->	0
	
	Eğer lc_gel_vers > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	lc_gel_ver
	7	credit				----->	0

	Eğer lc_damga_v > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	lc_damga_v
	7	credit				----->	0	
	
	Eğer lc_ssk_isci > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Ssk İşçi Payı"
	6	debit				----->	lc_ssk_isci
	7	credit				----->	0	
	
	Eğer lc_iss_p_isci > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşçi Payı"
	6	debit				----->	lc_iss_p_isci
	7	credit				----->	0	

	Eğer lc_ssk_isveren > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Ssk İşveren Payı"
	6	debit				----->	lc_ssk_isveren
	7	credit				----->	0
	
	Eğer lc_iss_p_isveren > 0 ise ;	
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İşsizlik Sigortası İşveren Payı"
	6	debit				----->	lc_iss_p_isveren
	7	credit				----->	0

	Eğer lc_oto_kat_bes > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Bes Kesintisi"
	6	debit				----->	lc_oto_kat_bes
	7	credit				----->	0

	Eğer lc_icra > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İcra Kesintisi"
	6	debit				----->	lc_icra
	7	credit				----->	0



--------------------------------------------------------------------------
------------------------------ BORÇ KAYDI ------------------------------
--------------------------------------------------------------------------
	Eğer lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Net Kazanç"
	6	debit				----->	0
	7	credit				----->	lc_n_odenen + lc_oto_kat_bes + lc_icra + lc_avans

	Eğer lc_ssk_isci > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_prim_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşçi Payı"
	6	debit				----->	0
	7	credit				----->	lc_ssk_isci

	Eğer od_ssk_isveren > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_prim_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Ssk Ödenecek İşveren Payı"
	6	debit				----->	0
	7	credit				----->	od_ssk_isveren

	Eğer lc_iss_p_isci > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isci_isz_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İşçi İşsizlik Sigortası Payı"
	6	debit				----->	0
	7	credit				----->	lc_iss_p_isci

	Eğer iss_p_isveren > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	sgk_isveren_isz_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İşveren İşsizlik sigortası Payı"
	6	debit				----->	0
	7	credit				----->	iss_p_isveren

	Eğer lc_damga_v > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	d_vergi_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Damga Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_damga_v

	Eğer lc_gel_ver > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	g_vergi_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Gelir Vergisi"
	6	debit				----->	0
	7	credit				----->	lc_gel_ver

	Eğer ssk_tesviki > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	haz_kat_payi_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Hazine Katkı Payı"
	6	debit				----->	0
	7	credit				----->	ssk_tesviki

	Eğer lc_oto_kat_bes > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	bes_kesinti_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"Bes Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_oto_kat_bes

	Eğer lc_icra > 0 ise ;

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	icra_kesinti_acc_id
	4	personnel_id		----->	tr_per_id
	5	description	text	----->	"İcra Kesintileri"
	6	debit				----->	0
	7	credit				----->	lc_icra





## TASLAK KAYIT

ADIM 2 - draft contratı olan personellerin aşağıadaki kayıtları da olacak.

	
	
	Eğer tr_elden_yuvarlamasi > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	personnel_id			----->	tr_per_id
	5	description	text	----->	"Elden Yuvarlama"
	6	debit				----->	tr_elden_yuvarlamasi
	7	credit				----->	0

	Eğer tr_elden_yuvarlamasi < 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	personnel_id			----->	tr_per_id
	5	description	text	----->	"Elden Yuvarlama"
	6	debit				----->	0
	7	credit				----->	|tr_elden_yuvarlamasi|

	Eğer tr_elden_kalan_yuvarlanmis > 0 ise ;
	
	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	maliyet_acc_id
	4	personnel_id			----->	tr_per_id
	5	description	text	----->	"Elden Ödenen"
	6	debit				----->	tr_elden_kalan_yuvarlanmis
	7	credit				----->	0

	
	Eğer tr_elden_kalan > 0 ise ;	

	table [transaction_lines]
	1	id					----->	PRIMARY (AUTO_INCREMENT)
	2	transaction_id		----->	tr_id
	3	account_id			----->	pe_accounts_id
	4	personnel_id			----->	tr_per_id
	5	description	text	----->	"Kalan Ödemesi"
	6	debit				----->	0
	7	credit				----->	tr_elden_kalan