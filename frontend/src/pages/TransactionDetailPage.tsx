import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Table, Button, Space, Tag, Spin } from 'antd';
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { transactionService, accountService, Transaction, Account } from '@/services/muhasebe.service';
import dayjs from 'dayjs';

const TransactionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [txResponse, accResponse] = await Promise.all([
          transactionService.getById(Number(id)),
          accountService.getAll(),
        ]);
        setTransaction(txResponse.data);
        setAccounts(accResponse.data);
      } catch (error) {
        console.error('Veri yüklenemedi:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  const getAccountName = (accountId: number) => {
    const account = accounts.find((a) => a.id === accountId);
    return account ? `${account.code} - ${account.name}` : `Hesap ${accountId}`;
  };

  const calculateTotal = () => {
    if (!transaction?.lines) return { debit: 0, credit: 0 };
    return transaction.lines.reduce(
      (acc, line) => ({
        debit: acc.debit + parseFloat(line.debit || '0'),
        credit: acc.credit + parseFloat(line.credit || '0'),
      }),
      { debit: 0, credit: 0 }
    );
  };

  const columns = [
    {
      title: 'Hesap',
      dataIndex: 'account_id',
      key: 'account_id',
      render: (accountId: number) => getAccountName(accountId),
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      align: 'right' as const,
      render: (value: string) => value && parseFloat(value) > 0 ? `${parseFloat(value).toFixed(2)} TL` : '-',
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      align: 'right' as const,
      render: (value: string) => value && parseFloat(value) > 0 ? `${parseFloat(value).toFixed(2)} TL` : '-',
    },
  ];

  const totals = calculateTotal();

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (!transaction) {
    return <div>Fiş bulunamadı</div>;
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/transactions')}>
          Geri
        </Button>
        <Button type="primary" icon={<EditOutlined />}>
          Düzenle
        </Button>
        <Button danger icon={<DeleteOutlined />}>
          Sil
        </Button>
      </Space>

      <Card title="Fiş Bilgileri" style={{ marginBottom: 16 }}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Fiş No">{transaction.transaction_number}</Descriptions.Item>
          <Descriptions.Item label="Tarih">
            {dayjs(transaction.transaction_date).format('DD.MM.YYYY')}
          </Descriptions.Item>
          <Descriptions.Item label="Dönem">{transaction.accounting_period}</Descriptions.Item>
          <Descriptions.Item label="Evrak Türü">
            {transaction.document_type ? <Tag color="blue">{transaction.document_type}</Tag> : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Evrak Alt Türü">
            {transaction.document_subtype ? <Tag color="cyan">{transaction.document_subtype}</Tag> : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Evrak No">
            {transaction.document_number || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="İlgili Fatura No">
            {transaction.related_invoice_number || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Masraf Merkezi">
            {transaction.cost_center_id ? `Masraf Merkezi ${transaction.cost_center_id}` : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Açıklama" span={2}>
            {transaction.description || '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="Fiş Satırları">
        <Table
          columns={columns}
          dataSource={transaction.lines}
          rowKey="id"
          pagination={false}
          summary={() => (
            <Table.Summary>
              <Table.Summary.Row style={{ fontWeight: 'bold', backgroundColor: '#fafafa' }}>
                <Table.Summary.Cell index={0} colSpan={2}>
                  TOPLAM
                </Table.Summary.Cell>
                <Table.Summary.Cell index={2} align="right">
                  {totals.debit.toFixed(2)} TL
                </Table.Summary.Cell>
                <Table.Summary.Cell index={3} align="right">
                  {totals.credit.toFixed(2)} TL
                </Table.Summary.Cell>
              </Table.Summary.Row>
              <Table.Summary.Row>
                <Table.Summary.Cell index={0} colSpan={2}>
                  Fark
                </Table.Summary.Cell>
                <Table.Summary.Cell index={2} colSpan={2} align="right">
                  {Math.abs(totals.debit - totals.credit).toFixed(2)} TL
                  {totals.debit === totals.credit && (
                    <Tag color="success" style={{ marginLeft: 8 }}>
                      Dengede
                    </Tag>
                  )}
                </Table.Summary.Cell>
              </Table.Summary.Row>
            </Table.Summary>
          )}
        />
      </Card>
    </div>
  );
};

export default TransactionDetailPage;
