import React, { useState, useMemo } from 'react';
import { Table, Tag, Button, Space, Modal, Form, Input, Select, message, Tabs, InputNumber, Descriptions, Drawer, Card, Row, Col, Statistic, Upload, Progress } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, TeamOutlined, ShopOutlined, UploadOutlined, FileTextOutlined, SearchOutlined, MailOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import axios from 'axios';
import dayjs from 'dayjs';
import api from '@/services/api';
import { CariReportModal } from '@/domains/reporting/reports/components/CariReportModal';

// 🆕 V2 Domain imports
import { useContactsList, useCreateContact, useUpdateContact, useDeleteContact } from '@/domains/partners/contacts/hooks/useContacts';
import type { Contact, ContactCreateRequest } from '@/domains/partners/contacts/types/contact.types';

const API_BASE = import.meta.env.VITE_API_URL || '';

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
  const { data: contactsData, isLoading: loading, refetch: refetchContacts } = useContactsList();
  const contacts = contactsData?.items || [];
  const createContactMutation = useCreateContact();
  const updateContactMutation = useUpdateContact();
  const deleteContactMutation = useDeleteContact();
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

  // Cari raporu state'leri - Sadeleştirildi
  const [reportModalVisible, setReportModalVisible] = useState(false);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  
  // Fiş detay state'leri
  const [transactionDetailVisible, setTransactionDetailVisible] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<TransactionDetail | null>(null);
  const [transactionLoading, setTransactionLoading] = useState(false);
  const [emailModalVisible, setEmailModalVisible] = useState(false);
  const [emailForm] = Form.useForm();

  // Arama filtresi - useMemo ile optimize edildi
  const filtered = useMemo(() => {
    if (!searchText.trim()) {
      return contacts;
    }

    const search = searchText.toLowerCase();
    return contacts.filter(
      (c) =>
        c.name.toLowerCase().includes(search) ||
        c.code?.toLowerCase().includes(search) ||
        c.tax_number?.toLowerCase().includes(search) ||
        c.tax_office?.toLowerCase().includes(search) ||
        c.phone?.toLowerCase().includes(search)
    );
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
      const response = await axios.post(`${API_BASE}/api/v2/partners/contacts/bulk-import`, formData, {
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

  const handleViewReport = (contact: Contact) => {
    setSelectedContact(contact);
    setReportModalVisible(true);
  };

  const handleDownloadExcel = async () => {
    if (!reportData || !selectedContact) return;
    
    try {
      message.loading({ content: 'Excel hazırlanıyor...', key: 'excel' });
      
      const response = await api.get('/reporting/reports/cari/excel', {
        params: {
          start_date: reportStartDate.format('YYYY-MM-DD'),
          end_date: reportEndDate.format('YYYY-MM-DD'),
          contact_id: selectedContact.id,
          account_filter: activeReportTab === 'all' ? undefined : [activeReportTab],
        },
        responseType: 'blob',
      });
      
      // Dosyayı indir
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `cari_ekstre_${selectedContact.code}_${reportStartDate.format('YYYYMMDD')}_${reportEndDate.format('YYYYMMDD')}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success({ content: 'Excel indirildi', key: 'excel' });
    } catch (error) {
      message.error({ content: 'Excel indirilemedi', key: 'excel' });
    }
  };

  const handleDownloadPDF = async () => {
    if (!reportData || !selectedContact) return;
    
    try {
      message.loading({ content: 'PDF hazırlanıyor...', key: 'pdf' });
      
      const response = await api.get('/reporting/reports/cari/pdf', {
        params: {
          start_date: reportStartDate.format('YYYY-MM-DD'),
          end_date: reportEndDate.format('YYYY-MM-DD'),
          contact_id: selectedContact.id,
          account_filter: activeReportTab === 'all' ? undefined : [activeReportTab],
        },
        responseType: 'blob',
      });
      
      // Dosyayı indir
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `cari_ekstre_${selectedContact.code}_${reportStartDate.format('YYYYMMDD')}_${reportEndDate.format('YYYYMMDD')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success({ content: 'PDF indirildi', key: 'pdf' });
    } catch (error) {
      message.error({ content: 'PDF indirilemedi', key: 'pdf' });
    }
  };

  const handleSendEmail = () => {
    if (!selectedContact) return;
    
    emailForm.setFieldsValue({
      recipient_email: selectedContact.email || '',
      cc_recipients: '',  // Kullanıcı dolduracak veya boş bırakacak
      report_type: 'PDF',
      account_filter: null,  // Tüm hesaplar
      subject: `Cari Hesap Ekstresi - ${selectedContact.name}`,
      message: `Merhaba,\n\nCari hesap ekstreniz ektedir.\n\nSaygılarımızla`,
    });
    setEmailModalVisible(true);
  };

  const handleEmailSubmit = async (values: any) => {
    if (!selectedContact) return;
    
    try {
      message.loading({ content: 'E-posta gönderiliyor...', key: 'email' });
      
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE}/api/v2/email/send-report`,
        {
          recipient_email: values.recipient_email,
          cc_recipients: values.cc_recipients || null,
          contact_id: selectedContact.id,
          start_date: reportStartDate.format('YYYY-MM-DD'),
          end_date: reportEndDate.format('YYYY-MM-DD'),
          report_type: values.report_type,
          account_filter: values.account_filter,
          subject: values.subject,
          message: values.message,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      message.success({ content: 'E-posta başarıyla gönderildi', key: 'email' });
      setEmailModalVisible(false);
      emailForm.resetFields();
    } catch (error: any) {
      console.error('E-posta gönderme hatası:', error);
      const errorMsg = error.response?.data?.detail || 'E-posta gönderilemedi';
      message.error({ content: errorMsg, key: 'email' });
    }
  };

  const contactTypeColors: Record<string, string> = {
    'Tedarikçi': 'blue',
    'Taşeron': 'orange',
    'Ana Firma': 'green',
    'İş Ortağı': 'purple',
  };

  const contactTypeNames: Record<string, string> = {
    'Tedarikçi': 'Tedarikçi',
    'Taşeron': 'Taşeron',
    'Ana Firma': 'Ana Firma',
    'İş Ortağı': 'İş Ortağı',
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
        { text: 'Tedarikçi', value: 'Tedarikçi' },
        { text: 'Taşeron', value: 'Taşeron' },
        { text: 'Ana Firma', value: 'Ana Firma' },
        { text: 'İş Ortağı', value: 'İş Ortağı' },
      ],
      onFilter: (value: any, record: Contact) => record.contact_type === value,
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
      width: 140,
      render: (_: any, record: Contact) => (
        <Select
          style={{ width: 130 }}
          placeholder="İşlemler"
          styles={{ popup: { root: { minWidth: 180 } } }}
          onSelect={(value) => {
            if (value === 'report') {
              handleViewReport(record);
            } else if (value === 'detail') {
              handleView(record);
            } else if (value === 'edit') {
              handleEdit(record);
            } else if (value === 'delete') {
              Modal.confirm({
                title: 'Silmek istediğinize emin misiniz?',
                content: `${record.name} silinecek.`,
                onOk: () => handleDelete(record.id!),
                okText: 'Evet',
                cancelText: 'Hayır',
              });
            }
          }}
        >
          <Select.Option value="report">
            <FileTextOutlined style={{ marginRight: 6, color: '#1890ff' }} /> <span>Rapor</span>
          </Select.Option>
          <Select.Option value="detail">
            <EyeOutlined style={{ marginRight: 6, color: '#52c41a' }} /> <span>Detay</span>
          </Select.Option>
          <Select.Option value="edit">
            <EditOutlined style={{ marginRight: 6, color: '#fa8c16' }} /> <span>Düzenle</span>
          </Select.Option>
          <Select.Option value="delete">
            <DeleteOutlined style={{ marginRight: 6, color: '#ff4d4f' }} /> <span>Sil</span>
          </Select.Option>
        </Select>
      ),
    },
  ];

  const handleViewTransactionDetail = async (transactionId: number) => {
    setTransactionLoading(true);
    setTransactionDetailVisible(true);

    try {
      const response = await api.get(`/accounting/transactions/${transactionId}`);
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
      width: 90,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Fiş No',
      dataIndex: 'transaction_number',
      key: 'transaction_number',
      width: 100,
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
      width: 120,
      ellipsis: true,
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      width: 250,
    },
    {
      title: 'Borç',
      dataIndex: 'debit',
      key: 'debit',
      align: 'right',
      width: 110,
      render: (val: any) => Number(val || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    },
    {
      title: 'Alacak',
      dataIndex: 'credit',
      key: 'credit',
      align: 'right',
      width: 110,
      render: (val: any) => Number(val || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    },
    {
      title: 'Yürüyen Bakiye',
      dataIndex: 'balance',
      key: 'balance',
      align: 'right',
      width: 120,
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
  ];

  const stats = {
    total: Array.isArray(filtered) ? filtered.length : 0,
    suppliers: Array.isArray(filtered) ? filtered.filter(c => c.contact_type === 'Tedarikçi').length : 0,
    taseron: Array.isArray(filtered) ? filtered.filter(c => c.contact_type === 'Taşeron').length : 0,
    anaFirma: Array.isArray(filtered) ? filtered.filter(c => c.contact_type === 'Ana Firma').length : 0,
    isOrtagi: Array.isArray(filtered) ? filtered.filter(c => c.contact_type === 'İş Ortağı').length : 0,
    active: Array.isArray(filtered) ? filtered.filter(c => c.is_active).length : 0,
    inactive: Array.isArray(filtered) ? filtered.filter(c => !c.is_active).length : 0,
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
              title="Tedarikçiler"
              value={stats.suppliers}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Taşeronlar"
              value={stats.taseron}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Ana Firmalar"
              value={stats.anaFirma}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="İş Ortakları"
              value={stats.isOrtagi}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Aktif"
              value={stats.active}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Pasif"
              value={stats.inactive}
              valueStyle={{ color: '#d9d9d9' }}
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
        dataSource={Array.isArray(filtered) ? filtered : []}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} cari`,
        }}
        className="contacts-table"
      />

      <Modal
        title={editingContact ? 'Cari Düzenle' : 'Yeni Cari'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={900}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Tabs defaultActiveKey="1" items={[
            {
              key: '1',
              label: 'Temel Bilgiler',
              children: (<>

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

              <Form.Item label="Tür" name="contact_type" initialValue="Tedarikçi">
                <Select>
                  <Select.Option value="Tedarikçi">Tedarikçi</Select.Option>
                  <Select.Option value="Taşeron">Taşeron</Select.Option>
                  <Select.Option value="Ana Firma">Ana Firma</Select.Option>
                  <Select.Option value="İş Ortağı">İş Ortağı</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="Durum" name="is_active" initialValue={true}>
                <Select>
                  <Select.Option value={true}>Aktif</Select.Option>
                  <Select.Option value={false}>Pasif</Select.Option>
                </Select>
              </Form.Item>
              </>)
            },
            {
              key: '2',
              label: 'İletişim',
              children: (<>

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
              </>)
            },
            {
              key: '3',
              label: 'Yetkili Kişi',
              children: (<>

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
              </>)
            },
            {
              key: '4',
              label: 'Finansal',
              children: (<>

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
              </>)
            },
            {
              key: '5',
              label: 'Banka',
              children: (<>

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
              </>)
            },
            {
              key: '6',
              label: 'Notlar',
              children: (<>

              <Form.Item label="Genel Notlar" name="notes">
                <Input.TextArea rows={4} placeholder="Genel notlar ve açıklamalar" />
              </Form.Item>

              <Form.Item label="Özel Notlar (Gizli)" name="private_notes">
                <Input.TextArea rows={4} placeholder="Sadece yetkili kişilerin görebileceği notlar" />
              </Form.Item>
              </>)
            }
          ]} />

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
            <Descriptions.Item label="Cari ID">{viewingContact.id}</Descriptions.Item>
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
                  title: 'Açıklama',
                  dataIndex: 'description',
                  key: 'description',
                  render: (text: string) => text || '-',
                },
                {
                  title: 'Borç',
                  dataIndex: 'debit',
                  key: 'debit',
                  align: 'right',
                  width: 130,
                  render: (val: number) =>
                    val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0,00',
                },
                {
                  title: 'Alacak',
                  dataIndex: 'credit',
                  key: 'credit',
                  align: 'right',
                  width: 130,
                  render: (val: number) =>
                    val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0,00',
                },
              ]}
              dataSource={selectedTransaction.lines}
              rowKey={(record) => record.id}
              pagination={false}
              size="small"
            />
          </>
        ) : null}
      </Modal>

      {/* E-posta Gönder Modal */}
      <Modal
        title="Cari Raporu E-posta ile Gönder"
        open={emailModalVisible}
        onCancel={() => setEmailModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={emailForm}
          layout="vertical"
          onFinish={handleEmailSubmit}
        >
          <Form.Item
            label="Alıcı E-posta"
            name="recipient_email"
            rules={[
              { required: true, message: 'E-posta adresi gerekli' },
              { type: 'email', message: 'Geçerli bir e-posta adresi girin' },
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="ornek@firma.com" />
          </Form.Item>

          <Form.Item
            label="CC (Kopya)"
            name="cc_recipients"
            tooltip="Birden fazla e-posta için virgülle ayırın (muhasebe@firma.com, yonetim@firma.com)"
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="muhasebe@firma.com, yonetim@firma.com" 
            />
          </Form.Item>

          <Form.Item
            label="Rapor Türü"
            name="report_type"
            rules={[{ required: true, message: 'Rapor türü seçin' }]}
          >
            <Select>
              <Select.Option value="PDF">PDF</Select.Option>
              <Select.Option value="Excel">Excel</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Hesap Filtresi"
            name="account_filter"
            tooltip="Birden fazla seçim yapabilirsiniz. Boş bırakırsanız tüm hesaplar dahil edilir."
          >
            <Select 
              mode="multiple"
              placeholder="Boş = Tüm hesaplar"
              allowClear
            >
              <Select.Option value="all">Birleştirilmiş Hesaplar (120+320 Tümü)</Select.Option>
              <Select.Option value="120">Müşteri Hesapları (120)</Select.Option>
              <Select.Option value="320">Tedarikçi Hesapları (320)</Select.Option>
              <Select.Option value="collateral">Teminat Mektupları</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Konu"
            name="subject"
            rules={[{ required: true, message: 'Konu gerekli' }]}
          >
            <Input placeholder="E-posta konusu" />
          </Form.Item>

          <Form.Item
            label="Mesaj"
            name="message"
          >
            <Input.TextArea rows={6} placeholder="E-posta mesajı (opsiyonel)" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space style={{ float: 'right' }}>
              <Button onClick={() => setEmailModalVisible(false)}>İptal</Button>
              <Button type="primary" htmlType="submit" icon={<MailOutlined />}>
                Gönder
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <style>{`
        .contacts-table .ant-table-thead > tr > th {
          font-size: 16px !important;
          font-weight: 600;
        }
        .contacts-table .ant-table-tbody > tr > td {
          font-size: 16px !important;
        }
        .contacts-table .ant-select {
          font-size: 14px !important;
        }
        .contacts-table .ant-tag {
          font-size: 13px !important;
        }
      `}</style>

      {/* Cari Rapor Modal - Ayrı Component */}
      <CariReportModal 
        visible={reportModalVisible}
        onClose={() => {
          setReportModalVisible(false);
          setSelectedContact(null);
        }}
        contact={selectedContact}
      />
    </div>
  );
};

export default ContactsPage;
