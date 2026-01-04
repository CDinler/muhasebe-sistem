import { useState, useEffect } from 'react';
import { Card, Table, InputNumber, Button, message, Tabs, Spin } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface SystemConfig {
  config_key: string;
  config_value: string;
  config_type: string;
  category: string;
  description: string;
}

interface TaxBracket {
  id: number;
  year: number;
  min_amount: number;
  max_amount: number | null;
  tax_rate: number;
  is_active: number;
}

export default function SystemConfigPage() {
  const [configs, setConfigs] = useState<Record<string, SystemConfig[]>>({});
  const [taxBrackets, setTaxBrackets] = useState<Record<string, TaxBracket[]>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [configRes, taxRes] = await Promise.all([
        axios.get(`${API_URL}/system-config/configs`),
        axios.get(`${API_URL}/system-config/tax-brackets`)
      ]);
      setConfigs(configRes.data);
      setTaxBrackets(taxRes.data);
    } catch (error) {
      message.error('Veriler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleConfigChange = (key: string, value: number) => {
    setConfigs(prev => {
      const updated = { ...prev };
      Object.keys(updated).forEach(category => {
        updated[category] = updated[category].map(cfg =>
          cfg.config_key === key ? { ...cfg, config_value: value.toString() } : cfg
        );
      });
      return updated;
    });
  };

  const saveConfig = async (key: string, value: string) => {
    setSaving(true);
    try {
      await axios.put(`${API_URL}/system-config/configs/${key}`, { config_value: value });
      message.success('Kaydedildi');
    } catch (error) {
      message.error('Kaydetme hatası');
    } finally {
      setSaving(false);
    }
  };

  const sskColumns = [
    {
      title: 'Ayar',
      dataIndex: 'description',
      key: 'description',
      width: '40%'
    },
    {
      title: 'Değer',
      dataIndex: 'config_value',
      key: 'config_value',
      render: (val: string, record: SystemConfig) => (
        <InputNumber
          value={parseFloat(val)}
          step={0.01}
          min={0}
          max={1}
          precision={4}
          onChange={(v) => handleConfigChange(record.config_key, v || 0)}
          style={{ width: 120 }}
        />
      )
    },
    {
      title: '',
      key: 'action',
      width: 100,
      render: (_: any, record: SystemConfig) => (
        <Button
          type="primary"
          size="small"
          icon={<SaveOutlined />}
          loading={saving}
          onClick={() => saveConfig(record.config_key, record.config_value)}
        >
          Kaydet
        </Button>
      )
    }
  ];

  const taxColumns = [
    {
      title: 'Min Tutar',
      dataIndex: 'min_amount',
      key: 'min_amount',
      render: (val: number) => val.toLocaleString('tr-TR') + ' ₺'
    },
    {
      title: 'Max Tutar',
      dataIndex: 'max_amount',
      key: 'max_amount',
      render: (val: number | null) => val ? val.toLocaleString('tr-TR') + ' ₺' : '∞'
    },
    {
      title: 'Vergi Oranı',
      dataIndex: 'tax_rate',
      key: 'tax_rate',
      render: (val: number) => '%' + (val * 100)
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card 
        title="Sistem Ayarları - Bordro Oranları" 
        extra={
          <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
            Yenile
          </Button>
        }
      >
        <Spin spinning={loading}>
          <Tabs
            items={[
              {
                key: 'SSK_ORANLAR',
                label: 'SSK Oranları',
                children: (
                  <Table
                    dataSource={configs.SSK_ORANLAR || []}
                    columns={sskColumns}
                    rowKey="config_key"
                    pagination={false}
                    size="small"
                  />
                )
              },
              {
                key: 'GENEL',
                label: 'Genel Ayarlar',
                children: (
                  <Table
                    dataSource={configs.GENEL || []}
                    columns={sskColumns}
                    rowKey="config_key"
                    pagination={false}
                    size="small"
                  />
                )
              },
              {
                key: 'tax',
                label: 'Vergi Dilimleri 2025',
                children: (
                  <Table
                    dataSource={taxBrackets['2025'] || []}
                    columns={taxColumns}
                    rowKey="id"
                    pagination={false}
                    size="small"
                  />
                )
              }
            ]}
          />
        </Spin>
      </Card>
    </div>
  );
}
