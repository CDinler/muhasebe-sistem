import React, { useEffect, useState } from 'react';
import { Table, Button, Tag, Space, Card, Row, Col, Statistic, Input, DatePicker } from 'antd';
import { PlusOutlined, EyeOutlined, FileTextOutlined, CalendarOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { transactionService, Transaction } from '@/services/muhasebe.service';
import dayjs, { Dayjs } from 'dayjs';

const { RangePicker } = DatePicker;

const TransactionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchText, setSearchText] = useState('');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [orderBy, setOrderBy] = useState<string>('date_desc');

  const loadTransactions = async (page: number = 1, size: number = 20, order: string = 'date_desc', search: string = '') => {
    setLoading(true);
    try {
      const skip = (page - 1) * size;
      
      // URL parametreleri
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: size.toString(),
        order_by: order
      });
      
      if (search.trim()) {
        params.append('search', search.trim());
      }
      
      const [transactionsResponse, countResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/transactions/?${params}`).then(r => r.json()),
        fetch(`http://localhost:8000/api/v1/transactions/count/total?${params}`).then(r => r.json())
      ]);
      
      setTransactions(transactionsResponse);
      setFilteredTransactions(transactionsResponse);
      setTotal(countResponse.total);
    } catch (error) {
      console.error('Fişler yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  // Arama yapıldığında backend'den yeniden yükle (debounce)
  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentPage(1); // Aramada ilk sayfaya dön
      loadTransactions(1, pageSize, orderBy, searchText);
    }, 500); // 500ms debounce

    return () => clearTimeout(timer);
  }, [searchText]);

  useEffect(() => {
    loadTransactions(currentPage, pageSize, orderBy, searchText);
  }, [currentPage, pageSize, orderBy]);

  const columns = [
    {
      title: 'Fiş No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 150,
      sorter: true,
      sortOrder: orderBy === 'number_asc' ? 'ascend' : orderBy === 'number_desc' ? 'descend' : null,
    },
    {
      title: 'Tarih',
      dataIndex: 'transaction_date',
      key: 'transaction_date',
      width: 120,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
      sorter: true,
      sortOrder: orderBy === 'date_asc' ? 'ascend' : orderBy === 'date_desc' ? 'descend' : null,
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
              value={filteredTransactions.length}
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
        dataSource={filteredTransactions}
        rowKey="id"
        loading={loading}
        onChange={(pagination, filters, sorter: any) => {
          // Sıralama değiştiğinde
          if (sorter && sorter.columnKey) {
            let newOrder = orderBy;
            if (sorter.columnKey === 'transaction_date') {
              newOrder = sorter.order === 'ascend' ? 'date_asc' : 'date_desc';
            } else if (sorter.columnKey === 'transaction_number') {
              newOrder = sorter.order === 'ascend' ? 'number_asc' : 'number_desc';
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
