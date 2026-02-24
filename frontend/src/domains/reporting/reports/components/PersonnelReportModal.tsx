import React, { useState, useEffect } from 'react';
import { Modal, Table, Spin, Alert, DatePicker, Button, Space, Statistic, Row, Col, Card } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { apiClient } from '@/shared/api/client';

const { RangePicker } = DatePicker;

interface PersonnelReportModalProps {
  visible: boolean;
  personnel: any | null;
  selectedPeriod?: string;
  onClose: () => void;
}

interface MuavinItem {
  transaction_date: string;
  transaction_number: string;
  description: string;
  debit: number;
  credit: number;
  balance: number;
}

interface MuavinReport {
  account_code: string;
  account_name: string;
  start_date: string;
  end_date: string;
  opening_balance: number;
  total_debit: number;
  total_credit: number;
  closing_balance: number;
  items: MuavinItem[];
}

export const PersonnelReportModal: React.FC<PersonnelReportModalProps> = ({
  visible,
  personnel,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportData, setReportData] = useState<MuavinReport | null>(null);
  const [accountCode, setAccountCode] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().startOf('year'),
    dayjs().endOf('year')
  ]);

  useEffect(() => {
    if (visible && personnel) {
      fetchAccountCode();
    }
  }, [visible, personnel]);

  const fetchAccountCode = async () => {
    if (!personnel?.id) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Get personnel details to find account_id
      const response = await apiClient.get(`/api/v2/personnel/${personnel.id}`);
      const personnelData = response.data;
      
      if (!personnelData.accounts_id) {
        setError('Bu personelin hesap kodu tanımlı değil. Lütfen önce hesap ataması yapın.');
        setLoading(false);
        return;
      }
      
      // Get account details
      const accountResponse = await apiClient.get(`/api/v2/accounts/${personnelData.accounts_id}`);
      const account = accountResponse.data;
      
      setAccountCode(account.code);
      // Auto-fetch report
      fetchReport(account.code, dateRange[0], dateRange[1]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Hesap kodu alınamadı');
      setLoading(false);
    }
  };

  const fetchReport = async (code: string, startDate: Dayjs, endDate: Dayjs) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get('/api/v2/reporting/reports/muavin', {
        params: {
          account_code: code,
          start_date: startDate.format('YYYY-MM-DD'),
          end_date: endDate.format('YYYY-MM-DD'),
        },
      });
      
      setReportData(response.data);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Rapor alınamadı');
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (accountCode) {
      fetchReport(accountCode, dateRange[0], dateRange[1]);
    }
  };

  const handleDateChange = (dates: any) => {
    if (dates && dates.length === 2) {
      setDateRange([dates[0], dates[1]]);
    }
  };

  const columns = [
    {
      title: 'Tarih',
      dataIndex: 'transaction_date',
      key: 'date',
      width: 120,
      render: (text: string) => dayjs(text).format('DD.MM.YYYY'),
    },
    {
      title: 'Fiş No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 120,
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      width: 150,
      align: 'right' as const,
      render: (value: number) => value > 0 ? value.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '-',
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      width: 150,
      align: 'right' as const,
      render: (value: number) => value > 0 ? value.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '-',
    },
    {
      title: 'Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      width: 150,
      align: 'right' as const,
      render: (value: number) => (
        <span style={{ color: value < 0 ? '#cf1322' : '#52c41a', fontWeight: 'bold' }}>
          {value.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  if (!personnel) return null;

  return (
    <Modal
      title={`Personel Hesap Ekstresi - ${personnel.ad || ''} ${personnel.soyad || ''}`}
      open={visible}
      onCancel={onClose}
      width={1200}
      footer={null}
      destroyOnClose
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Card size="small">
          <Row gutter={16}>
            <Col span={8}>
              <p style={{ margin: 0 }}><strong>TC Kimlik:</strong> {personnel.tc_kimlik_no}</p>
              <p style={{ margin: 0 }}><strong>Ad Soyad:</strong> {personnel.ad} {personnel.soyad}</p>
            </Col>
            <Col span={8}>
              <p style={{ margin: 0 }}><strong>Hesap Kodu:</strong> {accountCode || 'Yükleniyor...'}</p>
              {reportData && (
                <p style={{ margin: 0 }}><strong>Hesap Adı:</strong> {reportData.account_name}</p>
              )}
            </Col>
            <Col span={8}>
              <Space>
                <RangePicker
                  value={dateRange}
                  onChange={handleDateChange}
                  format="DD.MM.YYYY"
                />
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  disabled={!accountCode || loading}
                >
                  Yenile
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {error && (
          <Alert
            message="Hata"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
          />
        )}

        {loading && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" tip="Rapor yükleniyor..." />
          </div>
        )}

        {!loading && reportData && (
          <>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="Açılış Bakiyesi"
                  value={reportData.opening_balance}
                  precision={2}
                  valueStyle={{ color: reportData.opening_balance < 0 ? '#cf1322' : '#52c41a' }}
                  suffix="₺"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Toplam Borç"
                  value={reportData.total_debit}
                  precision={2}
                  valueStyle={{ color: '#1890ff' }}
                  suffix="₺"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Toplam Alacak"
                  value={reportData.total_credit}
                  precision={2}
                  valueStyle={{ color: '#fa8c16' }}
                  suffix="₺"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Kapanış Bakiyesi"
                  value={reportData.closing_balance}
                  precision={2}
                  valueStyle={{ color: reportData.closing_balance < 0 ? '#cf1322' : '#52c41a', fontWeight: 'bold' }}
                  suffix="₺"
                />
              </Col>
            </Row>

            <Table
              columns={columns}
              dataSource={reportData.items}
              rowKey={(record, index) => `${record.transaction_number}-${index}`}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `Toplam ${total} işlem`,
              }}
              size="small"
              scroll={{ x: 900 }}
              summary={() => (
                <Table.Summary fixed>
                  <Table.Summary.Row style={{ background: '#fafafa', fontWeight: 'bold' }}>
                    <Table.Summary.Cell index={0} colSpan={3} align="right">
                      TOPLAM
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={3} align="right">
                      {reportData.total_debit.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={4} align="right">
                      {reportData.total_credit.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={5} align="right">
                      <span style={{ color: reportData.closing_balance < 0 ? '#cf1322' : '#52c41a' }}>
                        {reportData.closing_balance.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                      </span>
                    </Table.Summary.Cell>
                  </Table.Summary.Row>
                </Table.Summary>
              )}
            />
          </>
        )}
      </Space>
    </Modal>
  );
};
