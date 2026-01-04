-- PERSONEL TABLOSU (LUCA-Compatible)
-- Tarih: 17 Aralık 2025

CREATE TABLE personnel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Temel Bilgiler
    code VARCHAR(20) UNIQUE NOT NULL,  -- P00001 formatında
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    tckn VARCHAR(11) UNIQUE,  -- TC Kimlik No
    
    -- İş Bilgileri
    sicil_no VARCHAR(50) UNIQUE,  -- Sicil numarası
    department VARCHAR(100),  -- Departman
    position VARCHAR(100),  -- Pozisyon/Ünvan
    employment_type VARCHAR(50) DEFAULT 'FULL_TIME',  -- FULL_TIME, PART_TIME, CONTRACT, INTERN
    start_date DATE,  -- İşe giriş tarihi
    end_date DATE,  -- İşten çıkış tarihi (NULL = aktif)
    is_active BOOLEAN DEFAULT TRUE,
    
    -- İletişim Bilgileri
    phone VARCHAR(50),
    phone2 VARCHAR(50),  -- Alternatif telefon
    email VARCHAR(100),
    emergency_contact VARCHAR(200),  -- Acil durum irtibat
    emergency_phone VARCHAR(50),
    
    -- Adres Bilgileri
    address TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    postal_code VARCHAR(10),
    
    -- Kişisel Bilgiler
    birth_date DATE,
    birth_place VARCHAR(100),
    gender VARCHAR(10),  -- MALE, FEMALE, OTHER
    marital_status VARCHAR(20),  -- SINGLE, MARRIED, DIVORCED, WIDOWED
    blood_type VARCHAR(5),  -- A+, B+, AB+, O+, A-, B-, AB-, O-
    
    -- Eğitim
    education_level VARCHAR(50),  -- PRIMARY, SECONDARY, HIGH_SCHOOL, ASSOCIATE, BACHELOR, MASTER, PHD
    
    -- SGK ve Vergi
    sgk_number VARCHAR(20),  -- SGK sicil numarası
    tax_office VARCHAR(100),
    iban VARCHAR(34),  -- Maaş ödemesi için
    bank_name VARCHAR(100),
    bank_branch VARCHAR(100),
    
    -- Maaş ve Ücret (Bordro için)
    base_salary DECIMAL(18,2) DEFAULT 0,  -- Brüt maaş
    net_salary DECIMAL(18,2) DEFAULT 0,  -- Net maaş
    currency VARCHAR(3) DEFAULT 'TRY',
    payment_method VARCHAR(50) DEFAULT 'BANK_TRANSFER',  -- CASH, BANK_TRANSFER, CHECK
    
    -- Diğer
    photo_url VARCHAR(500),  -- Personel fotoğrafı
    notes TEXT,
    private_notes TEXT,  -- Gizli notlar
    
    -- Sistem
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,  -- Kaydı oluşturan kullanıcı
    updated_by INT,  -- Son güncelleyen kullanıcı
    
    INDEX idx_personnel_code (code),
    INDEX idx_personnel_tckn (tckn),
    INDEX idx_personnel_sicil_no (sicil_no),
    INDEX idx_personnel_name (first_name, last_name),
    INDEX idx_personnel_is_active (is_active),
    INDEX idx_personnel_department (department)
);

-- PERSONEL EK BİLGİLER TABLOSU (İzin, Rapor, Eğitim vb. için genişletilebilir)
CREATE TABLE personnel_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    document_type VARCHAR(50) NOT NULL,  -- CONTRACT, LICENSE, CERTIFICATE, RESUME, etc.
    document_name VARCHAR(200),
    file_path VARCHAR(500),
    issue_date DATE,
    expiry_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
    INDEX idx_personnel_documents_personnel_id (personnel_id),
    INDEX idx_personnel_documents_type (document_type)
);

-- PERSONEL İZİNLER TABLOSU
CREATE TABLE personnel_leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    leave_type VARCHAR(50) NOT NULL,  -- ANNUAL, SICK, MATERNITY, UNPAID, etc.
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INT NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, APPROVED, REJECTED
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INT,  -- Onaylayan kullanıcı
    approved_date TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
    INDEX idx_personnel_leaves_personnel_id (personnel_id),
    INDEX idx_personnel_leaves_status (status),
    INDEX idx_personnel_leaves_dates (start_date, end_date)
);

-- PERSONEL RAPORLAR TABLOSU (Sağlık raporları)
CREATE TABLE personnel_health_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    report_type VARCHAR(50) NOT NULL,  -- SICK_LEAVE, WORK_ACCIDENT, OCCUPATIONAL_DISEASE
    report_number VARCHAR(50),
    hospital_name VARCHAR(200),
    doctor_name VARCHAR(200),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INT NOT NULL,
    diagnosis TEXT,
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
    INDEX idx_personnel_health_reports_personnel_id (personnel_id),
    INDEX idx_personnel_health_reports_dates (start_date, end_date)
);

-- PERSONEL PUANTAJ TABLOSU (Giriş-Çıkış kayıtları)
CREATE TABLE personnel_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    check_in_time TIME,
    check_out_time TIME,
    work_hours DECIMAL(5,2),  -- Çalışma saati
    overtime_hours DECIMAL(5,2),  -- Fazla mesai
    status VARCHAR(20) DEFAULT 'PRESENT',  -- PRESENT, ABSENT, LATE, HALF_DAY
    notes TEXT,
    
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
    INDEX idx_personnel_attendance_personnel_id (personnel_id),
    INDEX idx_personnel_attendance_date (attendance_date),
    UNIQUE KEY unique_personnel_date (personnel_id, attendance_date)
);

-- PERSONEL - CARİ İLİŞKİ TABLOSU (Bordro ödemeleri için)
-- Personel ile cari hesap arasında bağlantı kurulacak
ALTER TABLE personnel ADD COLUMN contact_id INT;
ALTER TABLE personnel ADD FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL;
CREATE INDEX idx_personnel_contact_id ON personnel(contact_id);

-- NOT: Personel için 335.xxx hesaplarında cari kartı açılacak
-- contact_id ile personel ve cari arasında ilişki kurulacak
