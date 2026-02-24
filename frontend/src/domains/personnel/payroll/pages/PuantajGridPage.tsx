import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  DatePicker, 
  message, 
  Space, 
  Upload, 
  Table, 
  Select,
  Spin,
  Tooltip,
  Typography,
  Modal,
  Dropdown,
  Tabs,
  Input
} from 'antd';
import { 
  SaveOutlined,
  UploadOutlined,
  DownloadOutlined,
  ReloadOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import apiClient from '@/services/api';
import dayjs, { Dayjs } from 'dayjs';
import 'dayjs/locale/tr';
import type { ColumnsType } from 'antd/es/table';

dayjs.locale('tr');

const { Title } = Typography;
const { Option } = Select;

// Durum kodları - Luca ile uyumlu
const DURUM_KODLARI = [
  { kod: 'N', aciklama: 'Normal', color: '#52c41a' },
  { kod: 'H', aciklama: 'Hafta Tatili', color: '#722ed1' },
  { kod: 'T', aciklama: 'Resmi Tatil', color: '#ff4d4f' },
  { kod: 'İ', aciklama: 'İzinli', color: '#faad14' },
  { kod: 'S', aciklama: 'Yıllık İzin', color: '#fa8c16' },
  { kod: 'R', aciklama: 'Raporlu', color: '#f5222d' },
  { kod: 'E', aciklama: 'Eksik Gün', color: '#ff7875' },
  { kod: 'Y', aciklama: 'Yarım Gün', color: '#ffc53d' },
  { kod: 'M', aciklama: 'Tatil Çalışması', color: '#13c2c2' },
  { kod: '-', aciklama: 'Sigortasız Günler', color: '#8c8c8c' },
];

interface PersonelRow {
  id: number;
  contract_id?: number;  // Contract ID - puantaj kaydını bu contract'a bağla
  draft_contract_id?: number;  // Draft Contract ID - hesaplama için gerekli
  sicil_no: string;
  adi_soyadi: string;
  tckn: string;
  cost_center_id?: number;
  toplam_fm?: number;
  disabled_days?: number[];  // Personelin çalışmadığı günler
  ise_giris_tarihi?: string;
  isten_cikis_tarihi?: string;
  row_type?: 'header' | 'data';
  departman?: string;
  taseron_name?: string;  // Taşeron firma adı
  meslek_adi?: string;  // Meslek adı (monthly_personnel_records'dan)
  calisma_takvimi?: string;  // Çalışma takvimi (atipi, btipi, ctipi)
  ucret_nevi?: string;  // Ücret nevi (aylik, sabit aylik, gunluk)
  fm_orani?: number;  // FM oranı
  tatil_orani?: number;  // Tatil oranı
  net_brut?: string;  // Bordro net/brüt
  ucret?: number;  // Bordro ücret
  maas2_tutar?: number;  // Maaş2 tutarı
  [key: string]: any; // gun_1, gun_2, ... gun_31 + fm_gun_1, fm_gun_2, ... fm_gun_31
}

const PuantajGridPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<PersonelRow[]>([]);
  const [allData, setAllData] = useState<PersonelRow[]>([]);
  const [editedCells, setEditedCells] = useState<Set<string>>(new Set());
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [selectedCostCenter, setSelectedCostCenter] = useState<number | null>(null);
  const [selectedDepartment, setSelectedDepartment] = useState<string | null>(null);
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [holidayDays, setHolidayDays] = useState<number[]>([]);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedPersonel, setSelectedPersonel] = useState<PersonelRow | null>(null);
  const [earningsInputs, setEarningsInputs] = useState({
    yol: 0,
    prim: 0,
    ikramiye: 0,
    bayram: 0,
    kira: 0
  });
  const [systemFmOrani, setSystemFmOrani] = useState<number>(1.5);
  const [systemTatilOrani, setSystemTatilOrani] = useState<number>(2.0);

  const donem = React.useMemo(() => selectedDate.format('YYYY-MM'), [selectedDate]);
  const ayin_toplam_gun_sayisi = selectedDate.daysInMonth();

  const fetchData = React.useCallback(async () => {
    // Cost center seçilmediyse veri yükleme
    if (!selectedCostCenter) {
      setData([]);
      setAllData([]);
      setHolidayDays([]);
      return;
    }
    
    setLoading(true);
    try {
      const params: any = { donem, cost_center_id: selectedCostCenter };
      
      const response = await apiClient.get('/personnel/puantaj-grid/', { params });
      const records = response.data.records || [];
      const holidays = response.data.holidays || [];
      
      // DEBUG: İlk 3 personelin draft_contract_id'sini kontrol et
      console.log('🔍 İlk 3 personel draft_contract_id:');
      records.slice(0, 3).forEach((r: any, index: number) => {
        console.log(`  [${index}] ${r.adi_soyadi}:`, {
          draft_contract_id: r.draft_contract_id,
          maas2_tutar: r.maas2_tutar,
          row_type: r.row_type
        });
      });
      
      // Header satırlarını filtrele, sadece data satırlarını al
      const dataRecords = records.filter((r: any) => r.row_type !== 'header' && r.row_type !== 'taseron_header');
      setAllData(dataRecords);
      // Departman filtresini uygula
      const filteredRecords = selectedDepartment 
        ? dataRecords.filter((r: any) => r.departman === selectedDepartment)
        : dataRecords;
      setData(filteredRecords);
      setHolidayDays(holidays);
      setEditedCells(new Set());
    } catch (error: any) {
      console.error('Puantaj veri yükleme hatası:', error);
      message.error('Veri yüklenemedi: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  }, [donem, selectedCostCenter]);

  useEffect(() => {
    const loadCostCenters = async () => {
      try {
        const response = await apiClient.get('/partners/cost-centers/', { params: { is_active: true } });
        const centers = response.data?.items || response.data || [];
        setCostCenters(centers);
      } catch (error) {
        console.error('Maliyet merkezleri yüklenemedi:', error);
      }
    };
    loadCostCenters();
  }, []);

  // Sistem ayarlarını yükle (FM ve Tatil oranları)
  useEffect(() => {
    const loadSystemConfigs = async () => {
      try {
        const response = await apiClient.get('/settings/config/configs');
        const configs = response.data;
        
        // GENEL kategorisindeki FM ve Tatil oranlarını bul
        if (configs.GENEL) {
          const fmConfig = configs.GENEL.find((c: any) => c.key === 'FM_ORANI');
          const tatilConfig = configs.GENEL.find((c: any) => c.key === 'TATIL_ORANI');
          
          if (fmConfig) setSystemFmOrani(parseFloat(fmConfig.value) || 1.5);
          if (tatilConfig) setSystemTatilOrani(parseFloat(tatilConfig.value) || 2.0);
        }
      } catch (error) {
        console.error('Sistem ayarları yüklenemedi:', error);
        // Varsayılan değerler zaten state'te
      }
    };
    
    loadSystemConfigs();
  }, []);

  useEffect(() => {
    fetchData();
  }, [donem, selectedCostCenter]);

  // Departman filtresi değiştiğinde veriyi filtrele
  useEffect(() => {
    if (selectedDepartment) {
      setData(allData.filter((r: any) => r.departman === selectedDepartment));
    } else {
      setData(allData);
    }
  }, [selectedDepartment, allData]);

  const handleCellChange = (personnelId: number, gunNo: number, value: string | number | null, type: 'durum' | 'fm' = 'durum') => {
    const cellKey = type === 'durum' ? `${personnelId}_${gunNo}` : `${personnelId}_fm_${gunNo}`;
    setEditedCells(prev => new Set(prev).add(cellKey));
    
    const fieldName = type === 'durum' ? `gun_${gunNo}` : `fm_gun_${gunNo}`;
    
    // Hem filtrelenmiş data'yı hem de allData'yı güncelle
    setData(prevData => 
      prevData.map(row => 
        row.id === personnelId 
          ? { ...row, [fieldName]: value }
          : row
      )
    );
    
    setAllData(prevData => 
      prevData.map(row => 
        row.id === personnelId 
          ? { ...row, [fieldName]: value }
          : row
      )
    );
  };

  // Personel için özet değerleri ve kazanç hesapla (optimize edilmiş)
  const calculateSummaryForPersonel = (
    personel: PersonelRow, 
    includeEarnings: boolean = false, 
    earningsData?: any,
    defaultFmOrani: number = 1.5,
    defaultTatilOrani: number = 2.0
  ) => {
    let calisilan_gun_sayisi = 0;
    let yillik_izin_gun = 0;
    let izin_gun_sayisi = 0;
    let rapor_gun_sayisi = 0;
    let yarim_gun_sayisi = 0;
    let eksik_gun_sayisi = 0;
    let tatil_calismasi = 0;
    let sigorta_girmedigi = 0;
    let hafta_tatili = 0;
    let resmi_tatil = 0;
    let gece_calismasi = 0;
    let fazla_calismasi = 0;
    let eksik_calismasi = 0; // Eksik mesai (fm_sum_base < 0 ise)

    for (let i = 1; i <= ayin_toplam_gun_sayisi; i++) {
      const val = personel[`gun_${i}`];
      const fm = personel[`fm_gun_${i}`];
      
      if (val === 'N') calisilan_gun_sayisi++;
      else if (val === 'S') yillik_izin_gun++;
      else if (val === 'İ') izin_gun_sayisi++;
      else if (val === 'R') rapor_gun_sayisi++;
      else if (val === 'Y') yarim_gun_sayisi += 0.5;
      else if (val === 'E') eksik_gun_sayisi++;
      else if (val === 'M') tatil_calismasi++;
      else if (val === 'H') hafta_tatili++;
      else if (val === 'T') resmi_tatil++;
      else if (val === 'G') gece_calismasi++;
      else if (val === '-') sigorta_girmedigi++;

      if (fm) fazla_calismasi += parseFloat(fm);
    }
    
    // Eksik mesai hesaplama - fm_sum_base negatifse eksik mesai var
    if (fazla_calismasi < 0) {
      eksik_calismasi = Math.abs(fazla_calismasi); // Mutlak değer
      fazla_calismasi = 0; // Fazla mesai 0
    }
    
    const tatiller = hafta_tatili + resmi_tatil + tatil_calismasi;
    const toplam_gun_sayisi = ayin_toplam_gun_sayisi - sigorta_girmedigi;
    const ssk_gun_sayisi = toplam_gun_sayisi - eksik_gun_sayisi;

    // Normal çalışma hesabı - aylık/sabit aylık ise ve tam ay çalıştıysa 30 gün
    const ucret_nevi = personel.ucret_nevi;
    // İzin günlerini 30 ile sınırla
    const izin_gun_sinirli = Math.min(izin_gun_sayisi, 30);
    const normal_calismasi = 
      ((ucret_nevi === 'aylik' || ucret_nevi === 'sabit aylik') && 
       eksik_gun_sayisi === 0 && ayin_toplam_gun_sayisi !== 30 && sigorta_girmedigi === 0 && rapor_gun_sayisi=== 0 && yarim_gun_sayisi=== 0)
      ? 30 - tatiller - izin_gun_sinirli - yillik_izin_gun
      : calisilan_gun_sayisi + yarim_gun_sayisi;

    // Temel özet
    const summary = {
      calisilan_gun_sayisi,
      ssk_gun_sayisi,
      yillik_izin_gun,
      izin_gun_sayisi,
      rapor_gun_sayisi,
      eksik_gun_sayisi,
      yarim_gun_sayisi,
      toplam_gun_sayisi,
      normal_calismasi,
      fazla_calismasi,
      eksik_calismasi, // Eksik mesai saati
      gece_calismasi,
      tatil_calismasi,
      sigorta_girmedigi,
      hafta_tatili,
      resmi_tatil,
      tatiller,
      // Ek ödemeler - personel objesinden al (modal'da girilmiş olabilir)
      yol: personel.yol || 0,
      prim: personel.prim || 0,
      ikramiye: personel.ikramiye || 0,
      bayram: personel.bayram || 0,
      kira: personel.kira || 0
    };

    // Kazanç hesaplamaları (sadece detay modal için)
    if (includeEarnings) {
      const maas2 = personel.maas2_tutar;
      // Personelin oranı varsa onu kullan, yoksa sistem ayarlarındaki varsayılan oranı kullan
      const fm_orani = personel.fm_orani || defaultFmOrani;
      const tatil_orani = personel.tatil_orani || defaultTatilOrani;
      
      let gunluk_kazanc = 0;
      let normal_kazanc = 0;
      let mesai_kazanc = 0;
      let eksik_kazanc = 0; // Eksik mesai kesintisi
      let tatil_kazanc = 0;
      let tatil_mesai_kazanc = 0;
      let yillik_izin_kazanc = 0;
      
      if (personel.draft_contract_id) {
        gunluk_kazanc = (ucret_nevi === 'aylik' || ucret_nevi === 'sabit aylik') ? maas2 / 30 : maas2;
        normal_kazanc = normal_calismasi * gunluk_kazanc;
        mesai_kazanc = (fazla_calismasi * gunluk_kazanc / 8) * fm_orani;
        eksik_kazanc = (eksik_calismasi * gunluk_kazanc / 8); // Eksik mesai kesintisi (oran yok)
        tatil_kazanc = tatiller * gunluk_kazanc;
        tatil_mesai_kazanc = tatil_calismasi * gunluk_kazanc * tatil_orani;
        yillik_izin_kazanc = yillik_izin_gun * gunluk_kazanc; // Yıllık izin kazancı
      }
      
      const earnings = earningsData || { yol: 0, prim: 0, ikramiye: 0, bayram: 0, kira: 0 };
      const toplam_kazanc = normal_kazanc + mesai_kazanc - eksik_kazanc + tatil_kazanc + tatil_mesai_kazanc + 
        yillik_izin_kazanc + earnings.yol + earnings.prim + earnings.ikramiye + earnings.bayram + earnings.kira;

      return {
        ...summary,
        maas2,
        fm_orani,
        tatil_orani,
        gunluk_kazanc,
        normal_kazanc,
        mesai_kazanc,
        eksik_kazanc, // Eksik mesai kesintisi
        tatil_kazanc,
        tatil_mesai_kazanc,
        yillik_izin_kazanc, // Yıllık izin kazancı
        toplam_kazanc,
        // Maas2 alanları (backend'e kaydetmek için)
        maas2_gunluk_kazanc: gunluk_kazanc,
        maas2_normal_kazanc: normal_kazanc,
        maas2_mesai_kazanc: mesai_kazanc,
        maas2_eksik_kazanc: eksik_kazanc, // Yeni alan
        maas2_tatil_kazanc: tatil_kazanc,
        maas2_tatil_mesai_kazanc: tatil_mesai_kazanc,
        maas2_yillik_izin_kazanc: yillik_izin_kazanc, // Yıllık izin kazancı
        maas2_toplam_kazanc: toplam_kazanc
      };
    }

    return summary;
  };

  const handleSave = async () => {
    setSaving(true);
    message.loading({ content: 'Kaydediliyor...', key: 'save' });
    
    try {
      // Değişiklikleri allData'ya uygula (filtrelenmiş data'daki güncellemeleri birleştir)
      const updatedAllData = allData.map(row => {
        const filteredRow = data.find(r => r.id === row.id);
        const currentRow = filteredRow || row;
        
        // Her personel için özet değerleri ve kazanç hesaplamalarını yap
        const summary = calculateSummaryForPersonel(currentRow, true);  // includeEarnings: true
        
        return {
          ...currentRow,
          ...summary
        };
      });

      await apiClient.post('/personnel/puantaj-grid/save', {
        donem,
        records: updatedAllData  // Tüm kayıtları özet değerleriyle birlikte gönder
      });
      
      message.success({
        content: 'Puantaj başarıyla kaydedildi',
        key: 'save'
      });
      
      setEditedCells(new Set());
      await fetchData();
    } catch (error: any) {
      message.error({
        content: 'Kayıt hatası: ' + (error.response?.data?.detail || error.message),
        key: 'save'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleHaftaTatiliSec = (selectedDays: string[]) => {
    let degisiklikSayisi = 0;
    
    const updateRowsWithHolidays = (rows: PersonelRow[]) => rows.map(row => {
      const newRow = { ...row };
      for (let i = 1; i <= ayin_toplam_gun_sayisi; i++) {
        const tarih = dayjs(`${donem}-${String(i).padStart(2, '0')}`);
        const gunAdi = tarih.format('dddd');
        const gunKey = `gun_${i}`;
        const oldValue = newRow[gunKey];
        
        // Önce mevcut H'yi temizle
        if (oldValue === 'H') {
          newRow[gunKey] = '';
          degisiklikSayisi++;
        }
        
        // Sonra seçilen günleri H yap
        if (selectedDays.includes(gunAdi)) {
          if (oldValue !== 'H') {
            degisiklikSayisi++;
          }
          newRow[gunKey] = 'H';
          const cellKey = `${row.id}-gun_${i}`;
          setEditedCells(prev => new Set([...prev, cellKey]));
        }
      }
      return newRow;
    });
    
    setData(updateRowsWithHolidays(data));
    setAllData(updateRowsWithHolidays(allData));
    message.success(`Hafta tatili güncellendi - sadece seçilen günler işaretli`);
  };

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    message.loading({ content: 'Excel yükleniyor...', key: 'upload' });

    try {
      const response = await apiClient.post(`/personnel/puantaj-grid/upload?donem=${donem}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Backend parse edilmiş datayı döndürüyor (DB'ye kaydetmiyor)
      // Bu datayı mevcut tabloya merge ediyoruz
      const uploadedRecords = response.data.records || [];
      
      console.log('📤 Excel Upload Response:', {
        total: response.data.total,
        recordsCount: uploadedRecords.length,
        firstRecord: uploadedRecords[0]
      });
      
      if (uploadedRecords.length > 0) {
        // Mevcut data'yı kopyala
        const updatedData = [...data];
        const newEditedCells = new Set(editedCells);
        
        // Upload edilen her kayıt için
        uploadedRecords.forEach((uploadedRow: any) => {
          // Aynı personeli bul (personnel_id ile - en güvenilir yöntem)
          const existingIndex = updatedData.findIndex(
            row => row.id === uploadedRow.id
          );
          
          if (existingIndex >= 0) {
            // Mevcut personel varsa, SADECE gün değerlerini güncelle
            const existing = updatedData[existingIndex];
            
            // Gün değerleri (gun_1...gun_31)
            for (let gun = 1; gun <= 31; gun++) {
              const gunKey = `gun_${gun}`;
              if (uploadedRow[gunKey] !== undefined && uploadedRow[gunKey] !== null) {
                existing[gunKey] = uploadedRow[gunKey];
                // Excel'den gelen değişiklikleri editedCells'e ekle (Kaydet butonunu aktif et)
                newEditedCells.add(`${existing.id}-${gunKey}`);
              }
            }
            
            // FM değerleri (fm_gun_1...fm_gun_31)
            for (let gun = 1; gun <= 31; gun++) {
              const fmGunKey = `fm_gun_${gun}`;
              if (uploadedRow[fmGunKey] !== undefined && uploadedRow[fmGunKey] !== null) {
                existing[fmGunKey] = uploadedRow[fmGunKey];
                // Excel'den gelen değişiklikleri editedCells'e ekle (Kaydet butonunu aktif et)
                newEditedCells.add(`${existing.id}-${fmGunKey}`);
              }
            }
            
            // Hesaplanan alanlar Excel'den gelmez - detay modalında girilir
            // Bu sayede duplikasyon olmaz ve hesaplamalar kaybolmaz
          }
          // NOT: Excel'de olup tabloda olmayan personel EKLENMEZ
          // Tabloda zaten tüm personel var (fetchData'dan geliyor)
          // Excel sadece mevcut personellerin gun/fm değerlerini güncellemek içindir
        });
        
        // State'i güncelle
        setData(updatedData);
        setAllData(updatedData);
        setEditedCells(newEditedCells);
        
        message.success({
          content: `${uploadedRecords.length} personel Excel'den yüklendi. Kaydetmek için 'Kaydet' butonuna basın.`,
          key: 'upload',
          duration: 5
        });
      } else {
        message.warning({
          content: 'Excel dosyasında veri bulunamadı',
          key: 'upload'
        });
      }

      setUploadModalVisible(false);
    } catch (error: any) {
      message.error({
        content: 'Upload hatası: ' + (error.response?.data?.detail || error.message),
        key: 'upload'
      });
    }

    return false;
  };

  const handleDownloadTemplate = async () => {
    if (!selectedCostCenter) {
      message.warning('Lütfen önce bir şantiye seçin');
      return;
    }

    message.loading({ content: 'Şablon hazırlanıyor...', key: 'template' });

    try {
      const response = await apiClient.get(
        `/personnel/puantaj-grid/template/download?donem=${donem}&cost_center_id=${selectedCostCenter}`,
        { responseType: 'blob' }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `puantaj_sablonu_${donem}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      message.success({
        content: 'Şablon indirildi',
        key: 'template'
      });
    } catch (error: any) {
      message.error({
        content: 'Şablon indirme hatası: ' + (error.response?.data?.detail || error.message),
        key: 'template'
      });
    }
  };

  // Excel benzeri kolonlar - ULTRA KOMPAKT (Luca gibi)
  const getColumns = (): ColumnsType<PersonelRow> => {
    const fixedColumns: ColumnsType<PersonelRow> = [
      {
        title: 'Personel',
        dataIndex: 'adi_soyadi',
        key: 'adi_soyadi',
        fixed: 'left',
        width: 200,
        ellipsis: false,
        render: (text, record) => {
          return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span style={{ fontSize: '11px', fontWeight: 500 }}>{text}</span>
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                {record.departman && (
                  <span style={{ 
                    fontSize: '9px', 
                    color: '#666',
                    backgroundColor: '#f0f0f0',
                    padding: '1px 4px',
                    borderRadius: '2px',
                    display: 'inline-block',
                    width: 'fit-content'
                  }}>
                    {record.departman}
                  </span>
                )}
                {record.taseron_name && (
                  <span style={{ 
                    fontSize: '9px', 
                    color: '#1890ff',
                    backgroundColor: '#e6f7ff',
                    padding: '1px 4px',
                    borderRadius: '2px',
                    display: 'inline-block',
                    width: 'fit-content',
                    border: '1px solid #91d5ff'
                  }}>
                    {record.taseron_name.split(' ').slice(0, 2).join(' ')}
                  </span>
                )}
              </div>
            </div>
          );
        }
      },
    ];

    // Günlük kolonlar (1-31)
    const dayColumns: ColumnsType<PersonelRow> = [];
    const gunKisaltmalari: { [key: string]: string } = {
      'Pazartesi': 'Pt',
      'Salı': 'Sa',
      'Çarşamba': 'Ça',
      'Perşembe': 'Pe',
      'Cuma': 'Cu',
      'Cumartesi': 'Ct',
      'Pazar': 'Pz'
    };
    
    for (let i = 1; i <= ayin_toplam_gun_sayisi; i++) {
      const tarih = dayjs(`${donem}-${String(i).padStart(2, '0')}`);
      const gunTam = tarih.format('dddd');
      const gunKisa = gunKisaltmalari[gunTam] || gunTam.substring(0, 2);
      const isHoliday = holidayDays.includes(i);
      
      dayColumns.push({
        title: (
          <Tooltip title={tarih.format('DD MMMM YYYY dddd') + (isHoliday ? ' - RESMİ TATİL' : '')}>
            <div style={{ 
              textAlign: 'center', 
              lineHeight: '1.1', 
              fontSize: '9px',
              backgroundColor: isHoliday ? '#ff4d4f20' : 'transparent',
              padding: '2px',
              borderRadius: '2px'
            }}>
              <div style={{ fontWeight: 'normal', color: isHoliday ? '#ff4d4f' : 'inherit' }}>{gunKisa}</div>
              <div style={{ fontWeight: 'bold', color: isHoliday ? '#ff4d4f' : 'inherit' }}>{i}</div>
              {isHoliday && <div style={{ fontSize: '7px', color: '#ff4d4f' }}>T</div>}
            </div>
          </Tooltip>
        ),
        dataIndex: `gun_${i}`,
        key: `gun_${i}`,
        width: 26,
        align: 'center',
        render: (value: string, record: PersonelRow) => {
          // Departman başlığı satırlarında gün kolonlarını boş göster
          if (record.row_type === 'header') {
            return null;
          }
          
          const cellKey = `${record.id}_${i}`;
          const fmKey = `${record.id}_fm_${i}`;
          const isEdited = editedCells.has(cellKey) || editedCells.has(fmKey);
          const durumInfo = DURUM_KODLARI.find(d => d.kod === value);
          const fmValue = record[`fm_gun_${i}`];
          const isEditing = editingCell === cellKey;
          
          return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1px', width: '100%' }}>
              {/* Durum kodu */}
              {isEditing ? (
                <Select
                  value={value || undefined}
                  placeholder=""
                  style={{ width: '100%', fontSize: '11px', fontWeight: 'bold' }}
                  size="small"
                  variant="borderless"
                  popupMatchSelectWidth={110}
                  onChange={(newValue) => {
                    handleCellChange(record.id, i, newValue, 'durum');
                    setEditingCell(null);
                  }}
                  onBlur={() => setEditingCell(null)}
                  autoFocus
                  open={true}
                  suffixIcon={null}
                  removeIcon={null}
                  clearIcon={null}
                  menuItemSelectedIcon={false}
                  optionLabelProp="value"
                >
                  <Option value=""></Option>
                  {DURUM_KODLARI.map(durum => (
                    <Option key={durum.kod} value={durum.kod} label={durum.kod}>
                      <span style={{ color: durum.color, fontWeight: 'bold', fontSize: '10px' }}>
                        {durum.kod}
                      </span>
                      <span style={{ fontSize: '9px', marginLeft: '6px', color: '#666' }}>
                        {durum.aciklama}
                      </span>
                    </Option>
                  ))}
                </Select>
              ) : (
                <div
                  onClick={() => setEditingCell(cellKey)}
                  style={{
                    width: '100%',
                    height: '18px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: value === '-' ? '14px' : '11px',
                    fontWeight: 'bold',
                    color: value === '-' ? '#666' : (durumInfo?.color || '#999'),
                    userSelect: 'none'
                  }}
                >
                  {value || ''}
                </div>
              )}
              
              {/* Fazla mesai - sadece çalışılan günlerde göster */}
              {value && value === 'N' && (
                <input
                  type="text"
                  inputMode="decimal"
                  value={fmValue || ''}
                  placeholder=""
                  onChange={(e) => {
                    const val = e.target.value.replace(',', '.');
                    const num = val ? parseFloat(val) : null;
                    if (val === '' || (!isNaN(num!) && num! >= 0 && num! <= 24)) {
                      handleCellChange(record.id, i, num, 'fm');
                    }
                  }}
                  style={{
                    width: '100%',
                    height: '16px',
                    fontSize: '8px',
                    padding: '1px 2px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '2px',
                    textAlign: 'center',
                    backgroundColor: 'white'
                  }}
                />
              )}
            </div>
          );
        },
        onCell: (record: PersonelRow) => {
          const value = record[`gun_${i}`];
          
          // '-' değeri için özel stil (sigortası olmayan günler)
          if (value === '-') {
            return {
              style: {
                backgroundColor: '#e0e0e0',
                padding: '1px'
              }
            };
          }
          
          const durumInfo = DURUM_KODLARI.find(d => d.kod === value);
          return {
            style: {
              backgroundColor: durumInfo ? `${durumInfo.color}15` : 'transparent',
              padding: '1px',
            }
          };
        }
      });
    }

    // Özet kolonlar - Detay butonu
    const summaryColumns: ColumnsType<PersonelRow> = [
      {
        title: 'Detay',
        key: 'detay',
        width: 60,
        align: 'center',
        fixed: 'right',
        render: (_: any, record: PersonelRow) => (
          <Button
            type="primary"
            size="small"
            onClick={() => {
              setSelectedPersonel(record);
              setDetailModalVisible(true);
            }}
            style={{ fontSize: '9px', padding: '0 6px', height: '22px' }}
          >
            Detay
          </Button>
        )
      }
    ];

    return [...fixedColumns, ...dayColumns, ...summaryColumns];
  };

  return (
    <div style={{ padding: '8px', height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      <Card styles={{ body: { padding: '8px', height: '100%', display: 'flex', flexDirection: 'column' } }}>
        {/* Ultra Kompakt Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <Title level={4} style={{ margin: 0, fontSize: '14px' }}>
            <CalendarOutlined /> Puantaj Takip
          </Title>
          <Space size="small">
            <DatePicker
              picker="month"
              value={selectedDate}
              onChange={(date) => date && setSelectedDate(date)}
              format="MMM YYYY"
              allowClear={false}
              size="small"
            />
            <Select
              placeholder="⚠️ Önce Şantiye Seçin"
              style={{ width: 200 }}
              allowClear
              size="small"
              value={selectedCostCenter}
              onChange={setSelectedCostCenter}
              showSearch
              optionFilterProp="children"
            >
              {costCenters.map(cc => (
                <Option key={cc.id} value={cc.id}>
                  {cc.name}
                </Option>
              ))}
            </Select>
            <Select
              placeholder="Tüm Departmanlar"
              style={{ width: 160 }}
              allowClear
              size="small"
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              disabled={!selectedCostCenter}
            >
              {[...new Set(allData.map((r: any) => r.departman).filter(Boolean))].map((dept: any) => (
                <Option key={dept} value={dept}>
                  {dept}
                </Option>
              ))}
            </Select>
            <Dropdown
              menu={{
                items: [
                  { key: 'cumartesi-pazar', label: 'Cumartesi-Pazar' },
                  { key: 'pazar', label: 'Pazar' },
                  { key: 'cumartesi', label: 'Cumartesi' },
                  { key: 'cuma', label: 'Cuma' },
                  { key: 'persembe', label: 'Perşembe' },
                  { key: 'carsamba', label: 'Çarşamba' },
                  { key: 'sali', label: 'Salı' },
                  { key: 'pazartesi', label: 'Pazartesi' },
                ],
                onClick: ({ key }) => {
                  switch(key) {
                    case 'cumartesi-pazar':
                      handleHaftaTatiliSec(['Cumartesi', 'Pazar']);
                      break;
                    case 'pazar':
                      handleHaftaTatiliSec(['Pazar']);
                      break;
                    case 'cumartesi':
                      handleHaftaTatiliSec(['Cumartesi']);
                      break;
                    case 'cuma':
                      handleHaftaTatiliSec(['Cuma']);
                      break;
                    case 'persembe':
                      handleHaftaTatiliSec(['Perşembe']);
                      break;
                    case 'carsamba':
                      handleHaftaTatiliSec(['Çarşamba']);
                      break;
                    case 'sali':
                      handleHaftaTatiliSec(['Salı']);
                      break;
                    case 'pazartesi':
                      handleHaftaTatiliSec(['Pazartesi']);
                      break;
                  }
                }
              }}
              disabled={!selectedCostCenter}
            >
              <Button size="small" disabled={!selectedCostCenter}>
                Hafta Tatili Seç
              </Button>
            </Dropdown>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchData}
              loading={loading}
              size="small"
            />
            <Button
              icon={<DownloadOutlined />}
              onClick={handleDownloadTemplate}
              disabled={!selectedCostCenter}
              size="small"
            >
              Şablon İndir
            </Button>
            <Upload
              accept=".xls,.xlsx"
              showUploadList={false}
              beforeUpload={handleUpload}
            >
              <Button icon={<UploadOutlined />} size="small" disabled={!selectedCostCenter}>
                Excel Yükle
              </Button>
            </Upload>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={saving}
              disabled={editedCells.size === 0}
              size="small"
            >
              Kaydet {editedCells.size > 0 && `(${editedCells.size})`}
            </Button>
          </Space>
        </div>

        {/* Ultra Kompakt Durum Kodları */}
        <div style={{ 
          marginBottom: '6px', 
          padding: '4px 6px', 
          backgroundColor: '#fafafa', 
          borderRadius: '3px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '6px'
        }}>
          {DURUM_KODLARI.map(durum => (
            <div key={durum.kod} style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <span 
                style={{ 
                  width: '16px', 
                  height: '16px', 
                  backgroundColor: `${durum.color}30`,
                  border: `1px solid ${durum.color}`,
                  borderRadius: '2px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '8px',
                  color: durum.color
                }}
              >
                {durum.kod}
              </span>
              <span style={{ fontSize: '9px' }}>{durum.aciklama}</span>
            </div>
          ))}
          <span style={{ fontSize: '9px', color: '#999', marginLeft: 'auto' }}>
            {data.length} personel
          </span>
        </div>

        {/* Puantaj Tablosu - Tam Yükseklik */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {!selectedCostCenter ? (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              color: '#999',
              fontSize: '14px'
            }}>
              ⬆️ Lütfen yukarıdan bir şantiye seçin
            </div>
          ) : (
            <Spin spinning={loading}>
              <Table
                columns={getColumns()}
                dataSource={data}
                rowKey="id"
                pagination={false}
                size="small"
                bordered
                scroll={{ x: '100%', y: 600 }}
                rowClassName={(record, index) => {
                  // Bir önceki satırla karşılaştır, taşeron veya departman değişiyorsa sınıf ekle
                  if (index && index > 0) {
                    const prevRecord = data[index - 1];
                    const currentTaseron = record.taseron_name || 'Taşeronsuz';
                    const prevTaseron = prevRecord ? (prevRecord.taseron_name || 'Taşeronsuz') : null;
                    const currentDepartman = record.departman || '';
                    const prevDepartman = prevRecord ? (prevRecord.departman || '') : null;
                    
                    // Taşeron değişmişse mavi kalın çizgi
                    if (prevTaseron && currentTaseron !== prevTaseron) {
                      return 'taseron-group-separator';
                    }
                    // Aynı taşeron içinde departman değişmişse gri kalın çizgi
                    if (prevDepartman !== null && currentDepartman !== prevDepartman && currentTaseron === prevTaseron) {
                      return 'departman-group-separator';
                    }
                  }
                  return '';
                }}
                onRow={(record, index) => {
                  return {};
                }}
              />
            </Spin>
          )}
        </div>
      </Card>

      <style>{`
        .edited-cell .ant-select-selector {
          background-color: #fffbe6 !important;
          border: 1px solid #faad14 !important;
        }
        
        .ant-table-cell {
          padding: 1px 2px !important;
          font-size: 9px !important;
          line-height: 1.2 !important;
        }
        
        .ant-table-thead > tr > th {
          padding: 2px 2px !important;
          font-size: 9px !important;
          font-weight: 600;
          line-height: 1.2 !important;
          background-color: #fafafa !important;
        }
        
        .ant-table-bordered .ant-table-cell {
          border-right: 1px solid #c0c0c0 !important;
        }
        
        .ant-table-bordered .ant-table-tbody > tr > td {
          border-bottom: 1px solid #c0c0c0 !important;
        }
        
        /* Taşeron grup ayırıcısı - kalın mavi çizgi */
        .taseron-group-separator td {
          border-top: 3px solid #1890ff !important;
        }
        
        /* Departman grup ayırıcısı - kalın gri çizgi */
        .departman-group-separator td {
          border-top: 3px solid #8c8c8c !important;
        }
          font-weight: bold !important;
          font-size: 12px !important;
          padding: 4px 8px !important;
        }
        
        .ant-select-single.ant-select-sm .ant-select-selector {
          height: 20px !important;
          font-size: 11px !important;
          font-weight: bold !important;
          padding: 0 4px !important;
        }
        
        .ant-select-selection-item {
          line-height: 18px !important;
          font-size: 11px !important;
          font-weight: bold !important;
          overflow: hidden !important;
          text-overflow: clip !important;
          white-space: nowrap !important;
        }
        
        .ant-select-selector .ant-select-selection-item {
          padding-right: 0 !important;
        }
        
        .ant-table-small .ant-table-tbody > tr > td {
          padding: 1px 2px !important;
        }
        
        .ant-table-small .ant-table-tbody > tr {
          height: 42px !important;
        }
        
        /* Kaydırma çubuğu gerekmedikçe gizle */
        .ant-table-body {
          overflow-x: hidden !important;
          overflow-y: auto !important;
        }
        
        /* Tablo container genişliği */
        .ant-table-wrapper {
          width: 100%;
        }
        
        .ant-table {
          width: 100% !important;
        }
        
        .ant-table-body::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        
        .ant-table-body::-webkit-scrollbar-track {
          background: #f1f1f1;
        }
        
        .ant-table-body::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 4px;
        }
        
        .ant-table-body::-webkit-scrollbar-thumb:hover {
          background: #555;
        }
      `}</style>

      {/* Detay Modal */}
      <Modal
        title={selectedPersonel ? `Puantaj Detayı - ${selectedPersonel.adi_soyadi}` : "Puantaj Detayı"}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedPersonel(null);
          setEarningsInputs({ yol: 0, prim: 0, ikramiye: 0, bayram: 0, kira: 0 });
        }}
        footer={[
          <Button key="close" onClick={() => {
            setDetailModalVisible(false);
            setSelectedPersonel(null);
            setEarningsInputs({ yol: 0, prim: 0, ikramiye: 0, bayram: 0, kira: 0 });
          }}>
            Kapat
          </Button>
        ]}
        width={700}
      >
        {selectedPersonel && (() => {
          // DEBUG: Modal açıldığında draft_contract_id kontrolü
          console.log('🔍 Modal - selectedPersonel.draft_contract_id:', selectedPersonel.draft_contract_id);
          console.log('🔍 Modal - selectedPersonel.maas2_tutar:', selectedPersonel.maas2_tutar);
          
          // Hesaplamaları optimize edilmiş fonksiyonla yap - sistem ayarlarındaki oranları kullan
          const hesaplamalar = calculateSummaryForPersonel(
            selectedPersonel, 
            true, 
            earningsInputs,
            systemFmOrani,
            systemTatilOrani
          );
          
          // Destructure - daha temiz kod
          const {
            calisilan_gun_sayisi, yillik_izin_gun, izin_gun_sayisi, rapor_gun_sayisi,
            yarim_gun_sayisi, eksik_gun_sayisi, tatil_calismasi, sigorta_girmedigi,
            hafta_tatili, resmi_tatil, toplam_gun_sayisi, ssk_gun_sayisi,
            normal_calismasi, fazla_calismasi, eksik_calismasi, tatiller,
            maas2, fm_orani, tatil_orani, gunluk_kazanc, normal_kazanc, mesai_kazanc, eksik_kazanc, tatil_kazanc,
            tatil_mesai_kazanc, toplam_kazanc
          } = hesaplamalar;

          const puantajTab = (
            <div style={{ fontSize: '13px' }}>
              <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>Özet Bilgiler</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <div><strong>Ayın Toplam Gün:</strong> {ayin_toplam_gun_sayisi}</div>
                  <div><strong>Sigorta Girmediği:</strong> {sigorta_girmedigi}</div>
                  <div><strong>Toplam Gün Sayısı:</strong> {toplam_gun_sayisi}</div>
                  <div><strong>SSK Gün:</strong> {ssk_gun_sayisi}</div>
                  <div><strong>Normal Çalışma:</strong> {normal_calismasi}</div>
                  <div><strong>Toplam Tatiller:</strong> {tatiller}</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#52c41a' }}>Çalışılan Gün:</strong> {calisilan_gun_sayisi}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#fa8c16' }}>Yıllık İzin:</strong> {yillik_izin_gun}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#faad14' }}>İzin:</strong> {izin_gun_sayisi}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#f5222d' }}>Rapor:</strong> {rapor_gun_sayisi}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#ffc53d' }}>Yarım Gün:</strong> {yarim_gun_sayisi}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#ff4d4f' }}>Eksik Gün:</strong> {eksik_gun_sayisi}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#1890ff' }}>Fazla Mesai (Saat):</strong> {fazla_calismasi.toFixed(1)}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#ff4d4f' }}>Eksik Mesai (Saat):</strong> {eksik_calismasi.toFixed(1)}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#13c2c2' }}>Tatil Çalışması:</strong> {tatil_calismasi}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#722ed1' }}>Hafta Tatili:</strong> {hafta_tatili}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <strong style={{ color: '#ff4d4f' }}>Resmi Tatil:</strong> {resmi_tatil}
                </div>
                <div style={{ padding: '8px', border: '1px solid #d9d9d9', borderRadius: '4px', gridColumn: 'span 2' }}>
                  <strong style={{ color: '#595959' }}>Toplam Tatiller:</strong> {tatiller}
                </div>
              </div>
            </div>
          );

          const pc_ucret_nevi = selectedPersonel.ucret_nevi;

          const kazancTab = (
            <div style={{ fontSize: '13px' }}>
              {!selectedPersonel.draft_contract_id ? (
                <div>
                  {/* Sözleşme Bilgileri - Draft kontrat yoksa */}
                  <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Sözleşme Bilgileri</div>
                    <div style={{ display: 'grid', gap: '6px', fontSize: '12px' }}>
                      {selectedPersonel.ucret_nevi && (
                        <div><strong>Ücret Nevi:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.ucret_nevi}</span></div>
                      )}
                      {selectedPersonel.net_brut && (
                        <div><strong>Bordro Net/Brüt:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.net_brut}</span></div>
                      )}
                      {selectedPersonel.ucret && (
                        <div><strong>Bordro Ücret:</strong> <span style={{ color: '#52c41a', fontWeight: 'bold' }}>₺{selectedPersonel.ucret.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
                      )}
                      {selectedPersonel.fm_orani && (
                        <div><strong>Fazla Mesai Oranı:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.fm_orani}</span></div>
                      )}
                      {selectedPersonel.tatil_orani && (
                        <div><strong>Tatil Mesai Oranı:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.tatil_orani}</span></div>
                      )}
                      {selectedPersonel.taseron_name && (
                        <div><strong>Taşeron:</strong> <span style={{ color: '#fa8c16' }}>{selectedPersonel.taseron_name}</span></div>
                      )}
                    </div>
                  </div>
                  
                  {/* Kazanç Mesajı */}
                  <div style={{ padding: '16px', textAlign: 'center', backgroundColor: '#fff7e6', border: '1px solid #ffd591', borderRadius: '4px' }}>
                    <strong style={{ color: '#d46b08', fontSize: '14px' }}>Kazancı Luca bordroya göre belirleniyor</strong>
                  </div>
                </div>
              ) : pc_ucret_nevi === 'sabit aylik' ? (
                <div>
                  {/* Sabit Aylık için basit görünüm */}
                  <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Sözleşme Bilgileri</div>
                    <div style={{ display: 'grid', gap: '6px', fontSize: '12px' }}>
                      <div><strong>Ücret Nevi:</strong> <span style={{ color: '#1890ff', fontWeight: 'bold' }}>Sabit Aylık</span></div>
                      {selectedPersonel.net_brut && (
                        <div><strong>Bordro Net/Brüt:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.net_brut}</span></div>
                      )}
                      {selectedPersonel.ucret && (
                        <div><strong>Bordro Ücret:</strong> <span style={{ color: '#52c41a', fontWeight: 'bold' }}>₺{selectedPersonel.ucret.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
                      )}
                      <div><strong>Net Ücret:</strong> <span style={{ color: '#52c41a', fontWeight: 'bold', fontSize: '16px' }}>₺{maas2.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
                      {selectedPersonel.fm_orani && (
                        <div><strong>Fazla Mesai Oranı:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.fm_orani}</span></div>
                      )}
                      {selectedPersonel.tatil_orani && (
                        <div><strong>Tatil Mesai Oranı:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.tatil_orani}</span></div>
                      )}
                      {selectedPersonel.taseron_name && (
                        <div><strong>Taşeron:</strong> <span style={{ color: '#fa8c16' }}>{selectedPersonel.taseron_name}</span></div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  {/* Hesaplanan Kazançlar */}
                  <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#e6f7ff', borderRadius: '4px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>Hesaplanan Kazançlar</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '8px', fontSize: '12px' }}>
                      <div><strong>Günlük Kazanç:</strong></div>
                      <div style={{ textAlign: 'right' }}>₺{gunluk_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                      
                      <div><strong>Normal Kazanç:</strong> <span style={{ color: '#666', fontSize: '10px' }}>({normal_calismasi} gün × ₺{gunluk_kazanc.toFixed(2)})</span></div>
                      <div style={{ textAlign: 'right' }}>₺{normal_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                      
                      <div><strong>Mesai Kazancı:</strong> <span style={{ color: '#666', fontSize: '10px' }}>({fazla_calismasi.toFixed(1)} saat × {fm_orani})</span></div>
                      <div style={{ textAlign: 'right' }}>₺{mesai_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                      
                      <div><strong style={{ color: '#ff4d4f' }}>Eksik Mesai Kesintisi:</strong> <span style={{ color: '#666', fontSize: '10px' }}>({eksik_calismasi.toFixed(1)} saat)</span></div>
                      <div style={{ textAlign: 'right', color: '#ff4d4f' }}>-₺{eksik_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                      
                      <div><strong>Tatil Kazancı:</strong> <span style={{ color: '#666', fontSize: '10px' }}>({tatiller} gün)</span></div>
                      <div style={{ textAlign: 'right' }}>₺{tatil_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                      
                      <div><strong>Tatil Mesai Kazancı:</strong> <span style={{ color: '#666', fontSize: '10px' }}>({tatil_calismasi} gün × {tatil_orani})</span></div>
                      <div style={{ textAlign: 'right' }}>₺{tatil_mesai_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                    </div>
                  </div>

                  {/* İki Kolonlu Bölüm: Sol - Sözleşme Bilgileri, Sağ - Ek Kazançlar */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                    {/* Sol Kolon - Sözleşme Bilgileri */}
                    <div style={{ padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Sözleşme Bilgileri</div>
                      <div style={{ display: 'grid', gap: '6px', fontSize: '12px' }}>
                        {selectedPersonel.ucret_nevi && (
                          <div><strong>Ücret Nevi:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.ucret_nevi}</span></div>
                        )}
                        {selectedPersonel.net_brut && (
                          <div><strong>Bordro Net/Brüt:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.net_brut}</span></div>
                        )}
                        {selectedPersonel.ucret && (
                          <div><strong>Bordro Ücret:</strong> <span style={{ color: '#52c41a', fontWeight: 'bold' }}>₺{selectedPersonel.ucret.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
                        )}
                        {maas2 && (
                          <div><strong>Net Ücret:</strong> <span style={{ color: '#52c41a', fontWeight: 'bold' }}>₺{maas2.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
                        )}
                        {selectedPersonel.fm_orani && (
                          <div><strong>Fazla Mesai Oranı:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.fm_orani}</span></div>
                        )}
                        {selectedPersonel.tatil_orani && (
                          <div><strong>Tatil Mesai Oranı:</strong> <span style={{ color: '#1890ff' }}>{selectedPersonel.tatil_orani}</span></div>
                        )}
                        {selectedPersonel.taseron_name && (
                          <div><strong>Taşeron:</strong> <span style={{ color: '#fa8c16' }}>{selectedPersonel.taseron_name}</span></div>
                        )}
                      </div>
                    </div>

                    {/* Sağ Kolon - Diğer Ek Kazançlar */}
                    <div style={{ padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Diğer Ek Kazançlar</div>
                      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '8px', fontSize: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}><strong>Yol:</strong></div>
                        <Input 
                          type="number" 
                          size="small"
                          value={earningsInputs.yol || ''}
                          onChange={(e) => setEarningsInputs({...earningsInputs, yol: parseFloat(e.target.value) || 0})}
                          prefix="₺"
                        />
                        
                        <div style={{ display: 'flex', alignItems: 'center' }}><strong>Prim:</strong></div>
                        <Input 
                          type="number" 
                          size="small"
                          value={earningsInputs.prim || ''}
                          onChange={(e) => setEarningsInputs({...earningsInputs, prim: parseFloat(e.target.value) || 0})}
                          prefix="₺"
                        />
                        
                        <div style={{ display: 'flex', alignItems: 'center' }}><strong>İkramiye:</strong></div>
                        <Input 
                          type="number" 
                          size="small"
                          value={earningsInputs.ikramiye || ''}
                          onChange={(e) => setEarningsInputs({...earningsInputs, ikramiye: parseFloat(e.target.value) || 0})}
                          prefix="₺"
                        />
                        
                        <div style={{ display: 'flex', alignItems: 'center' }}><strong>Bayram:</strong></div>
                        <Input 
                          type="number" 
                          size="small"
                          value={earningsInputs.bayram || ''}
                          onChange={(e) => setEarningsInputs({...earningsInputs, bayram: parseFloat(e.target.value) || 0})}
                          prefix="₺"
                        />
                        
                        <div style={{ display: 'flex', alignItems: 'center' }}><strong>Kira:</strong></div>
                        <Input 
                          type="number" 
                          size="small"
                          value={earningsInputs.kira || ''}
                          onChange={(e) => setEarningsInputs({...earningsInputs, kira: parseFloat(e.target.value) || 0})}
                          prefix="₺"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Toplam Kazanç */}
                  <div style={{ padding: '12px', backgroundColor: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: '4px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong style={{ fontSize: '15px', color: '#52c41a' }}>Toplam Kazanç:</strong>
                      <strong style={{ fontSize: '18px', color: '#52c41a' }}>₺{toplam_kazanc.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );

          return (
            <Tabs
              defaultActiveKey="puantaj"
              items={[
                {
                  key: 'puantaj',
                  label: 'Puantaj',
                  children: puantajTab
                },
                {
                  key: 'kazanc',
                  label: 'Kazanç',
                  children: kazancTab
                }
              ]}
            />
          );
        })()}
      </Modal>
    </div>
  );
};

export default PuantajGridPage;
