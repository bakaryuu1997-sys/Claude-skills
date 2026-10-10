# Quy Chuẩn Tích Hợp API Sống & Chống Mock Giả Lập (Live API Wiring & Anti-Mock Protocol)

Tài liệu này hướng dẫn cách cấu hình API Client, xử lý Token Interceptors, phân giải Error Envelope và quản lý kết nối thật với Backend NestJS/Express.

---

## 1. Mẫu Cấu Hình Typed API Client Chuẩn Enterprise (`src/lib/api-client.ts`)

```typescript
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Tự động đính kèm Token và Tenant ID
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    const tenantId = typeof window !== 'undefined' ? localStorage.getItem('x_tenant_id') : null;

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (tenantId && config.headers) {
      config.headers['x-tenant-id'] = tenantId;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response Interceptor: Xử lý Silent Refresh Token và Chuẩn hóa Error Envelope
apiClient.interceptors.response.use(
  (response) => response.data, // Tự động unwrap data envelope
  async (error: AxiosError<{ success: boolean; error: { code: string; message: string; statusCode: number } }>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Xử lý 401 Unauthorized và refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token available');

        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, { refreshToken });
        localStorage.setItem('access_token', data.accessToken);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshErr) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login?expired=true';
        }
        return Promise.reject(refreshErr);
      }
    }

    // Trích xuất error message từ backend envelope
    const serverMessage = error.response?.data?.error?.message || error.message || 'Lỗi kết nối máy chủ';
    return Promise.reject(new Error(serverMessage));
  },
);
```

---

## 2. Quy Chuẩn Data Fetching với TanStack Query

Mỗi entity nghiệp vụ (ví dụ Contract) bắt buộc có một hook query và các hooks mutation tương ứng:

```typescript
// features/contracts/api/useContractsQuery.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ContractDto, ContractFilterParams } from '../types/contract.dto';

export function useContractsQuery(params: ContractFilterParams) {
  return useQuery({
    queryKey: ['contracts', params],
    queryFn: async (): Promise<{ data: ContractDto[]; total: number }> => {
      const response = await apiClient.get('/contracts', { params });
      return response.data;
    },
    staleTime: 30 * 1000, // Dữ liệu coi là mới trong 30 giây
  });
}
```

```typescript
// features/contracts/api/useCreateContractMutation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { CreateContractDto, ContractDto } from '../types/contract.dto';

export function useCreateContractMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CreateContractDto): Promise<ContractDto> => {
      const response = await apiClient.post('/contracts', payload);
      return response.data;
    },
    onSuccess: () => {
      // Tự động làm mới cache danh sách hợp đồng
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}
```

---

## 3. Quy Tắc Anti-Mock (Tuyệt Đối Cấm Dữ Liệu Tĩnh Trong Code Production)

1. **Không tạo file `mock-data.ts` trong thư mục `src/`**: Mọi dữ liệu phải chảy từ Backend API.
2. **Xử lý Skeleton Loader**: Khi `isLoading === true`, render bộ khung Shimmer Table/Card có số lượng dòng giả lập hiệu ứng đang tải thay vì để trắng màn hình.
3. **Xử lý Empty State**: Khi mảng dữ liệu rỗng (`data.length === 0`), render UI thân thiện hướng dẫn người dùng tạo mới.
4. **Xử lý Error State**: Khi `isError === true`, hiển thị Alert với thông điệp từ API và nút bấm `refetch()`.
