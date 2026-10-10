# Chuẩn Mực Kiến Trúc Ứng Dụng Frontend Doanh Nghiệp (Enterprise Frontend Architecture Standards)

Tài liệu này định nghĩa cấu trúc thư mục, quy chuẩn tách lớp, quản lý trạng thái và nguyên tắc component cho các ứng dụng Web Frontend hiện đại (Next.js 14 App Router / React 18+).

---

## 1. Mô hình Phân Lớp theo Nghiệp Vụ (Feature-Driven Architecture)

Để tránh tình trạng thư mục `components/` biến thành "bãi rác" chứa hàng trăm component không phân biệt nghiệp vụ, mọi dự án Frontend BẮT BUỘC tổ chức theo kiến trúc hướng tính năng (Feature-Driven):

```
frontend/src/
├── app/                      # Next.js App Router (Layouts, Pages, Routes)
│   ├── (auth)/login/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx        # Shell layout (Sidebar + Header)
│   │   ├── contracts/page.tsx
│   │   ├── invoices/page.tsx
│   │   └── payments/page.tsx
├── components/               # Generic UI Primitives (Re-usable toàn dự án)
│   ├── ui/                   # shadcn/ui components (Button, Input, Dialog, Table...)
│   └── shared/               # Compound layout components (PageHeader, EmptyState, Shimmer...)
├── features/                 # Modules Nghiệp Vụ Chuyên Biệt
│   ├── contracts/
│   │   ├── api/              # useContractsQuery.ts, useCreateContractMutation.ts
│   │   ├── components/       # ContractTable.tsx, ContractFormModal.tsx, ProrationBadge.tsx
│   │   ├── hooks/            # useContractForm.ts, useContractFilter.ts
│   │   ├── types/            # contract.dto.ts, contract.schema.ts
│   │   └── index.ts          # Public API export của feature
│   ├── invoices/
│   ├── payments/
│   └── customers/
├── lib/                      # Core Utilities & Infrastructure
│   ├── api-client.ts         # Centralized Axios/Fetch Wrapper with Interceptors
│   ├── auth-store.ts         # User session & Token store (Zustand)
│   └── formatters.ts         # Currency, Date, Percentage formatters
└── config/                   # Constants, Envs, Route definitions
```

---

## 2. Quy Chuẩn Đặt Tên & Component Hierarchy

1. **Atoms / Primitives (`components/ui/`):**
   - Chỉ chứa các phần tử UI đơn giản, không mang logic nghiệp vụ (ví dụ: `Button`, `Badge`, `Avatar`, `Input`).
   - Sử dụng Radix UI primitives hoặc Tailwind variants (`cva`).
2. **Molecules / Features (`features/<module>/components/`):**
   - Ghép nối các UI primitives để phục vụ một chức năng nghiệp vụ cụ thể (ví dụ: `ContractStatusBadge`, `ZenginUploadDropzone`).
   - Có thể chứa local UI state (mở/đóng dropdown, tooltip).
3. **Organisms / Views (`features/<module>/components/<Name>View.tsx`):**
   - Chứa bảng dữ liệu hoàn chỉnh, form nhiều bước hoặc dashboard summary cards.
   - Kết nối với Custom Hooks để lấy dữ liệu từ API.
4. **Pages (`app/**/page.tsx`):**
   - Mỏng (Thin Controllers). Chỉ làm nhiệm vụ nạp Feature View và thiết lập Metadata/Breadcrumb.

---

## 3. Quản Lý Trạng Thái (State Management Protocol)

* **Server State (Dữ liệu từ API):** 100% quản lý bằng **TanStack Query (React Query)**. Cấm sao chép dữ liệu API vào Redux/Zustand toàn cục gây lỗi Out-of-sync cache.
* **Client UI State (Modal mở/đóng, Active tab):** Sử dụng `useState` nội bộ trong component.
* **URL State (Trang hiện tại, Từ khóa tìm kiếm, Bộ lọc):** 100% lưu trên Query Parameters của URL (`?page=2&status=ACTIVE&search=FPT`). Giúp người dùng có thể refresh trang hoặc chia sẻ link mà không mất trạng thái tìm kiếm.
* **Global Session State (User Profile, Access Token, Tenant ID):** Quản lý bằng Zustand hoặc Context API có persist vào Secure Cookie / Storage.
