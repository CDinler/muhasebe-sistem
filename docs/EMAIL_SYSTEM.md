# E-posta Gönderme Sistemi

## Genel Bakış
Kullanıcıların kendi e-posta hesaplarından cari raporları ve diğer belgeleri gönderebilmesi için e-posta sistemi.

## Mimari

### 1. Backend Bileşenleri

#### Email Service (`backend/app/services/email_service.py`)
- SMTP üzerinden e-posta gönderme
- PDF/Excel ek dosya desteği
- HTML e-posta şablonları
- CC/BCC desteği

#### User Email Settings Model (`backend/app/models/user_email_settings.py`)
- Kullanıcı başına SMTP ayarları
- Her kullanıcı kendi e-posta sunucusunu kullanabilir

#### Database Migration
- Tablo: `user_email_settings`
- Foreign key: `users.id`

### 2. Gerekli Endpoint'ler (Oluşturulacak)

```python
# backend/app/api/v1/endpoints/email.py

@router.post("/send-report")
def send_cari_report(
    contact_id: int,
    recipient_email: str,
    report_type: str = "PDF",  # PDF veya Excel
    current_user = Depends(get_current_user)
)

@router.get("/settings")
def get_email_settings(current_user = Depends(get_current_user))

@router.put("/settings")
def update_email_settings(
    settings: EmailSettingsUpdate,
    current_user = Depends(get_current_user)
)

@router.post("/test")
def test_email_connection(current_user = Depends(get_current_user))
```

### 3. Frontend Bileşenleri (Oluşturulacak)

#### Kullanıcı Ayarlar Sayfası (`/settings`)
```tsx
<Form>
  <Form.Item label="SMTP Sunucu">
    <Select>
      <Option value="smtp.gmail.com">Gmail</Option>
      <Option value="smtp.office365.com">Outlook</Option>
      <Option value="custom">Özel</Option>
    </Select>
  </Form.Item>
  
  <Form.Item label="E-posta">
    <Input type="email" />
  </Form.Item>
  
  <Form.Item label="Uygulama Şifresi">
    <Input.Password />
  </Form.Item>
  
  <Button>Test Et</Button>
  <Button type="primary">Kaydet</Button>
</Form>
```

#### Cari Raporu E-posta Butonu
```tsx
<Button 
  icon={<MailOutlined />}
  onClick={handleSendEmail}
>
  E-posta Gönder
</Button>

<Modal title="E-posta Gönder">
  <Form>
    <Form.Item label="Alıcı E-posta">
      <Input type="email" />
    </Form.Item>
    <Form.Item label="Format">
      <Radio.Group>
        <Radio value="PDF">PDF</Radio>
        <Radio value="Excel">Excel</Radio>
      </Radio.Group>
    </Form.Item>
  </Form>
</Modal>
```

## Kullanım Senaryosu

### 1. İlk Kurulum
```
1. Kullanıcı /settings sayfasına gider
2. E-posta ayarlarını yapılandırır:
   - Gmail için: smtp.gmail.com:587
   - E-posta: ornek@gmail.com
   - Uygulama Şifresi: (Google'dan alınacak)
3. "Test Et" butonuna tıklar
4. Başarılı ise "Kaydet" butonuna tıklar
```

### 2. Rapor Gönderme
```
1. Cari hesap ekstresi açılır
2. "E-posta Gönder" butonuna tıklanır
3. Alıcı e-posta girilir
4. Format seçilir (PDF/Excel)
5. Gönder
```

## Gmail Uygulama Şifresi Alma

1. Google Hesabına giriş yapın
2. Güvenlik > 2 Adımlı Doğrulama > Uygulama Şifreleri
3. "Diğer (Özel ad)" seçin
4. "Muhasebe Sistemi" yazın
5. Oluşturulan 16 haneli şifreyi kopyalayın
6. Ayarlar sayfasında bu şifreyi kullanın

## Güvenlik Notları

⚠️ **ÖNEMLİ**: 
- SMTP şifreleri veritabanında şifrelenmiş olarak saklanmalı (AES encryption)
- HTTPS kullanılması zorunlu
- Hassas bilgiler loglanmamalı
- Rate limiting uygulanmalı (spam önleme)

## Sonraki Adımlar

1. ✅ Email service oluşturuldu
2. ✅ User email settings modeli oluşturuldu
3. ✅ Database migration hazırlandı
4. ⏳ Backend endpoints oluşturulacak
5. ⏳ Frontend settings sayfası oluşturulacak
6. ⏳ Cari rapor e-posta butonu eklenecek
7. ⏳ Şifreleme sistemi eklenecek

## Örnek Kod

### Backend: Rapor Gönderme
```python
# Kullanıcının e-posta ayarlarını al
email_settings = db.query(UserEmailSettings).filter(
    UserEmailSettings.user_id == current_user.id
).first()

if not email_settings:
    raise HTTPException(400, "E-posta ayarları yapılmamış")

# Email service oluştur
email_service = EmailService(
    smtp_server=email_settings.smtp_server,
    smtp_port=email_settings.smtp_port,
    smtp_username=email_settings.smtp_username,
    smtp_password=decrypt(email_settings.smtp_password),
    use_tls=email_settings.use_tls
)

# Raporu oluştur
report_bytes = generate_pdf_report(contact_id, start_date, end_date)

# Gönder
email_service.send_report_email(
    to_email=recipient_email,
    contact_name=contact.name,
    report_file=report_bytes,
    report_filename=f"cari_ekstre_{contact.code}.pdf"
)
```

### Frontend: E-posta Gönder Modal
```tsx
const handleSendEmail = async (values: any) => {
  try {
    await api.post('/email/send-report', {
      contact_id: selectedContact.id,
      recipient_email: values.email,
      report_type: values.format,
      start_date: startDate,
      end_date: endDate
    });
    message.success('E-posta başarıyla gönderildi');
  } catch (error) {
    message.error('E-posta gönderilirken hata oluştu');
  }
};
```
