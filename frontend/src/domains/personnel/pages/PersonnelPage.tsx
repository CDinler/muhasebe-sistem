/**
 * Personnel Page - Clean composition, business logic in hooks
 */
import React, { useState } from 'react';
import { Table, Button, Modal, Form, Input, Space, Card } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import {
  usePersonnel,
  useCreatePersonnel,
  useUpdatePersonnel,
  useDeletePersonnel,
} from '../hooks/usePersonnel';
import { Personnel, PersonnelCreate, PersonnelUpdate } from '../types/personnel.types';

export const PersonnelPage: React.FC = () => {
  const [form] = Form.useForm();
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPersonnel, setEditingPersonnel] = useState<Personnel | null>(null);

  // Hooks - All business logic here
  const { data: personnelData, isLoading } = usePersonnel({
    search: searchTerm,
    limit: 1000,
  });
  const createMutation = useCreatePersonnel();
  const updateMutation = useUpdatePersonnel();
  const deleteMutation = useDeletePersonnel();

  const handleCreate = () => {
    setEditingPersonnel(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (record: Personnel) => {
    setEditingPersonnel(record);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Personel Sil',
      content: 'Bu personeli silmek istediğinizden emin misiniz?',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingPersonnel) {
        updateMutation.mutate({
          id: editingPersonnel.id,
          data: values as PersonnelUpdate,
        });
      } else {
        createMutation.mutate(values as PersonnelCreate);
      }
      setIsModalOpen(false);
      form.resetFields();
    } catch (error) {
      console.error('Form validation error:', error);
    }
  };

  const columns = [
    {
      title: 'TC Kimlik No',
      dataIndex: 'tc_kimlik_no',
      key: 'tc_kimlik_no',
      width: 150,
    },
    {
      title: 'Ad',
      dataIndex: 'ad',
      key: 'ad',
      width: 150,
    },
    {
      title: 'Soyad',
      dataIndex: 'soyad',
      key: 'soyad',
      width: 150,
    },
    {
      title: 'IBAN',
      dataIndex: 'iban',
      key: 'iban',
      width: 250,
    },
    {
      title: 'İşlemler',
      key: 'actions',
      fixed: 'right' as const,
      width: 120,
      render: (_: any, record: Personnel) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          />
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          />
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="Personel Yönetimi"
      extra={
        <Space>
          <Input
            placeholder="TC, Ad veya Soyad ile ara..."
            prefix={<SearchOutlined />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: 300 }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            Yeni Personel
          </Button>
        </Space>
      }
    >
      <Table
        columns={columns}
        dataSource={personnelData?.items || []}
        rowKey="id"
        loading={isLoading}
        pagination={{
          total: personnelData?.total || 0,
          pageSize: 1000,
          showTotal: (total) => `Toplam ${total} personel`,
        }}
        scroll={{ x: 1000 }}
      />

      <Modal
        title={editingPersonnel ? 'Personel Düzenle' : 'Yeni Personel'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="TC Kimlik No"
            name="tc_kimlik_no"
            rules={[
              { required: true, message: 'TC Kimlik No zorunludur' },
              { len: 11, message: 'TC Kimlik No 11 haneli olmalıdır' },
              { pattern: /^\d+$/, message: 'Sadece rakam giriniz' },
            ]}
          >
            <Input maxLength={11} placeholder="12345678901" />
          </Form.Item>

          <Form.Item
            label="Ad"
            name="ad"
            rules={[{ required: true, message: 'Ad zorunludur' }]}
          >
            <Input maxLength={100} />
          </Form.Item>

          <Form.Item
            label="Soyad"
            name="soyad"
            rules={[{ required: true, message: 'Soyad zorunludur' }]}
          >
            <Input maxLength={100} />
          </Form.Item>

          <Form.Item
            label="IBAN"
            name="iban"
            rules={[
              { len: 26, message: 'IBAN 26 karakter olmalıdır' },
              {
                pattern: /^TR\d{24}$/,
                message: 'IBAN TR ile başlamalı ve 24 rakam içermelidir',
              },
            ]}
          >
            <Input maxLength={26} placeholder="TR000000000000000000000000" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};
