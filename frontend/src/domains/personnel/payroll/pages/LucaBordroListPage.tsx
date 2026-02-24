import { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, message, Select, Space, Statistic, Row, Col } from 'antd';
import { ReloadOutlined, TeamOutlined, DollarOutlined } from '@ant-design/icons';
import apiClient from '@/services/api';

const API_URL = '/personnel';

interface LucaBordro {
  id: number;
  yil: number;
  ay: number;
  donem: string;
  sira_no: number | null;
  adi_soyadi: string | null;
  tckn: string | null;
  ssk_sicil_no: string | null;
  giris_t: string | null;
  cikis_t: string | null;
  t_gun: number | null;
  nor_kazanc: number | null;
  dig_kazanc: number | null;
  top_kazanc: number | null;
  ssk_m: number | null;
  g_v_m: number | null;
  ssk_isci: number | null;
  iss_p_isci: number | null;
  gel_ver: number | null;
  damga_v: number | null;
  ozel_kesinti: number | null;
  oto_kat_bes: number | null;
  icra: number | null;
  avans: number | null;
  n_odenen: number | null;
  isveren_maliyeti: number | null;
  ssk_isveren: number | null;
  iss_p_isveren: number | null;
  kanun: string | null;
  ssk_tesviki: number | null;
  upload_date: string;
  file_name: string | null;
  is_processed: number;
  contract_id: number | null;
  created_at: string;
  updated_at: string;
}

export default function LucaBordroListPage() {
  const [bordroList, setBordroList] = useState<LucaBordro[]>([]);
  const [donemler, setDonemler] = useState<string[]>([]);
  const [selectedDonem, setSelectedDonem] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(100);
  const [summary, setSummary] = useState({
    personel_sayisi: 0,
    toplam_net_odenen: 0,
    toplam_oto_kat_bes: 0,
    toplam_icra: 0,
    toplam_isveren_maliyeti: 0,
  });

  const loadDonemler = useCallback(async () => {
    try {
      const res = await apiClient.get(`${API_URL}/luca-bordro/donemler`);
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
      const res = await apiClient.get(`${API_URL}/luca-bordro/list`, {
        params: { donem: selectedDonem, page, page_size: pageSize }
      });
      setBordroList(res.data.items || res.data.bordro_list || []);
      setTotal(res.data.total || 0);
      setCurrentPage(page);
      setSummary(res.data.summary || {
        personel_sayisi: 0,
        toplam_net_odenen: 0,
        toplam_oto_kat_bes: 0,
        toplam_icra: 0,
        toplam_isveren_maliyeti: 0,
      });
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

  const columns = [
    {
      title: 'Sıra',
      dataIndex: 'sira_no',
      key: 'sira_no',
      width: 60,
      fixed: 'left' as const
    },
    {
      title: 'Ad Soyad',
      dataIndex: 'adi_soyadi',
      key: 'adi_soyadi',
      width: 200,
      fixed: 'left' as const
    },
    {
      title: 'TCKN',
      dataIndex: 'tckn',
      key: 'tckn',
      width: 120
    },
    {
      title: 'SSK Sicil',
      dataIndex: 'ssk_sicil_no',
      key: 'ssk_sicil_no',
      width: 120
    },
    {
      title: 'Dönem',
      dataIndex: 'donem',
      key: 'donem',
      width: 100
    },
    {
      title: 'Giriş T.',
      dataIndex: 'giris_t',
      key: 'giris_t',
      width: 110,
      render: (val: string) => val ? new Date(val).toLocaleDateString('tr-TR') : '-'
    },
    {
      title: 'Çıkış T.',
      dataIndex: 'cikis_t',
      key: 'cikis_t',
      width: 110,
      render: (val: string) => val ? new Date(val).toLocaleDateString('tr-TR') : '-'
    },
    {
      title: 'Gün',
      dataIndex: 't_gun',
      key: 't_gun',
      width: 60,
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
      title: 'Toplam Kazanç',
      dataIndex: 'top_kazanc',
      key: 'top_kazanc',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'SSK Matrah',
      dataIndex: 'ssk_m',
      key: 'ssk_m',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'GV Matrah',
      dataIndex: 'g_v_m',
      key: 'g_v_m',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'SSK İşçi',
      dataIndex: 'ssk_isci',
      key: 'ssk_isci',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'İşsizlik İşçi',
      dataIndex: 'iss_p_isci',
      key: 'iss_p_isci',
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
      title: 'Özel Kesinti',
      dataIndex: 'ozel_kesinti',
      key: 'ozel_kesinti',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'Net Ödenen',
      dataIndex: 'n_odenen',
      key: 'n_odenen',
      width: 130,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2, style: 'currency', currency: 'TRY' })
    },
    {
      title: 'SSK İşveren',
      dataIndex: 'ssk_isveren',
      key: 'ssk_isveren',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'İşsizlik İşveren',
      dataIndex: 'iss_p_isveren',
      key: 'iss_p_isveren',
      width: 120,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    },
    {
      title: 'İşveren Maliyeti',
      dataIndex: 'isveren_maliyeti',
      key: 'isveren_maliyeti',
      width: 140,
      align: 'right' as const,
      render: (val: number) => val?.toLocaleString('tr-TR', { minimumFractionDigits: 2, style: 'currency', currency: 'TRY' })
    },
    {
      title: 'Kanun',
      dataIndex: 'kanun',
      key: 'kanun',
      width: 80
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* İstatistikler */}
        {selectedDonem && (
          <Card>
            <Row gutter={16}>
              <Col span={4}>
                <Statistic 
                  title="Personel Sayısı" 
                  value={summary.personel_sayisi}
                  prefix={<TeamOutlined />}
                />
              </Col>
              <Col span={5}>
                <Statistic 
                  title="Toplam Net Ödenen" 
                  value={summary.toplam_net_odenen}
                  precision={2}
                  prefix={<DollarOutlined />}
                  suffix="₺"
                />
              </Col>
              <Col span={5}>
                <Statistic 
                  title="Toplam İşveren Maliyeti" 
                  value={summary.toplam_isveren_maliyeti}
                  precision={2}
                  prefix={<DollarOutlined />}
                  suffix="₺"
                />
              </Col>
              <Col span={5}>
                <Statistic 
                  title="Toplam Oto.Kat.Bes." 
                  value={summary.toplam_oto_kat_bes}
                  precision={2}
                  suffix="₺"
                />
              </Col>
              <Col span={5}>
                <Statistic 
                  title="Toplam İcra" 
                  value={summary.toplam_icra}
                  precision={2}
                  suffix="₺"
                />
              </Col>
            </Row>
          </Card>
        )}

        {/* Ana Tablo */}
        <Card 
          title={`Luca Bordro Listesi ${selectedDonem ? `- ${selectedDonem}` : ''}`}
          extra={
            <Space>
              <Select
                style={{ width: 150 }}
                placeholder="Dönem seçin"
                value={selectedDonem}
                onChange={setSelectedDonem}
                options={donemler.map(d => ({ label: d, value: d }))}
              />
              <Button icon={<ReloadOutlined />} onClick={() => loadBordro()} loading={loading}>
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
            scroll={{ x: 2400 }}
            size="small"
          />
        </Card>
      </Space>
    </div>
  );
}
