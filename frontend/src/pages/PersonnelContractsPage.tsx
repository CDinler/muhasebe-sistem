import { useState } from 'react';
import { Card, Table, Button, Space, Tag, Upload, message, Modal } from 'antd';
import { ReloadOutlined, DownloadOutlined, UploadOutlined, FileExcelOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

// 🆕 V2 Domain imports
import { useContractsList } from '@/domains/personnel/contracts/hooks/useContracts';
import type { PersonnelContract } from '@/domains/personnel/contracts/types/contracts.types';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1'; // Still using V1 for upload

export default function PersonnelContractsPage() {
  // 🆕 V2 React Query hooks
  const { data: contractData, isLoading: loading, refetch } = useContractsList();
  
  const contracts = contractData?.contracts || [];
  const total = contractData?.total || 0;
  
  const [uploading, setUploading] = useState(false);
  
  const loadContracts = () => {
    refetch();
  };

  const handleDownloadTemplate = async () => {
    try {
      const url = `${API_URL}/personnel-contracts/template`;
      const link = document.createElement('a');
      link.href = url;
      link.download = `Personel_Sozlesmeler_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      message.success('Şablon indiriliyor...');
    } catch (error) {
      message.error('Şablon indirme hatası');
    }
  };

  const handleUploadExcel = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post(`${API_URL}/personnel-contracts/upload-excel`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      Modal.success({
        title: 'Sözleşmeler Yüklendi',
        content: (
          <div>
            <p>✅ {res.data.uploaded_count} yeni sözleşme</p>
            <p>🔄 {res.data.updated_count} güncelleme</p>
            {res.data.errors?.length > 0 && (
              <div style={{ marginTop: 12, color: 'red' }}>
                <strong>Hatalar ({res.data.errors.length}):</strong>
                <ul style={{ maxHeight: 200, overflow: 'auto', fontSize: 12 }}>
                  {res.data.errors.slice(0, 10).map((err: string, i: number) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ),
        onOk: loadContracts
      });
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Yükleme hatası');
    } finally {
      setUploading(false);
    }
    
    return false; // Upload component otomatik yüklemesin
  };


  const columns: ColumnsType<PersonnelContract> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      fixed: 'left'
    },
    {
      title: 'Personel ID',
      dataIndex: 'personnel_id',
      key: 'personnel_id',
      width: 100
    },
    {
      title: 'TC Kimlik No',
      dataIndex: 'tc_kimlik_no',
      key: 'tc_kimlik_no',
      width: 120
    },
    {
      title: 'Departman',
      dataIndex: 'departman',
      key: 'departman',
      width: 150,
      render: (val: string | null) => val ? <Tag color="blue">{val}</Tag> : '-'
    },
    {
      title: 'Bölüm',
      dataIndex: 'bolum',
      key: 'bolum',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Pozisyon',
      dataIndex: 'pozisyon',
      key: 'pozisyon',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Unvan',
      dataIndex: 'unvan',
      key: 'unvan',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Başlangıç',
      dataIndex: 'baslangic_tarihi',
      key: 'baslangic_tarihi',
      width: 120,
      render: (val: string | null) => val || '-'
    },
    {
      title: 'Bitiş',
      dataIndex: 'bitis_tarihi',
      key: 'bitis_tarihi',
      width: 120,
      render: (val: string | null) => val || '-'
    },
    {
      title: 'Çalışma Takvimi',
      dataIndex: 'calisma_takvimi',
      key: 'calisma_takvimi',
      width: 120,
      render: (val: string | null) => val ? <Tag color="purple">{val.toUpperCase()}</Tag> : '-'
    },
    {
      title: 'Sigorta',
      dataIndex: 'sigorta_durumu',
      key: 'sigorta_durumu',
      width: 100,
      render: (val: string | null) => {
        if (!val) return '-';
        const color = val === 'vardir' ? 'green' : val === 'yoktur' ? 'red' : 'orange';
        return <Tag color={color}>{val}</Tag>;
      }
    },
    {
      title: 'Maaş Hesabı',
      dataIndex: 'maas_hesabi',
      key: 'maas_hesabi',
      width: 120,
      render: (val: string | null) => val ? <Tag>{val.toUpperCase()}</Tag> : '-'
    },
    {
      title: 'Taşeron',
      dataIndex: 'taseron',
      key: 'taseron',
      width: 80,
      render: (val: boolean | null) => val ? <Tag color="orange">Evet</Tag> : <Tag>Hayır</Tag>
    },
    {
      title: 'Durum',
      dataIndex: 'aktif',
      key: 'aktif',
      width: 80,
      render: (val: boolean) => (
        <Tag color={val ? 'green' : 'red'}>
          {val ? 'Aktif' : 'Pasif'}
        </Tag>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card 
        title={
          <Space>
            <FileExcelOutlined style={{ fontSize: 24, color: '#52c41a' }} />
            <span>Personel Sözleşmeleri</span>
          </Space>
        }
        extra={
          <Space>
            <Button 
              icon={<DownloadOutlined />} 
              onClick={handleDownloadTemplate}
              type="primary"
            >
              Şablon İndir
            </Button>
            <Upload
              beforeUpload={handleUploadExcel}
              maxCount={1}
              accept=".xlsx,.xls"
              showUploadList={false}
            >
              <Button 
                icon={<UploadOutlined />}
                loading={uploading}
                style={{ background: '#52c41a', borderColor: '#52c41a', color: 'white' }}
              >
                Excel Yükle
              </Button>
            </Upload>
            <Button icon={<ReloadOutlined />} onClick={loadContracts} loading={loading}>
              Yenile
            </Button>
          </Space>
        }
      >
        <div style={{ marginBottom: 16, padding: 12, background: '#e6f7ff', borderRadius: 4 }}>
          <strong>ℹ️ Kullanım:</strong>
          <ol style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
            <li>"Şablon İndir" ile mevcut personel + sözleşmeleri indirin</li>
            <li>Excel'de sözleşmeleri düzenleyin (Maaş1 BOŞ BIRAKILABİLİR - Luca'dan hesaplanacak)</li>
            <li>"Excel Yükle" ile toplu yükleme yapın</li>
          </ol>
        </div>
        
        <Table
          dataSource={contracts}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            total: total,
            pageSize: 100,
            showSizeChanger: false,
            showTotal: (total) => `Toplam ${total} sözleşme`
          }}
          scroll={{ x: 1400 }}
          size="small"
        />
      </Card>
    </div>
  );
}
