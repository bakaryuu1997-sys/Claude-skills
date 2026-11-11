# Chuẩn cho stack khác (Java/Kotlin, PHP, Go, .NET…)

Dùng khi `tech_stack.backend` không phải TypeScript hoặc Python. Nguyên tắc chung (mục 0) áp dụng cho mọi stack; bảng dưới cho biết công cụ tương ứng cần kiểm tra. Tên công cụ là gợi ý — chỉ dùng công cụ đã có trong dự án.

## 0. Nguyên tắc chung (mọi stack)
- Không nuốt lỗi (catch rỗng, bỏ qua kết quả trả về).
- Kiểu tường minh ở ranh giới API; validate tại biên trước khi vào service.
- Lỗi nghiệp vụ: `statusCode` + `code` `ERR-<DOMAIN>-<NNN>` (lấy từ Error Map của /b3-detail-design) + `message` an toàn.
- Ghi nhiều bảng / log lịch sử → transaction.
- Secret và cấu hình production: fail-fast khi thiếu, không có giá trị mặc định.

## 1. Bảng công cụ tương ứng

| Stack | Type/Schema | Transaction | Lỗi | Lint / Coverage (gợi ý) |
|---|---|---|---|---|
| Java/Kotlin (Spring) | Bean Validation (`@Valid`), record/data class | `@Transactional` | `@ControllerAdvice` + exception có `code` | Checkstyle/Detekt, JaCoCo |
| PHP (Laravel) | Form Request, `Validator` | `DB::transaction()` | `Handler` + exception có `code` | PHPStan/Larastan, PHPUnit `--coverage` |
| Go | struct + validator tag | `tx := db.Begin()` | error wrapping `%w`, mã lỗi sentinel | `golangci-lint`, `go test -cover` |
| .NET (C#) | FluentValidation / DataAnnotations | `TransactionScope` / EF `BeginTransaction` | `ProblemDetails` + mã lỗi | Roslyn analyzers, `dotnet test --collect` |

## 2. Việc cần làm khi áp dụng
- Ghi rõ công cụ thật của dự án (đọc file cấu hình: `pom.xml`, `composer.json`, `go.mod`, `*.csproj`) vào `ENGINEERING_STANDARDS.md`. Không có → `[CẦN ĐIỀN]`.
- Không suy đoán phiên bản framework; lấy từ manifest.
