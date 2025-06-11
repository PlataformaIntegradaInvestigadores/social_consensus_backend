# 📚 Documentación de API - Sistema de Autenticación Dual

## 🏗️ Arquitectura del Sistema

El sistema soporta **dos tipos de usuarios**:
- **Investigadores** (Users): Personas que participan en consensos académicos
- **Empresas** (Companies): Organizaciones que publican trabajos/jobs

---

## 🔐 Endpoints de Autenticación

### Base URL
```
http://localhost:8000/api/
```

---

## 👨‍🔬 INVESTIGADORES (Users)

### 1. Registro de Investigador
```http
POST /api/register/
```

**Request Body:**
```json
{
    "first_name": "Juan",
    "last_name": "Pérez",
    "username": "juan.perez@universidad.edu",
    "scopus_id": "12345678901",
    "password": "miPasswordSeguro123"
}
```

**Response Success (201):**
```json
{
    "id": "abcd123456",
    "first_name": "Juan",
    "last_name": "Pérez",
    "username": "juan.perez@universidad.edu",
    "scopus_id": "12345678901"
}
```

**Response Error (400):**
```json
{
    "errors": {
        "username": ["User with this EMAIL already exists."],
        "scopus_id": ["User with this SCOPUS ID already exists."]
    }
}
```

**Campos Requeridos:**
- `first_name`: Nombre (string, max 30 caracteres)
- `last_name`: Apellido (string, max 30 caracteres)
- `username`: Email único (email format)
- `password`: Contraseña (string)

**Campos Opcionales:**
- `scopus_id`: ID de Scopus (string, max 20 caracteres, único)

---

### 2. Login de Investigador
```http
POST /api/token/
```

**Request Body:**
```json
{
    "username": "juan.perez@universidad.edu",
    "password": "miPasswordSeguro123"
}
```

**Response Success (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": "abcd123456"
}
```

---

### 3. Obtener Perfil de Investigador
```http
GET /api/users/{user_id}/
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response Success (200):**
```json
{
    "first_name": "Juan",
    "last_name": "Pérez",
    "scopus_id": "12345678901",
    "institution": "Universidad Nacional",
    "website": "https://juan-perez.com",
    "investigation_camp": "Inteligencia Artificial",
    "profile_picture": "/media/profile_pictures/abc123.jpg",
    "email_institution": "juan@universidad.edu"
}
```

---

### 4. Actualizar Perfil de Investigador
```http
PATCH /api/users/{user_id}/update/
```

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
first_name: Juan Carlos
last_name: Pérez García
institution: Universidad Nacional de Colombia
website: https://juan-perez-researcher.com
investigation_camp: Machine Learning
profile_picture: [archivo de imagen]
email_institution: jc.perez@unal.edu.co
```

---

### 5. Listar Investigadores
```http
GET /api/users/
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response Success (200):**
```json
[
    {
        "id": "abcd123456",
        "first_name": "María",
        "last_name": "González",
        "username": "maria.gonzalez@uni.edu"
    },
    {
        "id": "efgh789012",
        "first_name": "Carlos",
        "last_name": "Rodríguez",
        "username": "carlos.rodriguez@tech.edu"
    }
]
```

---

## 🏢 EMPRESAS (Companies)

### 1. Registro de Empresa
```http
POST /api/companies/register/
```

**Request Body:**
```json
{
    "company_name": "TechCorp Solutions",
    "username": "contacto@techcorp.com",
    "password": "passwordSeguro123",
    "confirm_password": "passwordSeguro123",
    "industry": "technology",
    "description": "Empresa líder en desarrollo de software",
    "website": "https://techcorp.com",
    "phone": "+57 1 234 5678"
}
```

**Response Success (201):**
```json
{
    "message": "Empresa registrada exitosamente",
    "company_name": "TechCorp Solutions",
    "username": "contacto@techcorp.com",
    "industry": "Tecnología"
}
```

**Response Error (400):**
```json
{
    "errors": {
        "username": ["Ya existe una empresa con este correo electrónico."],
        "password": ["La contraseña debe tener al menos 8 caracteres."],
        "company_name": ["El nombre de la empresa es requerido."]
    }
}
```

**Campos Requeridos:**
- `company_name`: Nombre de la empresa (string, max 200 caracteres)
- `username`: Email único (email format)
- `password`: Contraseña (string, mín 8 caracteres)
- `confirm_password`: Confirmación de contraseña

**Campos Opcionales:**
- `industry`: Industria (choices)
- `description`: Descripción (string, max 1000 caracteres)
- `website`: Sitio web (URL format)
- `phone`: Teléfono (string, max 20 caracteres)

**Opciones de Industria:**
```json
{
    "technology": "Tecnología",
    "health": "Salud",
    "sales": "Ventas",
    "finance": "Finanzas",
    "education": "Educación",
    "manufacturing": "Manufactura",
    "retail": "Comercio",
    "consulting": "Consultoría",
    "energy": "Energía",
    "telecommunications": "Telecomunicaciones",
    "automotive": "Automotriz",
    "food": "Alimentaria",
    "real_estate": "Bienes Raíces",
    "media": "Medios de Comunicación",
    "transportation": "Transporte",
    "other": "Otro"
}
```

---

### 2. Login de Empresa
```http
POST /api/companies/token/
```

**Request Body:**
```json
{
    "username": "contacto@techcorp.com",
    "password": "passwordSeguro123"
}
```

**Response Success (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "company_id": "comp123456",
    "user_type": "company"
}
```

---

### 3. Obtener Perfil de Empresa (Propio)
```http
GET /api/companies/profile/
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response Success (200):**
```json
{
    "id": "comp123456",
    "company_name": "TechCorp Solutions",
    "username": "contacto@techcorp.com",
    "industry": "technology",
    "industry_display": "Tecnología",
    "description": "Empresa líder en desarrollo de software",
    "website": "https://techcorp.com",
    "phone": "+57 1 234 5678",
    "address": "Calle 123 #45-67, Bogotá",
    "logo": "/media/company_logos/logo123.jpg",
    "founded_year": 2015,
    "employee_count": "51-200",
    "is_verified": false,
    "date_joined": "2024-01-15T10:30:00Z"
}
```

---

### 4. Obtener Perfil de Empresa (Público)
```http
GET /api/companies/{company_id}/
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response Success (200):**
```json
{
    "id": "comp123456",
    "company_name": "TechCorp Solutions",
    "username": "contacto@techcorp.com",
    "industry": "technology",
    "industry_display": "Tecnología",
    "description": "Empresa líder en desarrollo de software",
    "website": "https://techcorp.com",
    "phone": "+57 1 234 5678",
    "address": "Calle 123 #45-67, Bogotá",
    "logo": "/media/company_logos/logo123.jpg",
    "founded_year": 2015,
    "employee_count": "51-200",
    "is_verified": true,
    "date_joined": "2024-01-15T10:30:00Z"
}
```

---

### 5. Actualizar Perfil de Empresa
```http
PATCH /api/companies/{company_id}/update/
```

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
company_name: TechCorp Solutions S.A.S.
industry: technology
description: Empresa líder en desarrollo de software y soluciones tecnológicas
website: https://www.techcorp.com
phone: +57 1 234 5678
address: Calle 123 #45-67, Bogotá, Colombia
logo: [archivo de imagen]
founded_year: 2015
employee_count: 51-200
```

---

### 6. Listar Empresas
```http
GET /api/companies/
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `verified_only=true`: Solo empresas verificadas

**Response Success (200):**
```json
[
    {
        "id": "comp123456",
        "company_name": "TechCorp Solutions",
        "username": "contacto@techcorp.com",
        "industry": "technology",
        "industry_display": "Tecnología",
        "is_verified": true
    },
    {
        "id": "comp789012",
        "company_name": "HealthCare Plus",
        "username": "info@healthcare.com",
        "industry": "health",
        "industry_display": "Salud",
        "is_verified": false
    }
]
```

---

## 🔄 Refresh Token (Ambos tipos)

### Renovar Token de Acceso
```http
POST /api/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response Success (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 🔧 Configuración de JWT

**Tiempos de vida de tokens:**
- Access Token: 24 horas (1440 minutos)
- Refresh Token: 7 días

**Headers requeridos para endpoints protegidos:**
```
Authorization: Bearer {access_token}
```

---

## 📄 Códigos de Estado HTTP

- `200`: OK - Operación exitosa
- `201`: Created - Recurso creado exitosamente
- `400`: Bad Request - Datos inválidos
- `401`: Unauthorized - Token inválido o expirado
- `403`: Forbidden - Sin permisos
- `404`: Not Found - Recurso no encontrado
- `500`: Internal Server Error - Error del servidor

---

## 🎯 Diferencias Clave entre Usuarios

| Aspecto | Investigadores | Empresas |
|---------|---------------|----------|
| Endpoint Login | `/api/token/` | `/api/companies/token/` |
| Endpoint Registro | `/api/register/` | `/api/companies/register/` |
| Token Payload | `user_id` | `company_id`, `user_type` |
| Campos Únicos | `scopus_id`, `investigation_camp` | `industry`, `employee_count` |
| Verificación | No aplica | `is_verified` |

---

## 🚀 Próximos Pasos

1. **Crear migraciones**: `python manage.py makemigrations`
2. **Aplicar migraciones**: `python manage.py migrate`
3. **Crear directorios de media**: `mkdir media/company_logos`
4. **Agregar logos por defecto**: Subir `default_company_logo.png`
5. **Configurar permisos**: Implementar roles específicos según necesidades
