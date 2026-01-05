import { useState, useEffect } from 'react';
import { Card, Table, InputNumber, Button, message, Tabs, Spin } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';

// 🆕 V2 Domain imports
import { useConfigs, useUpdateConfig, useTaxBrackets } from '@/domains/settings/config/hooks/useConfig';
import type { SystemConfig, TaxBracket } from '@/domains/settings/config/types/config.types';

export default function SystemConfigPage() {
  // 🆕 V2 React Query hooks
  const { data: configs = {}, isLoading: configLoading, refetch: refetchConfigs } = useConfigs();
  const { data: taxBracketsData = [], isLoading: taxLoading, refetch: refetchTax } = useTaxBrackets();
  const updateConfigMutation = useUpdateConfig();

  const [localConfigs, setLocalConfigs] = useState<Record<string, SystemConfig[]>>({});
  const [taxBrackets, setTaxBrackets] = useState<Record<string, TaxBracket[]>>({});
  const [saving, setSaving] = useState(false);

  const loading = configLoading || taxLoading;

  // Sync React Query data to local state for editing
  useEffect(() => {
    if (configs) {
      setLocalConfigs(configs);
    }
  }, [configs]);

  useEffect(() => {
    if (taxBracketsData) {
      // Group by year
      const grouped = taxBracketsData.reduce((acc: Record<string, TaxBracket[]>, bracket) => {
        const year = bracket.year.toString();
        if (!acc[year]) acc[year] = [];
        acc[year].push(bracket);
        return acc;
      }, {});
      setTaxBrackets(grouped);
    }
  }, [taxBracketsData]);

  const handleConfigChange = (key: string, value: number) => {
    setLocalConfigs(prev => {
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
    updateConfigMutation.mutate({ key, data: { config_value: value } }, {
      onSuccess: () => {
        refetchConfigs();
        setSaving(false);
      },
      onError: () => {
        setSaving(false);
      }
    });
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
          <Button icon={<ReloadOutlined />} onClick={() => { refetchConfigs(); refetchTax(); }} loading={loading}>
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
                    dataSource={localConfigs.SSK_ORANLAR || []}
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
                    dataSource={localConfigs.GENEL || []}
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
