import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, Modal, Form, Input, Select, message, Popconfirm } from 'antd';
import { PlusOutlined, StopOutlined, CheckCircleOutlined, DeleteOutlined } from '@ant-design/icons';

// 🆕 V2 Domain imports
import { useAccounts, useCreateAccount, useUpdateAccount, useDeleteAccount } from '@/domains/accounting/accounts/hooks/useAccounts';
import type { Account } from '@/domains/accounting/accounts/types/account.types';
import { contactService } from '@/services/muhasebe.service';
import { usePersonnel } from '@/domains/personnel/hooks/usePersonnel';

const AccountsPage: React.FC = () => {
  // 🆕 V2 React Query hooks
  const { data: accounts = [], isLoading: loading } = useAccounts();
  const createAccount = useCreateAccount();
  const updateAccount = useUpdateAccount();
  const deleteAccount = useDeleteAccount();
  const { data: personnelData } = usePersonnel({ limit: 10000 });
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [contacts, setContacts] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const contactsRes = await contactService.getAll({ limit: 10000 });
        setContacts(Array.isArray(contactsRes.data) ? contactsRes.data : contactsRes.data.items || []);
      } catch (error) {
        console.error('Veri yüklenemedi:', error);
      }
    };
    loadData();
  }, []);

  const personnel = personnelData?.items || [];

  const accountTypeColors = {
    asset: 'blue',
    liability: 'red',
    revenue: 'green',
    expense: 'orange',
  };

  const accountTypeNames = {
    asset: 'Aktif',
    liability: 'Pasif',
    revenue: 'Gelir',
    expense: 'Gider',
  };

  const columns = [
    {
      title: 'Kod',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      sorter: (a: Account, b: Account) => a.code.localeCompare(b.code),
    },
    {
      title: 'Hesap Adı',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Cari',
      dataIndex: 'contact_id',
      key: 'account_type',
      width: 120,
      render: (type: keyof typeof accountTypeNames) => (
        <Tag color={accountTypeColors[type]}>{accountTypeNames[type]}</Tag>
      ),
      filters: [
        { text: 'Aktif', value: 'asset' },
        { text: 'Pasif', value: 'liability' },
        { text: 'Gelir', value: 'revenue' },
        { text: 'Gider', value: 'expense' },
      ],
      filterMultiple: true,
      onFilter: (value: string | number | boolean, record: Account) => record.account_type === value,
    },
    {
      title: 'Durum',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Aktif' : 'Pasif'}
        </Tag>
      ),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 150,
      render: (_: any, record: Account) => (
        <Space size="small">
          <Button
            size="small"
            type={record.is_active ? 'default' : 'primary'}
            icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
            onClick={() => handleToggleStatus(record)}
          >
            {record.is_active ? 'Pasifleştir' : 'Aktifleştir'}
          </Button>
          <Popconfirm
            title="Hesabı silmek istediğinize emin misiniz?"
            description="Bu işlem geri alınamaz."
            onConfirm={() => handleDeleteAccount(record.id)}
            okText="Evet"
            cancelText="Hayır"
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              Sil
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleCreateAccount = async () => {
    try {
      const values = await form.validateFields();
      await createAccount.mutateAsync(values);
      message.success('Hesap başarıyla oluşturuldu');
      setIsModalOpen(false);
      form.resetFields();
    } catch (error) {
      if (error instanceof Error) {
        message.error('Hata: ' + error.message);
      }
    }
  };

  const handleToggleStatus = async (account: Account) => {
    try {
      await updateAccount.mutateAsync({
        id: account.id,
        data: { is_active: !account.is_active }
      });
      message.success(`Hesap ${!account.is_active ? 'aktifleştirildi' : 'pasifleştirildi'}`);
    } catch (error) {
      if (error instanceof Error) {
        message.error('Hata: ' + error.message);
      }
    }
  };

  const handleDeleteAccount = async (id: number) => {
    try {
      await deleteAccount.mutateAsync(id);
      message.success('Hesap başarıyla silindi');
    } catch (error) {
      if (error instanceof Error) {
        message.error('Hata: ' + error.message);
      }
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>Hesap Planı</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
          Yeni Hesap
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={accounts}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 50, showSizeChanger: true, showTotal: (total) => `Toplam ${total} hesap` }}
      />
      
      <Modal
        title="Yeni Hesap Oluştur"
        open={isModalOpen}
        onOk={handleCreateAccount}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        okText="Oluştur"
        cancelText="İptal"
        confirmLoading={createAccount.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 20 }}>
          <Form.Item
            name="code"
            label="Hesap Kodu"
            rules={[{ required: true, message: 'Hesap kodu zorunludur' }]}
          >
            <Input placeholder="örn: 100.01.001" />
          </Form.Item>
          
          <Form.Item
            name="name"
            label="Hesap Adı"
            rules={[{ required: true, message: 'Hesap adı zorunludur' }]}
          >
            <Input placeholder="örn: Kasa TL" />
          </Form.Item>
          
          <Form.Item
            name="account_type"
            label="Hesap Türü"
            rules={[{ required: true, message: 'Hesap türü zorunludur' }]}
          >
            <Select placeholder="Tür seçin">
              <Select.Option value="asset">Aktif</Select.Option>
              <Select.Option value="liability">Pasif</Select.Option>
              <Select.Option value="revenue">Gelir</Select.Option>
              <Select.Option value="expense">Gider</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="contact_id"
            label="Cari (Opsiyonel)"
          >
            <Select 
              showSearch
              allowClear
              placeholder="Cari seçin"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={contacts.map(c => ({
                value: c.id,
                label: `${c.code || ''} - ${c.name}`
              }))}
            />
          </Form.Item>

          <Form.Item
            name="personnel_id"
            label="Personel (Opsiyonel)"
          >
            <Select 
              showSearch
              allowClear
              placeholder="Personel seçin"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={personnel.map(p => ({
                value: p.id,
                label: `${p.personnel_number || ''} - ${p.first_name} ${p.last_name}`
              }))}
            />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Açıklama"
          >
            <Input.TextArea rows={3} placeholder="Opsiyonel açıklama" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AccountsPage;
