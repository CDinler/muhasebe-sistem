import React, { useState } from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', values.username);
      formData.append('password', values.password);

      const response = await axios.post(
        'http://127.0.0.1:8000/api/v1/auth/login',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      // AuthContext'e token'ı kaydet ve kullanıcı bilgilerini yükle
      await login(response.data.access_token);
      
      message.success('Giriş başarılı!');
      navigate('/');
    } catch (error: any) {
      console.error('Login error:', error);
      message.error(error.response?.data?.detail || 'Giriş başarısız');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        title={
          <div style={{ textAlign: 'center', fontSize: 24, fontWeight: 'bold' }}>
            Muhasebe Sistemi
          </div>
        }
        style={{ width: 400, boxShadow: '0 8px 16px rgba(0,0,0,0.1)' }}
      >
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Kullanıcı adı gerekli!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Kullanıcı Adı"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Şifre gerekli!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Şifre"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Giriş Yap
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center', color: '#888', fontSize: 12 }}>
            Demo: admin / admin123
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
