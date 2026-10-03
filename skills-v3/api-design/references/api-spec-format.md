# FORMAT `[TênDựÁn]_api_spec.json` — nguồn trung gian cho Postman + OpenAPI (v3.4.0)

> Đây là NGUỒN DỮ LIỆU DUY NHẤT cho `gen_postman.py` và `gen_openapi.py`.
> Mọi thay đổi endpoint → sửa file này → chạy lại 2 script. KHÔNG sửa tay 2 file output.
> File này LƯU vào workspace cùng các output khác (dùng cho re-run diff).

```json
{
  "project": "Tên dự án",
  "version": "1.0.0",
  "base_url": "http://localhost:3000/api/v1",
  "servers": [
    { "url": "http://localhost:3000/api/v1", "description": "Local" },
    { "url": "https://staging.example.com/api/v1", "description": "Staging" }
  ],
  "auth": {
    "login_path": "/auth/login",
    "token_field": "accessToken",
    "login_body_example": { "email": "test@example.com", "password": "test123" }
  },
  "modules": [
    {
      "name": "Auth",
      "endpoints": [
        {
          "method": "POST",
          "path": "/auth/login",
          "summary": "Đăng nhập bằng tài khoản công ty",
          "auth_required": false,
          "middleware": ["RateLimit(10/min)"],
          "query": [ { "name": "page", "type": "integer", "required": false, "example": 1 } ],
          "body_example": { "email": "test@example.com", "password": "test123" },
          "body_schema": null,
          "success_status": 200,
          "response_example": { "accessToken": "eyJ...", "user": { "id": 1 } },
          "errors": [
            { "status": 401, "code": "INVALID_CREDENTIALS", "message": "Tài khoản không hợp lệ" }
          ]
        }
      ]
    }
  ]
}
```

Quy tắc:
- `method` + `path` = khóa định danh endpoint (trùng với thuật toán re-run của SKILL.md).
- `auth_required: true` → gen_postman tự thêm header `Authorization: Bearer {{accessToken}}`; gen_openapi áp security mặc định.
- `auth.login_path` có giá trị → gen_postman tự tạo folder "⚙️ Setup & Auth" với test-script lưu token.
- `body_schema` để `null` → gen_openapi tự suy schema từ `body_example` (đủ dùng; cần schema chặt hơn thì điền tay).
- Path param viết dạng `{param}` → gen_openapi tự sinh parameters.
- Mọi giá trị ví dụ phải là dữ liệu THẬT của dự án (quy tắc VÍ DỤ MINH HỌA của bộ skill).
