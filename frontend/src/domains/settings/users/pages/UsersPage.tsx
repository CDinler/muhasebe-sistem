import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Space, Popconfirm, Card, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, LockOutlined } from '@ant-design/icons';
import axios from 'axios';
import type { ColumnsType } from 'antd/es/table';

const { Option } = Select;

const API_BASE = import.meta.env.VITE_API_URL || '';

interface User {
  id: number;
  username: string;
  email?: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface UserFormData {
  username: string;
  email?: string;
  password?: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  const roleLabels: Record<string, string> = {
    admin: 'Admin',
    muhasebeci: 'Muhasebeci',
    kullanici: 'Kullanıcı',
  };

  const roleColors: Record<string, string> = {
    admin: 'red',
    muhasebeci: 'blue',
    kullanici: 'green',
  };

  // Kullanıcıları yükle
  const loadUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/v2/users/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(response.data);
    } catch (error) {
      console.error('Kullanıcılar yüklenirken hata:', error);
      message.error('Kullanıcılar yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // Modal aç
  const showModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        is_active: user.is_active,
      });
    } else {
      setEditingUser(null);
      form.resetFields();
      form.setFieldsValue({ is_active: true, role: 'kullanici' });
    }
    setIsModalOpen(true);
  };

  // Modal kapat
  const handleCancel = () => {
    setIsModalOpen(false);
    setEditingUser(null);
    form.resetFields();
  };

  // Kullanıcı kaydet
  const handleSubmit = async (values: UserFormData) => {
    try {
      const token = localStorage.getItem('token');
      
      if (editingUser) {
        // Güncelleme
        const updateData: any = {
          username: values.username,
          email: values.email,
          full_name: values.full_name,
          role: values.role,
          is_active: values.is_active,
        };
        
        // Şifre varsa ekle
        if (values.password) {
          updateData.password = values.password;
        }
        
        await axios.put(
          `${API_BASE}/api/v2/users/${editingUser.id}`,
          updateData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        message.success('Kullanıcı başarıyla güncellendi');
      } else {
        // Yeni kullanıcı
        await axios.post(
          `${API_BASE}/api/v2/users/`,
          values,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        message.success('Kullanıcı başarıyla oluşturuldu');
      }
      
      handleCancel();
      loadUsers();
    } catch (error: any) {
      console.error('Kullanıcı kaydedilirken hata:', error);
      const errorMessage = error.response?.data?.detail || 'Kullanıcı kaydedilirken bir hata oluştu';
      message.error(errorMessage);
    }
  };

  // Kullanıcı sil
  const handleDelete = async (userId: number) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_BASE}/api/v2/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      message.success('Kullanıcı devre dışı bırakıldı');
      loadUsers();
    } catch (error: any) {
      console.error('Kullanıcı silinirken hata:', error);
      const errorMessage = error.response?.data?.detail || 'Kullanıcı silinirken bir hata oluştu';
      message.error(errorMessage);
    }
  };

  const columns: ColumnsType<User> = [
    {
      title: 'Kullanıcı Adı',
      dataIndex: 'username',
      key: 'username',
      width: 150,
    },
    {
      title: 'Ad Soyad',
      dataIndex: 'full_name',
      key: 'full_name',
      width: 200,
    },
    {
      title: 'E-posta',
      dataIndex: 'email',
      key: 'email',
      width: 200,
      render: (email: string) => email || '-',
    },
    {
      title: 'Rol',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role: string) => (
        <Tag color={roleColors[role] || 'default'}>
          {roleLabels[role] || role}
        </Tag>
      ),
    },
    {
      title: 'Durum',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (is_active: boolean) => (
        <Tag color={is_active ? 'success' : 'error'}>
          {is_active ? 'Aktif' : 'Pasif'}
        </Tag>
      ),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => showModal(record)}
            size="small"
          >
            Düzenle
          </Button>
          <Popconfirm
            title="Bu kullanıcıyı devre dışı bırakmak istediğinize emin misiniz?"
            onConfirm={() => handleDelete(record.id)}
            okText="Evet"
            cancelText="Hayır"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              Sil
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="Kullanıcı Yönetimi"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => showModal()}
          >
            Yeni Kullanıcı
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showTotal: (total) => `Toplam ${total} kullanıcı`,
            showSizeChanger: true,
          }}
        />
      </Card>

      <Modal
        title={editingUser ? 'Kullanıcı Düzenle' : 'Yeni Kullanıcı'}
        open={isModalOpen}
        onCancel={handleCancel}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ is_active: true, role: 'kullanici' }}
        >
          <Form.Item
            label="Kullanıcı Adı"
            name="username"
            rules={[{ required: true, message: 'Kullanıcı adı zorunludur' }]}
          >
            <Input placeholder="kullanici_adi" />
          </Form.Item>

          <Form.Item
            label="Ad Soyad"
            name="full_name"
            rules={[{ required: true, message: 'Ad soyad zorunludur' }]}
          >
            <Input placeholder="Ahmet Yılmaz" />
          </Form.Item>

          <Form.Item
            label="E-posta"
            name="email"
            rules={[
              { type: 'email', message: 'Geçerli bir e-posta adresi girin' },
            ]}
          >
            <Input placeholder="ornek@firma.com" />
          </Form.Item>

          <Form.Item
            label="Şifre"
            name="password"
            rules={[
              { required: !editingUser, message: 'Şifre zorunludur' },
              { min: 6, message: 'Şifre en az 6 karakter olmalıdır' },
            ]}
            help={editingUser ? 'Şifre değiştirmek istemiyorsanız boş bırakın' : undefined}
          >
            <Input.Password
              placeholder={editingUser ? 'Yeni şifre (opsiyonel)' : 'Şifre'}
              prefix={<LockOutlined />}
            />
          </Form.Item>

          <Form.Item
            label="Rol"
            name="role"
            rules={[{ required: true, message: 'Rol seçimi zorunludur' }]}
          >
            <Select placeholder="Rol seçin">
              <Option value="kullanici">Kullanıcı</Option>
              <Option value="muhasebeci">Muhasebeci</Option>
              <Option value="admin">Admin</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Durum"
            name="is_active"
            valuePropName="checked"
          >
            <Select>
              <Option value={true}>Aktif</Option>
              <Option value={false}>Pasif</Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
            <Space style={{ float: 'right' }}>
              <Button onClick={handleCancel}>İptal</Button>
              <Button type="primary" htmlType="submit">
                {editingUser ? 'Güncelle' : 'Oluştur'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UsersPage;
