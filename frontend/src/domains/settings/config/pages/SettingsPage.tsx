import React, { useState, useEffect } from 'react';
import { Card, Form, Input, InputNumber, Button, Switch, message, Space, Divider, Alert } from 'antd';
import { MailOutlined, LockOutlined, SaveOutlined, SendOutlined } from '@ant-design/icons';
import axios from 'axios';

interface EmailSettings {
  id?: number;
  smtp_server: string;
  smtp_port: number;
  smtp_username: string;
  smtp_password: string;
  use_tls: boolean;
}

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [hasSettings, setHasSettings] = useState(false);

  // Mevcut ayarları yükle
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:8000/api/v2/email/settings', {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      form.setFieldsValue({
        smtp_server: response.data.smtp_server,
        smtp_port: response.data.smtp_port,
        smtp_username: response.data.smtp_username,
        smtp_password: '********', // Mevcut şifreyi gösterme
        use_tls: response.data.use_tls,
      });
      setHasSettings(true);
    } catch (error: any) {
      if (error.response?.status === 404) {
        // 404 ise ayar yok, yeni oluşturulacak
        setHasSettings(false);
      } else {
        console.error('Ayarlar yüklenirken hata:', error);
        message.error(error.response?.data?.detail || 'Ayarlar yüklenirken hata oluştu');
        setHasSettings(false);
      }
    }
  };

  const handleSave = async (values: EmailSettings) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Eğer şifre değişmemişse (********), formdaki şifreyi gönderme
      const dataToSend = { ...values };
      if (values.smtp_password === '********') {
        delete dataToSend.smtp_password;
      }
      
      await axios.post(
        'http://127.0.0.1:8000/api/v2/email/settings',
        dataToSend,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      message.success('E-posta ayarları başarıyla kaydedildi');
      setHasSettings(true);
      loadSettings();
    } catch (error: any) {
      console.error('Ayarlar kaydedilirken hata:', error);
      message.error(error.response?.data?.detail || 'Ayarlar kaydedilirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    setTestLoading(true);
    try {
      const token = localStorage.getItem('token');
      const smtp_username = form.getFieldValue('smtp_username');
      
      if (!smtp_username) {
        message.error('Lütfen önce e-posta adresinizi girin');
        return;
      }
      
      await axios.post(
        'http://127.0.0.1:8000/api/v2/email/test',
        { recipient_email: smtp_username },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      message.success(`Test e-postası ${smtp_username} adresine gönderildi`);
    } catch (error: any) {
      console.error('Test e-postası gönderilirken hata:', error);
      message.error(error.response?.data?.detail || 'Test e-postası gönderilemedi');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="E-posta Ayarları">
        <Alert
          message="Gmail Kullanıcıları İçin Önemli"
          description={
            <div>
              <p><strong>Gmail kullanıyorsanız:</strong></p>
              <ol style={{ marginBottom: 0 }}>
                <li>Google hesabınıza giriş yapın</li>
                <li><a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer">
                  Uygulama Şifreleri</a> sayfasına gidin</li>
                <li>"Muhasebe Sistemi" adında yeni bir uygulama şifresi oluşturun</li>
                <li>Oluşturulan 16 haneli şifreyi aşağıdaki "Şifre" alanına yapıştırın</li>
              </ol>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={{
            smtp_server: 'smtp.gmail.com',
            smtp_port: 587,
            use_tls: true,
          }}
        >
          <Form.Item
            label="SMTP Sunucu"
            name="smtp_server"
            rules={[{ required: true, message: 'SMTP sunucu adresi gerekli' }]}
          >
            <Input placeholder="smtp.gmail.com" />
          </Form.Item>

          <Form.Item
            label="SMTP Port"
            name="smtp_port"
            rules={[{ required: true, message: 'SMTP port gerekli' }]}
          >
            <InputNumber min={1} max={65535} style={{ width: '100%' }} placeholder="587" />
          </Form.Item>

          <Form.Item
            label="E-posta Adresi"
            name="smtp_username"
            rules={[
              { required: true, message: 'E-posta adresi gerekli' },
              { type: 'email', message: 'Geçerli bir e-posta adresi girin' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="ornek@gmail.com"
            />
          </Form.Item>

          <Form.Item
            label="Şifre"
            name="smtp_password"
            rules={[{ required: !hasSettings, message: 'Şifre gerekli' }]}
            help={hasSettings ? 'Şifreyi değiştirmek istemiyorsanız boş bırakın' : 'Gmail için Uygulama Şifresi kullanın'}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={hasSettings ? '********' : 'Gmail Uygulama Şifresi'}
            />
          </Form.Item>

          <Form.Item
            label="TLS Kullan"
            name="use_tls"
            valuePropName="checked"
          >
            <Switch checkedChildren="Açık" unCheckedChildren="Kapalı" />
          </Form.Item>

          <Divider />

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                Kaydet
              </Button>
              
              <Button
                icon={<SendOutlined />}
                onClick={handleTestEmail}
                loading={testLoading}
                disabled={!hasSettings}
              >
                Test E-postası Gönder
              </Button>
            </Space>
          </Form.Item>
        </Form>

        <Divider />

        <Alert
          message="Diğer E-posta Sağlayıcıları"
          description={
            <div>
              <p><strong>Outlook/Hotmail:</strong></p>
              <ul>
                <li>SMTP: smtp-mail.outlook.com</li>
                <li>Port: 587</li>
                <li>TLS: Açık</li>
              </ul>
              
              <p><strong>Yahoo:</strong></p>
              <ul>
                <li>SMTP: smtp.mail.yahoo.com</li>
                <li>Port: 587</li>
                <li>TLS: Açık</li>
              </ul>
            </div>
          }
          type="warning"
          showIcon
        />
      </Card>
    </div>
  );
};

export default SettingsPage;
