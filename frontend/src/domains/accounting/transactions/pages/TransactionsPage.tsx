import React, { useEffect, useState } from 'react';
import { Table, Button, Tag, Space, Card, Row, Col, Statistic, Input, DatePicker } from 'antd';
import { PlusOutlined, EyeOutlined, FileTextOutlined, CalendarOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dayjs, { Dayjs } from 'dayjs';

// 🆕 V2 Domain imports
import { useTransactions } from '@/domains/accounting/transactions/hooks/useTransactions';
import type { Transaction, TransactionFilters } from '@/domains/accounting/transactions/types/transaction.types';

const { RangePicker } = DatePicker;

const TransactionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchText, setSearchText] = useState('');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [orderBy, setOrderBy] = useState<string>('number_desc');

  // 🆕 V2 Filters
  const [filters, setFilters] = useState<TransactionFilters>({
    skip: 0,
    limit: pageSize,
    order_by: orderBy,
  });

  // 🆕 React Query hooks
  const { data: transactionData, isLoading: loading } = useTransactions(filters);

  const transactions = transactionData?.items || [];
  const total = transactionData?.total || 0;

  // Update filters when search, page, or orderBy changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        order_by: orderBy,
        search: searchText.trim() || undefined,
      });
    }, 500); // 500ms debounce

    return () => clearTimeout(timer);
  }, [searchText, currentPage, pageSize, orderBy]);

  const columns = [
    {
      title: 'Fiş No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 150,
      sorter: true,
    },
    {
      title: 'Tarih',
      dataIndex: 'transaction_date',
      key: 'transaction_date',
      width: 120,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
      sorter: true,
    },
    {
      title: 'Dönem',
      dataIndex: 'accounting_period',
      key: 'accounting_period',
      width: 100,
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Evrak Türü',
      dataIndex: 'document_type',
      key: 'document_type',
      width: 120,
      render: (type: string) => type && <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Evrak Alt Türü',
      dataIndex: 'document_subtype',
      key: 'document_subtype',
      width: 130,
      render: (subtype: string) => subtype && <Tag color="cyan">{subtype}</Tag>,
    },
    {
      title: 'Evrak No',
      dataIndex: 'document_number',
      key: 'document_number',
      width: 120,
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 100,
      render: (_: any, record: Transaction) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/transactions/${record.id}`)}
          >
            Görüntüle
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Fişler</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/transactions/new')}>
          Yeni Fiş
        </Button>
      </div>

      {/* Arama ve Filtreleme */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="large" wrap>
          <Input
            placeholder="Fiş no, açıklama, evrak türü, evrak no ara..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 350 }}
            allowClear
          />
          <RangePicker
            value={dateRange}
            onChange={(dates) => setDateRange(dates as [Dayjs, Dayjs] | null)}
            format="DD.MM.YYYY"
            placeholder={['Başlangıç', 'Bitiş']}
          />
          {(searchText || dateRange) && (
            <Button
              onClick={() => {
                setSearchText('');
                setDateRange(null);
              }}
            >
              Filtreleri Temizle
            </Button>
          )}
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Toplam Fiş Sayısı"
              value={total}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Filtrelenmiş"
              value={transactions.length}
              suffix={searchText || dateRange ? '(filtreli)' : ''}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: searchText || dateRange ? '#1890ff' : undefined }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Toplam Sayfa"
              value={Math.ceil(total / pageSize)}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={transactions}
        rowKey="id"
        loading={loading}
        onChange={(_pagination, _filters, sorter: any) => {
          // Sıralama değiştiğinde
          if (sorter && sorter.columnKey) {
            let newOrder = orderBy;
            if (sorter.columnKey === 'transaction_date') {
              if (sorter.order === 'ascend') {
                newOrder = 'date_asc';
              } else if (sorter.order === 'descend') {
                newOrder = 'date_desc';
              } else {
                // Sıralama kaldırıldı, varsayılana dön
                newOrder = 'date_desc';
              }
            } else if (sorter.columnKey === 'transaction_number') {
              if (sorter.order === 'ascend') {
                newOrder = 'number_asc';
              } else if (sorter.order === 'descend') {
                newOrder = 'number_desc';
              } else {
                // Sıralama kaldırıldı, varsayılana dön
                newOrder = 'date_desc';
              }
            }
            if (newOrder !== orderBy) {
              setOrderBy(newOrder);
              setCurrentPage(1);
            }
          }
        }}
        pagination={{
          current: currentPage,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (total) => `${searchText ? 'Filtrelenmiş' : 'Toplam'} ${total.toLocaleString('tr-TR')} fiş`,
          onChange: (page, size) => {
            setCurrentPage(page);
            if (size !== pageSize) {
              setPageSize(size);
              setCurrentPage(1);
            }
          }
        }}
      />
    </div>
  );
};

export default TransactionsPage;
