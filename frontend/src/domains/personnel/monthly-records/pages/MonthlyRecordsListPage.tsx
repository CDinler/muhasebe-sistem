import React, { useState, useEffect } from 'react';
import { Table, Card, Select, Space, Button, message, Popconfirm, Tag } from 'antd';
import { DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import apiClient from '@/services/api';

interface MonthlyRecord {
  id: number;
  donem: string;
  personnel_id: number;
  adi: string;
  soyadi: string;
  tc_kimlik_no: string;
  ssk_no: string | null;
  unvan: string | null;
  bolum: string | null;
  ise_giris_tarihi: string | null;
  isten_cikis_tarihi: string | null;
  ucret: number | null;
  net_brut: string | null;
  created_at: string;
}

const MonthlyRecordsListPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<MonthlyRecord[]>([]);
  const [periods, setPeriods] = useState<string[]>([]);
  const [selectedDonem, setSelectedDonem] = useState<string>('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
    total: 0,
  });

  useEffect(() => {
    loadPeriods();
  }, []);

  useEffect(() => {
    if (selectedDonem) {
      loadRecords();
    }
  }, [selectedDonem, pagination.current, pagination.pageSize]);

  const loadPeriods = async () => {
    try {
      const response = await apiClient.get('/personnel/monthly-records/periods');
      setPeriods(response.data.periods || []);
      if (response.data.periods && response.data.periods.length > 0) {
        setSelectedDonem(response.data.periods[0]);
      }
    } catch (error) {
      console.error('Dönemler yüklenemedi:', error);
      message.error('Dönemler yüklenemedi');
    }
  };

  const loadRecords = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/personnel/monthly-records/', {
        params: {
          donem: selectedDonem,
          page: pagination.current,
          page_size: pagination.pageSize,
        },
      });

      setData(response.data.items || []);
      setPagination({
        ...pagination,
        total: response.data.total || 0,
      });
    } catch (error) {
      console.error('Kayıtlar yüklenemedi:', error);
      message.error('Kayıtlar yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await apiClient.delete(`/personnel/monthly-records/${id}`);
      message.success('Kayıt silindi');
      loadRecords();
    } catch (error: any) {
      console.error('Silme hatası:', error);
      message.error(error.response?.data?.detail || 'Silme sırasında hata oluştu');
    }
  };

  const columns: ColumnsType<MonthlyRecord> = [
    {
      title: 'Adı',
      dataIndex: 'adi',
      key: 'adi',
      width: 120,
      fixed: 'left',
    },
    {
      title: 'Soyadı',
      dataIndex: 'soyadi',
      key: 'soyadi',
      width: 120,
      fixed: 'left',
    },
    {
      title: 'TC Kimlik No',
      dataIndex: 'tc_kimlik_no',
      key: 'tc_kimlik_no',
      width: 120,
    },
    {
      title: 'SSK No',
      dataIndex: 'ssk_no',
      key: 'ssk_no',
      width: 120,
    },
    {
      title: 'Ünvan',
      dataIndex: 'unvan',
      key: 'unvan',
      width: 150,
    },
    {
      title: 'Bölüm',
      dataIndex: 'bolum',
      key: 'bolum',
      width: 150,
    },
    {
      title: 'Giriş Tarihi',
      dataIndex: 'ise_giris_tarihi',
      key: 'ise_giris_tarihi',
      width: 110,
      render: (date: string | null) => date ? new Date(date).toLocaleDateString('tr-TR') : '-',
    },
    {
      title: 'Çıkış Tarihi',
      dataIndex: 'isten_cikis_tarihi',
      key: 'isten_cikis_tarihi',
      width: 110,
      render: (date: string | null) => date ? new Date(date).toLocaleDateString('tr-TR') : '-',
    },
    {
      title: 'Ücret',
      dataIndex: 'ucret',
      key: 'ucret',
      width: 120,
      align: 'right',
      render: (value: number | null) => value ? value.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '-',
    },
    {
      title: 'Net/Brüt',
      dataIndex: 'net_brut',
      key: 'net_brut',
      width: 80,
      align: 'center',
      render: (value: string | null) => value ? (
        <Tag color={value === 'Net' ? 'green' : 'blue'}>{value}</Tag>
      ) : '-',
    },
    {
      title: 'İşlem',
      key: 'action',
      width: 80,
      align: 'center',
      fixed: 'right',
      render: (_: any, record: MonthlyRecord) => (
        <Popconfirm
          title="Silmek istediğinize emin misiniz?"
          onConfirm={() => handleDelete(record.id)}
          okText="Evet"
          cancelText="Hayır"
        >
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card 
        title="Aylık Personel Sicil Listesi" 
        bordered={false}
        extra={
          <Space>
            <Select
              style={{ width: 200 }}
              placeholder="Dönem seçiniz"
              value={selectedDonem}
              onChange={setSelectedDonem}
              options={periods.map(d => ({
                value: d,
                label: d,
              }))}
            />
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadRecords}
              loading={loading}
            >
              Yenile
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} kayıt`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize: pageSize || 50 });
            },
          }}
          scroll={{ x: 1400 }}
        />
      </Card>
    </div>
  );
};

export default MonthlyRecordsListPage;
