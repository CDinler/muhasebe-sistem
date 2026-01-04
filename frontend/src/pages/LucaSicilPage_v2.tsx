import { useState, useEffect, useMemo } from 'react';
import { Card, Button, Upload, Table, message, Space, Tag, Select, Statistic, Row, Col, Typography, Spin, Input, Modal } from 'antd';
import { UploadOutlined, ReloadOutlined, DeleteOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import axios from 'axios';

const { Title } = Typography;

const API_URL = 'http://localhost:8000/api/v1/luca-sicil';

// Columns tanımı - Component dışında (performans için)
const columns = [
  {
    title: 'Personel',
    dataIndex: 'personnel_name',
    key: 'personnel_name',
    width: 200,
    fixed: 'left' as const,
  },
  {
    title: 'Bölüm',
    dataIndex: 'bolum_adi',
    key: 'bolum_adi',
    width: 250,
  },
  {
    title: 'Maliyet Merkezi',
    dataIndex: 'cost_center_code',
    key: 'cost_center_code',
    width: 150,
    render: (code: string | null) => 
      code ? <Tag color="blue">{code}</Tag> : <Tag>-</Tag>,
  },
  {
    title: 'İşe Giriş',
    dataIndex: 'ise_giris_tarihi',
    key: 'ise_giris_tarihi',
    width: 120,
    render: (date: string) => date ? new Date(date).toLocaleDateString('tr-TR') : '-',
  },
  {
    title: 'İşten Çıkış',
    dataIndex: 'isten_cikis_tarihi',
    key: 'isten_cikis_tarihi',
    width: 120,
    render: (date: string | null) => date ? new Date(date).toLocaleDateString('tr-TR') : '-',
  },
  {
    title: 'Durum',
    key: 'status',
    width: 100,
    render: (_: any, record: SicilRecord) => 
      record.isten_cikis_tarihi ? 
        <Tag color="default">Pasif</Tag> : 
        <Tag color="success">Aktif</Tag>,
  },
  {
    title: 'Ücret',
    dataIndex: 'ucret',
    key: 'ucret',
    width: 120,
    align: 'right' as const,
    render: (ucret: number, record: SicilRecord) => 
      ucret ? `${ucret.toLocaleString('tr-TR')} ${record.ucret_tipi || ''}` : '-',
  },
  {
    title: 'Ünvan',
    dataIndex: 'unvan',
    key: 'unvan',
    width: 150,
  },
];

interface SicilRecord {
  id: number;
  personnel_id: number;
  personnel_name: string;
  donem: string;
  bolum_adi: string;
  cost_center_code: string | null;
  ise_giris_tarihi: string;
  isten_cikis_tarihi: string | null;
  ucret: number;
  ucret_tipi: string;
  isyeri: string;
  unvan: string;
}

export default function LucaSicilPage() {
  const [records, setRecords] = useState<SicilRecord[]>([]);
  const [periods, setPeriods] = useState<string[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('');
  const [uploadPeriod, setUploadPeriod] = useState<string>(''); // Manuel dönem girişi
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [warningsModalVisible, setWarningsModalVisible] = useState(false);
  const [uploadWarnings, setUploadWarnings] = useState<any[]>([]);
  const [uploadResult, setUploadResult] = useState<any>(null);
  
  // İstatistikleri memoize et - sadece records değişince hesapla
  const stats = useMemo(() => {
    const total = records.length;
    const active = records.filter(r => !r.isten_cikis_tarihi).length;
    const passive = total - active;
    return { total, active, passive };
  }, [records]);

  // Component mount kontrolü
  useEffect(() => {
    console.log('LucaSicilPage mounted');
    setMounted(true);
    return () => {
      console.log('LucaSicilPage unmounted');
      setMounted(false);
    };
  }, []);

  // Dönemleri yükle
  const loadPeriods = async () => {
    try {
      console.log('Loading periods...');
      const res = await axios.get(`${API_URL}/periods`);
      console.log('Periods loaded:', res.data);
      // API {periods: [...]} formatında dönüyor
      const periodsData = Array.isArray(res.data) ? res.data : (res.data.periods || []);
      setPeriods(periodsData);
      if (periodsData.length > 0 && !selectedPeriod) {
        setSelectedPeriod(periodsData[0]);
      }
    } catch (error: any) {
      console.error('Dönemler yüklenemedi:', error);
      if (error.response?.status === 404) {
        console.log('API endpoint not found - checking backend');
      }
      setPeriods([]);
    }
  };

  // Kayıtları yükle
  const loadRecords = async (donem?: string) => {
    setLoading(true);
    try {
      const params = donem ? { donem } : {};
      console.log('Loading records for:', params);
      const res = await axios.get(`${API_URL}/records`, { params });
      const data = res.data || [];
      console.log('Records loaded:', data.length);
      setRecords(data);
      
    } catch (error) {
      console.error('Kayıtlar yüklenemedi:', error);
      message.error('Kayıtlar yüklenemedi');
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mounted) {
      loadPeriods().catch(console.error);
    }
  }, [mounted]);

  useEffect(() => {
    if (selectedPeriod) {
      loadRecords(selectedPeriod).catch(console.error);
    }
  }, [selectedPeriod]);

  // Excel upload
  const uploadProps: UploadProps = {
    name: 'file',
    accept: '.xlsx,.xls',
    showUploadList: false,
    beforeUpload: async (file) => {
      // Dönem format kontrolü
      if (uploadPeriod && !/^\d{4}-\d{2}$/.test(uploadPeriod)) {
        message.error('Dönem formatı hatalı. YYYY-MM formatında olmalı (örn: 2025-01)');
        return false;
      }

      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const params: any = { force_update: false };
        if (uploadPeriod) {
          params.donem = uploadPeriod; // Manuel dönem
        }
        
        const res = await axios.post(`${API_URL}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          params,
        });
        
        setUploadResult(res.data);
        
        message.success(`✅ ${res.data.imported_records} kayıt import edildi (Dönem: ${res.data.donem})`);
        
        if (res.data.warnings && res.data.warnings.length > 0) {
          console.log('⚠️ UPLOAD UYARILARI:', res.data.warnings);
          setUploadWarnings(res.data.warnings);
          setWarningsModalVisible(true);
        }
        
        // Yenile
        await loadPeriods();
        setSelectedPeriod(res.data.donem);
        setUploadPeriod(''); // Temizle
        
      } catch (error: any) {
        const errorDetail = error.response?.data?.detail || error.response?.data || 'Upload başarısız';
        console.error('Upload Error:', error);
        console.error('Error Response:', error.response?.data);
        message.error(`Hata: ${typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail)}`);
      } finally {
        setUploading(false);
      }
      
      return false;
    },
  };

  // Dönem sil
  const deletePeriod = async (donem: string) => {
    try {
      await axios.delete(`${API_URL}/period/${donem}`);
      message.success(`${donem} dönemi silindi`);
      await loadPeriods();
      setSelectedPeriod('');
    } catch (error) {
      message.error('Dönem silinemedi');
      console.error(error);
    }
  };

  if (!mounted) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card 
        title={
          <div>
            <Title level={3} style={{ margin: 0 }}>Luca Personel Sicil</Title>
            <div style={{ fontSize: '14px', fontWeight: 'normal', color: '#666', marginTop: 4 }}>
              Luca'dan export edilen aylık personel sicil kayıtları
            </div>
          </div>
        }
        style={{ marginBottom: 16 }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Row gutter={16}>
            <Col span={6}>
              <Statistic 
                title="Toplam Kayıt" 
                value={stats.total} 
                prefix={<CheckCircleOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Aktif Personel" 
                value={stats.active}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Pasif Personel" 
                value={stats.passive}
                valueStyle={{ color: '#999' }}
              />
            </Col>
          </Row>
          
          <Space>
            <Space.Compact>
              <Input
                style={{ width: 150 }}
                placeholder="Dönem (YYYY-MM)"
                value={uploadPeriod}
                onChange={(e) => setUploadPeriod(e.target.value)}
                maxLength={7}
              />
              <Upload {...uploadProps}>
                <Button 
                  type="primary" 
                  icon={<UploadOutlined />} 
                  loading={uploading}
                >
                  Excel Yükle
                </Button>
              </Upload>
            </Space.Compact>
            
            <Select
              style={{ width: 200 }}
              placeholder="Dönem seçin"
              value={selectedPeriod || undefined}
              onChange={setSelectedPeriod}
              options={periods.map(p => ({ label: p, value: p }))}
            />
            
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => loadRecords(selectedPeriod)}
              loading={loading}
            >
              Yenile
            </Button>
            
            {selectedPeriod && (
              <Button 
                danger
                icon={<DeleteOutlined />} 
                onClick={() => {
                  if (window.confirm(`${selectedPeriod} dönemini silmek istediğinize emin misiniz?`)) {
                    deletePeriod(selectedPeriod);
                  }
                }}
              >
                Dönemi Sil
              </Button>
            )}
          </Space>
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={records}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400, y: 600 }}
          pagination={{
            total: records.length,
            defaultPageSize: 100,
            pageSize: 100,
            showTotal: (total) => `Toplam ${total} kayıt`,
            showSizeChanger: true,
            pageSizeOptions: ['50', '100', '200', '500'],
          }}
        />
      </Card>

      {/* Warnings Modal */}
      <Modal
        title={
          <Space>
            <WarningOutlined style={{ color: '#faad14' }} />
            <span>Upload Uyarıları ({uploadWarnings.length})</span>
          </Space>
        }
        open={warningsModalVisible}
        onCancel={() => setWarningsModalVisible(false)}
        width={800}
        footer={[
          <Button key="copy" onClick={() => {
            const text = uploadWarnings.map((w, i) => `${i + 1}. ${JSON.stringify(w)}`).join('\n');
            navigator.clipboard.writeText(text);
            message.success('Uyarılar panoya kopyalandı');
          }}>
            Kopyala
          </Button>,
          <Button key="close" type="primary" onClick={() => setWarningsModalVisible(false)}>
            Kapat
          </Button>
        ]}
      >
        {uploadResult && (
          <Card size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic title="Toplam Satır" value={uploadResult.total_rows} />
              </Col>
              <Col span={6}>
                <Statistic title="İmport Edilen" value={uploadResult.imported_records} valueStyle={{ color: '#52c41a' }} />
              </Col>
              <Col span={6}>
                <Statistic title="Güncellenen" value={uploadResult.updated_records} valueStyle={{ color: '#1890ff' }} />
              </Col>
              <Col span={6}>
                <Statistic title="Atlanan" value={uploadResult.skipped_records} valueStyle={{ color: '#ff4d4f' }} />
              </Col>
            </Row>
          </Card>
        )}
        
        <div style={{ maxHeight: 500, overflowY: 'auto' }}>
          <Table
            size="small"
            columns={[
              { title: '#', width: 60, render: (_: any, __: any, index: number) => index + 1 },
              { title: 'Satır', dataIndex: 'row', width: 80 },
              { title: 'TC', dataIndex: 'tc', width: 120 },
              { title: 'Mesaj', dataIndex: 'message', ellipsis: true },
            ]}
            dataSource={uploadWarnings}
            pagination={false}
            rowKey={(_, index) => index}
          />
        </div>
      </Modal>
    </div>
  );
}
