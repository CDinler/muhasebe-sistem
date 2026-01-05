import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, Modal, Form, Input, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';

// 🆕 V2 Domain imports
import { useCostCenters, useCreateCostCenter, useUpdateCostCenter, useDeleteCostCenter } from '@/domains/partners/cost_centers/hooks/useCostCenters';
import type { CostCenter, CostCenterCreateRequest } from '@/domains/partners/cost_centers/types/cost-center.types';

const CostCentersPage: React.FC = () => {
  // 🆕 V2 React Query hooks
  const { data: costCenters = [], isLoading: loading, refetch } = useCostCenters();
  const createMutation = useCreateCostCenter();
  const updateMutation = useUpdateCostCenter();
  const deleteMutation = useDeleteCostCenter();

  const [modalVisible, setModalVisible] = useState(false);
  const [editingCostCenter, setEditingCostCenter] = useState<CostCenter | null>(null);
  const [form] = Form.useForm();

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
    deleteMutation.mutate(id, {
      onSuccess: () => refetch()
    });
  };

  const handleSubmit = async (values: CostCenterCreateRequest) => {
    if (editingCostCenter?.id) {
      updateMutation.mutate({ id: editingCostCenter.id, data: values }, {
        onSuccess: () => {
          setModalVisible(false);
          refetch();
        }
      });
    } else {
      createMutation.mutate(values, {
        onSuccess: () => {
          setModalVisible(false);
          refetch();
        }
      });
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
