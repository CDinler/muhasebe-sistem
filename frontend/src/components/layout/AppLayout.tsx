import React from 'react';
import { Layout, Menu, theme, Button, Dropdown, Space } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FileTextOutlined,
  BookOutlined,
  TeamOutlined,
  SettingOutlined,
  ProjectOutlined,
  UserOutlined,
  LogoutOutlined,
  BarChartOutlined,
  LinkOutlined,
  DollarOutlined,
  SolutionOutlined,
  CalculatorOutlined,
  CalendarOutlined,
  TableOutlined,
} from '@ant-design/icons';
import { useAuth } from '@/contexts/AuthContext';

const { Header, Content, Sider } = Layout;

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: 'muhasebe',
      icon: <BookOutlined />,
      label: 'Muhasebe',
      children: [
        {
          key: '/transactions',
          icon: <FileTextOutlined />,
          label: 'Fişler',
        },
        {
          key: '/muavin',
          icon: <BookOutlined />,
          label: 'Muavin Defteri',
        },
        {
          key: '/accounts',
          icon: <BookOutlined />,
          label: 'Hesap Planı',
        },
      ],
    },
    {
      key: 'fatura',
      icon: <FileTextOutlined />,
      label: 'Fatura Yönetimi',
      children: [
        {
          key: '/einvoices',
          icon: <FileTextOutlined />,
          label: 'Fatura Takip',
        },
        {
          key: '/invoice-matching',
          icon: <LinkOutlined />,
          label: 'Fatura Eşleştirme',
        },
      ],
    },
    {
      key: '/contacts',
      icon: <TeamOutlined />,
      label: 'Cari Hesaplar',
    },
    {
      key: '/cost-centers',
      icon: <ProjectOutlined />,
      label: 'Masraf Merkezleri',
    },
    {
      key: 'personel',
      icon: <TeamOutlined />,
      label: 'Personel',
      children: [
        {
          key: '/personnel',
          icon: <TeamOutlined />,
          label: 'Personel Listesi',
        },
        {
          key: 'luca-entegrasyon',
          icon: <LinkOutlined />,
          label: 'Luca Entegrasyon',
          children: [
            {
              key: '/luca-bordro',
              icon: <FileTextOutlined />,
              label: 'Luca Bordrolar',
            },
            {
              key: '/luca-sicil',
              icon: <FileTextOutlined />,
              label: 'Luca Personel Sicil Kayıtları',
            },
          ],
        },
        {
          key: '/personnel-contracts',
          icon: <SolutionOutlined />,
          label: 'Personel Sözleşmeleri',
        },
        {
          key: '/puantaj-grid',
          icon: <TableOutlined />,
          label: 'Puantaj Takip',
        },
        {
          key: '/bordro-calculation',
          icon: <CalculatorOutlined />,
          label: 'Bordro Hesaplama',
        },
        {
          key: '/system-config',
          icon: <SettingOutlined />,
          label: 'Sistem Ayarları',
        },
      ],
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: 'Raporlar',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Ayarlar',
    },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      label: user?.full_name || user?.username,
      icon: <UserOutlined />,
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: 'Çıkış Yap',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <style>
        {`
          .ant-layout-sider {
            background: #d6e8f0 !important;
          }
          .ant-menu-light, .ant-menu-light > .ant-menu {
            background: transparent !important;
          }
          .ant-menu-light .ant-menu-sub,
          .ant-menu-light.ant-menu-sub,
          .ant-menu-submenu-popup.ant-menu-light .ant-menu-sub {
            background: #d6e8f0 !important;
          }
          .ant-menu-light .ant-menu-item-selected {
            background-color: rgba(0, 0, 0, 0.08) !important;
          }
          .ant-menu-light .ant-menu-item:hover,
          .ant-menu-light .ant-menu-submenu-title:hover {
            background-color: rgba(0, 0, 0, 0.04) !important;
          }
        `}
      </style>
      <Sider 
        breakpoint="lg" 
        collapsedWidth="0"
      >
        <div
          style={{
            height: 32,
            margin: 16,
            color: '#2c3e50',
            fontSize: 20,
            fontWeight: 'bold',
            textAlign: 'center',
          }}
        >
          Muhasebe
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: 18, fontWeight: 500 }}>
            Muhasebe Otomasyon Sistemi
          </div>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Button type="text" icon={<UserOutlined />}>
              <Space>
                {user?.full_name || user?.username}
              </Space>
            </Button>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;