import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Progress,
  Statistic,
  Row,
  Col,
  Modal,
  Form,
  InputNumber,
  DatePicker,
  Select,
  Input,
  message,
  Descriptions,
  Divider,
} from 'antd';
import {
  DollarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { EInvoice } from '@/domains/invoicing/einvoices/types/einvoice.types';

const UnpaidInvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<EInvoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [paymentModalVisible, setPaymentModalVisible] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<EInvoice | null>(null);
  const [paymentForm] = Form.useForm();
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [agingReport, setAgingReport] = useState<any>(null);

  // Ödenmeyen faturaları yükle
  const loadUnpaidInvoices = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v2/einvoices/unpaid?invoice_category=incoming');
      if (!response.ok) throw new Error('Faturalar yüklenemedi');
      const data = await response.json();
      setInvoices(data);
    } catch (error) {
      message.error('Ödenmeyen faturalar yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Yaşlandırma raporu yükle
  const loadAgingReport = async () => {
    try {
      const response = await fetch('/api/v2/einvoices/aging-report');
      if (!response.ok) throw new Error('Rapor yüklenemedi');
      const data = await response.json();
      setAgingReport(data);
    } catch (error) {
      message.error('Yaşlandırma raporu yüklenirken hata oluştu');
    }
  };

  useEffect(() => {
    loadUnpaidInvoices();
    loadAgingReport();
  }, []);

  const handlePayment = (invoice: EInvoice) => {
    setSelectedInvoice(invoice);
    setPaymentModalVisible(true);
  };

  const handlePaymentSubmit = async (values: any) => {
    if (!selectedInvoice) return;

    try {
      setPaymentLoading(true);

      const response = await fetch(`/api/v2/einvoices/${selectedInvoice.id}/payments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: values.transaction_id,
          payment_amount: values.payment_amount,
          payment_date: values.payment_date.format('YYYY-MM-DD'),
          payment_status: 'completed',
          notes: values.notes,
        }),
      });

      if (!response.ok) throw new Error('Ödeme kaydedilemedi');

      message.success('Ödeme başarıyla kaydedildi');
      setPaymentModalVisible(false);
      setSelectedInvoice(null);
      paymentForm.resetFields();
      
      // Listeyi yenile
      loadUnpaidInvoices();
      loadAgingReport();
    } catch (error) {
      message.error('Ödeme kaydedilirken hata oluştu');
    } finally {
      setPaymentLoading(false);
    }
  };

  const columns: ColumnsType<EInvoice> = [
    {
      title: 'Fatura No',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      width: 150,
      render: (text: string, record: EInvoice) => (
        <div>
          <div style={{ fontWeight: 600 }}>{text}</div>
          <div style={{ fontSize: 11, color: '#999' }}>
            {record.issue_date ? dayjs(record.issue_date).format('DD.MM.YYYY') : '-'}
          </div>
        </div>
      ),
    },
    {
      title: 'Tedarikçi',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      width: 250,
      render: (text: string, record: EInvoice) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 11, color: '#666' }}>
            VKN: {record.supplier_tax_number || '-'}
          </div>
        </div>
      ),
    },
    {
      title: 'Vade Tarihi',
      dataIndex: 'payment_due_date',
      key: 'payment_due_date',
      width: 120,
      render: (date: string) => {
        if (!date) return '-';
        const dueDate = dayjs(date);
        const today = dayjs();
        const isOverdue = dueDate.isBefore(today);
        const daysOverdue = today.diff(dueDate, 'day');

        return (
          <div>
            <div>{dueDate.format('DD.MM.YYYY')}</div>
            {isOverdue && (
              <Tag color="red" style={{ fontSize: 10, marginTop: 4 }}>
                {daysOverdue} gün gecikmiş
              </Tag>
            )}
          </div>
        );
      },
      sorter: (a, b) => {
        const dateA = a.payment_due_date ? dayjs(a.payment_due_date).unix() : 0;
        const dateB = b.payment_due_date ? dayjs(b.payment_due_date).unix() : 0;
        return dateA - dateB;
      },
    },
    {
      title: 'Toplam Tutar',
      dataIndex: 'payable_amount',
      key: 'payable_amount',
      width: 130,
      align: 'right',
      render: (amount: number) => (
        <strong>
          {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(amount)} ₺
        </strong>
      ),
    },
    {
      title: 'Ödenen',
      key: 'paid_amount',
      width: 130,
      align: 'right',
      render: (_, record: EInvoice) => (
        <span style={{ color: '#52c41a', fontWeight: 500 }}>
          {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(record.paid_amount || 0)} ₺
        </span>
      ),
    },
    {
      title: 'Kalan',
      key: 'remaining_amount',
      width: 130,
      align: 'right',
      render: (_, record: EInvoice) => (
        <strong style={{ color: '#f5222d', fontSize: 15 }}>
          {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(record.remaining_amount || record.payable_amount || 0)} ₺
        </strong>
      ),
      sorter: (a, b) => {
        const remainingA = a.remaining_amount || a.payable_amount || 0;
        const remainingB = b.remaining_amount || b.payable_amount || 0;
        return remainingA - remainingB;
      },
    },
    {
      title: 'Durum',
      key: 'payment_status',
      width: 150,
      render: (_, record: EInvoice) => {
        const statusConfig = {
          'UNPAID': { color: 'red', icon: <ClockCircleOutlined />, text: 'ÖDENMEDİ' },
          'PARTIALLY_PAID': { color: 'orange', icon: <WarningOutlined />, text: 'KISMİ ÖDEME' },
        };

        const status = record.payment_status || 'UNPAID';
        const config = statusConfig[status] || statusConfig['UNPAID'];
        const percentage = record.payment_percentage || 0;

        return (
          <div>
            <Tag color={config.color} icon={config.icon} style={{ marginBottom: 8 }}>
              {config.text}
            </Tag>
            <Progress
              percent={percentage}
              size="small"
              strokeColor={config.color === 'orange' ? '#faad14' : '#f5222d'}
              showInfo={false}
            />
            <div style={{ fontSize: 11, color: '#666', textAlign: 'center', marginTop: 4 }}>
              {percentage.toFixed(1)}%
            </div>
          </div>
        );
      },
    },
    {
      title: 'İşlem',
      key: 'action',
      width: 120,
      render: (_, record: EInvoice) => (
        <Button
          type="primary"
          size="small"
          icon={<DollarOutlined />}
          onClick={() => handlePayment(record)}
        >
          Ödeme Kaydet
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>
        <ClockCircleOutlined /> Ödenmeyen Faturalar
      </h1>

      {/* Yaşlandırma Raporu */}
      {agingReport && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="📅 Vadesi Gelmemiş (0-30 gün)"
                value={agingReport.current?.count || 0}
                suffix="adet"
                valueStyle={{ color: '#52c41a' }}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(agingReport.current?.amount || 0).toLocaleString('tr-TR', {
                  minimumFractionDigits: 2,
                })} ₺
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="⚠️ 30-60 Gün Gecikmiş"
                value={agingReport.overdue_30?.count || 0}
                suffix="adet"
                valueStyle={{ color: '#faad14' }}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(agingReport.overdue_30?.amount || 0).toLocaleString('tr-TR', {
                  minimumFractionDigits: 2,
                })} ₺
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="🔴 60-90 Gün Gecikmiş"
                value={agingReport.overdue_60?.count || 0}
                suffix="adet"
                valueStyle={{ color: '#ff7a45' }}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(agingReport.overdue_60?.amount || 0).toLocaleString('tr-TR', {
                  minimumFractionDigits: 2,
                })} ₺
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="🚨 90+ Gün Gecikmiş"
                value={agingReport.overdue_90?.count || 0}
                suffix="adet"
                valueStyle={{ color: '#f5222d' }}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(agingReport.overdue_90?.amount || 0).toLocaleString('tr-TR', {
                  minimumFractionDigits: 2,
                })} ₺
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* Fatura Listesi */}
      <Card>
        <Table
          columns={columns}
          dataSource={invoices}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} ödenmeyen fatura`,
          }}
          summary={(pageData) => {
            const totalRemaining = pageData.reduce(
              (sum, record) => sum + (record.remaining_amount || record.payable_amount || 0),
              0
            );

            return (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0} colSpan={5} align="right">
                  <strong>TOPLAM BORÇ:</strong>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={1} align="right">
                  <strong style={{ color: '#f5222d', fontSize: 16 }}>
                    {totalRemaining.toLocaleString('tr-TR', {
                      minimumFractionDigits: 2,
                    })} ₺
                  </strong>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={2} colSpan={2} />
              </Table.Summary.Row>
            );
          }}
        />
      </Card>

      {/* Ödeme Modal */}
      <Modal
        title={
          <Space>
            <DollarOutlined style={{ color: '#52c41a' }} />
            <span>Ödeme Kaydet</span>
          </Space>
        }
        open={paymentModalVisible}
        onCancel={() => {
          setPaymentModalVisible(false);
          setSelectedInvoice(null);
          paymentForm.resetFields();
        }}
        onOk={() => paymentForm.submit()}
        confirmLoading={paymentLoading}
        width={600}
        okText="Ödemeyi Kaydet"
        cancelText="İptal"
      >
        {selectedInvoice && (
          <>
            {/* Fatura Özeti */}
            <Card size="small" style={{ marginBottom: 16, backgroundColor: '#fafafa' }}>
              <Descriptions size="small" column={2}>
                <Descriptions.Item label="Fatura No">
                  {selectedInvoice.invoice_number}
                </Descriptions.Item>
                <Descriptions.Item label="Tedarikçi">
                  {selectedInvoice.supplier_name}
                </Descriptions.Item>
                <Descriptions.Item label="Toplam Tutar">
                  <strong>
                    {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(
                      selectedInvoice.payable_amount || 0
                    )} ₺
                  </strong>
                </Descriptions.Item>
                <Descriptions.Item label="Ödenen">
                  <strong style={{ color: '#52c41a' }}>
                    {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(
                      selectedInvoice.paid_amount || 0
                    )} ₺
                  </strong>
                </Descriptions.Item>
                <Descriptions.Item label="Kalan" span={2}>
                  <strong style={{ color: '#f5222d', fontSize: 16 }}>
                    {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(
                      selectedInvoice.remaining_amount || selectedInvoice.payable_amount || 0
                    )} ₺
                  </strong>
                </Descriptions.Item>
              </Descriptions>

              <div style={{ marginTop: 12 }}>
                <div style={{ fontSize: 12, marginBottom: 4, color: '#666' }}>
                  Ödeme Durumu: {selectedInvoice.payment_percentage?.toFixed(1)}%
                </div>
                <Progress
                  percent={selectedInvoice.payment_percentage || 0}
                  strokeColor={
                    selectedInvoice.payment_status === 'PARTIALLY_PAID' ? '#faad14' : '#f5222d'
                  }
                />
              </div>
            </Card>

            {/* Ödeme Formu */}
            <Form form={paymentForm} layout="vertical" onFinish={handlePaymentSubmit}>
              <Form.Item
                label="Ödeme Tutarı"
                name="payment_amount"
                rules={[
                  { required: true, message: 'Ödeme tutarı zorunlu' },
                  {
                    validator: (_, value) => {
                      const remaining =
                        selectedInvoice.remaining_amount || selectedInvoice.payable_amount || 0;
                      if (value > remaining) {
                        return Promise.reject(
                          `Kalan tutardan fazla olamaz (Maks: ${remaining.toFixed(2)} ₺)`
                        );
                      }
                      if (value <= 0) {
                        return Promise.reject("Ödeme tutarı 0'dan büyük olmalı");
                      }
                      return Promise.resolve();
                    },
                  },
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder={`Kalan: ${(
                    selectedInvoice.remaining_amount ||
                    selectedInvoice.payable_amount ||
                    0
                  ).toFixed(2)} ₺`}
                  precision={2}
                  min={0}
                  max={selectedInvoice.remaining_amount || selectedInvoice.payable_amount || 0}
                  addonAfter="₺"
                />
              </Form.Item>

              <Form.Item
                label="İşlem (Banka/Kasa Fişi)"
                name="transaction_id"
                rules={[{ required: true, message: 'İşlem seçimi zorunlu' }]}
                extra="Ödemenin yapıldığı banka havalesi veya kasa fişini seçin"
              >
                <Select placeholder="İşlem seçin" showSearch optionFilterProp="children">
                  {/* TODO: Transaction listesi API'den gelecek */}
                  <Select.Option value={1}>Örnek İşlem 1 - 10,000 ₺</Select.Option>
                  <Select.Option value={2}>Örnek İşlem 2 - 5,000 ₺</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="Ödeme Tarihi"
                name="payment_date"
                rules={[{ required: true, message: 'Ödeme tarihi zorunlu' }]}
                initialValue={dayjs()}
              >
                <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
              </Form.Item>

              <Form.Item
                label="Notlar"
                name="notes"
                extra="Taksit bilgisi, ödeme yöntemi vb. ekstra bilgiler"
              >
                <Input.TextArea
                  rows={3}
                  placeholder="Örn: 1. taksit, Banka havalesi ile ödendi"
                />
              </Form.Item>
            </Form>

            <Card
              size="small"
              style={{ marginTop: 16, backgroundColor: '#e6f7ff', borderColor: '#91d5ff' }}
            >
              <div style={{ fontSize: 12 }}>
                <strong>💡 Bilgi:</strong>
                <ul style={{ marginTop: 8, marginBottom: 0, paddingLeft: 20 }}>
                  <li>Tam ödeme için kalan tutarın tamamını girin</li>
                  <li>Kısmi ödeme için taksit tutarını girin</li>
                  <li>Birden fazla taksit için her taksit için ayrı ödeme kaydı yapın</li>
                </ul>
              </div>
            </Card>
          </>
        )}
      </Modal>
    </div>
  );
};

export default UnpaidInvoicesPage;
