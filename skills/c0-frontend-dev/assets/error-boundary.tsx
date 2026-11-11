'use client';

// Mẫu ErrorBoundary cục bộ: cô lập khối lỗi, không làm trắng trang (xem SKILL.md c0, trụ cột 9).
// Dùng bọc từng khu vực nội dung/feature, không chỉ bọc toàn app.
import { Component, type ReactNode } from 'react';

type Props = { children: ReactNode; label?: string; onRetry?: () => void };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: { componentStack?: string | null }) {
    // Gửi về hệ thống log/monitoring của dự án; KHÔNG hiển thị stack trace cho người dùng.
    console.error('[ErrorBoundary]', this.props.label ?? 'block', error.message, info.componentStack);
  }

  private retry = () => {
    this.setState({ error: null });
    this.props.onRetry?.();
  };

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div role="alert" className="rounded-md border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <p className="font-medium text-slate-900 dark:text-slate-100">
          {/* Thông điệp hiển thị theo settings.languages.client_facing; [CẦN ĐIỀN] nếu chưa có bản dịch */}
          Không tải được khu vực này.
        </p>
        <button type="button" onClick={this.retry} className="mt-3 rounded-md border px-3 py-1.5 text-sm">
          Thử lại tác vụ
        </button>
      </div>
    );
  }
}
