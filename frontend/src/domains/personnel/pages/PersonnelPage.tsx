/**
 * Personnel Page - Clean composition, business logic in hooks
 */
import React, { useState } from 'react';
import { Table, Button, Modal, Form, Input, Space, Card, Select } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, FileTextOutlined } from '@ant-design/icons';
import { PersonnelReportModal } from '@/domains/reporting/reports/components/PersonnelReportModal';
import dayjs from 'dayjs';
import {
  usePersonnel,
  useCreatePersonnel,
  useUpdatePersonnel,
  useDeletePersonnel,
} from '../hooks/usePersonnel';
import { Personnel, PersonnelCreate, PersonnelUpdate } from '../types/personnel.types';

const { Option } = Select;

export const PersonnelPage: React.FC = () => {
  const [form] = Form.useForm();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState<number | undefined>(undefined);
  const [selectedMonth, setSelectedMonth] = useState<number | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPersonnel, setEditingPersonnel] = useState<Personnel | null>(null);
  const [reportModalVisible, setReportModalVisible] = useState(false);
  const [selectedPersonnelForReport, setSelectedPersonnelForReport] = useState<any>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50 });

  // Hooks - All business logic here
  const { data: personnelData, isLoading } = usePersonnel({
    search: searchTerm,
    year_filter: selectedYear,
    month_filter: selectedMonth,
    skip: (pagination.current - 1) * pagination.pageSize,
    limit: pagination.pageSize,
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
      width: 130,
      render: (_: any, record: Personnel) => (
        <Select
          style={{ width: 130 }}
          placeholder="İşlemler"
          onSelect={(value) => {
            if (value === 'report') {
              setSelectedPersonnelForReport({
                tc_kimlik_no: record.tc_kimlik_no,
                ad: record.ad,
                soyad: record.soyad,
                id: record.id
              });
              setReportModalVisible(true);
            } else if (value === 'edit') {
              handleEdit(record);
            } else if (value === 'delete') {
              handleDelete(record.id);
            }
          }}
        >
          <Select.Option value="report">
            <FileTextOutlined style={{ marginRight: 6, color: '#1890ff' }} /> <span>Rapor</span>
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

  return (
    <Card
      title="Personel Yönetimi"
      extra={
        <Space>
          <Select
            placeholder="Yıl Seç (Çalışma Yılı)"
            allowClear
            value={selectedYear}
            onChange={(year) => {
              setSelectedYear(year);
              if (!year) setSelectedMonth(undefined); // Yıl kaldırılınca ay'ı da temizle
            }}
            style={{ width: 150 }}
          >
            {Array.from({ length: 10 }, (_, i) => {
              const year = dayjs().year() - i; // İleriye değil geriye doğru
              return <Option key={year} value={year}>{year}</Option>;
            })}
          </Select>
          <Select
            placeholder="Ay Seç"
            allowClear
            value={selectedMonth}
            onChange={setSelectedMonth}
            disabled={!selectedYear}
            style={{ width: 120 }}
          >
            <Option value={undefined}>Tümü</Option>
            <Option value={1}>Ocak</Option>
            <Option value={2}>Şubat</Option>
            <Option value={3}>Mart</Option>
            <Option value={4}>Nisan</Option>
            <Option value={5}>Mayıs</Option>
            <Option value={6}>Haziran</Option>
            <Option value={7}>Temmuz</Option>
            <Option value={8}>Ağustos</Option>
            <Option value={9}>Eylül</Option>
            <Option value={10}>Ekim</Option>
            <Option value={11}>Kasım</Option>
            <Option value={12}>Aralık</Option>
          </Select>
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
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: personnelData?.total || 0,
          showTotal: (total) => `Toplam ${total} personel`,
          showSizeChanger: true,
          pageSizeOptions: ['20', '50', '100', '200'],
          onChange: (page, pageSize) => {
            setPagination({ current: page, pageSize: pageSize || 50 });
          },
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

    <PersonnelReportModal
      visible={reportModalVisible}
      personnel={selectedPersonnelForReport}
      onClose={() => {
        setReportModalVisible(false);
        setSelectedPersonnelForReport(null);
      }}
    />
  </Card>
);
};