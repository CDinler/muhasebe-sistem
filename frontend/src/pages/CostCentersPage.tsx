import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, Modal, Form, Input, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { costCenterService, CostCenter } from '@/services/muhasebe.service';

const CostCentersPage: React.FC = () => {
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCostCenter, setEditingCostCenter] = useState<CostCenter | null>(null);
  const [form] = Form.useForm();

  const loadCostCenters = async () => {
    setLoading(true);
    try {
      const response = await costCenterService.getAll();
      setCostCenters(response.data);
    } catch (error) {
      console.error('Masraf merkezleri yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCostCenters();
  }, []);

  const handleAdd = () => {
    form.resetFields();
    setEditingCostCenter(null);
    setModalVisible(true);
  };

  const handleEdit = (costCenter: CostCenter) => {
    form.setFieldsValue(costCenter);
    setEditingCostCenter(costCenter);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await costCenterService.delete(id);
      message.success('Masraf merkezi silindi');
      loadCostCenters();
    } catch (error) {
      message.error('Masraf merkezi silinemedi');
    }
  };

  const handleSubmit = async (values: CostCenter) => {
    try {
      if (editingCostCenter?.id) {
        await costCenterService.update(editingCostCenter.id, values);
        message.success('Masraf merkezi güncellendi');
      } else {
        await costCenterService.create(values);
        message.success('Masraf merkezi oluşturuldu');
      }
      setModalVisible(false);
      loadCostCenters();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'İşlem başarısız');
    }
  };

  const columns = [
    {
      title: 'Kod',
      dataIndex: 'code',
      key: 'code',
      width: 150,
      sorter: (a: CostCenter, b: CostCenter) => a.code.localeCompare(b.code),
    },
    {
      title: 'Ad',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: CostCenter, b: CostCenter) => a.name.localeCompare(b.name),
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
      width: 150,
      render: (_: any, record: CostCenter) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            Düzenle
          </Button>
          <Button
            type="link"
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

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>Masraf Merkezleri</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Yeni Masraf Merkezi
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={costCenters}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} masraf merkezi`,
        }}
      />

      <Modal
        title={editingCostCenter ? 'Masraf Merkezi Düzenle' : 'Yeni Masraf Merkezi'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="Kod"
            name="code"
            rules={[{ required: true, message: 'Kod gerekli!' }]}
          >
            <Input placeholder="OFIS" />
          </Form.Item>

          <Form.Item
            label="Ad"
            name="name"
            rules={[{ required: true, message: 'Ad gerekli!' }]}
          >
            <Input placeholder="Ofis Giderleri" />
          </Form.Item>

          <Form.Item name="is_active" initialValue={true} label="Durum">
            <Input.Group compact>
              <Button
                type={form.getFieldValue('is_active') === true ? 'primary' : 'default'}
                onClick={() => form.setFieldsValue({ is_active: true })}
              >
                Aktif
              </Button>
              <Button
                type={form.getFieldValue('is_active') === false ? 'primary' : 'default'}
                onClick={() => form.setFieldsValue({ is_active: false })}
              >
                Pasif
              </Button>
            </Input.Group>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Kaydet
              </Button>
              <Button onClick={() => setModalVisible(false)}>İptal</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CostCentersPage;
