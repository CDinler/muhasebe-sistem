import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, Modal, Form, Input, Select, message, Tabs, InputNumber, Descriptions, Drawer, Card, Row, Col, Statistic, Upload, Progress } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, TeamOutlined, ShoppingOutlined, ShopOutlined, UploadOutlined, FileTextOutlined, SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import axios from 'axios';
import dayjs, { Dayjs } from 'dayjs';
import api from '@/services/api';

// 🆕 V2 Domain imports
import { useContactsList, useCreateContact, useUpdateContact, useDeleteContact } from '@/domains/partners/contacts/hooks/useContacts';
import type { Contact, ContactCreateRequest } from '@/domains/partners/contacts/types/contact.types';

const { TabPane } = Tabs;

interface CariReportItem {
  transaction_id: number;
  transaction_number: string;
  transaction_date: string;
  due_date: string | null;
  document_type: string | null;
  description: string | null;
  account_code: string;
  account_name: string;
  account_type: string;
  currency: string | null;
  currency_debit: number | null;
  currency_credit: number | null;
  currency_balance: number | null;
  debit: number;
  credit: number;
  balance: number;
}

interface CariReport {
  contact_id: number | null;
  contact_code: string | null;
  contact_name: string;
  tax_number: string | null;
  start_date: string;
  end_date: string;
  opening_balance: number;
  items: CariReportItem[];
  closing_balance: number;
  total_debit: number;
  total_credit: number;
}

interface TransactionDetail {
  id: number;
  transaction_number: string;
  transaction_date: string;
  description: string | null;
  lines: Array<{
    account_code: string;
    account_name: string;
    debit: number;
    credit: number;
  }>;
}

const ContactsPage: React.FC = () => {
  // 🆕 V2 React Query hooks
  const { data: contacts = [], isLoading: loading, refetch: refetchContacts } = useContactsList();
  const createContactMutation = useCreateContact();
  const updateContactMutation = useUpdateContact();
  const deleteContactMutation = useDeleteContact();

  const [filteredContacts, setFilteredContacts] = useState<Contact[]>([]);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [viewingContact, setViewingContact] = useState<Contact | null>(null);
  const [form] = Form.useForm();
  
  // Toplu yükleme state'leri
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  // Cari raporu state'leri
  const [reportModalVisible, setReportModalVisible] = useState(false);
  const [reportData, setReportData] = useState<CariReport | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [transactionDetailVisible, setTransactionDetailVisible] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<TransactionDetail | null>(null);
  const [transactionLoading, setTransactionLoading] = useState(false);

  // Arama filtresi
  useEffect(() => {
    if (!searchText.trim()) {
      setFilteredContacts(contacts);
      return;
    }

    const search = searchText.toLowerCase();
    const filtered = contacts.filter(
      (c) =>
        c.name.toLowerCase().includes(search) ||
        c.code?.toLowerCase().includes(search) ||
        c.tax_number?.toLowerCase().includes(search) ||
        c.tax_office?.toLowerCase().includes(search) ||
        c.phone?.toLowerCase().includes(search)
    );
    setFilteredContacts(filtered);
  }, [searchText, contacts]);

  const handleAdd = () => {
    form.resetFields();
    setEditingContact(null);
    setModalVisible(true);
  };

  const handleEdit = (contact: Contact) => {
    form.setFieldsValue(contact);
    setEditingContact(contact);
    setModalVisible(true);
  };

  const handleView = (contact: Contact) => {
    setViewingContact(contact);
    setDetailDrawerVisible(true);
  };

  const handleDelete = async (id: number) => {
    deleteContactMutation.mutate(id, {
      onSuccess: () => {
        refetchContacts();
      }
    });
  };

  const handleSubmit = async (values: ContactCreateRequest) => {
    if (editingContact?.id) {
      updateContactMutation.mutate({ id: editingContact.id, data: values }, {
        onSuccess: () => {
          setModalVisible(false);
          refetchContacts();
        }
      });
    } else {
      createContactMutation.mutate(values, {
        onSuccess: () => {
          setModalVisible(false);
          refetchContacts();
        }
      });
    }
  };

  const handleBulkUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    setUploadModalVisible(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/v1/contacts/bulk-import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total 
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setUploadProgress(progress);
        },
      });

      message.success(`${response.data.added} cari eklendi, ${response.data.updated} cari güncellendi`);
      refetchContacts();
      
      setTimeout(() => {
        setUploadModalVisible(false);
        setUploadProgress(0);
      }, 1500);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Yükleme başarısız');
      setUploadModalVisible(false);
    } finally {
      setUploading(false);
    }

    return false; // Prevent auto upload
  };

  const handleViewReport = async (contact: Contact) => {
    setSelectedContact(contact);
    setReportModalVisible(true);
    setReportLoading(true);

    try {
      // Son 1 yıllık rapor
      const endDate = dayjs();
      const startDate = dayjs().subtract(1, 'year');

      const response = await api.get<CariReport>('/reports/cari', {
        params: {
          start_date: startDate.format('YYYY-MM-DD'),
          end_date: endDate.format('YYYY-MM-DD'),
          contact_id: contact.id,
        },
      });

      setReportData(response.data);
    } catch (error) {
      message.error('Cari raporu yüklenirken hata oluştu');
      setReportModalVisible(false);
    } finally {
      setReportLoading(false);
    }
  };

  const contactTypeColors: Record<string, string> = {
    customer: 'blue',
    supplier: 'orange',
    both: 'purple',
  };

  const contactTypeNames: Record<string, string> = {
    customer: 'Müşteri',
    supplier: 'Tedarikçi',
    both: 'Her İkisi',
  };

  const columns = [
    {
      title: 'Cari Kodu',
      dataIndex: 'code',
      key: 'code',
      width: 120,
      sorter: (a: Contact, b: Contact) => (a.code || '').localeCompare(b.code || ''),
    },
    {
      title: 'Unvan',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: Contact, b: Contact) => a.name.localeCompare(b.name),
    },
    {
      title: 'Vergi No',
      dataIndex: 'tax_number',
      key: 'tax_number',
      width: 130,
    },
    {
      title: 'Vergi Dairesi',
      dataIndex: 'tax_office',
      key: 'tax_office',
      width: 150,
    },
    {
      title: 'Tür',
      dataIndex: 'contact_type',
      key: 'contact_type',
      width: 120,
      render: (type: string | null) =>
        type && <Tag color={contactTypeColors[type]}>{contactTypeNames[type]}</Tag>,
      filters: [
        { text: 'Müşteri', value: 'customer' },
        { text: 'Tedarikçi', value: 'supplier' },
        { text: 'Her İkisi', value: 'both' },
      ],
      onFilter: (value: any, record: Contact) => record.contact_type === value,
    },
    {
      title: 'Telefon',
      dataIndex: 'phone',
      key: 'phone',
      width: 130,
    },
    {
      title: 'Durum',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>{isActive ? 'Aktif' : 'Pasif'}</Tag>
      ),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 280,
      render: (_: any, record: Contact) => (
        <Space>
          <Button type="link" size="small" icon={<FileTextOutlined />} onClick={() => handleViewReport(record)}>
            Rapor
          </Button>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleView(record)}>
            Detay
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            Düzenle
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id!)}
          >
            Sil
          </Button>
        </Space>
      ),
    },
  ];

  const handleViewTransactionDetail = async (transactionId: number) => {
    setTransactionLoading(true);
    setTransactionDetailVisible(true);

    try {
      const response = await api.get(`/transactions/${transactionId}`);
      setSelectedTransaction(response.data);
    } catch (error) {
      message.error('Fiş detayı yüklenirken hata oluştu');
      setTransactionDetailVisible(false);
    } finally {
      setTransactionLoading(false);
    }
  };

  const reportColumns: ColumnsType<CariReportItem> = [
    {
      title: 'Tarih',
      dataIndex: 'transaction_date',
      key: 'transaction_date',
      width: 100,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Evrak No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 120,
      render: (text: string, record: CariReportItem) => (
        <Button
          type="link"
          size="small"
          onClick={() => handleViewTransactionDetail(record.transaction_id)}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'Evrak Türü',
      dataIndex: 'document_type',
      key: 'document_type',
      width: 150,
      ellipsis: true,
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      width: 200,
    },
    {
      title: 'Dvz Cinsi',
      dataIndex: 'currency',
      key: 'currency',
      width: 80,
      align: 'center',
    },
    {
      title: 'Dvz Borç',
      dataIndex: 'currency_debit',
      key: 'currency_debit',
      align: 'right',
      width: 120,
      render: (val: number | null) => val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
    },
    {
      title: 'Dvz Alacak',
      dataIndex: 'currency_credit',
      key: 'currency_credit',
      align: 'right',
      width: 120,
      render: (val: number | null) => val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
    },
    {
      title: 'Dvz Bakiye',
      dataIndex: 'currency_balance',
      key: 'currency_balance',
      align: 'right',
      width: 120,
      render: (val: number | null) => val ? (
        <span
          style={{
            color: val > 0 ? '#cf1322' : val < 0 ? '#3f8600' : '#666',
            fontWeight: 'bold',
          }}
        >
          {val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      ) : '',
    },
    {
      title: 'B/A',
      key: 'currency_ba',
      width: 50,
      align: 'center',
      render: (_: any, record: CariReportItem) => {
        if (!record.currency_balance || record.currency_balance === 0) return '';
        return record.currency_balance > 0 ? 'B' : 'A';
      },
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      align: 'right',
      width: 130,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      align: 'right',
      width: 130,
      render: (val: number) => val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    },
    {
      title: 'Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      align: 'right',
      width: 130,
      fixed: 'right',
      render: (val: number) => (
        <span
          style={{
            color: val > 0 ? '#cf1322' : val < 0 ? '#3f8600' : '#666',
            fontWeight: 'bold',
          }}
        >
          {val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      title: 'B/A',
      key: 'ba',
      width: 50,
      align: 'center',
      fixed: 'right',
      render: (_: any, record: CariReportItem) => {
        if (record.balance === 0) return '';
        return record.balance > 0 ? 'B' : 'A';
      },
    },
    {
      title: 'Vade Tarihi',
      dataIndex: 'due_date',
      key: 'due_date',
      width: 100,
      fixed: 'right',
      render: (date: string | null) => date ? dayjs(date).format('DD.MM.YYYY') : '',
    },
  ];

  const stats = {
    total: filteredContacts.length,
    customers: filteredContacts.filter(c => c.contact_type === 'customer').length,
    suppliers: filteredContacts.filter(c => c.contact_type === 'supplier').length,
    both: filteredContacts.filter(c => c.contact_type === 'both').length,
    active: filteredContacts.filter(c => c.is_active).length,
    inactive: filteredContacts.filter(c => !c.is_active).length,
  };

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>Cariler</h1>
        <Space>
          <Upload
            accept=".xlsx,.xls"
            showUploadList={false}
            beforeUpload={handleBulkUpload}
          >
            <Button icon={<UploadOutlined />}>Toplu Yükleme (Excel)</Button>
          </Upload>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Yeni Cari
          </Button>
        </Space>
      </div>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Toplam Cari"
              value={stats.total}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Müşteriler"
              value={stats.customers}
              prefix={<ShoppingOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Tedarikçiler"
              value={stats.suppliers}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Her İkisi"
              value={stats.both}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }}>
        <Input
          placeholder="Cari ara (ünvan, kod, vergi no, telefon...)"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 400 }}
          allowClear
        />
      </Space>

      <Table
        columns={columns}
        dataSource={filteredContacts}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} cari`,
        }}
      />

      <Modal
        title={editingContact ? 'Cari Düzenle' : 'Yeni Cari'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={900}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Tabs defaultActiveKey="1">
            <TabPane tab="Temel Bilgiler" key="1">
              <Form.Item label="Cari Kodu" name="code">
                <Input placeholder="320.00001 (Otomatik)" disabled={!!editingContact} />
              </Form.Item>

              <Form.Item
                label="Ünvan"
                name="name"
                rules={[{ required: true, message: 'Ünvan gerekli!' }]}
              >
                <Input placeholder="Firma/Şahıs Ünvanı" />
              </Form.Item>

              <Form.Item label="Vergi No" name="tax_number">
                <Input placeholder="1234567890" />
              </Form.Item>

              <Form.Item label="Vergi Dairesi" name="tax_office">
                <Input placeholder="Kadıköy" />
              </Form.Item>

              <Form.Item label="Tür" name="contact_type" initialValue="supplier">
                <Select>
                  <Select.Option value="customer">Müşteri</Select.Option>
                  <Select.Option value="supplier">Tedarikçi</Select.Option>
                  <Select.Option value="both">Her İkisi</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="Durum" name="is_active" initialValue={true}>
                <Select>
                  <Select.Option value={true}>Aktif</Select.Option>
                  <Select.Option value={false}>Pasif</Select.Option>
                </Select>
              </Form.Item>
            </TabPane>

            <TabPane tab="İletişim" key="2">
              <Form.Item label="Telefon 1" name="phone">
                <Input placeholder="0555 123 4567" />
              </Form.Item>

              <Form.Item label="Telefon 2" name="phone2">
                <Input placeholder="0555 987 6543" />
              </Form.Item>

              <Form.Item label="E-posta" name="email">
                <Input type="email" placeholder="email@ornek.com" />
              </Form.Item>

              <Form.Item label="Website" name="website">
                <Input placeholder="https://www.ornek.com" />
              </Form.Item>

              <Form.Item label="Adres" name="address">
                <Input.TextArea rows={3} placeholder="Sokak, Mahalle, Bina No" />
              </Form.Item>

              <Space style={{ width: '100%' }}>
                <Form.Item label="İl" name="city" style={{ width: 200 }}>
                  <Input placeholder="İstanbul" />
                </Form.Item>

                <Form.Item label="İlçe" name="district" style={{ width: 200 }}>
                  <Input placeholder="Kadıköy" />
                </Form.Item>

                <Form.Item label="Posta Kodu" name="postal_code" style={{ width: 150 }}>
                  <Input placeholder="34000" />
                </Form.Item>
              </Space>

              <Form.Item label="Ülke" name="country" initialValue="TÜRKİYE">
                <Input />
              </Form.Item>
            </TabPane>

            <TabPane tab="Yetkili Kişi" key="3">
              <Form.Item label="Yetkili Adı" name="contact_person">
                <Input placeholder="Ad Soyad" />
              </Form.Item>

              <Form.Item label="Ünvan" name="contact_person_title">
                <Input placeholder="Mali Müşavir, Müdür vs." />
              </Form.Item>

              <Form.Item label="Telefon" name="contact_person_phone">
                <Input placeholder="0555 123 4567" />
              </Form.Item>

              <Form.Item label="E-posta" name="contact_person_email">
                <Input type="email" placeholder="yetkili@ornek.com" />
              </Form.Item>
            </TabPane>

            <TabPane tab="Finansal" key="4">
              <Form.Item label="Risk Limiti (TL)" name="risk_limit" initialValue={0}>
                <InputNumber style={{ width: '100%' }} min={0} placeholder="0.00" />
              </Form.Item>

              <Form.Item label="Vade Günü" name="payment_term_days" initialValue={0}>
                <InputNumber style={{ width: '100%' }} min={0} placeholder="0 = Peşin" />
              </Form.Item>

              <Form.Item label="Ödeme Şekli" name="payment_method" initialValue="Havale">
                <Select>
                  <Select.Option value="Nakit">Nakit</Select.Option>
                  <Select.Option value="Çek">Çek</Select.Option>
                  <Select.Option value="Havale">Havale/EFT</Select.Option>
                  <Select.Option value="Kredi Kartı">Kredi Kartı</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="İskonto Oranı (%)" name="discount_rate" initialValue={0}>
                <InputNumber style={{ width: '100%' }} min={0} max={100} placeholder="0.00" />
              </Form.Item>

              <Form.Item label="Sektör" name="sector">
                <Input placeholder="İnşaat, Gıda vs." />
              </Form.Item>

              <Form.Item label="Bölge/Grup" name="region">
                <Input placeholder="İstanbul Anadolu" />
              </Form.Item>

              <Form.Item label="Müşteri Grubu" name="customer_group">
                <Input placeholder="VIP, Standart vs." />
              </Form.Item>
            </TabPane>

            <TabPane tab="Banka" key="5">
              <Form.Item label="Banka Adı" name="bank_name">
                <Input placeholder="Garanti BBVA" />
              </Form.Item>

              <Form.Item label="Şube" name="bank_branch">
                <Input placeholder="Kadıköy Şubesi" />
              </Form.Item>

              <Form.Item label="Hesap No" name="bank_account_no">
                <Input placeholder="1234567890" />
              </Form.Item>

              <Form.Item label="IBAN" name="iban">
                <Input placeholder="TR00 0000 0000 0000 0000 0000 00" maxLength={34} />
              </Form.Item>

              <Form.Item label="SWIFT" name="swift">
                <Input placeholder="TGBATRIS" maxLength={11} />
              </Form.Item>
            </TabPane>

            <TabPane tab="Notlar" key="6">
              <Form.Item label="Genel Notlar" name="notes">
                <Input.TextArea rows={4} placeholder="Genel notlar ve açıklamalar" />
              </Form.Item>

              <Form.Item label="Özel Notlar (Gizli)" name="private_notes">
                <Input.TextArea rows={4} placeholder="Sadece yetkili kişilerin görebileceği notlar" />
              </Form.Item>
            </TabPane>
          </Tabs>

          <Form.Item style={{ marginTop: 16, marginBottom: 0 }}>
            <Space>
              <Button type="primary" htmlType="submit">
                Kaydet
              </Button>
              <Button onClick={() => setModalVisible(false)}>İptal</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Drawer
        title="Cari Detayları"
        placement="right"
        width={600}
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
      >
        {viewingContact && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="Cari Kodu">{viewingContact.code || '-'}</Descriptions.Item>
            <Descriptions.Item label="Ünvan">{viewingContact.name}</Descriptions.Item>
            <Descriptions.Item label="Vergi No">{viewingContact.tax_number || '-'}</Descriptions.Item>
            <Descriptions.Item label="Vergi Dairesi">{viewingContact.tax_office || '-'}</Descriptions.Item>
            <Descriptions.Item label="Tür">
              <Tag color={contactTypeColors[viewingContact.contact_type || 'both']}>
                {contactTypeNames[viewingContact.contact_type || 'both']}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Telefon">{viewingContact.phone || '-'}</Descriptions.Item>
            <Descriptions.Item label="Telefon 2">{viewingContact.phone2 || '-'}</Descriptions.Item>
            <Descriptions.Item label="E-posta">{viewingContact.email || '-'}</Descriptions.Item>
            <Descriptions.Item label="Website">{viewingContact.website || '-'}</Descriptions.Item>
            <Descriptions.Item label="Adres">{viewingContact.address || '-'}</Descriptions.Item>
            <Descriptions.Item label="İl/İlçe">
              {viewingContact.city || '-'} / {viewingContact.district || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="Yetkili Kişi">{viewingContact.contact_person || '-'}</Descriptions.Item>
            <Descriptions.Item label="Yetkili Telefon">{viewingContact.contact_person_phone || '-'}</Descriptions.Item>
            <Descriptions.Item label="Risk Limiti">{viewingContact.risk_limit || 0} TL</Descriptions.Item>
            <Descriptions.Item label="Vade Günü">{viewingContact.payment_term_days || 0} gün</Descriptions.Item>
            <Descriptions.Item label="Ödeme Şekli">{viewingContact.payment_method || '-'}</Descriptions.Item>
            <Descriptions.Item label="IBAN">{viewingContact.iban || '-'}</Descriptions.Item>
            <Descriptions.Item label="Güncel Bakiye">
              <strong>{viewingContact.current_balance || 0} TL</strong>
            </Descriptions.Item>
            <Descriptions.Item label="Notlar">{viewingContact.notes || '-'}</Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>

      {/* Toplu Yükleme Progress Modal */}
      <Modal
        title="Toplu Cari Yükleniyor"
        open={uploadModalVisible}
        footer={null}
        closable={false}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Progress type="circle" percent={uploadProgress} />
          <p style={{ marginTop: 16 }}>
            {uploadProgress < 100 ? 'Cariler yükleniyor...' : 'Tamamlandı!'}
          </p>
        </div>
      </Modal>

      {/* Cari Raporu Modal */}
      <Modal
        title={null}
        open={reportModalVisible}
        onCancel={() => setReportModalVisible(false)}
        footer={null}
        width={1600}
        bodyStyle={{ padding: 0 }}
      >
        {reportLoading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Progress type="circle" percent={50} status="active" />
            <p style={{ marginTop: 16 }}>Rapor yükleniyor...</p>
          </div>
        ) : reportData ? (
          <div style={{ padding: '24px' }}>
            {/* Zirve Formatı Başlık */}
            <div style={{
              borderBottom: '2px solid #d9d9d9',
              paddingBottom: 16,
              marginBottom: 16
            }}>
              <Row justify="space-between" align="top">
                <Col>
                  <h2 style={{ margin: 0, fontSize: 20, fontWeight: 'bold', color: '#c41d7f' }}>
                    Cari Hesap Ekstresi
                  </h2>
                  <div style={{ marginTop: 8 }}>
                    <div><strong>Firma:</strong> ONUR GRUP PLASTİK DIŞ TİCARET LİMİTED ŞİRKETİ</div>
                  </div>
                </Col>
                <Col style={{ textAlign: 'right' }}>
                  <div><strong>Sayfa No:</strong> 1/1</div>
                  <div><strong>Rapor Tarihi:</strong> {dayjs().format('DD.MM.YYYY - HH:mm')}</div>
                </Col>
              </Row>
              <div style={{ marginTop: 12, padding: '8px 0', borderTop: '1px solid #f0f0f0', borderBottom: '1px solid #f0f0f0' }}>
                <Row>
                  <Col span={12}>
                    <strong>Cari Kodu:</strong> {reportData.contact_code || '-'}
                  </Col>
                  <Col span={12}>
                    <strong>Cari Adı:</strong> {reportData.contact_name}
                  </Col>
                </Row>
              </div>
            </div>

            {(() => {
              // Raporu 120 ve 320'ye ayır
              const items120 = reportData.items.filter(item => item.account_code.startsWith('120'));
              const items320 = reportData.items.filter(item => item.account_code.startsWith('320'));
              
              // Her grubun toplamlarını hesapla
              const calc120 = items120.reduce((acc, item) => ({
                debit: acc.debit + item.debit,
                credit: acc.credit + item.credit,
              }), { debit: 0, credit: 0 });
              
              const calc320 = items320.reduce((acc, item) => ({
                debit: acc.debit + item.debit,
                credit: acc.credit + item.credit,
              }), { debit: 0, credit: 0 });
              
              const closing120 = calc120.debit - calc120.credit;
              const closing320 = calc320.debit - calc320.credit;
              
              // Hem 120 hem 320 varsa 3 sekme göster
              const has120 = items120.length > 0;
              const has320 = items320.length > 0;
              const showTabs = has120 && has320;

              return showTabs ? (
                <Tabs defaultActiveKey="all">
                  <TabPane tab="Birleşik (120 + 320)" key="all">
                    {/* Özet Kartlar - Birleşik */}
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                      <Col span={6}>
                        <Card size="small">
                          <Statistic
                            title="Açılış Bakiyesi"
                            value={reportData.opening_balance}
                            precision={2}
                            suffix={reportData.opening_balance > 0 ? 'B' : reportData.opening_balance < 0 ? 'A' : ''}
                            valueStyle={{
                              color:
                                reportData.opening_balance > 0
                                  ? '#cf1322'
                                  : reportData.opening_balance < 0
                                  ? '#3f8600'
                                  : '#666',
                            }}
                          />
                        </Card>
                      </Col>
                      <Col span={6}>
                        <Card size="small">
                          <Statistic
                            title="Toplam Borç"
                            value={reportData.total_debit}
                            precision={2}
                            suffix="B"
                            valueStyle={{ color: '#cf1322' }}
                          />
                        </Card>
                      </Col>
                      <Col span={6}>
                        <Card size="small">
                          <Statistic
                            title="Toplam Alacak"
                            value={reportData.total_credit}
                            precision={2}
                            suffix="A"
                            valueStyle={{ color: '#3f8600' }}
                          />
                        </Card>
                      </Col>
                      <Col span={6}>
                        <Card size="small">
                          <Statistic
                            title="Kapanış Bakiyesi"
                            value={reportData.closing_balance}
                            precision={2}
                            suffix={reportData.closing_balance > 0 ? 'B' : reportData.closing_balance < 0 ? 'A' : ''}
                            valueStyle={{
                              color:
                                reportData.closing_balance > 0
                                  ? '#cf1322'
                                  : reportData.closing_balance < 0
                                  ? '#3f8600'
                                  : '#666',
                              fontSize: 24,
                              fontWeight: 'bold',
                            }}
                          />
                        </Card>
                      </Col>
                    </Row>

                    {/* Tablo - Birleşik */}
                    <Table
                      columns={reportColumns}
                      dataSource={reportData.items}
                      rowKey={(record) => `${record.transaction_id}_${record.account_code}`}
                      pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Toplam ${total} kayıt` }}
                      scroll={{ x: 1400 }}
                      size="small"
                      bordered
                      summary={() => (
                        <Table.Summary fixed>
                          <Table.Summary.Row style={{ backgroundColor: '#fafafa', fontWeight: 'bold' }}>
                            <Table.Summary.Cell index={0} colSpan={5} align="right">
                              Toplam Tutarlar
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={5} align="right">
                              {reportData.total_debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={6} align="right">
                              {reportData.total_credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={7} colSpan={2}></Table.Summary.Cell>
                            <Table.Summary.Cell index={9} align="right">
                              {reportData.total_debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={10} align="right">
                              {reportData.total_credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={11} align="right" style={{
                              color: reportData.closing_balance > 0 ? '#cf1322' : reportData.closing_balance < 0 ? '#3f8600' : '#666'
                            }}>
                              {reportData.closing_balance.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={12} align="center">
                              {reportData.closing_balance > 0 ? 'B' : reportData.closing_balance < 0 ? 'A' : ''}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={13}></Table.Summary.Cell>
                          </Table.Summary.Row>
                        </Table.Summary>
                      )}
                    />
                  </TabPane>

                  <TabPane tab="320 - Satıcılar" key="320">
                    {/* Özet Kartlar - 320 */}
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                      <Col span={8}>
                        <Card size="small">
                          <Statistic
                            title="Toplam Borç (320)"
                            value={calc320.debit}
                            precision={2}
                            suffix="B"
                            valueStyle={{ color: '#cf1322' }}
                          />
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small">
                          <Statistic
                            title="Toplam Alacak (320)"
                            value={calc320.credit}
                            precision={2}
                            suffix="A"
                            valueStyle={{ color: '#3f8600' }}
                          />
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small">
                          <Statistic
                            title="Bakiye (320)"
                            value={closing320}
                            precision={2}
                            suffix={closing320 > 0 ? 'B' : closing320 < 0 ? 'A' : ''}
                            valueStyle={{
                              color: closing320 > 0 ? '#cf1322' : closing320 < 0 ? '#3f8600' : '#666',
                              fontSize: 24,
                              fontWeight: 'bold',
                            }}
                          />
                        </Card>
                      </Col>
                    </Row>

                    {/* Tablo - 320 */}
                    <Table
                      columns={reportColumns}
                      dataSource={items320}
                      rowKey={(record) => `${record.transaction_id}_${record.account_code}`}
                      pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Toplam ${total} kayıt` }}
                      scroll={{ x: 1400 }}
                      size="small"
                      bordered
                      summary={() => (
                        <Table.Summary fixed>
                          <Table.Summary.Row style={{ backgroundColor: '#fafafa', fontWeight: 'bold' }}>
                            <Table.Summary.Cell index={0} colSpan={5} align="right">
                              Toplam (320)
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={5} align="right">
                              {calc320.debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={6} align="right">
                              {calc320.credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={7} colSpan={2}></Table.Summary.Cell>
                            <Table.Summary.Cell index={9} align="right">
                              {calc320.debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={10} align="right">
                              {calc320.credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={11} align="right" style={{
                              color: closing320 > 0 ? '#cf1322' : closing320 < 0 ? '#3f8600' : '#666'
                            }}>
                              {closing320.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={12} align="center">
                              {closing320 > 0 ? 'B' : closing320 < 0 ? 'A' : ''}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={13}></Table.Summary.Cell>
                          </Table.Summary.Row>
                        </Table.Summary>
                      )}
                    />
                  </TabPane>

                  <TabPane tab="120 - Müşteriler" key="120">
                    {/* Özet Kartlar - 120 */}
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                      <Col span={8}>
                        <Card size="small">
                          <Statistic
                            title="Toplam Borç (120)"
                            value={calc120.debit}
                            precision={2}
                            suffix="B"
                            valueStyle={{ color: '#cf1322' }}
                          />
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small">
                          <Statistic
                            title="Toplam Alacak (120)"
                            value={calc120.credit}
                            precision={2}
                            suffix="A"
                            valueStyle={{ color: '#3f8600' }}
                          />
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small">
                          <Statistic
                            title="Bakiye (120)"
                            value={closing120}
                            precision={2}
                            suffix={closing120 > 0 ? 'B' : closing120 < 0 ? 'A' : ''}
                            valueStyle={{
                              color: closing120 > 0 ? '#cf1322' : closing120 < 0 ? '#3f8600' : '#666',
                              fontSize: 24,
                              fontWeight: 'bold',
                            }}
                          />
                        </Card>
                      </Col>
                    </Row>

                    {/* Tablo - 120 */}
                    <Table
                      columns={reportColumns}
                      dataSource={items120}
                      rowKey={(record) => `${record.transaction_id}_${record.account_code}`}
                      pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Toplam ${total} kayıt` }}
                      scroll={{ x: 1400 }}
                      size="small"
                      bordered
                      summary={() => (
                        <Table.Summary fixed>
                          <Table.Summary.Row style={{ backgroundColor: '#fafafa', fontWeight: 'bold' }}>
                            <Table.Summary.Cell index={0} colSpan={5} align="right">
                              Toplam (120)
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={5} align="right">
                              {calc120.debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={6} align="right">
                              {calc120.credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={7} colSpan={2}></Table.Summary.Cell>
                            <Table.Summary.Cell index={9} align="right">
                              {calc120.debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={10} align="right">
                              {calc120.credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={11} align="right" style={{
                              color: closing120 > 0 ? '#cf1322' : closing120 < 0 ? '#3f8600' : '#666'
                            }}>
                              {closing120.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={12} align="center">
                              {closing120 > 0 ? 'B' : closing120 < 0 ? 'A' : ''}
                            </Table.Summary.Cell>
                            <Table.Summary.Cell index={13}></Table.Summary.Cell>
                          </Table.Summary.Row>
                        </Table.Summary>
                      )}
                    />
                  </TabPane>
                </Tabs>
              ) : (
                <>
                  {/* Özet Kartlar - Tek hesap */}
                  <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={6}>
                      <Card size="small">
                        <Statistic
                          title="Açılış Bakiyesi"
                          value={reportData.opening_balance}
                          precision={2}
                          suffix={reportData.opening_balance > 0 ? 'B' : reportData.opening_balance < 0 ? 'A' : ''}
                          valueStyle={{
                            color:
                              reportData.opening_balance > 0
                                ? '#cf1322'
                                : reportData.opening_balance < 0
                                ? '#3f8600'
                                : '#666',
                          }}
                        />
                      </Card>
                    </Col>
                    <Col span={6}>
                      <Card size="small">
                        <Statistic
                          title="Toplam Borç"
                          value={reportData.total_debit}
                          precision={2}
                          suffix="B"
                          valueStyle={{ color: '#cf1322' }}
                        />
                      </Card>
                    </Col>
                    <Col span={6}>
                      <Card size="small">
                        <Statistic
                          title="Toplam Alacak"
                          value={reportData.total_credit}
                          precision={2}
                          suffix="A"
                          valueStyle={{ color: '#3f8600' }}
                        />
                      </Card>
                    </Col>
                    <Col span={6}>
                      <Card size="small">
                        <Statistic
                          title="Kapanış Bakiyesi"
                          value={reportData.closing_balance}
                          precision={2}
                          suffix={reportData.closing_balance > 0 ? 'B' : reportData.closing_balance < 0 ? 'A' : ''}
                          valueStyle={{
                            color:
                              reportData.closing_balance > 0
                                ? '#cf1322'
                                : reportData.closing_balance < 0
                                ? '#3f8600'
                                : '#666',
                            fontSize: 24,
                            fontWeight: 'bold',
                          }}
                        />
                      </Card>
                    </Col>
                  </Row>

                  {/* Tablo - Tek hesap */}
                  <Table
                    columns={reportColumns}
                    dataSource={reportData.items}
                    rowKey={(record) => `${record.transaction_id}_${record.account_code}`}
                    pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Toplam ${total} kayıt` }}
                    scroll={{ x: 1400 }}
                    size="small"
                    bordered
                    summary={() => (
                      <Table.Summary fixed>
                        <Table.Summary.Row style={{ backgroundColor: '#fafafa', fontWeight: 'bold' }}>
                          <Table.Summary.Cell index={0} colSpan={5} align="right">
                            Toplam Tutarlar
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={5} align="right">
                            {reportData.total_debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={6} align="right">
                            {reportData.total_credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={7} colSpan={2}></Table.Summary.Cell>
                          <Table.Summary.Cell index={9} align="right">
                            {reportData.total_debit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={10} align="right">
                            {reportData.total_credit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={11} align="right" style={{
                            color: reportData.closing_balance > 0 ? '#cf1322' : reportData.closing_balance < 0 ? '#3f8600' : '#666'
                          }}>
                            {reportData.closing_balance.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={12} align="center">
                            {reportData.closing_balance > 0 ? 'B' : reportData.closing_balance < 0 ? 'A' : ''}
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={13}></Table.Summary.Cell>
                        </Table.Summary.Row>
                      </Table.Summary>
                    )}
                  />
                </>
              );
            })()}
          </div>
        ) : null}
      </Modal>

      {/* Fiş Detay Modal */}
      <Modal
        title={
          <Space>
            <FileTextOutlined />
            <span>
              Fiş Detayı
              {selectedTransaction && ` - ${selectedTransaction.transaction_number}`}
            </span>
          </Space>
        }
        open={transactionDetailVisible}
        onCancel={() => setTransactionDetailVisible(false)}
        footer={null}
        width={800}
      >
        {transactionLoading ? (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <Progress type="circle" percent={50} status="active" />
          </div>
        ) : selectedTransaction ? (
          <>
            <Descriptions bordered size="small" column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Fiş No">
                {selectedTransaction.transaction_number}
              </Descriptions.Item>
              <Descriptions.Item label="Tarih">
                {dayjs(selectedTransaction.transaction_date).format('DD.MM.YYYY')}
              </Descriptions.Item>
              <Descriptions.Item label="Açıklama" span={2}>
                {selectedTransaction.description || '-'}
              </Descriptions.Item>
            </Descriptions>
            <Table
              columns={[
                {
                  title: 'Hesap Kodu',
                  dataIndex: 'account_code',
                  key: 'account_code',
                  width: 120,
                },
                {
                  title: 'Hesap Adı',
                  dataIndex: 'account_name',
                  key: 'account_name',
                },
                {
                  title: 'Borç',
                  dataIndex: 'debit',
                  key: 'debit',
                  align: 'right',
                  width: 150,
                  render: (val: number) =>
                    val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
                },
                {
                  title: 'Alacak',
                  dataIndex: 'credit',
                  key: 'credit',
                  align: 'right',
                  width: 150,
                  render: (val: number) =>
                    val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
                },
              ]}
              dataSource={selectedTransaction.lines}
              rowKey={(record) => record.account_code}
              pagination={false}
              size="small"
            />
          </>
        ) : null}
      </Modal>
    </div>
  );
};

export default ContactsPage;
