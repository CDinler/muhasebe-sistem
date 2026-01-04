import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Space, message, Select, DatePicker, Statistic, Row, Col, Tag } from 'antd';
import { CalculatorOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface PayrollRecord {
  id: number;
  adi_soyadi: string;
  tckn: string;
  santiye_adi: string;
  ucret_nevi: string;
  kanun_tipi: string;
  maas1_net_odenen: number;
  maas1_ssk_isci: number;
  maas1_gelir_vergisi: number;
  maas2_toplam: number;
  elden_ucret_yuvarlanmis: number;
  yevmiye_tipi: 'A' | 'B' | 'C' | null;
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
      const response = await axios.get<PayrollListResponse>(`${API_URL}/bordro/list`, {
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
        typeA: acc.typeA + (item.yevmiye_tipi === 'A' ? 1 : 0),
        typeB: acc.typeB + (item.yevmiye_tipi === 'B' ? 1 : 0),
        typeC: acc.typeC + (item.yevmiye_tipi === 'C' ? 1 : 0),
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
    const donem = selectedDate.format('YYYY-MM');
    
    setCalculating(true);
    try {
      const response = await axios.post(`${API_URL}/bordro/calculate`, {
        yil,
        ay,
        donem
      });
      
      message.success(`✅ ${response.data.total} kayıt hesaplandı (${response.data.calculated} yeni, ${response.data.updated} güncelleme)`);
      
      if (response.data.errors && response.data.errors.length > 0) {
        message.warning(`⚠️ ${response.data.errors.length} kayıtta hata oluştu`, 5);
      }
      
      // Listeyi yenile
      await fetchPayrollData();
      
    } catch (error: any) {
      message.error('Bordro hesaplaması başarısız: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCalculating(false);
    }
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
      dataIndex: 'santiye_adi',
      key: 'santiye_adi',
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
          'A': 'blue',
          'B': 'green',
          'C': 'orange',
        };
        return <Tag color={colors[val]}>{val}</Tag>;
      },
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
          scroll={{ x: 1200 }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default BordroCalculationPage;
