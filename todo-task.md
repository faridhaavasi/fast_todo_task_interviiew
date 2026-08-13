## تسک پروژه FastAPI — Todo App (نسخه تمرینی نزدیک به پروژه واقعی)

### هدف پروژه

پیاده‌سازی یک **Todo Application** با استفاده از **FastAPI + SQLAlchemy + PostgreSQL** به شکلی که علاوه بر CRUD ساده، ساختارهای رایج توسعه وب و بک‌اند مدرن را نیز پوشش دهد.

این پروژه برای تمرین موارد زیر طراحی شده است:

- ساختاردهی پروژه
- احراز هویت Stateful یا Stateless
- طراحی RESTful API
- CRUD کامل
- جستجو، فیلتر، مرتب‌سازی و صفحه‌بندی
- مدیریت خطا
- اعتبارسنجی داده‌ها
- لایه‌بندی سرویس و Repository
- مستندسازی API
- تست و Migration

---

## مشخصات فنی

### تکنولوژی‌ها

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Pydantic v2
- Passlib / bcrypt
- JWT Authentication
- Pytest

---

## ساختار پیشنهادی پروژه

```text
app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── database.py
│   └── exceptions.py
├── api/
│   └── v1/
│       ├── auth.py
│       ├── users.py
│       └── todos.py
├── models/
│   ├── user.py
│   └── todo.py
├── schemas/
│   ├── auth.py
│   ├── user.py
│   └── todo.py
├── repositories/
│   ├── user_repository.py
│   └── todo_repository.py
├── services/
│   ├── auth_service.py
│   └── todo_service.py
├── dependencies/
│   └── auth.py
├── tests/
│   ├── test_auth.py
│   └── test_todos.py
└── migrations/
```

---

## بخش ۱ — احراز هویت

### مدل User

```python
id
email
username
password (hashed)
is_active
created_at
updated_at
```

### Endpoint ها

| متد | آدرس | توضیح |
|---|---|---|
| POST | /api/v1/auth/register | ثبت‌نام |
| POST | /api/v1/auth/login | ورود |
| POST | /api/v1/auth/refresh | دریافت access token جدید |
| POST | /api/v1/auth/logout | خروج |
| GET | /api/v1/users/me | اطلاعات کاربر جاری |

### الزامات

- رمز عبور Hash شود.
- JWT شامل `sub` و `exp` باشد.
- Access Token کوتاه‌مدت و Refresh Token بلندمدت باشد.
- فقط کاربر احراز هویت شده بتواند به Todoهای خودش دسترسی داشته باشد.

---

## بخش ۲ — مدیریت Todo

### مدل Todo

```python
id
title
description
is_completed
priority        # low, medium, high (use enum)
due_date
owner_id
created_at
updated_at
```

---

## بخش ۳ — CRUD کامل

### Endpoint ها

| متد | آدرس | توضیح |
|---|---|---|
| POST | /api/v1/todos | ایجاد تسک |
| GET | /api/v1/todos | دریافت لیست |
| GET | /api/v1/todos/{id} | دریافت یک تسک |
| PATCH | /api/v1/todos/{id} | ویرایش جزئی |
| PUT | /api/v1/todos/{id} | جایگزینی کامل |
| DELETE | /api/v1/todos/{id} | حذف |

### نکات

- کاربر فقط Todoهای خودش را ببیند.
- در صورت نبودن رکورد، `404` برگردانده شود.
- در صورت دسترسی غیرمجاز، `403` برگردانده شود.

---

## بخش ۴ — جستجو و فیلتر

### Query Parameters

#### جستجو

```http
GET /api/v1/todos?q=meeting
```

فیلدهای جستجو:

- `title`
- `description`

---

### فیلتر وضعیت

```http
GET /api/v1/todos?is_completed=true
```

---

### فیلتر اولویت

```http
GET /api/v1/todos?priority=high
```

---

### فیلتر بازه زمانی

```http
GET /api/v1/todos?due_from=2026-08-01&due_to=2026-08-31
```

---

## بخش ۵ — مرتب‌سازی (Sorting)

### پارامترها

```http
GET /api/v1/todos?sort_by=created_at&order=desc
```

فیلدهای مجاز:

- `created_at`
- `updated_at`
- `due_date`
- `priority`
- `title`

اگر فیلد نامعتبر بود:

```json
{
  "detail": "invalid sort field"
}
```

---

## بخش ۶ — صفحه‌بندی

### پارامترها

```http
GET /api/v1/todos?page=1&page_size=10
```

### پاسخ استاندارد

```json
{
  "results": [],
  "page": 1,
  "page_size": 10,
  "total": 57,
  "pages": 6
}
```

---

## بخش ۷ — اعتبارسنجی

### قوانین

#### title

- اجباری
- حداقل ۳ کاراکتر
- حداکثر ۱۰۰ کاراکتر

#### description

- اختیاری
- حداکثر ۱۰۰۰ کاراکتر

#### due_date

- نباید در گذشته باشد.

نمونه:

```python
@field_validator("due_date")
@classmethod
def validate_due_date(cls, value):
    if value and value < datetime.utcnow():
        raise ValueError("due date cannot be in the past")
    return value
```

---

## بخش ۸ — مدیریت خطا

### ساختار پاسخ خطا

```json
{
  "success": false,
  "error": {
    "code": "TODO_NOT_FOUND",
    "message": "Todo not found"
  }
}
```

### Custom Exception ها

- `TodoNotFoundException`
- `PermissionDeniedException`
- `InvalidSortFieldException`
- `AuthenticationException`

---

## بخش ۹ — لایه Service و Repository

### Repository

فقط مسئول ارتباط با دیتابیس:

```python
class TodoRepository:
    async def create(self, db, todo):
        ...

    async def get_by_id(self, db, todo_id):
        ...

    async def list(self, db, filters):
        ...
```

---

### Service

شامل Business Logic:

```python
class TodoService:
    async def create_todo(self, user, data):
        ...

    async def complete_todo(self, user, todo_id):
        ...
```

---

## بخش ۱۰ — مستندسازی API

### الزامات Swagger

برای هر Endpoint موارد زیر مشخص شود:

- summary
- description
- response_model
- status_code
- examples

نمونه:

```python
@router.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo"
)
```

---

## بخش ۱۱ — Migration

### تسک‌ها

- ایجاد Migration اولیه
- Migration افزودن فیلد `priority`
- Migration افزودن Index روی `owner_id`
- Migration افزودن Index ترکیبی:

```sql
(owner_id, is_completed)
```

---

## بخش ۱۲ — تست

### تست‌های اجباری

#### Auth

- ثبت‌نام موفق
- ثبت‌نام با ایمیل تکراری
- ورود موفق
- ورود با رمز اشتباه

#### Todo

- ایجاد تسک
- دریافت لیست
- فیلتر completed
- جستجو
- مرتب‌سازی
- حذف
- جلوگیری از دسترسی به تسک کاربر دیگر

---

## بخش ۱۳ — ویژگی‌های تکمیلی (اختیاری)

### Soft Delete

فیلد:

```python
deleted_at
```

به جای حذف واقعی:

```python
todo.deleted_at = datetime.utcnow()
```

---

### Bulk Operations

```http
PATCH /api/v1/todos/bulk-complete
DELETE /api/v1/todos/bulk-delete
```

---

### Statistics Endpoint

```http
GET /api/v1/todos/stats
```

پاسخ:

```json
{
  "total": 20,
  "completed": 12,
  "pending": 8,
  "overdue": 3
}
```

---

## تعریف نهایی تسک (نسخه‌ای که می‌توان به دانشجو داد)

### Minimum Requirements

- [ ] Layerd architecture
- [ ] JWT Authentication
- [ ] CRUD کامل Todo
- [ ] Ownership permissions
- [ ] Search
- [ ] Filter
- [ ] Sort
- [ ] Pagination
- [ ] Validation
- [ ] Custom Exception Handler
- [ ] Alembic Migration
- [ ] Swagger Documentation
- [ ] 10 Tests at least

---

## سطح‌بندی پروژه

### سطح ۱ — Junior

- Register/Login
- CRUD ساده
- Pagination

### سطح ۲ — Mid-Level

- Search + Filter + Sort
- Service/Repository Layer
- Custom Exceptions
- تست

### سطح ۳ — Senior

- Refresh Token Rotation
- Soft Delete
- Bulk Operations
- Index Optimization
- Docker + CI/CD
- Rate Limiting
- Structured Logging
- Observability (Prometheus / OpenTelemetry)

---

## خروجی مورد انتظار

دانشجو باید در پایان بتواند:

- یک **REST API واقعی** طراحی کند.
- ساختار مناسب پروژه FastAPI را پیاده‌سازی کند.
- احراز هویت مبتنی بر JWT را به صورت اصولی انجام دهد.
- APIهای قابل جستجو، فیلتر و مرتب‌سازی طراحی کند.
- خطاها و پاسخ‌ها را به صورت استاندارد مدیریت کند.
- پروژه را برای توسعه و نگهداری آینده آماده نگه دارد.