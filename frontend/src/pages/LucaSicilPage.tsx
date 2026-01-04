import React, { useState, useEffect } from 'react';
import { Card, Button, Upload, Table, message, Space, Tag, Select, Statistic, Row, Col, Typography } from 'antd';
import { UploadOutlined, ReloadOutlined, DeleteOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import axios from 'axios';

const { Title } = Typography;

const API_URL = 'http://localhost:8000/api/v1/luca-sicil';

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
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    passive: 0,
  });

  // Dönemleri yükle
  const loadPeriods = async () => {
    try {
      const res = await axios.get(`${API_URL}/periods`);
      setPeriods(res.data || []);
      if (res.data && res.data.length > 0 && !selectedPeriod) {
        setSelectedPeriod(res.data[0]);
      }
    } catch (error) {
      console.error('Dönemler yüklenemedi:', error);
      setPeriods([]);
    }
  };

  // Kayıtları yükle
  const loadRecords = async (donem?: string) => {
    setLoading(true);
    try {
      const params = donem ? { donem } : {};
      const res = await axios.get(`${API_URL}/records`, { params });
      const data = res.data || [];
      setRecords(data);
      
      // İstatistikler
      const total = data.length;
      const active = data.filter((r: SicilRecord) => !r.isten_cikis_tarihi).length;
      const passive = total - active;
      setStats({ total, active, passive });
      
    } catch (error) {
      message.error('Kayıtlar yüklenemedi');
      console.error(error);
      setRecords([]);
      setStats({ total: 0, active: 0, passive: 0 });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPeriods().catch(console.error);
  }, []);

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
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const res = await axios.post(`${API_URL}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          params: { force_update: false },
        });
        
        message.success(`✅ ${res.data.imported_records} kayıt import edildi (Dönem: ${res.data.donem})`);
        
        if (res.data.warnings && res.data.warnings.length > 0) {
          message.warning(`⚠️ ${res.data.warnings.length} uyarı var`);
        }
        
        // Yenile
        await loadPeriods();
        setSelectedPeriod(res.data.donem);
        
      } catch (error: any) {
        message.error(`Hata: ${error.response?.data?.detail || 'Upload başarısız'}`);
        console.error(error);
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
        `${ucret?.toLocaleString('tr-TR')} ${record.ucret_tipi || ''}`,
    },
    {
      title: 'Ünvan',
      dataIndex: 'unvan',
      key: 'unvan',
      width: 150,
    },
  ];

  return (
    <>
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
            <Upload {...uploadProps}>
              <Button 
                type="primary" 
                icon={<UploadOutlined />} 
                loading={uploading}
              >
                Excel Yükle
              </Button>
            </Upload>
            
            <Select
              style={{ width: 200 }}
              placeholder="Dönem seçin"
              value={selectedPeriod}
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
          scroll={{ x: 1400 }}
          pagination={{
            total: records.length,
            pageSize: 50,
            showTotal: (total) => `Toplam ${total} kayıt`,
            showSizeChanger: true,
            pageSizeOptions: ['20', '50', '100', '200'],
          }}
        />
      </Card>
    </>
  );
}
