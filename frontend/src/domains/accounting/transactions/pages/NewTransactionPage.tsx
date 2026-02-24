import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
  Spin,
  Popconfirm,
} from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { 
  transactionService, 
  accountService, 
  documentTypeService,
  costCenterService,
  Account, 
  TransactionLine,
  DocumentType,
  CostCenter
} from '@/services/muhasebe.service';
import dayjs from 'dayjs';

const { TextArea } = Input;

interface FormLine extends TransactionLine {
  key: string;
}

const NewTransactionPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [form] = Form.useForm();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [lines, setLines] = useState<FormLine[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(!!id);

  useEffect(() => {
    loadCommonData();
  }, []);

  useEffect(() => {
    if (id) {
      loadTransaction();
    }
  }, [id]);

  const loadCommonData = async () => {
    await Promise.all([
      loadAccounts(),
      loadDocumentTypes(),
      loadCostCenters()
    ]);
  };

  const loadTransaction = async () => {
    if (!id) return;
    
    setInitialLoading(true);
    try {
      const response = await transactionService.getById(Number(id));
      const transaction = response.data;
      
      // Form'u doldur
      form.setFieldsValue({
        transaction_number: transaction.transaction_number,
        transaction_date: dayjs(transaction.transaction_date),
        accounting_period: transaction.accounting_period,
        cost_center_id: transaction.cost_center_id,
        description: transaction.description,
        document_type_id: transaction.document_type_id,
        document_number: transaction.document_number,
      });
      
      // Satırları doldur
      const formLines: FormLine[] = transaction.lines.map((line: any) => ({
        ...line,
        key: line.id.toString(),
      }));
      setLines(formLines);
    } catch (error) {
      console.error('Fiş yüklenemedi:', error);
      message.error('Fiş yüklenemedi');
      navigate('/transactions');
    } finally {
      setInitialLoading(false);
    }
  };

  const loadAccounts = async () => {
    try {
      const response = await accountService.getAll();
      const accountsData = Array.isArray(response.data) ? response.data : response.data.items || [];
      console.log('Loaded accounts:', accountsData.length, accountsData.slice(0, 3));
      setAccounts(accountsData);
    } catch (error) {
      console.error('Hesaplar yüklenemedi:', error);
    }
  };

  const loadDocumentTypes = async () => {
    try {
      const response = await documentTypeService.getAll({ is_active: true });
      setDocumentTypes(Array.isArray(response.data) ? response.data : response.data.items || []);
    } catch (error) {
      console.error('Evrak türleri yüklenemedi:', error);
    }
  };

  const loadCostCenters = async () => {
    try {
      const response = await costCenterService.getAll({ is_active: true });
      setCostCenters(Array.isArray(response.data) ? response.data : response.data.items || []);
    } catch (error) {
      console.error('Masraf merkezleri yüklenemedi:', error);
    }
  };

  const addLine = () => {
    const newLine: FormLine = {
      key: Date.now().toString(),
      account_id: 0,
      description: '',
      debit: 0,
      credit: 0,
      quantity: 0,
      unit: '',
    };
    setLines([...lines, newLine]);
  };

  const removeLine = (key: string) => {
    setLines(lines.filter((line) => line.key !== key));
  };

  const updateLine = (key: string, field: keyof FormLine, value: any) => {
    const updatedLines = lines.map((line) =>
      line.key === key ? { ...line, [field]: value || 0 } : line
    );
    setLines(updatedLines);
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
        transaction_number: id ? values.transaction_number : "",  // Yeni kayıtta boş, backend otomatik verir
        transaction_date: values.transaction_date.format('YYYY-MM-DD'),
        accounting_period: values.transaction_date.format('YYYY-MM'),
        description: values.description || null,
        cost_center_id: values.cost_center_id || null,
        personnel_id: null,  // Şimdilik null, gerekirse form'a eklenebilir
        document_type_id: values.document_type_id || null,
        document_number: values.document_number || null,
        related_invoice_number: null,  // Junction table kullanılıyor artık
        draft: false,  // Resmi kayıt
        lines: lines.map((line) => ({
          account_id: line.account_id,
          contact_id: null,
          description: line.description || null,
          debit: line.debit?.toString() || '0.00',
          credit: line.credit?.toString() || '0.00',
          quantity: line.quantity || null,
          unit: line.unit || null,
          vat_rate: null,
          withholding_rate: null,
          vat_base: null,
        })),
      };

      if (id) {
        // Güncelleme modu
        await transactionService.update(Number(id), transaction);
        message.success('Fiş başarıyla güncellendi!');
      } else {
        // Yeni oluşturma modu
        await transactionService.create(transaction);
        message.success('Fiş başarıyla oluşturuldu!');
      }
      
      navigate('/transactions');
    } catch (error: any) {
      message.error(error.response?.data?.detail || (id ? 'Fiş güncellenemedi!' : 'Fiş oluşturulamadı!'));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    
    if (!window.confirm('Fişi silmek istediğinize emin misiniz? Bu işlem geri alınamaz!')) {
      return;
    }
    
    console.log('handleDelete called with id:', id);
    setLoading(true);
    try {
      await transactionService.delete(Number(id));
      message.success('Fiş başarıyla silindi!');
      navigate('/transactions');
    } catch (error: any) {
      console.error('Delete error:', error);
      message.error(error.response?.data?.detail || 'Fiş silinemedi!');
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
          filterOption={(input, option) =>
            (option?.children?.toString().toLowerCase() ?? '').includes(input.toLowerCase())
          }
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
      width: '20%',
      render: (_: any, record: FormLine) => (
        <Input
          value={record.description}
          onChange={(e) => updateLine(record.key, 'description', e.target.value)}
          placeholder="Açıklama"
        />
      ),
    },
    {
      title: 'Miktar',
      dataIndex: 'quantity',
      key: 'quantity',
      width: '10%',
      render: (_: any, record: FormLine) => (
        <InputNumber
          style={{ width: '100%' }}
          value={record.quantity || undefined}
          onChange={(value) => updateLine(record.key, 'quantity', value || 0)}
          min={0}
          precision={4}
          placeholder="0"
        />
      ),
    },
    {
      title: 'Birim',
      dataIndex: 'unit',
      key: 'unit',
      width: '8%',
      render: (_: any, record: FormLine) => (
        <Input
          style={{ width: '100%' }}
          value={record.unit || ''}
          onChange={(e) => updateLine(record.key, 'unit', e.target.value)}
          placeholder="Adet"
        />
      ),
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      width: '12%',
      render: (_: any, record: FormLine) => (
        <InputNumber
          style={{ width: '100%' }}
          value={record.debit || undefined}
          onChange={(value) => {
            const newValue = value || 0;
            setLines(lines.map((line) =>
              line.key === record.key 
                ? { ...line, debit: newValue, credit: newValue > 0 ? 0 : line.credit }
                : line
            ));
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
      width: '12%',
      render: (_: any, record: FormLine) => (
        <InputNumber
          style={{ width: '100%' }}
          value={record.credit || undefined}
          onChange={(value) => {
            const newValue = value || 0;
            setLines(lines.map((line) =>
              line.key === record.key 
                ? { ...line, credit: newValue, debit: newValue > 0 ? 0 : line.debit }
                : line
            ));
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

  if (initialLoading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/transactions')}>
          Geri
        </Button>
      </Space>

      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Card title={id ? "Fiş Düzenle" : "Yeni Fiş"} style={{ marginBottom: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item
              label="Fiş No"
              name="transaction_number"
              rules={[{ required: false }]}
              initialValue={!id ? "(Otomatik verilecek)" : undefined}
            >
              <Input placeholder="Otomatik verilecek" disabled={!id} />
            </Form.Item>

            <Form.Item
              label="Tarih"
              name="transaction_date"
              rules={[{ required: true, message: 'Tarih gerekli!' }]}
              initialValue={!id ? dayjs() : undefined}
            >
              <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
            </Form.Item>

            <Form.Item label="Evrak Türü" name="document_type_id">
              <Select
                placeholder="Evrak türü seçin"
                allowClear
                showSearch
                optionFilterProp="children"
              >
                {documentTypes.map(dt => (
                  <Select.Option key={dt.id} value={dt.id}>
                    {dt.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item label="Evrak No" name="document_number">
              <Input placeholder="Evrak numarası (dekont no, banka kayıt no, vb.)" />
            </Form.Item>

            <Form.Item label="Masraf Merkezi" name="cost_center_id">
              <Select
                placeholder="Masraf merkezi seçin"
                allowClear
                showSearch
                optionFilterProp="children"
              >
                {costCenters.map(cc => (
                  <Select.Option key={cc.id} value={cc.id}>
                    {cc.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </div>

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
            rowKey="key"
            pagination={false}
            summary={() => (
              <Table.Summary>
                <Table.Summary.Row style={{ fontWeight: 'bold', backgroundColor: '#fafafa' }}>
                  <Table.Summary.Cell index={0} colSpan={4}>
                    TOPLAM
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={4} align="right">
                    {totals.debit.toFixed(2)} TL
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={5} align="right">
                    {totals.credit.toFixed(2)} TL
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={6} />
                </Table.Summary.Row>
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0} colSpan={4}>
                    Fark
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={4} colSpan={2} align="right">
                    {Math.abs(totals.debit - totals.credit).toFixed(2)} TL
                    {totals.debit === totals.credit && totals.debit > 0 && (
                      <span style={{ color: '#52c41a', marginLeft: 8 }}>✓ Dengede</span>
                    )}
                    {totals.debit !== totals.credit && (totals.debit > 0 || totals.credit > 0) && (
                      <span style={{ color: '#ff4d4f', marginLeft: 8 }}>✗ Dengesiz</span>
                    )}
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={6} />
                </Table.Summary.Row>
              </Table.Summary>
            )}
          />
        </Card>

        <div style={{ marginTop: 16 }}>
          <Space>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
              {id ? 'Güncelle' : 'Kaydet'}
            </Button>
            <Button htmlType="button" onClick={() => navigate('/transactions')}>İptal</Button>
            {id && (
              <Button 
                htmlType="button" 
                danger 
                icon={<DeleteOutlined />} 
                loading={loading}
                onClick={handleDelete}
              >
                Sil
              </Button>
            )}
          </Space>
        </div>
      </Form>
    </div>
  );
};

export default NewTransactionPage;
