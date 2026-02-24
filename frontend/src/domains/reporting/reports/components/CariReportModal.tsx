import React, { useState, useEffect } from 'react';
import { Modal, Table, Card, Row, Col, Statistic, Tabs, Space, Button, Progress, DatePicker, Input, Form, Radio, message as antMessage } from 'antd';
import { FileTextOutlined, DownloadOutlined, MailOutlined, PrinterOutlined } from '@ant-design/icons';
import type { Contact } from '@/domains/partners/types/contact.types';
import type { CariReport } from '@/types/reports';
import apiClient from '@/services/api';
import { downloadCariExcel, downloadCariPDF, printCariReport } from '@/services/cariReportService';
import dayjs, { Dayjs } from 'dayjs';
import { useNavigate } from 'react-router-dom';

const { RangePicker } = DatePicker;
const { TextArea } = Input;

interface CariReportModalProps {
  visible: boolean;
  onClose: () => void;
  contact: Contact | null;
}

export const CariReportModal: React.FC<CariReportModalProps> = ({ visible, onClose, contact }) => {
  const navigate = useNavigate();
  const [reportData, setReportData] = useState<CariReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [startDate, setStartDate] = useState<Dayjs>(dayjs().subtract(1, 'year'));
  const [endDate, setEndDate] = useState<Dayjs>(dayjs());
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [availableTabs, setAvailableTabs] = useState<{ has120: boolean; has320: boolean; has326: boolean }>({
    has120: false,
    has320: false,
    has326: false,
  });
  const [emailModalVisible, setEmailModalVisible] = useState(false);
  const [emailAddress, setEmailAddress] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailCc, setEmailCc] = useState('');
  const [emailMessage, setEmailMessage] = useState('');
  const [emailFormat, setEmailFormat] = useState<'excel' | 'pdf'>('pdf');

  // İlk açılışta tüm hesapları yükle
  useEffect(() => {
    if (visible && contact) {
      setIsInitialLoad(true);
      setActiveTab(null);
      loadInitialReport();
    }
  }, [visible, contact]);

  // Tab değiştiğinde (ilk yükleme hariç) raporu yükle
  useEffect(() => {
    if (visible && contact && activeTab !== null && !isInitialLoad) {
      loadReport();
    }
  }, [activeTab]);

  // Tarih değiştiğinde raporu yükle
  useEffect(() => {
    if (visible && contact && activeTab !== null && !isInitialLoad) {
      loadReport();
    }
  }, [startDate, endDate]);

  const loadInitialReport = async () => {
    if (!contact) return;

    setLoading(true);
    try {
      // Tüm hesapları çek (filtre yok)
      const allResponse = await apiClient.get<CariReport>('/reporting/reports/cari', {
        params: {
          start_date: startDate.format('YYYY-MM-DD'),
          end_date: endDate.format('YYYY-MM-DD'),
          contact_id: contact.id,
        },
      });
      
      // Backend'den dönen has_*_account alanlarını kullan, yoksa items'dan belirle
      const has120 = allResponse.data.has_120_account ?? allResponse.data.items.some((item: any) => item.account_code?.startsWith('120.'));
      const has320 = allResponse.data.has_320_account ?? allResponse.data.items.some((item: any) => item.account_code?.startsWith('320.'));
      const has326 = allResponse.data.has_326_account ?? allResponse.data.items.some((item: any) => item.account_code?.startsWith('326.'));
      
      console.log('🔍 Available tabs:', { has120, has320, has326 });
      console.log('📊 All items:', allResponse.data.items.length);
      
      // Sekmeleri kaydet
      setAvailableTabs({ has120, has320, has326 });
      
      // İlk tab'ı belirle
      let firstTab: string | null = null;
      if (has120) firstTab = '120';
      else if (has320) firstTab = '320';
      else if (has326) firstTab = 'collateral';
      
      if (firstTab) {
        // İlk tab için veriyi çek
        const response = await apiClient.get<CariReport>('/reporting/reports/cari', {
          params: {
            start_date: startDate.format('YYYY-MM-DD'),
            end_date: endDate.format('YYYY-MM-DD'),
            contact_id: contact.id,
            account_filter: [firstTab],
          },
        });
        setReportData(response.data);
        setActiveTab(firstTab);
        
        // İlk yükleme bittiğinde flag'i kapat
        setTimeout(() => setIsInitialLoad(false), 100);
      } else {
        // Hiç hesap yoksa
        setReportData(allResponse.data);
        setIsInitialLoad(false);
      }
    } catch (error) {
      console.error('Rapor yüklenemedi:', error);
      setIsInitialLoad(false);
    } finally {
      setLoading(false);
    }
  };

  const loadReport = async () => {
    if (!contact) return;

    setLoading(true);
    try {
      const response = await apiClient.get<CariReport>('/reporting/reports/cari', {
        params: {
          start_date: startDate.format('YYYY-MM-DD'),
          end_date: endDate.format('YYYY-MM-DD'),
          contact_id: contact.id,
          account_filter: activeTab ? [activeTab] : undefined,
        },
      });
      setReportData(response.data);
    } catch (error) {
      console.error('Rapor yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadExcel = () => {
    if (!contact) return;
    downloadCariExcel(contact.id, contact.code || String(contact.id), startDate, endDate, activeTab || undefined);
  };

  const handleDownloadPDF = () => {
    if (!contact) return;
    downloadCariPDF(contact.id, contact.code || String(contact.id), startDate, endDate, activeTab || undefined);
  };

  const handleSendEmail = async () => {
    if (!contact) return;
    
    // Email modalını aç ve varsayılan değerleri ayarla
    setEmailAddress(contact.email || '');
    const accountType = activeTab === '120' ? 'Müşteri' : activeTab === '320' ? 'Satıcı' : 'Nakit Teminat';
    setEmailSubject(`Cari Ekstre - ${contact.name} (${accountType})`);
    setEmailCc('');
    setEmailMessage(`Sayın ${contact.name},\n\n${startDate.format('DD.MM.YYYY')} - ${endDate.format('DD.MM.YYYY')} tarihleri arasındaki cari ekstreniz ekte yer almaktadır.\n\nİyi çalışmalar dileriz.`);
    setEmailFormat('pdf');
    setEmailModalVisible(true);
  };

  const handleEmailSend = async () => {
    if (!contact || !emailAddress) {
      antMessage.error('Email adresi gereklidir');
      return;
    }
    
    if (!emailSubject) {
      antMessage.error('Konu gereklidir');
      return;
    }

    try {
      setLoading(true);
      const endpoint = emailFormat === 'excel' 
        ? '/reporting/reports/cari/email-excel'
        : '/reporting/reports/cari/email';
      
      const response = await apiClient.post(endpoint, {
        contact_id: contact.id,
        email: emailAddress,
        cc: emailCc || undefined,
        subject: emailSubject,
        message: emailMessage || undefined,
        start_date: startDate.format('YYYY-MM-DD'),
        end_date: endDate.format('YYYY-MM-DD'),
        account_filter: activeTab || undefined,
      });

      if (response.data) {
        antMessage.success('E-posta başarıyla gönderildi');
        setEmailModalVisible(false);
      }
    } catch (error: any) {
      console.error('Email gönderme hatası:', error);
      const errorMsg = error.response?.data?.detail || 'E-posta gönderilemedi';
      antMessage.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const reportColumns = [
    {
      title: 'Fiş No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 100,
      render: (text: string, record: any) => {
        if (record.transaction_id === -1) return '';
        return (
          <a onClick={() => navigate(`/transactions/${record.transaction_id}`)}>
            {text}
          </a>
        );
      },
    },
    {
      title: 'Tarih',
      dataIndex: 'transaction_date',
      key: 'transaction_date',
      width: 100,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Hesap',
      dataIndex: 'account_code',
      key: 'account_code',
      width: 120,
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      width: 120,
      align: 'right' as const,
      render: (val: number) =>
        val > 0 ? new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(val) : '',
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      width: 120,
      align: 'right' as const,
      render: (val: number) =>
        val > 0 ? new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(val) : '',
    },
    {
      title: 'Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      width: 120,
      align: 'right' as const,
      render: (val: number) => (
        <span style={{ color: val > 0 ? '#cf1322' : val < 0 ? '#3f8600' : '#666', fontWeight: 'bold' }}>
          {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(Math.abs(val))}
          {val > 0 ? ' B' : val < 0 ? ' A' : ''}
        </span>
      ),
    },
  ];

  if (!reportData) return null;

  // Tablo verisi hazırla
  const dataWithBalance: any[] = [];
  if (Number(reportData.opening_balance || 0) !== 0) {
    dataWithBalance.push({
      transaction_id: -1,
      transaction_number: '',
      transaction_date: reportData.start_date,
      description: 'AÇILIŞ BAKİYESİ',
      account_code: '',
      debit: 0,
      credit: 0,
      balance: Number(reportData.opening_balance || 0),
    });
  }
  let prevBalance = Number(reportData.opening_balance || 0);
  reportData.items.forEach((item) => {
    const balance = prevBalance + Number(item.debit || 0) - Number(item.credit || 0);
    prevBalance = balance;
    dataWithBalance.push({ ...item, balance });
  });

  const renderTabContent = (title: string) => (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title={`Toplam Borç (${title})`}
              value={Number(reportData.total_debit || 0)}
              precision={2}
              suffix="B"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title={`Toplam Alacak (${title})`}
              value={Number(reportData.total_credit || 0)}
              precision={2}
              suffix="A"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title={`Bakiye (${title})`}
              value={Number(reportData.closing_balance || 0)}
              precision={2}
              suffix={Number(reportData.closing_balance || 0) > 0 ? 'B' : Number(reportData.closing_balance || 0) < 0 ? 'A' : ''}
              valueStyle={{
                color: Number(reportData.closing_balance || 0) > 0 ? '#cf1322' : Number(reportData.closing_balance || 0) < 0 ? '#3f8600' : '#666',
                fontSize: 24,
                fontWeight: 'bold',
              }}
            />
          </Card>
        </Col>
      </Row>
      <Table
        columns={reportColumns}
        dataSource={dataWithBalance}
        rowKey={(record) => `${record.transaction_id}_${record.account_code}_${Math.random()}`}
        pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Toplam ${total} kayıt` }}
        scroll={{ x: 900 }}
        size="small"
        bordered
        summary={() => (
          <Table.Summary fixed>
            <Table.Summary.Row style={{ backgroundColor: '#fafafa', fontWeight: 'bold' }}>
              <Table.Summary.Cell index={0} colSpan={4} align="right">
                Toplam ({title})
              </Table.Summary.Cell>
              <Table.Summary.Cell index={4} align="right">
                {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(reportData.total_debit)}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={5} align="right">
                {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(reportData.total_credit)}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={6} align="right" style={{
                color: reportData.closing_balance > 0 ? '#cf1322' : reportData.closing_balance < 0 ? '#3f8600' : '#666'
              }}>
                {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(reportData.closing_balance)}
              </Table.Summary.Cell>
            </Table.Summary.Row>
          </Table.Summary>
        )}
      />
    </div>
  );

  // Dinamik tab listesi - availableTabs state'inden al
  const tabs = [];
  if (availableTabs.has120) tabs.push({ key: '120', label: '120 - Müşteriler', children: renderTabContent('120') });
  if (availableTabs.has320) tabs.push({ key: '320', label: '320 - Satıcılar', children: renderTabContent('320') });
  if (availableTabs.has326) tabs.push({ key: 'collateral', label: 'Nakit Teminat (326)', children: renderTabContent('326') });

  return (
    <Modal
      title={`Cari Ekstre - ${contact?.name || ''}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1400}
      styles={{ body: { padding: 0 } }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Progress type="circle" percent={50} status="active" />
          <p style={{ marginTop: 16 }}>Rapor yükleniyor...</p>
        </div>
      ) : (
        <div style={{ padding: '24px' }}>
          {/* Tarih Seçimi */}
          <div style={{ 
            marginBottom: 24, 
            padding: '16px', 
            backgroundColor: '#fafafa', 
            borderRadius: 8,
            border: '1px solid #d9d9d9'
          }}>
            <Space size="large" align="center">
              <div>
                <strong style={{ marginRight: 8 }}>Rapor Dönemi:</strong>
                <RangePicker
                  value={[startDate, endDate]}
                  onChange={(dates) => {
                    if (dates && dates[0] && dates[1]) {
                      setStartDate(dates[0]);
                      setEndDate(dates[1]);
                    }
                  }}
                  format="DD.MM.YYYY"
                  style={{ width: 280 }}
                />
              </div>
              <Button type="primary" onClick={() => { setIsInitialLoad(true); loadInitialReport(); }} icon={<FileTextOutlined />}>
                Raporu Yenile
              </Button>
              <Button onClick={handleDownloadExcel} icon={<DownloadOutlined />} style={{ backgroundColor: '#52c41a', borderColor: '#52c41a', color: 'white' }}>
                Excel
              </Button>
              <Button onClick={handleDownloadPDF} icon={<DownloadOutlined />} danger>
                PDF
              </Button>
              <Button onClick={printCariReport} icon={<PrinterOutlined />}>
                Yazdır
              </Button>
              <Button onClick={handleSendEmail} icon={<MailOutlined />}>
                E-posta Gönder
              </Button>
            </Space>
          </div>

          {/* Başlık */}
          <div style={{ borderBottom: '2px solid #d9d9d9', paddingBottom: 16, marginBottom: 16 }}>
            <Row justify="space-between" align="top">
              <Col>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 'bold' }}>
                  {contact?.name}
                </h2>
                <p style={{ margin: '4px 0', color: '#666' }}>
                  Vergi No: {contact?.tax_number} | Vergi Dairesi: {contact?.tax_office}
                </p>
                <p style={{ margin: '4px 0', color: '#666' }}>
                  Contact ID: {contact?.id}
                </p>
              </Col>
              <Col>
                <p style={{ margin: 0, fontSize: 14 }}>
                  <strong>Dönem:</strong> {startDate.format('DD.MM.YYYY')} - {endDate.format('DD.MM.YYYY')}
                </p>
              </Col>
            </Row>
          </div>

          {/* Tabs */}
          {tabs.length > 0 ? (
            <Tabs activeKey={activeTab || undefined} onChange={setActiveTab} items={tabs} />
          ) : (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <p>Bu contact için hiç hesap bulunamadı.</p>
            </div>
          )}
        </div>
      )}

      {/* Email Gönder Modal */}
      <Modal
        title="Cari Raporu E-posta ile Gönder"
        open={emailModalVisible}
        onOk={handleEmailSend}
        onCancel={() => setEmailModalVisible(false)}
        okText="Gönder"
        cancelText="İptal"
        width={600}
        confirmLoading={loading}
      >
        <Form layout="vertical">
          <Form.Item label="E-posta Adresi" required>
            <Input
              type="email"
              placeholder="ornek@email.com"
              value={emailAddress}
              onChange={(e) => setEmailAddress(e.target.value)}
            />
          </Form.Item>

          <Form.Item label="Konu" required>
            <Input
              placeholder="E-posta konusu"
              value={emailSubject}
              onChange={(e) => setEmailSubject(e.target.value)}
            />
          </Form.Item>

          <Form.Item label="CC (İsteğe bağlı)">
            <Input
              type="email"
              placeholder="cc@email.com (virgülle ayırarak birden fazla adres ekleyebilirsiniz)"
              value={emailCc}
              onChange={(e) => setEmailCc(e.target.value)}
            />
          </Form.Item>

          <Form.Item label="Mesaj (İsteğe bağlı)">
            <TextArea
              rows={6}
              placeholder="E-posta içeriği..."
              value={emailMessage}
              onChange={(e) => setEmailMessage(e.target.value)}
            />
          </Form.Item>

          <Form.Item label="Dosya Formatı" required>
            <Radio.Group value={emailFormat} onChange={(e) => setEmailFormat(e.target.value)}>
              <Radio value="pdf">PDF</Radio>
              <Radio value="excel">Excel</Radio>
            </Radio.Group>
          </Form.Item>

          <div style={{ padding: '12px', backgroundColor: '#f5f5f5', borderRadius: 4, marginTop: 8 }}>
            <p style={{ color: '#666', fontSize: 12, margin: 0 }}>
              <strong>Ek:</strong> Cari Ekstre Raporu ({emailFormat === 'pdf' ? 'PDF' : 'Excel'})<br/>
              <strong>Tarih Aralığı:</strong> {startDate.format('DD.MM.YYYY')} - {endDate.format('DD.MM.YYYY')}<br/>
              <strong>Hesap Tipi:</strong> {activeTab ? (activeTab === '120' ? 'Müşteriler (120)' : activeTab === '320' ? 'Satıcılar (320)' : 'Nakit Teminat (326)') : 'Tüm Hesaplar'}
            </p>
          </div>
        </Form>
      </Modal>
    </Modal>
  );
};
