import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Space, message, DatePicker, Tag, Modal, Descriptions, Spin, Select, Tabs, Alert } from 'antd';
import { CalculatorOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v2/personnel';

interface LucaBordro {
  id: number;
  personnel_id: number;
  contract_id: number;
  monthly_personnel_records_id: number;
  ssk_sicil_no: string;
  giris_t: string | null;
  cikis_t: string | null;
  t_gun: number;
  nor_kazanc: number;
  dig_kazanc: number;
  top_kazanc: number;
  ssk_m: number;
  g_v_m: number;
  ssk_isci: number;
  iss_p_isci: number;
  gel_ver: number;
  damga_v: number;
  ozel_kesinti: number;
  oto_kat_bes: number;
  icra: number;
  avans: number;
  n_odenen: number;
  isveren_maliyeti: number;
  ssk_isveren: number;
  iss_p_isveren: number;
  kanun: string;
  ssk_tesviki: number;
  adi_soyadi: string;
  tckn: string;
}

interface CalculationDetail {
  // Basic info
  id: number;
  personnel_id: number;
  adi_soyadi: string;
  tckn: string;
  
  // Dönem
  yil: number;
  ay: number;
  donem: string;
  
  // IDs - Relations
  contract_id: number | null;
  draft_contract_id: number | null;
  luca_bordro_id: number | null;
  puantaj_id: number | null;
  cost_center_id: number | null;
  
  // Maliyet & Ücret
  maliyet_merkezi: string;
  ucret_nevi: string;
  kanun_tipi: string;
  yevmiye_tipi: string;
  
  // Maas1 fields (from Luca)
  maas1_net_odenen: number;
  maas1_icra: number;
  maas1_bes: number;
  maas1_avans: number;
  maas1_gelir_vergisi: number;
  maas1_damga_vergisi: number;
  maas1_ssk_isci: number;
  maas1_issizlik_isci: number;
  maas1_ssk_isveren: number;
  maas1_issizlik_isveren: number;
  maas1_ssk_tesviki: number;
  maas1_diger_kesintiler: number;
  
  // Maas2 fields (from PPG calculation)
  maas2_anlaşilan: number;
  maas2_normal_calismasi: number;
  maas2_hafta_tatili: number;
  maas2_fm_calismasi: number;
  maas2_em_calismasi: number;
  maas2_resmi_tatil: number;
  maas2_tatil_calismasi: number;
  maas2_toplam_tatil_calismasi: number;
  maas2_yillik_izin: number;
  maas2_yol: number;
  maas2_prim: number;
  maas2_ikramiye: number;
  maas2_bayram: number;
  maas2_kira: number;
  maas2_toplam: number;
  
  // Puantaj details (gün/saat)
  normal_gun: number;
  hafta_tatili_gun: number;
  fazla_mesai_saat: number;
  eksik_mesai_saat: number;
  tatil_mesai_gun: number;
  yillik_izin_gun: number;
  
  // Elden calculation
  elden_ucret_ham: number;
  elden_ucret_yuvarlanmis: number;
  elden_yuvarlama: number;
  elden_yuvarlama_yon: string | null;
  
  // Account code
  account_code_335: string | null;
  
  // Transaction info
  transaction_id: number | null;
  fis_no: string | null;
  
  // Status
  is_approved: boolean;
  is_exported: boolean;
  has_error: boolean;
  error_message: string | null;
  
  // Metadata
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
  calculated_by: string | null;
  approved_by: string | null;
}

interface PayrollGrouped {
  personnel_id: number;
  tckn: string;
  adi_soyadi: string;
  has_active_draft_contract: boolean;
  has_puantaj_grid: boolean;
  total_net_odenen: number;
  total_bes: number;
  total_icra: number;
  total_elden_ucret: number;
  total_kazanc: number;
  total_isveren_maliyet: number;
  calculations: CalculationDetail[];
}

interface PayrollListResponse {
  total: number;
  items: PayrollGrouped[];
}

interface CostCenter {
  id: number;
  name: string;
  is_active: boolean;
}

export const BordroCalculationPageGrouped: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [payrollData, setPayrollData] = useState<PayrollGrouped[]>([]);
  const [total, setTotal] = useState(0);
  const [selectedRecord, setSelectedRecord] = useState<PayrollGrouped | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [actionModalVisible, setActionModalVisible] = useState(false);
  const [actionModalType, setActionModalType] = useState<'bordrolar' | 'maas-hesabi' | 'yevmiye-kaydi' | 'puantaj-bilgileri'>('bordrolar');
  const [actionModalData, setActionModalData] = useState<any>(null);
  const [actionModalLoading, setActionModalLoading] = useState(false);
  const [selectedBordroIndex, setSelectedBordroIndex] = useState<number>(0);
  
  
  // Yevmiye Kaydı için yeni state'ler
  const [yevmiyeData, setYevmiyeData] = useState<any>(null);
  const [yevmiyeLoading, setYevmiyeLoading] = useState(false);
  const [yevmiyeSaving, setYevmiyeSaving] = useState(false);
  
  // Toplu seçim için state'ler
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [bulkSaving, setBulkSaving] = useState(false);
  


  const fetchPayrollData = async () => {
    const yil = selectedDate.year();
    const ay = selectedDate.month() + 1;
    
    setLoading(true);
    try {
      const params: any = { yil, ay, limit: 1000 };
      
      const response = await axios.get<PayrollListResponse>(`${API_URL}/bordro-calculation/list-grouped`, {
        params
      });
      
      setPayrollData(response.data.items);
      setTotal(response.data.total);
      
    } catch (error: any) {
      message.error('Bordro listesi yüklenemedi: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayrollData();
  }, [selectedDate]);

  // Toplu yevmiye kaydı oluşturma
  const handleBulkSaveYevmiye = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Lütfen en az bir personel seçin');
      return;
    }

    Modal.confirm({
      title: 'Toplu Yevmiye Kaydı',
      content: `Seçili ${selectedRowKeys.length} personel için yevmiye kayıtları oluşturulacak. Devam edilsin mi?`,
      okText: 'Evet',
      cancelText: 'İptal',
      onOk: async () => {
        setBulkSaving(true);
        let successCount = 0;
        let errorCount = 0;
        const errors: string[] = [];

        for (const personnelId of selectedRowKeys) {
          try {
            const response = await axios.post(
              `${API_URL}/bordro-calculation/save-yevmiye-personnel?personnel_id=${personnelId}&yil=${selectedDate.year()}&ay=${selectedDate.month() + 1}`
            );
            
            if (response.data.success) {
              successCount++;
            } else {
              errorCount++;
              const record = payrollData.find(p => p.personnel_id === personnelId);
              errors.push(`${record?.adi_soyadi}: ${response.data.message || 'Hata'}`);
            }
          } catch (error: any) {
            errorCount++;
            const record = payrollData.find(p => p.personnel_id === personnelId);
            errors.push(`${record?.adi_soyadi}: ${error.response?.data?.detail || error.message}`);
          }
        }

        setBulkSaving(false);

        if (successCount > 0) {
          message.success(`${successCount} personel için yevmiye kaydı oluşturuldu`);
        }
        
        if (errorCount > 0) {
          Modal.error({
            title: `${errorCount} personel için hata oluştu`,
            content: (
              <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                {errors.map((err, idx) => (
                  <div key={idx} style={{ marginBottom: 8 }}>{err}</div>
                ))}
              </div>
            ),
            width: 600
          });
        }

        // Başarılı kayıtlar varsa, listeyi yenile
        if (successCount > 0) {
          await fetchPayrollData();
          setSelectedRowKeys([]);
        }
      }
    });
  };

  const handleCalculate = async () => {
    const yil = selectedDate.year();
    const ay = selectedDate.month() + 1;
    
    setCalculating(true);
    try {
      // Cost center filtresi sadece listeleme için - hesaplama tüm personeller için yapılır
      const response = await axios.post(`${API_URL}/bordro-calculation/calculate?yil=${yil}&ay=${ay}`);
      
      message.success(`✅ ${response.data.total} kayıt hesaplandı (${response.data.calculated} yeni, ${response.data.updated} güncelleme)`);
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.error('Bordro hesaplama hataları:', response.data.errors);
        message.warning(`⚠️ ${response.data.errors.length} kayıtta hata oluştu (Detaylar console'da)`, 5);
      }
      
      await fetchPayrollData();
      
    } catch (error: any) {
      message.error('Bordro hesaplaması başarısız: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCalculating(false);
    }
  };

  const showDetail = (record: PayrollGrouped) => {
    setSelectedRecord(record);
    setDetailModalVisible(true);
  };

  const handleActionSelect = async (actionType: 'bordrolar' | 'maas-hesabi' | 'yevmiye-kaydi' | 'puantaj-bilgileri', record: PayrollGrouped) => {
    setActionModalType(actionType);
    setActionModalVisible(true);
    setActionModalLoading(true);
    setSelectedRecord(record);

    try {
      const yil = selectedDate.year();
      const ay = selectedDate.month() + 1;

      if (actionType === 'bordrolar') {
        // Luca bordro verilerini getir
        const response = await axios.get(`${API_URL}/bordro-calculation/bordro-data`, {
          params: { yil, ay, personnel_id: record.personnel_id }
        });
        setActionModalData(response.data.items);
      } else if (actionType === 'maas-hesabi') {
        // Maaş hesabı verilerini getir (draft contract + puantaj)
        const response = await axios.get(`${API_URL}/bordro-calculation/maas-hesabi-data`, {
          params: { yil, ay, personnel_id: record.personnel_id }
        });
        setActionModalData(response.data);
      } else if (actionType === 'yevmiye-kaydi') {
        // YENİ SİSTEM: Personel bazında yevmiye önizlemesi
        setYevmiyeLoading(true);
        const response = await axios.get(`${API_URL}/bordro-calculation/preview-yevmiye-personnel`, {
          params: { personnel_id: record.personnel_id, yil, ay }
        });
        setYevmiyeData(response.data);
        setYevmiyeLoading(false);
      } else if (actionType === 'puantaj-bilgileri') {
        // Puantaj grid verilerini getir
        const response = await axios.get(`${API_URL}/bordro-calculation/puantaj-data`, {
          params: { yil, ay, personnel_id: record.personnel_id }
        });
        setActionModalData(response.data);
      }
    } catch (error: any) {
      message.error('Veri yüklenemedi: ' + (error.response?.data?.detail || error.message));
      setActionModalVisible(false);
    } finally {
      setActionModalLoading(false);
    }
  };
  
  const handleSaveYevmiyePersonnel = async () => {
    if (!selectedRecord) return;
    
    const yil = selectedDate.year();
    const ay = selectedDate.month() + 1;
    
    setYevmiyeSaving(true);
    try {
      const response = await axios.post(`${API_URL}/bordro-calculation/save-yevmiye-personnel`, null, {
        params: { personnel_id: selectedRecord.personnel_id, yil, ay }
      });
      
      message.success(`✅ Yevmiye kayıtları başarıyla oluşturuldu: ${response.data.transactions.length} transaction`);
      
      setActionModalVisible(false);
      setYevmiyeData(null);
      
      await fetchPayrollData();
      
    } catch (error: any) {
      message.error('Yevmiye kaydetme hatası: ' + (error.response?.data?.detail || error.message));
    } finally {
      setYevmiyeSaving(false);
    }
  };

  const columns = [
    {
      title: 'TC',
      dataIndex: 'tckn',
      key: 'tckn',
      width: 95,
      fixed: 'left' as const,
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.tckn.localeCompare(b.tckn),
    },
    {
      title: 'Adı Soyadı',
      dataIndex: 'adi_soyadi',
      key: 'adi_soyadi',
      width: 150,
      fixed: 'left' as const,
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.adi_soyadi.localeCompare(b.adi_soyadi),
    },
    {
      title: 'Net Ödenen',
      dataIndex: 'total_net_odenen',
      key: 'total_net_odenen',
      align: 'right' as const,
      width: 100,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.total_net_odenen - b.total_net_odenen,
    },
    {
      title: 'BES',
      dataIndex: 'total_bes',
      key: 'total_bes',
      align: 'right' as const,
      width: 80,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.total_bes - b.total_bes,
    },
    {
      title: 'İcra',
      dataIndex: 'total_icra',
      key: 'total_icra',
      align: 'right' as const,
      width: 80,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.total_icra - b.total_icra,
    },
    {
      title: 'Elden Ücret',
      dataIndex: 'total_elden_ucret',
      key: 'total_elden_ucret',
      align: 'right' as const,
      width: 95,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.total_elden_ucret - b.total_elden_ucret,
    },
    {
      title: 'Toplam Kazanç',
      dataIndex: 'total_kazanc',
      key: 'total_kazanc',
      align: 'right' as const,
      width: 110,
      render: (val: number) => <strong>{val.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}</strong>,
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => a.total_kazanc - b.total_kazanc,
    },
    {
      title: 'Durum',
      key: 'durum',
      align: 'center' as const,
      width: 120,
      render: (_: any, record: PayrollGrouped) => {
        // ÖNCELİK 1: Draft contract var ama puantaj grid yok mu kontrol et
        // (Yevmiye kaydedilmiş olsa bile puantaj yoksa bu durum gösterilir)
        if (record.has_active_draft_contract && !record.has_puantaj_grid) {
          return <Tag color="blue" style={{ fontSize: 10 }}>PUANTAJ BEKLİYOR</Tag>;
        }
        
        // ÖNCELİK 2: Herhangi bir bordro kaydının yevmiyeye işlenmiş olup olmadığını kontrol et
        // transaction_id > 0 olanlar işlenmiş, yevmiye_tipi="SATIR YOK" olanlar atlanmış
        const hasProcessedTransaction = record.calculations.some(
          calc => calc.transaction_id && calc.transaction_id > 0 && calc.yevmiye_tipi !== "SATIR YOK"
        );
        
        if (hasProcessedTransaction) {
          return <Tag color="green" style={{ fontSize: 10 }}>İŞLENDİ</Tag>;
        }
        
        // ÖNCELİK 3: Diğer durumlar
        return <Tag color="orange" style={{ fontSize: 10 }}>BEKLEMEDE</Tag>;
      },
      sorter: (a: PayrollGrouped, b: PayrollGrouped) => {
        const aProcessed = a.calculations.some(
          calc => calc.transaction_id && calc.transaction_id > 0 && calc.yevmiye_tipi !== "SATIR YOK"
        );
        const bProcessed = b.calculations.some(
          calc => calc.transaction_id && calc.transaction_id > 0 && calc.yevmiye_tipi !== "SATIR YOK"
        );
        
        // Öncelik sırası:
        // 1. Puantaj bekliyor (draft var, puantaj yok) → en üstte
        // 2. Beklemede (diğerleri) → ortada
        // 3. İşlenmiş → en altta
        
        const aWaitingPuantaj = a.has_active_draft_contract && !a.has_puantaj_grid && !aProcessed;
        const bWaitingPuantaj = b.has_active_draft_contract && !b.has_puantaj_grid && !bProcessed;
        
        // Puantaj bekleyenler en üstte
        if (aWaitingPuantaj && !bWaitingPuantaj) return -1;
        if (!aWaitingPuantaj && bWaitingPuantaj) return 1;
        
        // İşlenmişler en altta
        if (aProcessed && !bProcessed) return 1;
        if (!aProcessed && bProcessed) return -1;
        
        return 0;
      },
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 165,
      fixed: 'right' as const,
      render: (_: any, record: PayrollGrouped) => {
        const options = [
          { label: 'Bordroları', value: 'bordrolar' },
          { label: 'Yevmiye Kaydı', value: 'yevmiye-kaydi' },
        ];
        
        // Eğer aktif draft contract varsa Maaş Hesabı ve Puantaj Bilgileri seçeneklerini ekle
        if (record.has_active_draft_contract) {
          options.push({ label: 'Maaş Hesabı', value: 'maas-hesabi' });
          options.push({ label: 'Puantaj Bilgileri', value: 'puantaj-bilgileri' });
        }
        
        return (
          <Select
            placeholder="İşlem Seçin"
            style={{ width: 150 }}
            size="small"
            value={null}
            onChange={(value) => handleActionSelect(value, record)}
            options={options}
          />
        );
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="Bordro Hesaplama (Personel Bazlı)" style={{ marginBottom: 24 }}>
        <Space size="large" wrap>
          <DatePicker.MonthPicker
            value={selectedDate}
            onChange={(date) => date && setSelectedDate(date)}
            format="YYYY-MM"
            placeholder="Dönem Seçin"
          />
          <Button
            type="primary"
            icon={<CalculatorOutlined />}
            onClick={handleCalculate}
            loading={calculating}
          >
            Bordro Hesapla
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchPayrollData}
            loading={loading}
          >
            Yenile
          </Button>
          <Button
            type="primary"
            onClick={handleBulkSaveYevmiye}
            loading={bulkSaving}
            disabled={selectedRowKeys.length === 0}
          >
            Seçili Personellerin Yevmiye Kayıtlarını Kaydet ({selectedRowKeys.length})
          </Button>
        </Space>
      </Card>

      <Card>
        <Table
          dataSource={payrollData}
          columns={columns}
          rowKey="personnel_id"
          loading={loading}
          pagination={{ pageSize: 20, showTotal: (total) => `Toplam ${total} kayıt` }}
          scroll={{ y: 600 }}
          size="small"
          rowSelection={{
            selectedRowKeys,
            onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys),
            selections: [
              Table.SELECTION_ALL,
              Table.SELECTION_INVERT,
              Table.SELECTION_NONE,
            ],
          }}
        />
      </Card>

      {/* Detay Modal */}
      <Modal
        title={`Bordro Detayı - ${selectedRecord?.adi_soyadi || ''}`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={1000}
        footer={null}
      >
        {selectedRecord && (
          <div>
            {selectedRecord.calculations.map((calc, idx) => (
              <Card 
                key={idx} 
                size="small" 
                title={`${calc.maliyet_merkezi} - ${calc.ucret_nevi}`}
                style={{ marginBottom: 16 }}
              >
                <Descriptions bordered column={2} size="small">
                  {/* ID'ler ve Dönem */}
                  <Descriptions.Item label="Dönem">{calc.donem}</Descriptions.Item>
                  <Descriptions.Item label="Yevmiye Tipi">{calc.yevmiye_tipi || '-'}</Descriptions.Item>
                  {calc.luca_bordro_id && <Descriptions.Item label="Luca Bordro ID">{calc.luca_bordro_id}</Descriptions.Item>}
                  {calc.draft_contract_id && <Descriptions.Item label="Draft Contract ID">{calc.draft_contract_id}</Descriptions.Item>}
                  {calc.contract_id && <Descriptions.Item label="Contract ID">{calc.contract_id}</Descriptions.Item>}
                  {calc.puantaj_id && <Descriptions.Item label="Puantaj ID">{calc.puantaj_id}</Descriptions.Item>}
                  
                  {/* Maliyet Merkezi & Ücret Bilgileri */}
                  <Descriptions.Item label="Kanun">{calc.kanun_tipi}</Descriptions.Item>
                  <Descriptions.Item label="Ücret Nevi">{calc.ucret_nevi}</Descriptions.Item>
                  
                  {/* Maas1 - Luca Verileri */}
                  <Descriptions.Item label="Net Ödenen" span={2}><strong>{calc.maas1_net_odenen.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</strong></Descriptions.Item>
                  <Descriptions.Item label="BES">{calc.maas1_bes?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                  <Descriptions.Item label="Avans">{calc.maas1_avans?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                  <Descriptions.Item label="İcra">{calc.maas1_icra.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="SSK Teşviki">{calc.maas1_ssk_tesviki?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                  <Descriptions.Item label="SSK İşçi">{calc.maas1_ssk_isci.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="SSK İşveren">{calc.maas1_ssk_isveren.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="İşsizlik İşçi">{calc.maas1_issizlik_isci.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="İşsizlik İşveren">{calc.maas1_issizlik_isveren.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="Gelir Vergisi">{calc.maas1_gelir_vergisi.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="Damga Vergisi">{calc.maas1_damga_vergisi.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  
                  {/* Maas2 - Hesaplanan Veriler (TASLAK kayıtlar için) */}
                  {(calc.maas2_anlaşilan > 0 || calc.maas2_toplam > 0) && (
                    <>
                      <Descriptions.Item label="Anlaşılan Ücret" span={2}><strong style={{color: '#1890ff'}}>{calc.maas2_anlaşilan?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</strong></Descriptions.Item>
                      <Descriptions.Item label="Normal Çalışma">{calc.maas2_normal_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Hafta Tatili">{calc.maas2_hafta_tatili?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Fazla Mesai">{calc.maas2_fm_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Resmi Tatil">{calc.maas2_resmi_tatil?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Tatil Çalışması">{calc.maas2_tatil_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Toplam Tatil Çalışması">{calc.maas2_toplam_tatil_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Yıllık İzin">{calc.maas2_yillik_izin?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Yol">{calc.maas2_yol?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Prim">{calc.maas2_prim?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="İkramiye">{calc.maas2_ikramiye?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Bayram">{calc.maas2_bayram?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Kira">{calc.maas2_kira?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                      <Descriptions.Item label="Toplam Maaş2" span={2}><strong style={{color: '#52c41a'}}>{calc.maas2_toplam?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</strong></Descriptions.Item>
                    </>
                  )}
                  
                  {/* Puantaj Detayları (TASLAK kayıtlar için) */}
                  {(calc.normal_gun > 0 || calc.hafta_tatili_gun > 0 || calc.fazla_mesai_saat > 0) && (
                    <>
                      <Descriptions.Item label="Normal Gün">{calc.normal_gun || 0} gün</Descriptions.Item>
                      <Descriptions.Item label="Hafta Tatili">{calc.hafta_tatili_gun || 0} gün</Descriptions.Item>
                      <Descriptions.Item label="Fazla Mesai">{calc.fazla_mesai_saat || 0} saat</Descriptions.Item>
                      <Descriptions.Item label="Tatil Mesai">{calc.tatil_mesai_gun || 0} gün</Descriptions.Item>
                      <Descriptions.Item label="Yıllık İzin">{calc.yillik_izin_gun || 0} gün</Descriptions.Item>
                    </>
                  )}
                  
                  {/* Elden Ücret */}
                  <Descriptions.Item label="Elden Ücret (Ham)">{calc.elden_ucret_ham?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) || 0} ₺</Descriptions.Item>
                  <Descriptions.Item label="Elden Ücret (Yuvarlanmış)">{calc.elden_ucret_yuvarlanmis.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  {calc.elden_yuvarlama && <Descriptions.Item label="Yuvarlama">{calc.elden_yuvarlama?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺ ({calc.elden_yuvarlama_yon})</Descriptions.Item>}
                  
                  {/* Transaction Bilgileri */}
                  <Descriptions.Item label="Fiş No">{calc.fis_no || '-'}</Descriptions.Item>
                  <Descriptions.Item label="Transaction ID">{calc.transaction_id || '-'}</Descriptions.Item>
                  {calc.account_code_335 && <Descriptions.Item label="Hesap Kodu 335">{calc.account_code_335}</Descriptions.Item>}
                  
                  {/* Status ve Metadata */}
                  {calc.is_approved && <Descriptions.Item label="Onaylandı"><Tag color="success">Evet</Tag></Descriptions.Item>}
                  {calc.is_exported && <Descriptions.Item label="Export Edildi"><Tag color="processing">Evet</Tag></Descriptions.Item>}
                  {calc.has_error && <Descriptions.Item label="Hata" span={2}><Tag color="error">{calc.error_message}</Tag></Descriptions.Item>}
                  {calc.created_at && <Descriptions.Item label="Oluşturma">{new Date(calc.created_at).toLocaleString('tr-TR')}</Descriptions.Item>}
                  {calc.updated_at && <Descriptions.Item label="Güncelleme">{new Date(calc.updated_at).toLocaleString('tr-TR')}</Descriptions.Item>}
                </Descriptions>
              </Card>
            ))}
          </div>
        )}
      </Modal>

      {/* İşlemler Modal */}
      <Modal
        title={`${selectedRecord?.adi_soyadi} - ${
          actionModalType === 'bordrolar' ? 'Bordroları' : 
          actionModalType === 'maas-hesabi' ? 'Maaş Hesabı' : 
          actionModalType === 'puantaj-bilgileri' ? 'Puantaj Bilgileri' :
          'Yevmiye Kaydı'
        }`}
        open={actionModalVisible}
        onCancel={() => setActionModalVisible(false)}
        width={actionModalType === 'bordrolar' || actionModalType === 'puantaj-bilgileri' || actionModalType === 'maas-hesabi' ? 1000 : 900}
        footer={null}
      >
        {actionModalLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
          </div>
        ) : actionModalType === 'bordrolar' ? (
          <Tabs
            defaultActiveKey="detay"
            items={[
              {
                key: 'detay',
                label: 'Bordro Detayı',
                children: (
                  <div style={{ padding: '8px' }}>
                    <Space direction="vertical" style={{ width: '100%' }} size="middle">
                      {/* Bordro Seçimi */}
                      <Select
                        style={{ width: '100%' }}
                        value={selectedBordroIndex}
                        onChange={setSelectedBordroIndex}
                        options={(actionModalData || []).map((bordro: any, idx: number) => ({
                          value: idx,
                          label: bordro.bolum || `Bordro ${idx + 1}`
                        }))}
                      />

                      {/* Seçilen Bordro Detayı */}
                      {actionModalData && actionModalData[selectedBordroIndex] && (
                        <div style={{ maxHeight: '450px', overflowY: 'auto' }}>
                          <Space direction="vertical" style={{ width: '100%' }} size="middle">
                            {(() => {
                              const bordro = actionModalData[selectedBordroIndex];
                              return (
                                <>
                                  {/* Bordro ve Contract Bilgileri */}
                                  <Descriptions title="Bordro ve Contract Bilgileri" bordered size="small" column={3}>
                                    <Descriptions.Item label="Bordro ID">{bordro.id}</Descriptions.Item>
                                    <Descriptions.Item label="Contract ID">{bordro.contract_id}</Descriptions.Item>
                                    <Descriptions.Item label="Maliyet Merkezi">{bordro.maliyet_merkezi || '-'}</Descriptions.Item>
                                  </Descriptions>

                                  {/* Kişisel Bilgiler */}
                                  <Descriptions title="Kişisel Bilgiler" bordered size="small" column={3}>
                                    <Descriptions.Item label="Personnel ID">{bordro.personnel_id}</Descriptions.Item>
                                    <Descriptions.Item label="TC Kimlik">{bordro.tckn}</Descriptions.Item>
                                    <Descriptions.Item label="Adı Soyadı">{bordro.adi_soyadi}</Descriptions.Item>
                                    <Descriptions.Item label="SSK Sicil">{bordro.ssk_sicil_no}</Descriptions.Item>
                                    <Descriptions.Item label="Kanun">{bordro.kanun}</Descriptions.Item>
                                    <Descriptions.Item label="Monthly Record ID">{bordro.monthly_personnel_records_id}</Descriptions.Item>
                                  </Descriptions>

                                  {/* Çalışma Bilgileri */}
                                  <Descriptions title="Çalışma Bilgileri" bordered size="small" column={3}>
                                    <Descriptions.Item label="Giriş Tarihi">
                                      {bordro.giris_t ? dayjs(bordro.giris_t).format('DD.MM.YYYY') : '-'}
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Çıkış Tarihi">
                                      {bordro.cikis_t ? dayjs(bordro.cikis_t).format('DD.MM.YYYY') : '-'}
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Toplam Gün">{bordro.t_gun}</Descriptions.Item>
                                  </Descriptions>

                                  {/* Kazanç ve Matrah Bilgileri */}
                                  <Descriptions title="Kazanç ve Matrah" bordered size="small" column={2}>
                                    <Descriptions.Item label="Normal Kazanç">
                                      {bordro.nor_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Diğer Kazanç">
                                      {bordro.dig_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Toplam Kazanç">
                                      <strong>{bordro.top_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</strong>
                                    </Descriptions.Item>
                                    <Descriptions.Item label="SSK Matrahı">
                                      {bordro.ssk_m?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Gelir Vergisi Matrahı">
                                      {bordro.g_v_m?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                  </Descriptions>

                                  {/* İşçi Kesintileri */}
                                  <Descriptions title="İşçi Kesintileri" bordered size="small" column={2}>
                                    <Descriptions.Item label="SSK İşçi Payı">
                                      {bordro.ssk_isci?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="İşsizlik Primi İşçi">
                                      {bordro.iss_p_isci?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Gelir Vergisi">
                                      {bordro.gel_ver?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Damga Vergisi">
                                      {bordro.damga_v?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Özel Kesinti">
                                      {bordro.ozel_kesinti?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="BES">
                                      {bordro.oto_kat_bes?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="İcra">
                                      {bordro.icra?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Avans">
                                      {bordro.avans?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                  </Descriptions>

                                  {/* Net Ödeme */}
                                  <Descriptions title="Net Ödeme" bordered size="small" column={1}>
                                    <Descriptions.Item label="Net Ödenen">
                                      <strong style={{ color: '#3f8600', fontSize: '16px' }}>
                                        {bordro.n_odenen?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                      </strong>
                                    </Descriptions.Item>
                                  </Descriptions>

                                  {/* İşveren Maliyeti */}
                                  <Descriptions title="İşveren Maliyeti" bordered size="small" column={2}>
                                    <Descriptions.Item label="Toplam İşveren Maliyeti">
                                      <strong style={{ color: '#cf1322', fontSize: '16px' }}>
                                        {bordro.isveren_maliyeti?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                      </strong>
                                    </Descriptions.Item>
                                    <Descriptions.Item label="SSK Teşviki">
                                      {bordro.ssk_tesviki?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="SSK İşveren Payı">
                                      {bordro.ssk_isveren?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                    <Descriptions.Item label="İşsizlik Primi İşveren">
                                      {bordro.iss_p_isveren?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                    </Descriptions.Item>
                                  </Descriptions>
                                </>
                              );
                            })()}
                          </Space>
                        </div>
                      )}
                    </Space>
                  </div>
                )
              },
              {
                key: 'toplam',
                label: 'Toplamlar',
                children: (
                  <div style={{ padding: '8px', maxHeight: '500px', overflowY: 'auto' }}>
                    {(() => {
                      const bordrolar = actionModalData || [];
                      const toplam = bordrolar.reduce((acc: any, bordro: any) => ({
                        top_kazanc: (acc.top_kazanc || 0) + (Number(bordro.top_kazanc) || 0),
                        ssk_isci: (acc.ssk_isci || 0) + (Number(bordro.ssk_isci) || 0),
                        iss_p_isci: (acc.iss_p_isci || 0) + (Number(bordro.iss_p_isci) || 0),
                        gel_ver: (acc.gel_ver || 0) + (Number(bordro.gel_ver) || 0),
                        damga_v: (acc.damga_v || 0) + (Number(bordro.damga_v) || 0),
                        ozel_kesinti: (acc.ozel_kesinti || 0) + (Number(bordro.ozel_kesinti) || 0),
                        oto_kat_bes: (acc.oto_kat_bes || 0) + (Number(bordro.oto_kat_bes) || 0),
                        icra: (acc.icra || 0) + (Number(bordro.icra) || 0),
                        avans: (acc.avans || 0) + (Number(bordro.avans) || 0),
                        n_odenen: (acc.n_odenen || 0) + (Number(bordro.n_odenen) || 0),
                        isveren_maliyeti: (acc.isveren_maliyeti || 0) + (Number(bordro.isveren_maliyeti) || 0),
                        ssk_isveren: (acc.ssk_isveren || 0) + (Number(bordro.ssk_isveren) || 0),
                        iss_p_isveren: (acc.iss_p_isveren || 0) + (Number(bordro.iss_p_isveren) || 0),
                        ssk_tesviki: (acc.ssk_tesviki || 0) + (Number(bordro.ssk_tesviki) || 0),
                      }), {});

                      return (
                        <Space direction="vertical" style={{ width: '100%' }} size="middle">
                          {/* Bordro Listesi */}
                          <Card size="small" title={`Toplam ${bordrolar.length} Bordro`}>
                            <Space direction="vertical" style={{ width: '100%' }} size="small">
                              {bordrolar.map((bordro: any, idx: number) => (
                                <div key={idx} style={{ padding: '4px 0', borderBottom: idx < bordrolar.length - 1 ? '1px solid #f0f0f0' : 'none' }}>
                                  <strong>{bordro.bolum || 'Bölüm Yok'}</strong> - {bordro.maliyet_merkezi || '-'}
                                </div>
                              ))}
                            </Space>
                          </Card>

                          {/* Kazanç Toplamları */}
                          <Descriptions title="Kazanç Toplamları" bordered size="small" column={1}>
                            <Descriptions.Item label="Toplam Kazanç">
                              <strong style={{ fontSize: '16px' }}>{toplam.top_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</strong>
                            </Descriptions.Item>
                          </Descriptions>

                          {/* Kesinti Toplamları */}
                          <Descriptions title="Kesinti Toplamları" bordered size="small" column={2}>
                            <Descriptions.Item label="SSK İşçi">{toplam.ssk_isci?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                            <Descriptions.Item label="İşsizlik İşçi">{toplam.iss_p_isci?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                            <Descriptions.Item label="Gelir Vergisi">{toplam.gel_ver?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                            <Descriptions.Item label="Damga Vergisi">{toplam.damga_v?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                            {toplam.ozel_kesinti > 0 && <Descriptions.Item label="Özel Kesinti">{toplam.ozel_kesinti?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>}
                            {toplam.oto_kat_bes > 0 && <Descriptions.Item label="BES">{toplam.oto_kat_bes?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>}
                            {toplam.icra > 0 && <Descriptions.Item label="İcra">{toplam.icra?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>}
                            {toplam.avans > 0 && <Descriptions.Item label="Avans">{toplam.avans?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>}
                          </Descriptions>

                          {/* Net ve Maliyet Toplamları */}
                          <Descriptions bordered size="small" column={1}>
                            <Descriptions.Item label="Toplam Net Ödenen">
                              <strong style={{ color: '#3f8600', fontSize: '18px' }}>
                                {toplam.n_odenen?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                              </strong>
                            </Descriptions.Item>
                            <Descriptions.Item label="Toplam İşveren Maliyeti">
                              <strong style={{ color: '#cf1322', fontSize: '18px' }}>
                                {toplam.isveren_maliyeti?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                              </strong>
                            </Descriptions.Item>
                          </Descriptions>

                          {/* İşveren Kesinti Detayları */}
                          <Descriptions title="İşveren Kesinti Detayları" bordered size="small" column={2}>
                            <Descriptions.Item label="SSK İşveren">{toplam.ssk_isveren?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                            <Descriptions.Item label="İşsizlik İşveren">{toplam.iss_p_isveren?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                            {toplam.ssk_tesviki > 0 && <Descriptions.Item label="SSK Teşviki">{toplam.ssk_tesviki?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>}
                          </Descriptions>
                        </Space>
                      );
                    })()}
                  </div>
                )
              }
            ]}
          />
        ) : actionModalType === 'maas-hesabi' ? (
          <div style={{ padding: '8px', maxHeight: '600px', overflowY: 'auto' }}>
            {actionModalData && (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {/* Draft Contract Bilgileri */}
                <Descriptions title="Taslak Sözleşme Bilgileri" bordered size="small" column={3}>
                  <Descriptions.Item label="Taslak Sözleşme ID">{actionModalData.draft_contracts_id}</Descriptions.Item>
                  <Descriptions.Item label="Maliyet Merkezi ID">{actionModalData.cc_id || '-'}</Descriptions.Item>
                  <Descriptions.Item label="Maliyet Merkezi">{actionModalData.cost_center_name}</Descriptions.Item>
                  <Descriptions.Item label="Net Ücret">
                    <strong>{actionModalData.net_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</strong>
                  </Descriptions.Item>
                  <Descriptions.Item label="Ücret Nevi">{actionModalData.ucret_nevi}</Descriptions.Item>
                  <Descriptions.Item label="Günlük Ücret">
                    {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                  </Descriptions.Item>
                  <Descriptions.Item label="Fazla Mesai Oranı">% {(actionModalData.fm_orani * 100).toFixed(0)}</Descriptions.Item>
                  <Descriptions.Item label="Tatil Mesai Oranı">% {(actionModalData.tatil_orani * 100).toFixed(0)}</Descriptions.Item>
                </Descriptions>

                {/* Puantaj Bilgileri */}
                <Descriptions title="Puantaj Verileri" bordered size="small" column={3}>
                  <Descriptions.Item label="Normal Çalışma">{actionModalData.normal_calismasi} gün</Descriptions.Item>
                  <Descriptions.Item label="İzin Günleri (İ)">{actionModalData.izin_gun_sayisi || 0} gün</Descriptions.Item>
                  <Descriptions.Item label="Yıllık İzin (S)">{actionModalData.yillik_izin_gun || 0} gün</Descriptions.Item>
                  <Descriptions.Item label="Fazla Çalışma">{actionModalData.fazla_calismasi} saat</Descriptions.Item>
                  <Descriptions.Item label="Hafta Tatili">{actionModalData.hafta_tatili} gün</Descriptions.Item>
                  <Descriptions.Item label="Resmi Tatil">{actionModalData.resmi_tatil} gün</Descriptions.Item>
                  <Descriptions.Item label="Tatil Çalışması">{actionModalData.tatil_calismasi} gün</Descriptions.Item>
                  <Descriptions.Item label="Toplam Tatiller">
                    <strong>{actionModalData.hafta_tatili + actionModalData.resmi_tatil + actionModalData.tatil_calismasi} gün</strong>
                  </Descriptions.Item>
                </Descriptions>

                {/* Kazanç Hesaplamaları */}
                <Descriptions title="Kazanç Hesaplamaları" bordered size="small" column={2}>
                  <Descriptions.Item label="Normal Kazanç">
                    {actionModalData.normal_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.normal_calismasi} × {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })})
                    </div>
                  </Descriptions.Item>
                  <Descriptions.Item label="İzin Kazanç (İ)">
                    {actionModalData.izin_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.izin_gun_sayisi || 0} İzin × {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })})
                    </div>
                  </Descriptions.Item>
                  <Descriptions.Item label="Fazla Fazla Mesai Kazancı">
                    {actionModalData.mesai_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.fazla_calismasi} × {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} / 8) × {actionModalData.fm_orani}
                    </div>
                  </Descriptions.Item>
                  <Descriptions.Item label="Eksik Mesai Kesintisi">
                    <span style={{ color: '#cf1322' }}>-{actionModalData.eksik_mesai_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</span>
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.eksik_calismasi} × {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} / 8)
                    </div>
                  </Descriptions.Item>
                  <Descriptions.Item label="Tatil Kazancı">
                    {actionModalData.tatil_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.hafta_tatili + actionModalData.resmi_tatil + actionModalData.tatil_calismasi} × {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })})
                    </div>
                  </Descriptions.Item>
                  <Descriptions.Item label="Tatil Mesai Kazancı">
                    {actionModalData.tatil_mesai_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.tatil_calismasi} × {actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} × {actionModalData.tatil_orani})
                    </div>
                  </Descriptions.Item>
                  <Descriptions.Item label="Yıllık İzin Kazancı" span={2}>
                    {actionModalData.yillik_izin_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      ({actionModalData.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} × {actionModalData.yillik_izin_gun})
                    </div>
                  </Descriptions.Item>
                </Descriptions>

                {/* Ek Ödemeler */}
                <Descriptions title="Ek Ödemeler" bordered size="small" column={3}>
                  <Descriptions.Item label="Yol">{actionModalData.yol?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="Prim">{actionModalData.prim?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="İkramiye">{actionModalData.ikramiye?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="Bayram">{actionModalData.bayram?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                  <Descriptions.Item label="Kira">{actionModalData.kira?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                </Descriptions>

                {/* Toplam Kazanç */}
                <Card>
                  <Descriptions bordered size="small" column={1}>
                    <Descriptions.Item label={<strong style={{ fontSize: '16px' }}>TOPLAM KAZANÇ</strong>}>
                      <strong style={{ color: '#52c41a', fontSize: '20px' }}>
                        {actionModalData.toplam_kazanc?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                      </strong>
                      <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                        Normal + İzin (İ) + Fazla Mesai - Eksik Mesai + Tatil + Tatil Mesai + Yıllık İzin (S) + Yol + Prim + İkramiye + Bayram + Kira
                      </div>
                    </Descriptions.Item>
                  </Descriptions>
                </Card>

                {/* Hesaplama Formülleri */}
                <Card size="small" title="Hesaplama Formülleri">
                  <ul style={{ margin: 0, paddingLeft: 20, fontSize: '12px' }}>
                    <li><strong>Günlük Ücret:</strong> Net Ücret / 30 (aylık/sabit aylık için) veya Net Ücret (günlük için)</li>
                    <li><strong>Normal Kazanç:</strong> Normal Çalışma × Günlük Ücret</li>
                    <li><strong>İzin Kazancı (İ):</strong> İzin Gün Sayısı × Günlük Ücret (ücretli izin)</li>
                    <li><strong>Fazla Mesai Kazancı:</strong> (Fazla Çalışma × Günlük Ücret / 8) × FM Oranı</li>
                    <li><strong>Eksik Mesai Kesintisi:</strong> (Eksik Çalışma × Günlük Ücret / 8)</li>
                    <li><strong>Tatil Kazancı:</strong> (Hafta Tatili + Resmi Tatil + Tatil Çalışması) × Günlük Ücret</li>
                    <li><strong>Tatil Mesai Kazancı:</strong> Tatil Çalışması × Günlük Ücret × Tatil Oranı</li>
                    <li><strong>Yıllık İzin Kazancı (S):</strong> Günlük Ücret × Yıllık İzin Günü</li>
                  </ul>
                </Card>
              </Space>
            )}
          </div>
        ) : actionModalType === 'puantaj-bilgileri' ? (
          <div style={{ padding: '8px', maxHeight: '600px', overflowY: 'auto' }}>
            {actionModalData && (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {/* Dönem ve Ücret Bilgileri */}
                <Descriptions title="Genel Bilgiler" bordered size="small" column={3}>
                  <Descriptions.Item label="Dönem">{actionModalData.donem}</Descriptions.Item>
                  <Descriptions.Item label="Ücret Nevi" span={2}>{actionModalData.ucret_nevi}</Descriptions.Item>
                </Descriptions>

                {/* Çalışma Günleri */}
                <Descriptions title="Çalışma Günleri" bordered size="small" column={3}>
                  <Descriptions.Item label="Çalışılan Gün (N)">{actionModalData.calisilan_gun_sayisi}</Descriptions.Item>
                  <Descriptions.Item label="Yıllık İzin (S)">{actionModalData.yillik_izin_gun}</Descriptions.Item>
                  <Descriptions.Item label="İzin Günü (İ)">{actionModalData.izin_gun_sayisi}</Descriptions.Item>
                  <Descriptions.Item label="Rapor Günü (R)">{actionModalData.rapor_gun_sayisi}</Descriptions.Item>
                  <Descriptions.Item label="Yarım Gün (Y)">{actionModalData.yarim_gun_sayisi}</Descriptions.Item>
                  <Descriptions.Item label="Eksik Gün (E)">{actionModalData.eksik_gun_sayisi}</Descriptions.Item>
                </Descriptions>

                {/* Fazla Mesai ve Tatiller */}
                <Descriptions title="Fazla Mesai ve Tatiller" bordered size="small" column={3}>
                  <Descriptions.Item label="Fazla Çalışma (FM)">{actionModalData.fazla_calismasi}</Descriptions.Item>
                  <Descriptions.Item label="Tatil Çalışması (M)">{actionModalData.tatil_calismasi}</Descriptions.Item>
                  <Descriptions.Item label="Hafta Tatili (H)">{actionModalData.hafta_tatili}</Descriptions.Item>
                  <Descriptions.Item label="Resmi Tatil (T)">{actionModalData.resmi_tatil}</Descriptions.Item>
                  <Descriptions.Item label="Sigorta Girmediği (DISABLE)">{actionModalData.sigorta_girmedigi}</Descriptions.Item>
                  <Descriptions.Item label="Toplam Tatiller (TT)">
                    <strong>{actionModalData.toplam_tatiller}</strong> (H+T+M)
                  </Descriptions.Item>
                </Descriptions>

                {/* Hesaplanan Değerler */}
                <Descriptions title="Hesaplanan Değerler" bordered size="small" column={2}>
                  <Descriptions.Item label="Normal Çalışması (NC)">
                    <strong style={{ color: '#1890ff', fontSize: '15px' }}>{actionModalData.normal_calismasi}</strong>
                  </Descriptions.Item>
                  <Descriptions.Item label="Toplam Gün (TG)">
                    <strong>{actionModalData.toplam_gun_sayisi}</strong> (30-DISABLE)
                  </Descriptions.Item>
                  <Descriptions.Item label="SSK Gün Sayısı (SG)">
                    <strong style={{ color: '#52c41a', fontSize: '15px' }}>{actionModalData.ssk_gun_sayisi}</strong> (TG-E)
                  </Descriptions.Item>
                </Descriptions>

                {/* Ek Ödemeler */}
                <Descriptions title="Ek Ödemeler" bordered size="small" column={3}>
                  <Descriptions.Item label="Yol (YOL)">
                    {actionModalData.yol?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                  </Descriptions.Item>
                  <Descriptions.Item label="Prim (PRI)">
                    {actionModalData.prim?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                  </Descriptions.Item>
                  <Descriptions.Item label="İkramiye (IKR)">
                    {actionModalData.ikramiye?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                  </Descriptions.Item>
                  <Descriptions.Item label="Bayram (BAY)">
                    {actionModalData.bayram?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                  </Descriptions.Item>
                  <Descriptions.Item label="Kira (KIR)">
                    {actionModalData.kira?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                  </Descriptions.Item>
                </Descriptions>

                {/* Normal Çalışma Formülü Açıklaması */}
                <Card size="small" title="Normal Çalışma (NC) Hesaplama Formülü">
                  <ul style={{ margin: 0, paddingLeft: 20, fontSize: '13px' }}>
                    <li><strong>Aylık ücretli ve eksik gün yok:</strong> NC = 30 (ay 30 günden farklıysa)</li>
                    <li><strong>Sabit aylık ve sigorta girmediği = 0:</strong> NC = 30</li>
                    <li><strong>Sabit aylık ve sigorta girmediği {'>'} 0:</strong> NC = Toplam Gün (TG)</li>
                    <li><strong>Günlük veya diğer:</strong> NC = Çalışılan Gün (N) + Yarım Gün (Y)</li>
                  </ul>
                </Card>
              </Space>
            )}
          </div>
        ) : (
          <Spin spinning={yevmiyeLoading}>
            <div style={{ padding: '16px' }}>
              {yevmiyeData && (
                <Tabs
                  defaultActiveKey="resmi"
                  items={[
                    {
                      key: 'resmi',
                      label: 'Resmi Kayıtlar',
                      children: (
                        <Space direction="vertical" style={{ width: '100%' }} size="middle">
                          {/* Resmi Kayıtlar Listesi - Hepsi gösteriliyor */}
                          {(yevmiyeData.resmi_kayitlar || []).map((kayit: any, idx: number) => (
                              <Card key={idx} size="small" title={`Bordro #${kayit.luca_bordro_id} - ${kayit.bolum}`}>
                                {/* Transaction Bilgileri */}
                                <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f5f5f5', borderRadius: 4 }}>
                                  <div style={{ display: 'flex', gap: '24px', fontSize: '13px', flexWrap: 'wrap' }}>
                                    <span><strong>Fiş No:</strong> {kayit.transaction_number}</span>
                                    <span><strong>Tarih:</strong> {kayit.transaction_date}</span>
                                    <span><strong>Dönem:</strong> {kayit.accounting_period}</span>
                                    <span><strong>Masraf Merkezi:</strong> {kayit.cost_center_name}</span>
                                    <span><strong>Personel ID:</strong> {kayit.personnel_id}</span>
                                    <span><strong>Belge Tipi:</strong> {kayit.document_type_name}</span>
                                    <span><strong>Açıklama:</strong> {kayit.description}</span>
                                  </div>
                                </div>
                                <Table
                                  dataSource={kayit.lines || []}
                                  columns={[
                                    { title: 'Hesap Kodu', dataIndex: 'account_code', key: 'account_code', width: 120 },
                                    { title: 'Hesap Adı', dataIndex: 'account_name', key: 'account_name', width: 250 },
                                    { title: 'Açıklama', dataIndex: 'description', key: 'description', width: 200 },
                                    {
                                      title: 'Borç',
                                      dataIndex: 'debit',
                                      key: 'debit',
                                      width: 120,
                                      render: (val: number) => val > 0 ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' ₺' : '-'
                                    },
                                    {
                                      title: 'Alacak',
                                      dataIndex: 'credit',
                                      key: 'credit',
                                      width: 120,
                                      render: (val: number) => val > 0 ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' ₺' : '-'
                                    }
                                  ]}
                                  pagination={false}
                                  size="small"
                                  summary={() => (
                                    <Table.Summary fixed>
                                      <Table.Summary.Row>
                                        <Table.Summary.Cell index={0} colSpan={3}>
                                          <strong>TOPLAM</strong>
                                        </Table.Summary.Cell>
                                        <Table.Summary.Cell index={1}>
                                          <strong style={{ color: '#cf1322' }}>
                                            {kayit.total_debit?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                          </strong>
                                        </Table.Summary.Cell>
                                        <Table.Summary.Cell index={2}>
                                          <strong style={{ color: '#52c41a' }}>
                                            {kayit.total_credit?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                          </strong>
                                        </Table.Summary.Cell>
                                      </Table.Summary.Row>
                                    </Table.Summary>
                                  )}
                                />
                              </Card>
                            ))}
                        </Space>
                      )
                    },
                    ...(yevmiyeData.taslak_kayitlar && yevmiyeData.taslak_kayitlar.length > 0 ? [{
                      key: 'taslak',
                      label: 'Taslak Kayıtlar',
                      children: (
                        <Space direction="vertical" style={{ width: '100%' }} size="middle">
                          {/* Taslak Kayıtlar Listesi - Hepsi gösteriliyor */}
                          {yevmiyeData.taslak_kayitlar.map((kayit: any, idx: number) => (
                            <Card key={idx} size="small" title={`Draft Contract #${kayit.draft_contract_id} - ${kayit.cost_center_name}`}>
                              {/* Transaction Bilgileri */}
                              <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f5f5f5', borderRadius: 4 }}>
                                <div style={{ display: 'flex', gap: '24px', fontSize: '13px', flexWrap: 'wrap' }}>
                                  <span><strong>Fiş No:</strong> {kayit.transaction_number}</span>
                                  <span><strong>Tarih:</strong> {kayit.transaction_date}</span>
                                  <span><strong>Dönem:</strong> {kayit.accounting_period}</span>
                                  <span><strong>Masraf Merkezi:</strong> {kayit.cost_center_name}</span>
                                  <span><strong>Personel ID:</strong> {kayit.personnel_id}</span>
                                  <span><strong>Belge Tipi:</strong> {kayit.document_type_name}</span>
                                  <span><strong>Açıklama:</strong> {kayit.description}</span>
                                </div>
                              </div>
                              <Table
                                dataSource={kayit.lines || []}
                                columns={[
                                  { title: 'Hesap Kodu', dataIndex: 'account_code', key: 'account_code', width: 120 },
                                  { title: 'Hesap Adı', dataIndex: 'account_name', key: 'account_name', width: 250 },
                                  { title: 'Açıklama', dataIndex: 'description', key: 'description', width: 200 },
                                  {
                                    title: 'Borç',
                                    dataIndex: 'debit',
                                    key: 'debit',
                                    width: 120,
                                    render: (val: number) => val > 0 ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' ₺' : '-'
                                  },
                                  {
                                    title: 'Alacak',
                                    dataIndex: 'credit',
                                    key: 'credit',
                                    width: 120,
                                    render: (val: number) => val > 0 ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' ₺' : '-'
                                  }
                                ]}
                                pagination={false}
                                size="small"
                                summary={() => (
                                  <Table.Summary fixed>
                                    <Table.Summary.Row>
                                      <Table.Summary.Cell index={0} colSpan={3}>
                                        <strong>TOPLAM</strong>
                                      </Table.Summary.Cell>
                                      <Table.Summary.Cell index={1}>
                                        <strong style={{ color: '#cf1322' }}>
                                          {kayit.total_debit?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                        </strong>
                                      </Table.Summary.Cell>
                                      <Table.Summary.Cell index={2}>
                                        <strong style={{ color: '#52c41a' }}>
                                          {kayit.total_credit?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                                        </strong>
                                      </Table.Summary.Cell>
                                    </Table.Summary.Row>
                                  </Table.Summary>
                                )}
                              />
                            </Card>
                          ))}
                        </Space>
                      )
                    }] : [])
                  ]
                }
              />
            )}

              {/* Onayla ve Kaydet Butonu */}
              {yevmiyeData && (
                <div style={{ marginTop: 16, textAlign: 'center' }}>
                  {(() => {
                    // Herhangi bir kayıt zaten kaydedilmiş mi kontrol et
                    const hasExistingTransaction = (yevmiyeData.resmi_kayitlar || []).some((k: any) => k.transaction_id && k.transaction_id > 0) ||
                                                   (yevmiyeData.taslak_kayitlar || []).some((k: any) => k.transaction_id && k.transaction_id > 0);
                    
                    if (hasExistingTransaction) {
                      return (
                        <Alert 
                          message="Bu personelin yevmiye kaydı zaten yapılmış" 
                          type="info" 
                          showIcon 
                          style={{ marginBottom: 16 }}
                        />
                      );
                    }
                    
                    return (
                      <Button
                        type="primary"
                        size="large"
                        loading={yevmiyeSaving}
                        onClick={handleSaveYevmiyePersonnel}
                        icon={<span style={{ marginRight: 8 }}>✓</span>}
                      >
                        Onayla ve Kaydet ({(yevmiyeData.resmi_kayitlar?.length || 0) + (yevmiyeData.taslak_kayitlar?.length || 0)} Kayıt)
                      </Button>
                    );
                  })()}
                </div>
              )}
            </div>
          </Spin>
        )}
      </Modal>
    </div>
  );
};

export default BordroCalculationPageGrouped;
