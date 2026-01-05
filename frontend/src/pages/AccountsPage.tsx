import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

// 🆕 V2 Domain imports
import { useAccounts } from '@/domains/accounting/accounts/hooks/useAccounts';
import type { Account } from '@/domains/accounting/accounts/types/account.types';

const AccountsPage: React.FC = () => {
  // 🆕 V2 React Query hooks
  const { data: accounts = [], isLoading: loading } = useAccounts();

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
      title: 'Tür',
      dataIndex: 'account_type',
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
      onFilter: (value: any, record: Account) => record.account_type === value,
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
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>Hesap Planı</h1>
        <Button type="primary" icon={<PlusOutlined />}>
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
    </div>
  );
};

export default AccountsPage;
