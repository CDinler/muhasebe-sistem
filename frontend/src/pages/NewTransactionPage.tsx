import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Form,
  Input,
  DatePicker,
  Select,
  Button,
  Card,
  Table,
  InputNumber,
  Space,
  message,
} from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { transactionService, accountService, Account, TransactionLine } from '@/services/muhasebe.service';
import dayjs from 'dayjs';

const { TextArea } = Input;

interface FormLine extends TransactionLine {
  key: string;
}

const NewTransactionPage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [lines, setLines] = useState<FormLine[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await accountService.getAll();
      setAccounts(response.data);
    } catch (error) {
      console.error('Hesaplar yüklenemedi:', error);
    }
  };

  const addLine = () => {
    const newLine: FormLine = {
      key: Date.now().toString(),
      account_id: 0,
      description: '',
      debit: null,
      credit: null,
    };
    setLines([...lines, newLine]);
  };

  const removeLine = (key: string) => {
    setLines(lines.filter((line) => line.key !== key));
  };

  const updateLine = (key: string, field: keyof FormLine, value: any) => {
    setLines(
      lines.map((line) =>
        line.key === key ? { ...line, [field]: value } : line
      )
    );
  };

  const calculateTotals = () => {
    return lines.reduce(
      (acc, line) => ({
        debit: acc.debit + parseFloat(line.debit?.toString() || '0'),
        credit: acc.credit + parseFloat(line.credit?.toString() || '0'),
      }),
      { debit: 0, credit: 0 }
    );
  };

  const handleSubmit = async (values: any) => {
    const totals = calculateTotals();
    
    if (totals.debit !== totals.credit) {
      message.error('Borç ve alacak tutarları eşit olmalıdır!');
      return;
    }

    if (lines.length < 2) {
      message.error('En az 2 satır girmelisiniz!');
      return;
    }

    setLoading(true);
    try {
      const transaction = {
        transaction_number: values.transaction_number,
        transaction_date: values.transaction_date.format('YYYY-MM-DD'),
        accounting_period: values.transaction_date.format('YYYY-MM'),
        description: values.description,
        document_type: values.document_type || 'STANDART',
        lines: lines.map((line) => ({
          account_id: line.account_id,
          description: line.description,
          debit: line.debit?.toString() || '0.00',
          credit: line.credit?.toString() || '0.00',
        })),
      };

      await transactionService.create(transaction);
      message.success('Fiş başarıyla oluşturuldu!');
      navigate('/transactions');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Fiş oluşturulamadı!');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Hesap',
      dataIndex: 'account_id',
      key: 'account_id',
      width: '30%',
      render: (_: any, record: FormLine) => (
        <Select
          showSearch
          style={{ width: '100%' }}
          placeholder="Hesap seçin"
          optionFilterProp="children"
          value={record.account_id || undefined}
          onChange={(value) => updateLine(record.key, 'account_id', value)}
        >
          {accounts.map((acc) => (
            <Select.Option key={acc.id} value={acc.id}>
              {acc.code} - {acc.name}
            </Select.Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
      width: '30%',
      render: (_: any, record: FormLine) => (
        <Input
          value={record.description}
          onChange={(e) => updateLine(record.key, 'description', e.target.value)}
          placeholder="Açıklama"
        />
      ),
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      width: '15%',
      render: (_: any, record: FormLine) => (
        <InputNumber
          style={{ width: '100%' }}
          value={record.debit as any}
          onChange={(value) => {
            updateLine(record.key, 'debit', value);
            if (value && value > 0) {
              updateLine(record.key, 'credit', null);
            }
          }}
          min={0}
          precision={2}
          placeholder="0.00"
        />
      ),
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      width: '15%',
      render: (_: any, record: FormLine) => (
        <InputNumber
          style={{ width: '100%' }}
          value={record.credit as any}
          onChange={(value) => {
            updateLine(record.key, 'credit', value);
            if (value && value > 0) {
              updateLine(record.key, 'debit', null);
            }
          }}
          min={0}
          precision={2}
          placeholder="0.00"
        />
      ),
    },
    {
      title: '',
      key: 'actions',
      width: '10%',
      render: (_: any, record: FormLine) => (
        <Button
          danger
          icon={<DeleteOutlined />}
          onClick={() => removeLine(record.key)}
        />
      ),
    },
  ];

  const totals = calculateTotals();

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/transactions')}>
          Geri
        </Button>
      </Space>

      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Card title="Fiş Bilgileri" style={{ marginBottom: 16 }}>
          <Form.Item
            label="Fiş No"
            name="transaction_number"
            rules={[{ required: true, message: 'Fiş numarası gerekli!' }]}
            initialValue={`FIS-${dayjs().format('YYYY-MM-DD')}-${Date.now().toString().slice(-4)}`}
          >
            <Input placeholder="FIS-2025-001" />
          </Form.Item>

          <Form.Item
            label="Tarih"
            name="transaction_date"
            rules={[{ required: true, message: 'Tarih gerekli!' }]}
            initialValue={dayjs()}
          >
            <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
          </Form.Item>

          <Form.Item label="Evrak Türü" name="document_type" initialValue="STANDART">
            <Select>
              <Select.Option value="STANDART">STANDART</Select.Option>
              <Select.Option value="AÇILIŞ">AÇILIŞ</Select.Option>
              <Select.Option value="KAPANIŞ">KAPANIŞ</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="Açıklama" name="description">
            <TextArea rows={2} placeholder="Fiş açıklaması" />
          </Form.Item>
        </Card>

        <Card
          title="Fiş Satırları"
          extra={
            <Button type="dashed" icon={<PlusOutlined />} onClick={addLine}>
              Satır Ekle
            </Button>
          }
        >
          <Table
            columns={columns}
            dataSource={lines}
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
                  <Table.Summary.Cell index={4} />
                </Table.Summary.Row>
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0} colSpan={2}>
                    Fark
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={2} colSpan={3}>
                    {Math.abs(totals.debit - totals.credit).toFixed(2)} TL
                    {totals.debit === totals.credit && totals.debit > 0 && (
                      <span style={{ color: '#52c41a', marginLeft: 8 }}>✓ Dengede</span>
                    )}
                    {totals.debit !== totals.credit && (totals.debit > 0 || totals.credit > 0) && (
                      <span style={{ color: '#ff4d4f', marginLeft: 8 }}>✗ Dengesiz</span>
                    )}
                  </Table.Summary.Cell>
                </Table.Summary.Row>
              </Table.Summary>
            )}
          />
        </Card>

        <Form.Item style={{ marginTop: 16 }}>
          <Space>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
              Kaydet
            </Button>
            <Button onClick={() => navigate('/transactions')}>İptal</Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
};

export default NewTransactionPage;
