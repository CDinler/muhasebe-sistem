import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Table, Button, Space, Tag, Spin, message } from 'antd';
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { transactionService, accountService, costCenterService, Transaction, Account, CostCenter } from '@/services/muhasebe.service';
import dayjs from 'dayjs';

const TransactionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [txResponse, accResponse, ccResponse] = await Promise.all([
          transactionService.getById(Number(id)),
          accountService.getAll(),
          costCenterService.getAll(),
        ]);
        setTransaction(txResponse.data);
        setAccounts(Array.isArray(accResponse.data) ? accResponse.data : accResponse.data.items || []);
        setCostCenters(Array.isArray(ccResponse.data) ? ccResponse.data : ccResponse.data.items || []);
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

  const getCostCenterName = (costCenterId: number | null | undefined) => {
    if (!costCenterId) return '-';
    const costCenter = costCenters.find((cc) => cc.id === costCenterId);
    return costCenter ? costCenter.name : `Masraf Merkezi ${costCenterId}`;
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

  const handleDelete = async () => {
    if (!id) return;
    
    if (!window.confirm('Fişi silmek istediğinize emin misiniz? Bu işlem geri alınamaz!')) {
      return;
    }
    
    setDeleting(true);
    try {
      await transactionService.delete(Number(id));
      message.success('Fiş başarıyla silindi!');
      navigate('/transactions');
    } catch (error: any) {
      console.error('Delete error:', error);
      message.error(error.response?.data?.detail || 'Fiş silinemedi!');
    } finally {
      setDeleting(false);
    }
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
        <Button type="primary" icon={<EditOutlined />} onClick={() => navigate(`/transactions/${id}/edit`)}>
          Düzenle
        </Button>
        <Button danger icon={<DeleteOutlined />} onClick={handleDelete} loading={deleting}>
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
          <Descriptions.Item label="Evrak No">
            {transaction.document_number || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Masraf Merkezi">
            {getCostCenterName(transaction.cost_center_id)}
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
