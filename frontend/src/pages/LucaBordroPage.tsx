import { useState, useEffect, useCallback } from 'react';
import { Card, Table, Upload, Button, message, Select, Space, Tag } from 'antd';
import { UploadOutlined, ReloadOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface LucaBordro {
  id: number;
  donem: string;  // date ISO string
  personnel_id: number | null;
  cost_center_id: number | null;
  tc: string | null;
  adi: string | null;
  soyadi: string | null;
  giris_t: string | null;  // ise_giris_tarihi
  cikis_t: string | null;  // isten_cikis_tarihi
  t_gun: number | null;  // toplam_gun
  ucretli_izin_gun: number | null;
  ucretsiz_izin_gun: number | null;
  nor_kazanc: number | null;  // normal_kazanc
  dig_kazanc: number | null;  // diger_kazanc
  fazla_mes: number | null;  // fazla_mesai
  t_kazanc: number | null;  // toplam_kazanc
  sgk_iscisi: number | null;  // sgk_isci_payi
  issiz_iscisi: number | null;  // issizlik_isci_payi
  gel_ver: number | null;  // gelir_vergisi
  damga_v: number | null;  // damga_vergisi
  t_kesinti: number | null;  // toplam_kesinti
  net_ucret: number | null;
  sgk_isveren: number | null;  // sgk_isveren_payi
  issiz_isveren: number | null;  // issizlik_isveren_payi
  t_isveren_maliyet: number | null;  // toplam_isveren_maliyet
  created_at: string;
  updated_at: string;
}

export default function LucaBordroPage() {
  const [bordroList, setBordroList] = useState<LucaBordro[]>([]);
  const [donemler, setDonemler] = useState<string[]>([]);
  const [selectedDonem, setSelectedDonem] = useState<string>('');
  const [uploadDonem, setUploadDonem] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(100);

  const loadDonemler = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/luca-bordro/donemler`);
      const periods = res.data.donemler || [];
      setDonemler(periods);
      if (periods.length > 0 && !selectedDonem) {
        setSelectedDonem(periods[0]);
      }
    } catch (error) {
      message.error('Dönemler yüklenemedi');
    }
  }, [selectedDonem]);

  const loadBordro = useCallback(async (page = 1) => {
    if (!selectedDonem) return;
    
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/luca-bordro/`, {
        params: { donem: selectedDonem, page, page_size: pageSize }
      });
      // Backend artık { items, total, page, page_size } formatında dönüyor
      setBordroList(res.data.items || []);
      setTotal(res.data.total || 0);
      setCurrentPage(page);
    } catch (error) {
      message.error('Bordro listesi yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  }, [selectedDonem, pageSize]);

  useEffect(() => {
    loadDonemler();
  }, [loadDonemler]);

  useEffect(() => {
    if (selectedDonem) {
      loadBordro();
    }
  }, [selectedDonem, loadBordro]);
  }, [selectedDonem]);

  const handleUpload = async (file: UploadFile) => {
    if (!uploadDonem) {
      message.error('Lütfen yüklemek istediğiniz dönemi seçin (örn: 2025-11)');
      return false;
    }

    const formData = new FormData();
    formData.append('file', file as any);

    setUploading(true);
    try {
      const res = await axios.post(`${API_URL}/luca-bordro/upload?donem=${uploadDonem}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (res.data.success) {
        message.success(res.data.message);
        setSelectedDonem(uploadDonem);  // Upload edilen dönemi göster
        await loadDonemler();
        await loadBordro();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Yükleme hatası');
    } finally {
      setUploading(false);
    }
    
    return false;
  };

  const columns = [
    {
      title: 'Ad',
      dataIndex: 'adi',
      key: 'adi',
      width: 120,
      fixed: 'left' as const
    },
    {
      title: 'Soyad',
      dataIndex: 'soyadi',
      key: 'soyadi',
      width: 120,
      fixed: 'left' as const
    },
    {
      title: 'TC',
      dataIndex: 'tc',
      key: 'tc',
      width: 120
    },
    {
      title: 'Dönem',
      dataIndex: 'donem',
      key: 'donem',
      width: 120,
      render: (val: string) => val ? new Date(val).toLocaleDateString('tr-TR', { year: 'numeric', month: 'long' }) : '-'
    },
    {
      title: 'Toplam Gün',
      dataIndex: 't_gun',
      key: 't_gun',
      width: 100,
      align: 'center' as const
    },
    {
      title: 'Normal Kazanç',
      dataIndex: 'nor_kazanc',
      key: 'nor_kazanc',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Diğer Kazanç',
      dataIndex: 'dig_kazanc',
      key: 'dig_kazanc',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Fazla Mesai',
      dataIndex: 'fazla_mes',
      key: 'fazla_mes',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Toplam Kazanç',
      dataIndex: 't_kazanc',
      key: 't_kazanc',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2, style: 'currency', currency: 'TRY' })
    },
    {
      title: 'SGK İşçi',
      dataIndex: 'sgk_iscisi',
      key: 'sgk_iscisi',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Gelir Vergisi',
      dataIndex: 'gel_ver',
      key: 'gel_ver',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Damga Vergisi',
      dataIndex: 'damga_v',
      key: 'damga_v',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Toplam Kesinti',
      dataIndex: 't_kesinti',
      key: 't_kesinti',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Net Ücret',
      dataIndex: 'net_ucret',
      key: 'net_ucret',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2, style: 'currency', currency: 'TRY' })
    },
    {
      title: 'SGK İşveren',
      dataIndex: 'sgk_isveren',
      key: 'sgk_isveren',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Toplam Maliyet',
      dataIndex: 't_isveren_maliyet',
      key: 't_isveren_maliyet',
      width: 140,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2, style: 'currency', currency: 'TRY' })
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card 
        title="Luca Bordro Yönetimi"
        extra={
          <Space>
            <Select
              style={{ width: 150 }}
              placeholder="Dönem seçin"
              value={selectedDonem}
              onChange={setSelectedDonem}
              options={donemler.map(d => ({ label: d, value: d }))}
            />
            <Select
              style={{ width: 150 }}
              placeholder="Upload Dönem"
              value={uploadDonem}
              onChange={setUploadDonem}
              allowClear
              options={[
                { label: '2025-01', value: '2025-01' },
                { label: '2025-02', value: '2025-02' },
                { label: '2025-03', value: '2025-03' },
                { label: '2025-04', value: '2025-04' },
                { label: '2025-05', value: '2025-05' },
                { label: '2025-06', value: '2025-06' },
                { label: '2025-07', value: '2025-07' },
                { label: '2025-08', value: '2025-08' },
                { label: '2025-09', value: '2025-09' },
                { label: '2025-10', value: '2025-10' },
                { label: '2025-11', value: '2025-11' },
                { label: '2025-12', value: '2025-12' },
              ]}
            />
            <Upload
              beforeUpload={handleUpload}
              showUploadList={false}
              accept=".xlsx,.xls"
            >
              <Button icon={<UploadOutlined />} loading={uploading}>
                Excel Yükle
              </Button>
            </Upload>
            <Button icon={<ReloadOutlined />} onClick={loadBordro} loading={loading}>
              Yenile
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={bordroList}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            total,
            current: currentPage,
            pageSize,
            showSizeChanger: false,
            showTotal: (total) => `Toplam ${total} kayıt`,
            onChange: (page) => loadBordro(page),
          }}
          scroll={{ x: 1200 }}
          size="small"
        />
      </Card>
    </div>
  );
}
