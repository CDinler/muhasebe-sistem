import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Statistic,
  Row,
  Col,
  message,
  Spin,
} from 'antd';
import {
  DollarOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { EInvoice } from '@/domains/invoicing/einvoices/types/einvoice.types';

const UnpaidInvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<EInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [agingReport, setAgingReport] = useState<any>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        
        // Ödenmeyen faturaları yükle
        const invoicesResponse = await fetch('/api/v2/invoicing/einvoices/unpaid?invoice_category=incoming', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (invoicesResponse.ok) {
          const invoicesData = await invoicesResponse.json();
          setInvoices(invoicesData);
        } else {
          message.error('Faturalar yüklenemedi');
        }

        // Yaşlandırma raporu yükle
        const agingResponse = await fetch('/api/v2/invoicing/einvoices/aging-report', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (agingResponse.ok) {
          const agingData = await agingResponse.json();
          setAgingReport(agingData);
        }
      } catch (error) {
        console.error('Load error:', error);
        message.error('Veri yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);


  const columns: ColumnsType<EInvoice> = [
    {
      title: 'Fatura No',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      width: 150,
    },
    {
      title: 'Tedarikçi',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      width: 250,
    },
    {
      title: 'Tarih',
      dataIndex: 'issue_date',
      key: 'issue_date',
      width: 120,
      render: (date: string) => date ? dayjs(date).format('DD.MM.YYYY') : '-',
    },
    {
      title: 'Toplam',
      dataIndex: 'payable_amount',
      key: 'payable_amount',
      width: 130,
      align: 'right' as const,
      render: (amount: number) => new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(amount) + ' ₺',
    },
    {
      title: 'Kalan',
      key: 'remaining',
      width: 130,
      align: 'right' as const,
      render: (_: any, record: EInvoice) => {
        const remaining = (record.payable_amount || 0) - (record.paid_amount || 0);
        return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(remaining) + ' ₺';
      },
    },
    {
      title: 'Durum',
      key: 'status',
      width: 120,
      render: (_: any, record: EInvoice) => {
        const paid = record.paid_amount || 0;
        const total = record.payable_amount || 0;
        if (paid === 0) return <Tag color="red">ÖDENMEDİ</Tag>;
        if (paid < total) return <Tag color="orange">KISMİ</Tag>;
        return <Tag color="green">ÖDENDİ</Tag>;
      },
    },
  ];


  return (
    <div style={{ padding: 24 }}>
      <h1>
        <ClockCircleOutlined /> Ödenmeyen Faturalar
      </h1>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" tip="Yükleniyor..." />
        </div>
      ) : (
        <>
          {/* Yaşlandırma Raporu */}
          {agingReport && (
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="0-30 Gün"
                    value={(agingReport.current?.amount || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                    suffix="₺"
                    valueStyle={{ color: '#52c41a', fontSize: 20 }}
                  />
                  <div style={{ marginTop: 4, fontSize: 12, color: '#666' }}>
                    {agingReport.current?.count || 0} fatura
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="30-60 Gün"
                    value={(agingReport['30_60']?.amount || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                    suffix="₺"
                    valueStyle={{ color: '#faad14', fontSize: 20 }}
                  />
                  <div style={{ marginTop: 4, fontSize: 12, color: '#666' }}>
                    {agingReport['30_60']?.count || 0} fatura
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="60-90 Gün"
                    value={(agingReport['60_90']?.amount || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                    suffix="₺"
                    valueStyle={{ color: '#ff7a45', fontSize: 20 }}
                  />
                  <div style={{ marginTop: 4, fontSize: 12, color: '#666' }}>
                    {agingReport['60_90']?.count || 0} fatura
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="90+ Gün"
                    value={(agingReport.over_90?.amount || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                    suffix="₺"
                    valueStyle={{ color: '#f5222d', fontSize: 20 }}
                  />
                  <div style={{ marginTop: 4, fontSize: 12, color: '#666' }}>
                    {agingReport.over_90?.count || 0} fatura
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
              rowKey="id"
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `Toplam ${total} fatura`,
              }}
            />
          </Card>
        </>
      )}
    </div>
  );
};

export default UnpaidInvoicesPage;
