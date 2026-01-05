import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Table, Row, Col, Statistic, Tabs, DatePicker, message } from 'antd';
import { FileTextOutlined, BarChartOutlined, TeamOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';

// 🆕 V2 Domain imports
import { useMizanReport, useIncomeStatement, useDebtorCreditorReport, useCariReport } from '@/domains/reporting/reports/hooks/useReports';
import type { MizanItem, MizanReport, IncomeStatementItem, IncomeStatement, DebtorCreditorItem, DebtorCreditorReport, CariReportItem, CariReport } from '@/domains/reporting/reports/types/reports.types';
import { useCostCenters } from '@/domains/partners/cost_centers/hooks/useCostCenters';

const { RangePicker } = DatePicker;

const ReportsPage: React.FC = () => {
  // State
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().startOf('month'),
    dayjs().endOf('month'),
  ]);
  const [mizanData, setMizanData] = useState<MizanReport | null>(null);
  const [incomeData, setIncomeData] = useState<IncomeStatement | null>(null);
  const [debtorCreditorData, setDebtorCreditorData] = useState<DebtorCreditorReport | null>(null);
  const [cariData, setCariData] = useState<CariReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [selectedCostCenter, setSelectedCostCenter] = useState<number | null>(null);

  // Load cost centers
  useEffect(() => {
    costCenterService.getAll({ is_active: true }).then(res => setCostCenters(res.data));
  }, []);

  // Fetch Functions
  const fetchMizan = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/mizan', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      });
      setMizanData(response.data);
      message.success('Mizan raporu yüklendi');
    } catch (error) {
      message.error('Mizan raporu yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const fetchIncomeStatement = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/income-statement', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      });
      setIncomeData(response.data);
      message.success('Gelir-Gider raporu yüklendi');
    } catch (error) {
      message.error('Gelir-Gider raporu yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const fetchDebtorCreditor = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/debtor-creditor', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      });
      setDebtorCreditorData(response.data);
      message.success('Borç-Alacak raporu yüklendi');
    } catch (error) {
      message.error('Borç-Alacak raporu yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const fetchCariReport = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/cari', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      });
      setCariData(response.data);
      message.success('Cari raporu yüklendi');
    } catch (error) {
      message.error('Cari raporu yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const downloadPersonnelAccountsExcel = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/personnel-accounts/excel', {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'personel_hesaplari_335.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('335 Personel Hesapları Excel dosyası indirildi');
    } catch (error: any) {
      console.error('Excel download error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Bilinmeyen hata';
      message.error(`Excel indirme hatası: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  // Column Definitions
  const mizanColumns: ColumnsType<MizanItem> = [
    {
      title: 'Hesap Kodu',
      dataIndex: 'account_code',
      key: 'account_code',
      width: 120,
      fixed: 'left',
    },
    {
      title: 'Hesap Adı',
      dataIndex: 'account_name',
      key: 'account_name',
      width: 250,
      fixed: 'left',
    },
    {
      title: 'Açılış Borç',
      dataIndex: 'opening_debit',
      key: 'opening_debit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Açılış Alacak',
      dataIndex: 'opening_credit',
      key: 'opening_credit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Dönem Borç',
      dataIndex: 'period_debit',
      key: 'period_debit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Dönem Alacak',
      dataIndex: 'period_credit',
      key: 'period_credit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Kapanış Borç',
      dataIndex: 'closing_debit',
      key: 'closing_debit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Kapanış Alacak',
      dataIndex: 'closing_credit',
      key: 'closing_credit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
  ];

  const incomeColumns: ColumnsType<IncomeStatementItem> = [
    {
      title: 'Hesap Kodu',
      dataIndex: 'account_code',
      key: 'account_code',
      width: 120,
    },
    {
      title: 'Hesap Adı',
      dataIndex: 'account_name',
      key: 'account_name',
    },
    {
      title: 'Tutar',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
  ];

  const debtorCreditorColumns: ColumnsType<DebtorCreditorItem> = [
    {
      title: 'Cari Adı',
      dataIndex: 'contact_name',
      key: 'contact_name',
    },
    {
      title: 'Vergi No',
      dataIndex: 'tax_number',
      key: 'tax_number',
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      align: 'right',
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      align: 'right',
      render: (val: number) => (
        <span style={{ color: val > 0 ? 'red' : 'green' }}>
          {val.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  const cariReportColumns: ColumnsType<CariReportItem> = [
    {
      title: 'Hesap',
      dataIndex: 'account_code',
      key: 'account_code',
      width: 100,
      render: (code: string) => (
        <span style={{ color: code.startsWith('120') ? '#1890ff' : '#52c41a' }}>
          {code}
        </span>
      ),
    },
    {
      title: 'Cari Kodu',
      dataIndex: 'contact_code',
      key: 'contact_code',
      width: 100,
    },
    {
      title: 'Cari Adı',
      dataIndex: 'contact_name',
      key: 'contact_name',
      width: 250,
    },
    {
      title: 'VKN',
      dataIndex: 'tax_number',
      key: 'tax_number',
      width: 120,
    },
    {
      title: 'Açılış Borç',
      dataIndex: 'opening_debit',
      key: 'opening_debit',
      align: 'right',
      width: 120,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Açılış Alacak',
      dataIndex: 'opening_credit',
      key: 'opening_credit',
      align: 'right',
      width: 120,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Dönem Borç',
      dataIndex: 'period_debit',
      key: 'period_debit',
      align: 'right',
      width: 120,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Dönem Alacak',
      dataIndex: 'period_credit',
      key: 'period_credit',
      align: 'right',
      width: 120,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Kapanış Borç',
      dataIndex: 'closing_debit',
      key: 'closing_debit',
      align: 'right',
      width: 120,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Kapanış Alacak',
      dataIndex: 'closing_credit',
      key: 'closing_credit',
      align: 'right',
      width: 120,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2 }),
    },
    {
      title: 'Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      align: 'right',
      width: 120,
      fixed: 'right',
      render: (val: number) => (
        <span style={{ 
          color: val > 0 ? '#cf1322' : val < 0 ? '#3f8600' : '#666',
          fontWeight: 'bold'
        }}>
          {val.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title="Raporlar" extra={
        <Space>
          <RangePicker
            value={dateRange}
            onChange={(dates) => dates && setDateRange(dates as [Dayjs, Dayjs])}
            format="DD.MM.YYYY"
          />
        </Space>
      }>
        <Tabs
          items={[
            {
              key: '740-service-costs',
              label: (
                <span>
                  <FileTextOutlined /> 740 Hizmet/Üretim Maliyetleri
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <RangePicker
                      value={dateRange}
                      onChange={(dates) => dates && setDateRange(dates as [Dayjs, Dayjs])}
                      format="DD.MM.YYYY"
                    />
                    <select
                      style={{ minWidth: 200, marginLeft: 8, padding: '4px 11px', borderRadius: '6px', border: '1px solid #d9d9d9' }}
                      value={selectedCostCenter ?? ''}
                      onChange={e => setSelectedCostCenter(e.target.value ? Number(e.target.value) : null)}
                    >
                      <option value="">Tüm Maliyet Merkezleri</option>
                      {costCenters.map(cc => (
                        <option key={cc.id} value={cc.id}>{cc.code} - {cc.name}</option>
                      ))}
                    </select>
                    <Button
                      type="primary"
                      onClick={async () => {
                        setLoading(true);
                        try {
                          const params: any = {
                            start_date: dateRange[0].format('YYYY-MM-DD'),
                            end_date: dateRange[1].format('YYYY-MM-DD'),
                          };
                          if (selectedCostCenter) params.cost_center_id = selectedCostCenter;
                          const response = await api.get('/reports/740-service-costs/excel', {
                            params,
                            responseType: 'blob',
                          });
                          const url = window.URL.createObjectURL(new Blob([response.data]));
                          const link = document.createElement('a');
                          link.href = url;
                          link.setAttribute('download', `740_service_costs_${params.start_date}_${params.end_date}${selectedCostCenter ? '_cc' + selectedCostCenter : ''}.xlsx`);
                          document.body.appendChild(link);
                          link.click();
                          link.remove();
                          window.URL.revokeObjectURL(url);
                          message.success('740 Hizmet/Üretim Maliyetleri Excel indirildi');
                        } catch (error: any) {
                          message.error('Excel indirme hatası');
                        } finally {
                          setLoading(false);
                        }
                      }}
                      loading={loading}
                      icon={<FileTextOutlined />}
                    >
                      740 Hizmet/Üretim Maliyetleri Excel İndir
                    </Button>
                  </Space>
                  <Card>
                    <p>
                      <strong>740 Hizmet ve Üretim Maliyetleri Raporu</strong> seçilen tarih aralığı ve maliyet merkezi için Excel olarak indirilecektir.
                    </p>
                    <ul>
                      <li>Cost Center, Hesap Kodu, Hesap Adı, Toplam Gider (Borç), Toplam Gelir (Alacak)</li>
                    </ul>
                  </Card>
                </div>
              ),
            },
            {
              key: 'mizan',
              label: (
                <span>
                  <FileTextOutlined /> Mizan
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <Button type="primary" onClick={fetchMizan} loading={loading}>
                      Raporu Getir
                    </Button>
                  </Space>
                  {mizanData && (
                    <>
                      <Row gutter={16} style={{ marginBottom: 16 }}>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="Açılış Borç"
                              value={mizanData.total_opening_debit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="Açılış Alacak"
                              value={mizanData.total_opening_credit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="Kapanış Borç"
                              value={mizanData.total_closing_debit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="Kapanış Alacak"
                              value={mizanData.total_closing_credit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                      </Row>
                      <Table
                        columns={mizanColumns}
                        dataSource={mizanData.items}
                        rowKey="account_code"
                        pagination={false}
                        scroll={{ x: 1200 }}
                        size="small"
                      />
                    </>
                  )}
                </div>
              ),
            },
            {
              key: 'income',
              label: (
                <span>
                  <BarChartOutlined /> Gelir-Gider
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <Button type="primary" onClick={fetchIncomeStatement} loading={loading}>
                      Raporu Getir
                    </Button>
                  </Space>
                  {incomeData && (
                    <>
                      <Row gutter={16} style={{ marginBottom: 16 }}>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Toplam Gelir"
                              value={incomeData.total_income}
                              precision={2}
                              valueStyle={{ color: '#3f8600' }}
                            />
                          </Card>
                        </Col>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Toplam Gider"
                              value={incomeData.total_expense}
                              precision={2}
                              valueStyle={{ color: '#cf1322' }}
                            />
                          </Card>
                        </Col>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Net Kar/Zarar"
                              value={incomeData.net_profit}
                              precision={2}
                              valueStyle={{ color: incomeData.net_profit > 0 ? '#3f8600' : '#cf1322' }}
                            />
                          </Card>
                        </Col>
                      </Row>
                      <Row gutter={16}>
                        <Col span={12}>
                          <Card title="Gelirler" size="small">
                            <Table
                              columns={incomeColumns}
                              dataSource={incomeData.income_items}
                              rowKey="account_code"
                              pagination={false}
                              size="small"
                            />
                          </Card>
                        </Col>
                        <Col span={12}>
                          <Card title="Giderler" size="small">
                            <Table
                              columns={incomeColumns}
                              dataSource={incomeData.expense_items}
                              rowKey="account_code"
                              pagination={false}
                              size="small"
                            />
                          </Card>
                        </Col>
                      </Row>
                    </>
                  )}
                </div>
              ),
            },
            {
              key: 'debtor-creditor',
              label: (
                <span>
                  <TeamOutlined /> Borç-Alacak
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <Button type="primary" onClick={fetchDebtorCreditor} loading={loading}>
                      Raporu Getir
                    </Button>
                  </Space>
                  {debtorCreditorData && (
                    <>
                      <Row gutter={16} style={{ marginBottom: 16 }}>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Toplam Borçlu"
                              value={debtorCreditorData.total_debtors}
                              precision={2}
                              valueStyle={{ color: '#cf1322' }}
                            />
                          </Card>
                        </Col>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Toplam Alacaklı"
                              value={debtorCreditorData.total_creditors}
                              precision={2}
                              valueStyle={{ color: '#3f8600' }}
                            />
                          </Card>
                        </Col>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Net Bakiye"
                              value={debtorCreditorData.net_balance}
                              precision={2}
                            />
                          </Card>
                        </Col>
                      </Row>
                      <Row gutter={16}>
                        <Col span={12}>
                          <Card title="Borçlular" size="small">
                            <Table
                              columns={debtorCreditorColumns}
                              dataSource={debtorCreditorData.debtors}
                              rowKey="contact_id"
                              pagination={false}
                              size="small"
                            />
                          </Card>
                        </Col>
                        <Col span={12}>
                          <Card title="Alacaklılar" size="small">
                            <Table
                              columns={debtorCreditorColumns}
                              dataSource={debtorCreditorData.creditors}
                              rowKey="contact_id"
                              pagination={false}
                              size="small"
                            />
                          </Card>
                        </Col>
                      </Row>
                    </>
                  )}
                </div>
              ),
            },
            {
              key: 'cari',
              label: (
                <span>
                  <TeamOutlined /> Cari Raporu
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <Button type="primary" onClick={fetchCariReport} loading={loading}>
                      Raporu Getir
                    </Button>
                  </Space>
                  {cariData && (
                    <>
                      <Row gutter={16} style={{ marginBottom: 16 }}>
                        <Col span={4}>
                          <Card>
                            <Statistic
                              title="Açılış Borç"
                              value={cariData.total_opening_debit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={4}>
                          <Card>
                            <Statistic
                              title="Açılış Alacak"
                              value={cariData.total_opening_credit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={4}>
                          <Card>
                            <Statistic
                              title="Dönem Borç"
                              value={cariData.total_period_debit}
                              precision={2}
                              valueStyle={{ color: '#cf1322' }}
                            />
                          </Card>
                        </Col>
                        <Col span={4}>
                          <Card>
                            <Statistic
                              title="Dönem Alacak"
                              value={cariData.total_period_credit}
                              precision={2}
                              valueStyle={{ color: '#3f8600' }}
                            />
                          </Card>
                        </Col>
                        <Col span={4}>
                          <Card>
                            <Statistic
                              title="Kapanış Borç"
                              value={cariData.total_closing_debit}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={4}>
                          <Card>
                            <Statistic
                              title="Net Bakiye"
                              value={cariData.total_balance}
                              precision={2}
                              valueStyle={{ 
                                color: cariData.total_balance > 0 ? '#cf1322' : cariData.total_balance < 0 ? '#3f8600' : '#666'
                              }}
                            />
                          </Card>
                        </Col>
                      </Row>
                      <Table
                        columns={cariReportColumns}
                        dataSource={cariData.items}
                        rowKey={(record) => `${record.account_code}_${record.contact_id || 'null'}`}
                        pagination={{ 
                          pageSize: 50,
                          showSizeChanger: true,
                          showTotal: (total) => `Toplam ${total} cari`
                        }}
                        scroll={{ x: 1500 }}
                        size="small"
                      />
                    </>
                  )}
                </div>
              ),
            },
            {
              key: 'cost-center-monthly',
              label: (
                <span>
                  <FileTextOutlined /> Cost Center Aylık Excel
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <DatePicker
                      picker="month"
                      onChange={(date) => setDateRange([
                        date ? date.startOf('month') : dayjs().startOf('month'),
                        date ? date.endOf('month') : dayjs().endOf('month'),
                      ])}
                      value={dateRange[0]}
                      format="YYYY-MM"
                    />
                    <Button
                      type="primary"
                      onClick={async () => {
                        setLoading(true);
                        try {
                          const year = dateRange[0].year();
                          const month = dateRange[0].month() + 1;
                          const response = await api.get('/reports/cost-center-monthly/excel', {
                            params: { year, month },
                            responseType: 'blob',
                          });
                          const url = window.URL.createObjectURL(new Blob([response.data]));
                          const link = document.createElement('a');
                          link.href = url;
                          link.setAttribute('download', `cost_center_report_${year}_${month.toString().padStart(2, '0')}.xlsx`);
                          document.body.appendChild(link);
                          link.click();
                          link.remove();
                          window.URL.revokeObjectURL(url);
                          message.success('Cost Center aylık Excel indirildi');
                        } catch (error: any) {
                          message.error('Cost Center Excel indirme hatası');
                        } finally {
                          setLoading(false);
                        }
                      }}
                      loading={loading}
                      icon={<FileTextOutlined />}
                    >
                      Cost Center Aylık Excel İndir
                    </Button>
                  </Space>
                  <Card>
                    <p>
                      <strong>Cost Center Aylık Hizmet Üretim Maliyetleri Raporu</strong> seçilen yıl ve ay için Excel olarak indirilecektir.
                    </p>
                    <ul>
                      <li>Cost Center, Hesap Tipi, Toplam Gider (Borç), Toplam Gelir (Alacak)</li>
                    </ul>
                  </Card>
                </div>
              ),
            },
            {
              key: 'personnel-accounts',
              label: (
                <span>
                  <TeamOutlined /> 335 Personel Hesapları
                </span>
              ),
              children: (
                <div>
                  <Space style={{ marginBottom: 16 }}>
                    <Button 
                      type="primary" 
                      onClick={downloadPersonnelAccountsExcel} 
                      loading={loading}
                      icon={<FileTextOutlined />}
                    >
                      335 Personel Hesapları Excel İndir
                    </Button>
                  </Space>
                  <Card>
                    <p>
                      <strong>335 Personel Hesapları Raporu</strong>, tüm personellerin 335.{'{'}TCKN{'}'} formatındaki
                      hesaplarını ve bakiyelerini listeler.
                    </p>
                    <p>Excel dosyasında şu bilgiler yer alır:</p>
                    <ul>
                      <li>TC Kimlik No, Ad Soyad</li>
                      <li>Departman, Pozisyon</li>
                      <li>Hesap Kodu (335.{'{'}TCKN{'}'}), Hesap Adı</li>
                      <li>Bakiye (Borç/Alacak)</li>
                      <li>Personel Durumu (Aktif/Pasif)</li>
                      <li>Özet: Toplam bakiye, aktif/pasif personel sayısı</li>
                    </ul>
                  </Card>
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default ReportsPage;
