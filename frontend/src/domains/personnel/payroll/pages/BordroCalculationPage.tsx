import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Space, message, DatePicker, Statistic, Row, Col, Tag, Modal, Descriptions, Spin } from 'antd';
import { CalculatorOutlined, ReloadOutlined, FileTextOutlined, EyeOutlined, SaveOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL || ''}/api/v2/personnel`;

interface PayrollRecord {
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
  yevmiye_tipi: 'tipa' | 'tipb' | 'tipc' | null;
  
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

interface PayrollListResponse {
  total: number;
  items: PayrollRecord[];
}

export const BordroCalculationPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [payrollData, setPayrollData] = useState<PayrollRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [selectedRecord, setSelectedRecord] = useState<PayrollRecord | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [yevmiyePreviewVisible, setYevmiyePreviewVisible] = useState(false);
  const [yevmiyePreviewData, setYevmiyePreviewData] = useState<any>(null);
  const [yevmiyePreviewLoading, setYevmiyePreviewLoading] = useState(false);
  const [currentCalculationId, setCurrentCalculationId] = useState<number | null>(null);
  const [stats, setStats] = useState({
    totalNet: 0,
    totalSSK: 0,
    totalTax: 0,
    totalElden: 0,
    typeA: 0,
    typeB: 0,
    typeC: 0,
  });

  const fetchPayrollData = async () => {
    const yil = selectedDate.year();
    const ay = selectedDate.month() + 1;
    
    setLoading(true);
    try {
      const response = await axios.get<PayrollListResponse>(`${API_URL}/bordro-calculation/list`, {
        params: { yil, ay, limit: 1000 }
      });
      
      setPayrollData(response.data.items);
      setTotal(response.data.total);
      
      // İstatistikleri hesapla
      const stats = response.data.items.reduce((acc, item) => ({
        totalNet: acc.totalNet + Number(item.maas1_net_odenen || 0),
        totalSSK: acc.totalSSK + Number(item.maas1_ssk_isci || 0),
        totalTax: acc.totalTax + Number(item.maas1_gelir_vergisi || 0),
        totalElden: acc.totalElden + Number(item.elden_ucret_yuvarlanmis || 0),
        typeA: acc.typeA + (item.yevmiye_tipi === 'tipa' ? 1 : 0),
        typeB: acc.typeB + (item.yevmiye_tipi === 'tipb' ? 1 : 0),
        typeC: acc.typeC + (item.yevmiye_tipi === 'tipc' ? 1 : 0),
      }), {
        totalNet: 0,
        totalSSK: 0,
        totalTax: 0,
        totalElden: 0,
        typeA: 0,
        typeB: 0,
        typeC: 0,
      });
      
      setStats(stats);
      
    } catch (error: any) {
      message.error('Bordro listesi yüklenemedi: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = async () => {
    const yil = selectedDate.year();
    const ay = selectedDate.month() + 1;
    
    setCalculating(true);
    try {
      const response = await axios.post(`${API_URL}/bordro-calculation/calculate?yil=${yil}&ay=${ay}`);
      
      message.success(`✅ ${response.data.total} kayıt hesaplandı (${response.data.calculated} yeni, ${response.data.updated} güncelleme)`);
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.error('Bordro hesaplama hataları:', response.data.errors);
        console.table(response.data.errors);
        message.warning(`⚠️ ${response.data.errors.length} kayıtta hata oluştu (Detaylar console'da)`, 5);
      }
      
      // Listeyi yenile
      await fetchPayrollData();
      
    } catch (error: any) {
      message.error('Bordro hesaplaması başarısız: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCalculating(false);
    }
  };

  const handleShowYevmiyePreview = async (calculationId: number) => {
    setCurrentCalculationId(calculationId);
    setYevmiyePreviewLoading(true);
    setYevmiyePreviewVisible(true);
    
    try {
      const response = await axios.get(`${API_URL}/bordro-calculation/preview-yevmiye/${calculationId}`);
      setYevmiyePreviewData(response.data);
    } catch (error: any) {
      message.error('Yevmiye ön izleme hatası: ' + (error.response?.data?.detail || error.message));
      setYevmiyePreviewVisible(false);
    } finally {
      setYevmiyePreviewLoading(false);
    }
  };

  const handleSaveYevmiye = async () => {
    if (!currentCalculationId) return;
    
    setYevmiyePreviewLoading(true);
    try {
      await axios.post(`${API_URL}/bordro-calculation/save-yevmiye/${currentCalculationId}`);
      
      message.success('✅ Yevmiye kaydı başarıyla oluşturuldu');
      
      setYevmiyePreviewVisible(false);
      setYevmiyePreviewData(null);
      setCurrentCalculationId(null);
      
      // Listeyi yenile
      await fetchPayrollData();
      
    } catch (error: any) {
      message.error('Yevmiye kaydetme hatası: ' + (error.response?.data?.detail || error.message));
    } finally {
      setYevmiyePreviewLoading(false);
    }
  };

  const showDetail = (record: PayrollRecord) => {
    setSelectedRecord(record);
    setDetailModalVisible(true);
  };

  useEffect(() => {
    fetchPayrollData();
  }, [selectedDate]);

  const columns = [
    {
      title: 'TC',
      dataIndex: 'tckn',
      key: 'tckn',
      width: 120,
    },
    {
      title: 'Adı Soyadı',
      dataIndex: 'adi_soyadi',
      key: 'adi_soyadi',
      width: 180,
    },
    {
      title: 'Şantiye',
      dataIndex: 'maliyet_merkezi',
      key: 'maliyet_merkezi',
      width: 150,
    },
    {
      title: 'Ücret Türü',
      dataIndex: 'ucret_nevi',
      key: 'ucret_nevi',
      width: 100,
    },
    {
      title: 'Kanun',
      dataIndex: 'kanun_tipi',
      key: 'kanun_tipi',
      width: 80,
    },
    {
      title: 'Net Ödenen',
      dataIndex: 'maas1_net_odenen',
      key: 'maas1_net_odenen',
      align: 'right' as const,
      width: 120,
      render: (val: number) => val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '0.00',
    },
    {
      title: 'SSK İşçi',
      dataIndex: 'maas1_ssk_isci',
      key: 'maas1_ssk_isci',
      align: 'right' as const,
      width: 110,
      render: (val: number) => val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '0.00',
    },
    {
      title: 'Elden Ücret',
      dataIndex: 'elden_ucret_yuvarlanmis',
      key: 'elden_ucret_yuvarlanmis',
      align: 'right' as const,
      width: 120,
      render: (val: number) => val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '0.00',
    },
    {
      title: 'Yevmiye Tipi',
      dataIndex: 'yevmiye_tipi',
      key: 'yevmiye_tipi',
      width: 100,
      render: (val: string) => {
        if (!val) return '-';
        const colors: Record<string, string> = {
          'tipa': 'blue',
          'tipb': 'green',
          'tipc': 'orange',
        };
        const labels: Record<string, string> = {
          'tipa': 'Tip A',
          'tipb': 'Tip B',
          'tipc': 'Tip C',
        };
        return <Tag color={colors[val]}>{labels[val] || val}</Tag>;
      },
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 200,
      render: (_: any, record: PayrollRecord) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => showDetail(record)}
          >
            Detay
          </Button>
          {!record.transaction_id ? (
            <Button
              type="primary"
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => handleShowYevmiyePreview(record.id, record.adi_soyadi)}
            >
              Yevmiye
            </Button>
          ) : (
            <Tag color="success">Fiş: {record.fis_no}</Tag>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="Bordro Hesaplama" style={{ marginBottom: 24 }}>
        <Space size="large">
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
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card>
            <Statistic 
              title="Toplam Personel" 
              value={total} 
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic 
              title="Net Ödenen Toplam" 
              value={stats.totalNet.toFixed(0)} 
              suffix="₺"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic 
              title="SSK İşçi Toplam" 
              value={stats.totalSSK.toFixed(0)} 
              suffix="₺"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic 
              title="Elden Ücret Toplam" 
              value={stats.totalElden.toFixed(0)} 
              suffix="₺"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic 
              title="Yevmiye Tipleri" 
              value={`A:${stats.typeA} B:${stats.typeB} C:${stats.typeC}`}
              valueStyle={{ fontSize: 16 }}
            />
          </Card>
        </Col>
      </Row>

      <Card title={`Hesaplanan Bordro (${selectedDate.format('YYYY-MM')})`}>
        <Table
          columns={columns}
          dataSource={payrollData}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} kayıt`,
          }}
          scroll={{ x: 1500 }}
          size="small"
        />
      </Card>

      <Modal
        title="Bordro Detayı"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={800}
        footer={null}
      >
        {selectedRecord && (
          <Descriptions bordered column={2} size="small">
            <Descriptions.Item label="TC" span={1}>{selectedRecord.tckn}</Descriptions.Item>
            <Descriptions.Item label="Adı Soyadı" span={1}>{selectedRecord.adi_soyadi}</Descriptions.Item>
            <Descriptions.Item label="Maliyet Merkezi" span={1}>{selectedRecord.maliyet_merkezi}</Descriptions.Item>
            <Descriptions.Item label="Ücret Türü" span={1}>{selectedRecord.ucret_nevi}</Descriptions.Item>
            <Descriptions.Item label="Kanun" span={1}>{selectedRecord.kanun_tipi}</Descriptions.Item>
            <Descriptions.Item label="Yevmiye Tipi" span={1}>
              {selectedRecord.yevmiye_tipi ? (
                <Tag color={
                  selectedRecord.yevmiye_tipi === 'tipa' ? 'blue' : 
                  selectedRecord.yevmiye_tipi === 'tipb' ? 'green' : 'orange'
                }>
                  {selectedRecord.yevmiye_tipi.toUpperCase()}
                </Tag>
              ) : '-'}
            </Descriptions.Item>

            <Descriptions.Item label="LUCA Maaş (Maaş1)" span={2} style={{ fontWeight: 'bold', background: '#f0f5ff' }}>
            </Descriptions.Item>
            <Descriptions.Item label="Net Ödenen">{selectedRecord.maas1_net_odenen?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="SSK İşçi">{selectedRecord.maas1_ssk_isci?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="SSK İşveren">{selectedRecord.maas1_ssk_isveren?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="İşsizlik İşçi">{selectedRecord.maas1_issizlik_isci?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="İşsizlik İşveren">{selectedRecord.maas1_issizlik_isveren?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Gelir Vergisi">{selectedRecord.maas1_gelir_vergisi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Damga Vergisi">{selectedRecord.maas1_damga_vergisi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Diğer Kesintiler">{selectedRecord.maas1_diger_kesintiler?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>

            <Descriptions.Item label="Puantaj Maaş (Maaş2)" span={2} style={{ fontWeight: 'bold', background: '#f6ffed' }}>
            </Descriptions.Item>
            <Descriptions.Item label="Normal Çalışma">{selectedRecord.maas2_normal_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Fazla Mesai">{selectedRecord.maas2_fm_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Eksik Mesai" style={{ color: '#cf1322' }}>-{selectedRecord.maas2_em_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Tatil Çalışması">{selectedRecord.maas2_tatil_calismasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Yıllık İzin">{selectedRecord.maas2_yillik_izin?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Toplam Maaş2" span={2} style={{ fontWeight: 'bold' }}>{selectedRecord.maas2_toplam?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>

            <Descriptions.Item label="Elden Ücret (Ham)" span={2} style={{ fontWeight: 'bold', background: '#fff7e6' }}>
            </Descriptions.Item>
            <Descriptions.Item label="Ham Tutar">{selectedRecord.elden_ucret_ham?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
            <Descriptions.Item label="Yuvarlanmış" style={{ fontSize: 16, fontWeight: 'bold', color: '#52c41a' }}>{selectedRecord.elden_ucret_yuvarlanmis?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      <Modal
        title="Yevmiye Önizleme"
        open={yevmiyePreviewVisible}
        onCancel={() => {
          setYevmiyePreviewVisible(false);
          setYevmiyePreviewData(null);
          setCurrentCalculationId(null);
        }}
        width={1000}
        footer={[
          <Button 
            key="cancel" 
            onClick={() => {
              setYevmiyePreviewVisible(false);
              setYevmiyePreviewData(null);
              setCurrentCalculationId(null);
            }}
          >
            İptal
          </Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            loading={yevmiyePreviewLoading}
            onClick={handleSaveYevmiye}
          >
            Kaydet
          </Button>,
        ]}
      >
        {yevmiyePreviewLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Yevmiye hazırlanıyor...</p>
          </div>
        ) : yevmiyePreviewData?.preview ? (
          <div>
            {yevmiyePreviewData.preview.map((entry: any, idx: number) => (
              <Card 
                key={idx} 
                title={entry.type === 'RESMİ KAYIT' ? '📋 Resmi Kayıt' : '✍️ Taslak Kayıt (Elden Ödeme)'}
                style={{ marginBottom: 16 }}
                size="small"
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span><strong>Fiş No:</strong> {entry.transaction_number}</span>
                    <span><strong>Tarih:</strong> {entry.transaction_date}</span>
                  </div>
                  
                  <Table
                    dataSource={entry.lines}
                    columns={[
                      {
                        title: 'Hesap Kodu',
                        dataIndex: 'account_code',
                        key: 'account_code',
                        width: 120,
                      },
                      {
                        title: 'Açıklama',
                        dataIndex: 'description',
                        key: 'description',
                      },
                      {
                        title: 'Borç',
                        dataIndex: 'debit',
                        key: 'debit',
                        align: 'right' as const,
                        width: 150,
                        render: (val: number) => val > 0 ? 
                          <span style={{ color: '#cf1322', fontWeight: 500 }}>
                            {val.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                          </span> : '-',
                      },
                      {
                        title: 'Alacak',
                        dataIndex: 'credit',
                        key: 'credit',
                        align: 'right' as const,
                        width: 150,
                        render: (val: number) => val > 0 ? 
                          <span style={{ color: '#3f8600', fontWeight: 500 }}>
                            {val.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                          </span> : '-',
                      },
                    ]}
                    pagination={false}
                    size="small"
                    rowKey={(_, index) => `${idx}-${index}`}
                    summary={() => (
                      <Table.Summary fixed>
                        <Table.Summary.Row style={{ fontWeight: 'bold', background: '#fafafa' }}>
                          <Table.Summary.Cell index={0} colSpan={2}>
                            TOPLAM
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={2} align="right">
                            <span style={{ color: '#cf1322', fontWeight: 600 }}>
                              {entry.total_debit.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                            </span>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={3} align="right">
                            <span style={{ color: '#3f8600', fontWeight: 600 }}>
                              {entry.total_credit.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                            </span>
                          </Table.Summary.Cell>
                        </Table.Summary.Row>
                      </Table.Summary>
                    )}
                  />
                  
                  <div style={{ textAlign: 'right', marginTop: 8 }}>
                    {entry.balanced ? (
                      <Tag color="success" style={{ fontSize: 14 }}>✓ Dengeli</Tag>
                    ) : (
                      <Tag color="error" style={{ fontSize: 14 }}>✗ Dengesiz</Tag>
                    )}
                  </div>
                  
                  {entry.calculation_details && (
                    <Descriptions 
                      bordered 
                      column={2} 
                      size="small"
                      title="Hesaplama Detayları"
                      style={{ marginTop: 16 }}
                    >
                      <Descriptions.Item label="Günlük Ücret">{entry.calculation_details.gunluk_ucret?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Normal Çalışma">{entry.calculation_details.normal_calisma_tutar?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Fazla Mesai">{entry.calculation_details.fazla_calisma_tutar?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Tatil">{entry.calculation_details.tatil_tutar?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Tatil Çalışması">{entry.calculation_details.tatil_calismasi_tutar?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Yıllık İzin">{entry.calculation_details.yillik_izin_tutar?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Net Maaş Tutarı" span={2} style={{ fontWeight: 'bold' }}>{entry.calculation_details.net_maas_tutar?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Bordro Net Toplamı">{entry.calculation_details.bordro_net_toplami?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Elden Kalan">{entry.calculation_details.elden_kalan?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Yuvarlanmış">{entry.calculation_details.elden_kalan_yuvarlanmis?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                      <Descriptions.Item label="Yuvarlama Farkı">{entry.calculation_details.elden_yuvarlamasi?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</Descriptions.Item>
                    </Descriptions>
                  )}
                </Space>
              </Card>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>Önizleme verisi yüklenmedi</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BordroCalculationPage;
