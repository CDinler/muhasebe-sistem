# 🚀 Domain Migration Guide (Hızlı Başvuru)

## Backend Domain Migration (5 Adım)

### 1. Domain Klasörü Oluştur
```bash
mkdir backend/app/domains/<domain_name>
cd backend/app/domains/<domain_name>
```

### 2. Dosyaları Oluştur

#### `models.py`
```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

#### `schemas.py`
```python
from pydantic import BaseModel

class YourBase(BaseModel):
    name: str

class YourCreate(YourBase):
    pass

class YourUpdate(BaseModel):
    name: str | None = None

class YourResponse(YourBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

#### `repository.py`
```python
from app.shared.base.repository import CRUDBase
from .models import YourModel
from .schemas import YourCreate, YourUpdate

class YourRepository(CRUDBase[YourModel, YourCreate, YourUpdate]):
    pass

your_repo = YourRepository(YourModel)
```

#### `service.py`
```python
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessException
from .repository import your_repo
from .schemas import YourCreate

class YourService:
    def create(self, db: Session, data: YourCreate):
        # Business logic here
        if not data.name:
            raise BusinessException("Name required")
        return your_repo.create(db, data)

your_service = YourService()
```

#### `router.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from .service import your_service
from .schemas import YourCreate, YourResponse

router = APIRouter()

@router.post("/", response_model=YourResponse)
def create(data: YourCreate, db: Session = Depends(get_db)):
    return your_service.create(db, data)
```

### 3. main.py'a Ekle
```python
from app.domains.your_domain.router import router as your_router
app.include_router(your_router, prefix="/api/v2/your-domain", tags=["Your Domain"])
```

### 4. Test Et
```bash
python -c "from app.main import app; print('✅ OK')"
```

---

## Frontend Domain Migration (4 Adım)

### 1. Domain Klasörü Oluştur
```bash
mkdir -p frontend/src/domains/<domain-name>/{api,hooks,types,pages}
```

### 2. Dosyaları Oluştur

#### `types/your.types.ts`
```typescript
export interface YourModel {
  id: number;
  name: string;
}

export interface YourCreate {
  name: string;
}

export interface YourUpdate {
  name?: string;
}
```

#### `api/your.api.ts`
```typescript
import { CRUDService } from '@/shared/api/base.api';
import { YourModel, YourCreate, YourUpdate } from '../types/your.types';

class YourAPI extends CRUDService<YourModel, YourCreate, YourUpdate> {
  constructor() {
    super('/api/v2/your-domain');
  }
}

export const yourAPI = new YourAPI();
```

#### `hooks/useYour.ts`
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { yourAPI } from '../api/your.api';
import { YourCreate, YourUpdate } from '../types/your.types';
import { message } from 'antd';

const QUERY_KEY = 'your-data';

export function useYourData() {
  return useQuery({
    queryKey: [QUERY_KEY],
    queryFn: () => yourAPI.getAll(),
  });
}

export function useCreateYour() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: YourCreate) => yourAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('Created successfully');
    },
  });
}
```

#### `pages/YourPage.tsx`
```typescript
import React from 'react';
import { Table, Button } from 'antd';
import { useYourData, useCreateYour } from '../hooks/useYour';

export const YourPage: React.FC = () => {
  const { data, isLoading } = useYourData();
  const createMutation = useCreateYour();

  return (
    <div>
      <Table 
        dataSource={data} 
        loading={isLoading}
        rowKey="id"
      />
    </div>
  );
};
```

### 3. App.tsx'e Ekle
```typescript
import { YourPage } from './domains/your-domain/pages/YourPage';

// Routes içine:
<Route path="your-domain" element={<YourPage />} />
```

### 4. Test Et
```bash
npm run dev
```

---

## ⚡ Hızlı Kopya-Yapıştır Şablonlar

### Backend Full Domain (Tek Dosya)
```bash
# domains/<name>/__init__.py
touch domains/<name>/__init__.py

# Tüm dosyaları oluştur
touch domains/<name>/{models,schemas,repository,service,router}.py
```

### Frontend Full Domain (Tek Komut)
```bash
mkdir -p domains/<name>/{api,hooks,types,pages,components}
touch domains/<name>/api/<name>.api.ts
touch domains/<name>/hooks/use<Name>.ts
touch domains/<name>/types/<name>.types.ts
touch domains/<name>/pages/<Name>Page.tsx
```

---

## 🔧 Sık Kullanılan Patterns

### Error Handling
```python
# Backend
from app.core.exceptions import BusinessException, NotFoundException

if not found:
    raise NotFoundException("Resource", id)

if invalid:
    raise BusinessException("Invalid data")
```

### Pagination
```python
# Backend
from app.shared.base.schemas import PaginatedResponse

@router.get("/", response_model=PaginatedResponse[YourResponse])
def get_all(skip: int = 0, limit: int = 100):
    items = your_repo.get_multi(db, skip, limit)
    total = your_repo.count(db)
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )
```

### Search
```python
# Repository
def search(self, db: Session, term: str):
    return db.query(self.model).filter(
        self.model.name.contains(term)
    ).all()

# Frontend Hook
export function useSearch(term: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'search', term],
    queryFn: () => yourAPI.search(term),
    enabled: term.length >= 2,
  });
}
```

---

## ✅ Migration Checklist

### Backend
- [ ] Domain klasörü oluşturuldu
- [ ] models.py oluşturuldu
- [ ] schemas.py oluşturuldu (Create, Update, Response)
- [ ] repository.py oluşturuldu (CRUDBase extend)
- [ ] service.py oluşturuldu (business logic)
- [ ] router.py oluşturuldu (endpoints)
- [ ] main.py'a router eklendi
- [ ] Import test geçti

### Frontend
- [ ] Domain klasörü oluşturuldu
- [ ] types/*.types.ts oluşturuldu
- [ ] api/*.api.ts oluşturuldu (CRUDService extend)
- [ ] hooks/use*.ts oluşturuldu (React Query)
- [ ] pages/*Page.tsx oluşturuldu
- [ ] App.tsx'e route eklendi
- [ ] Compile error yok

---

## 🎯 Best Practices

### DO ✅
- Business logic'i service'e koy
- Validation'ı Pydantic/Zod ile yap
- React Query hooks kullan
- Error handling merkezi yap
- Type safety koru

### DON'T ❌
- Router'da business logic yazma
- Page component'te API call yapma
- Hata mesajlarını hardcode etme
- Type'sız kod yazma
- Duplicate CRUD logic

---

**Şablon Kopyala:**
```bash
# Backend
cp -r backend/app/domains/personnel backend/app/domains/<new_domain>

# Frontend  
cp -r frontend/src/domains/personnel frontend/src/domains/<new-domain>
```

Sonra içeriği domain'e göre değiştir!
