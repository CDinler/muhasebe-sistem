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
} from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { 
  transactionService, 
  accountService, 
  documentTypeService,
  documentSubtypeService,
  costCenterService,
  Account, 
  TransactionLine,
  DocumentType,
  DocumentSubtype,
  CostCenter
} from '@/services/muhasebe.service';
import { generateTransactionNumber } from '@/utils/numberGenerators';
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
  const [documentSubtypes, setDocumentSubtypes] = useState<DocumentSubtype[]>([]);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [lines, setLines] = useState<FormLine[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(!!id);
  const [selectedDocType, setSelectedDocType] = useState<number | null>(null);
  const [requiresSubtype, setRequiresSubtype] = useState<boolean>(false);

  useEffect(() => {
    loadInitialData();
  }, [id]);

  const loadInitialData = async () => {
    await Promise.all([
      loadAccounts(),
      loadDocumentTypes(),
      loadCostCenters()
    ]);
    if (id) {
      await loadTransaction();
    }
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
        document_subtype_id: transaction.document_subtype_id,
        document_number: transaction.document_number,
      });
      
      // Evrak türü seçiliyse alt türleri yükle
      if (transaction.document_type_id) {
        setSelectedDocType(transaction.document_type_id);
        await loadDocumentSubtypes(transaction.document_type_id);
      }
      
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
      setAccounts(response.data);
    } catch (error) {
      console.error('Hesaplar yüklenemedi:', error);
    }
  };

  const loadDocumentTypes = async () => {
    try {
      const response = await documentTypeService.getAll({ is_active: true });
      setDocumentTypes(response.data);
    } catch (error) {
      console.error('Evrak türleri yüklenemedi:', error);
    }
  };

  const loadDocumentSubtypes = async (documentTypeId: number) => {
    try {
      const response = await documentSubtypeService.getAll({ 
        is_active: true,
        document_type_id: documentTypeId 
      });
      setDocumentSubtypes(response.data);
    } catch (error) {
      console.error('Alt evrak türleri yüklenemedi:', error);
    }
  };

  const loadCostCenters = async () => {
    try {
      const response = await costCenterService.getAll({ is_active: true });
      setCostCenters(response.data);
    } catch (error) {
      console.error('Masraf merkezleri yüklenemedi:', error);
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
        cost_center_id: values.cost_center_id || null,
        document_type_id: values.document_type_id || null,
        document_subtype_id: values.document_subtype_id || null,
        document_number: values.document_number || null,
        lines: lines.map((line) => ({
          account_id: line.account_id,
          description: line.description,
          debit: line.debit?.toString() || '0.00',
          credit: line.credit?.toString() || '0.00',
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
              rules={[{ required: true, message: 'Fiş numarası gerekli!' }]}
              initialValue={!id ? generateTransactionNumber() : undefined}
            >
              <Input placeholder="FIS-20260105-0001" />
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
                onChange={(value) => {
                  setSelectedDocType(value);
                  
                  // Alt tür gerekli mi kontrol et
                  const docType = documentTypes.find(dt => dt.id === value);
                  const needsSubtype = docType?.requires_subtype || false;
                  setRequiresSubtype(needsSubtype);
                  
                  // Alt türü sıfırla
                  form.setFieldValue('document_subtype_id', null);
                  
                  // Eğer alt tür gerekiyorsa yükle
                  if (value && needsSubtype) {
                    loadDocumentSubtypes(value);
                  } else {
                    setDocumentSubtypes([]);
                  }
                }}
              >
                {documentTypes.map(dt => (
                  <Select.Option key={dt.id} value={dt.id}>
                    {dt.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {/* Alt evrak türü - SADECE requires_subtype=true ise göster */}
            {requiresSubtype && (
              <Form.Item 
                label="Alt Evrak Türü" 
                name="document_subtype_id"
                rules={[{ required: true, message: 'Alt evrak türü gerekli!' }]}
              >
                <Select
                  placeholder="Alt tür seçin"
                  allowClear
                  showSearch
                  optionFilterProp="children"
                  disabled={!selectedDocType}
                >
                  {documentSubtypes
                    .filter(dst => !selectedDocType || dst.document_type_id === selectedDocType)
                    .map(dst => (
                      <Select.Option key={dst.id} value={dst.id}>
                        {dst.name}
                      </Select.Option>
                    ))}
                </Select>
              </Form.Item>
            )}

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
              {id ? 'Güncelle' : 'Kaydet'}
            </Button>
            <Button onClick={() => navigate('/transactions')}>İptal</Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
};

export default NewTransactionPage;
