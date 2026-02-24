import React, { useState, useEffect } from 'react';
import { Table, Card, Row, Col, Statistic, DatePicker, Button, Space, message, Progress, AutoComplete } from 'antd';
import { SearchOutlined, FileTextOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import api from '@/services/api';
import { accountService, Account } from '@/services/muhasebe.service';

const { RangePicker } = DatePicker;

interface MuavinItem {
  transaction_id: number;
  transaction_number: string;
  transaction_date: string;
  description: string | null;
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
  items: MuavinItem[];
  closing_balance: number;
  total_debit: number;
  total_credit: number;
}

const MuavinPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<MuavinReport | null>(null);
  const [accountCode, setAccountCode] = useState('');
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountOptions, setAccountOptions] = useState<{ value: string; label: string }[]>([]);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(1, 'year'),
    dayjs(),
  ]);

  useEffect(() => {
    const loadAccounts = async () => {
      try {
        const response = await accountService.getAll({ limit: 10000 });
        const accountsData = Array.isArray(response.data) ? response.data : response.data.items || [];
        setAccounts(accountsData);
      } catch (error) {
        console.error('Hesaplar yüklenemedi:', error);
      }
    };
    loadAccounts();
  }, []);

  const handleAccountSearch = (searchText: string) => {
    if (!searchText || searchText.length < 1) {
      setAccountOptions([]);
      return;
    }

    if (!Array.isArray(accounts)) {
      console.error('Accounts is not an array:', accounts);
      setAccountOptions([]);
      return;
    }

    const filtered = accounts
      .filter(acc => 
        acc.code.toLowerCase().includes(searchText.toLowerCase()) ||
        acc.name.toLowerCase().includes(searchText.toLowerCase())
      )
      .slice(0, 20)
      .map(acc => ({
        value: acc.code,
        label: `${acc.code} - ${acc.name}`
      }));
    
    setAccountOptions(filtered);
  };

  const handleSearch = async () => {
    if (!accountCode.trim()) {
      message.warning('Lütfen hesap kodu girin');
      return;
    }

    setLoading(true);
    try {
      const response = await api.get<MuavinReport>('/reporting/reports/muavin', {
        params: {
          account_code: accountCode.trim(),
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      });

      setReportData(response.data);
      
      if (response.data.items.length === 0) {
        message.info('Seçilen dönemde hareket bulunmamaktadır');
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Rapor yüklenirken hata oluştu');
      setReportData(null);
    } finally {
      setLoading(false);
    }
  };

  const columns: ColumnsType<MuavinItem> = [
    {
      title: 'Tarih',
      dataIndex: 'transaction_date',
      key: 'transaction_date',
      width: 110,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Fiş No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 130,
      render: (text: string, record: MuavinItem) => (
        <a 
          onClick={() => navigate(`/transactions/${record.transaction_id}`)}
          style={{ color: '#1890ff', cursor: 'pointer' }}
        >
          {text}
        </a>
      ),
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
      align: 'right',
      width: 150,
      render: (val: number) =>
        val > 0 ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      align: 'right',
      width: 150,
      render: (val: number) =>
        val > 0 ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
    },
    {
      title: 'Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      align: 'right',
      width: 150,
      fixed: 'right',
      render: (val: number) => (
        <span
          style={{
            color: val > 0 ? '#cf1322' : val < 0 ? '#3f8600' : '#666',
            fontWeight: 'bold',
          }}
        >
          {val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      title: 'B/A',
      key: 'ba',
      width: 60,
      align: 'center',
      fixed: 'right',
      render: (_: any, record: MuavinItem) => {
        if (record.balance === 0) return '';
        return record.balance > 0 ? 'B' : 'A';
      },
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1>
          <FileTextOutlined /> Muavin Defteri
        </h1>
        <p style={{ color: '#666' }}>
          Belirli bir hesap kodunun dönem içindeki tüm hareketlerini görüntüleyin
        </p>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Space size="large" style={{ width: '100%' }} wrap>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>Hesap Kodu</div>
            <AutoComplete
              placeholder="100, 120.00001, 320.00001 veya hesap adı"
              value={accountCode}
              onChange={setAccountCode}
              onSearch={handleAccountSearch}
              options={accountOptions}
              style={{ width: 350 }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') handleSearch();
              }}
              filterOption={false}
            />
          </div>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>Tarih Aralığı</div>
            <RangePicker
              value={dateRange}
              onChange={(dates) => dates && setDateRange(dates as [Dayjs, Dayjs])}
              format="DD.MM.YYYY"
            />
          </div>
          <div style={{ paddingTop: 28 }}>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
            >
              Raporu Getir
            </Button>
          </div>
        </Space>
      </Card>

      {loading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Progress type="circle" percent={50} status="active" />
            <p style={{ marginTop: 16 }}>Rapor yükleniyor...</p>
          </div>
        </Card>
      ) : reportData ? (
        <>
          {/* Başlık */}
          <Card style={{ marginBottom: 16 }}>
            <div style={{ borderBottom: '2px solid #d9d9d9', paddingBottom: 16, marginBottom: 16 }}>
              <Row justify="space-between" align="top">
                <Col>
                  <h2 style={{ margin: 0, fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>
                    Muavin Defteri
                  </h2>
                  <div style={{ marginTop: 8 }}>
                    <div>
                      <strong>Hesap Kodu:</strong> {reportData.account_code}
                    </div>
                    <div>
                      <strong>Hesap Adı:</strong> {reportData.account_name}
                    </div>
                  </div>
                </Col>
                <Col style={{ textAlign: 'right' }}>
                  <div>
                    <strong>Dönem:</strong>{' '}
                    {dayjs(reportData.start_date).format('DD.MM.YYYY')} -{' '}
                    {dayjs(reportData.end_date).format('DD.MM.YYYY')}
                  </div>
                  <div>
                    <strong>Rapor Tarihi:</strong> {dayjs().format('DD.MM.YYYY - HH:mm')}
                  </div>
                </Col>
              </Row>
            </div>

            {/* Özet Kartlar */}
            <Row gutter={16}>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Açılış Bakiyesi"
                    value={reportData.opening_balance}
                    precision={2}
                    suffix={
                      reportData.opening_balance > 0
                        ? 'B'
                        : reportData.opening_balance < 0
                        ? 'A'
                        : ''
                    }
                    valueStyle={{
                      color:
                        reportData.opening_balance > 0
                          ? '#cf1322'
                          : reportData.opening_balance < 0
                          ? '#3f8600'
                          : '#666',
                    }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Toplam Borç"
                    value={reportData.total_debit}
                    precision={2}
                    suffix="B"
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Toplam Alacak"
                    value={reportData.total_credit}
                    precision={2}
                    suffix="A"
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Kapanış Bakiyesi"
                    value={reportData.closing_balance}
                    precision={2}
                    suffix={
                      reportData.closing_balance > 0
                        ? 'B'
                        : reportData.closing_balance < 0
                        ? 'A'
                        : ''
                    }
                    valueStyle={{
                      color:
                        reportData.closing_balance > 0
                          ? '#cf1322'
                          : reportData.closing_balance < 0
                          ? '#3f8600'
                          : '#666',
                      fontSize: 20,
                      fontWeight: 'bold',
                    }}
                  />
                </Card>
              </Col>
            </Row>
          </Card>

          {/* Tablo */}
          <Card>
            <Table
              columns={columns}
              dataSource={reportData.items}
              rowKey={(record, index) => `${record.transaction_id}_${record.transaction_number}_${index}`}
              pagination={{
                pageSize: 50,
                showSizeChanger: true,
                showTotal: (total) => `Toplam ${total} hareket`,
              }}
              scroll={{ x: 1000 }}
              size="small"
              bordered
              summary={() => (
                <Table.Summary fixed>
                  <Table.Summary.Row style={{ backgroundColor: '#fafafa', fontWeight: 'bold' }}>
                    <Table.Summary.Cell index={0} colSpan={3} align="right">
                      Toplam
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={3} align="right">
                      {reportData.total_debit.toLocaleString('tr-TR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={4} align="right">
                      {reportData.total_credit.toLocaleString('tr-TR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </Table.Summary.Cell>
                    <Table.Summary.Cell
                      index={5}
                      align="right"
                      style={{
                        color:
                          reportData.closing_balance > 0
                            ? '#cf1322'
                            : reportData.closing_balance < 0
                            ? '#3f8600'
                            : '#666',
                      }}
                    >
                      {reportData.closing_balance.toLocaleString('tr-TR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={6} align="center">
                      {reportData.closing_balance > 0
                        ? 'B'
                        : reportData.closing_balance < 0
                        ? 'A'
                        : ''}
                    </Table.Summary.Cell>
                  </Table.Summary.Row>
                </Table.Summary>
              )}
            />
          </Card>
        </>
      ) : (
        <Card>
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
            <FileTextOutlined style={{ fontSize: 64, marginBottom: 16 }} />
            <p>Hesap kodu girin ve raporu getir butonuna tıklayın</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default MuavinPage;
