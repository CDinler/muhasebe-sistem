import React from 'react';
import { Card, Row, Col, Statistic, Table } from 'antd';
import { FileTextOutlined, DollarOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons';

const Dashboard: React.FC = () => {
  const recentTransactions = [
    {
      key: '1',
      number: 'FIS-2025-001',
      date: '2025-12-14',
      description: 'Kasadan bankaya transfer',
      amount: '5,000.00 TL',
    },
  ];

  const columns = [
    { title: 'Fiş No', dataIndex: 'number', key: 'number' },
    { title: 'Tarih', dataIndex: 'date', key: 'date' },
    { title: 'Açıklama', dataIndex: 'description', key: 'description' },
    { title: 'Tutar', dataIndex: 'amount', key: 'amount' },
  ];

  return (
    <div>
      <h1>Dashboard</h1>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Toplam Fiş"
              value={1}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Kasa Bakiyesi"
              value={-5000}
              prefix={<DollarOutlined />}
              suffix="TL"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Banka Bakiyesi"
              value={5000}
              prefix={<RiseOutlined />}
              suffix="TL"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Hesap Sayısı"
              value={23}
              prefix={<FallOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Son İşlemler">
        <Table columns={columns} dataSource={recentTransactions} pagination={false} />
      </Card>
    </div>
  );
};

export default Dashboard;
