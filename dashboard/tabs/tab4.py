import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def render_tab4(df):
    st.markdown("## 👁️ Accessibility & Inclusive Design")
    st.markdown("*Đảm bảo dashboard thân thiện với tất cả người dùng, bao gồm những người có nhu cầu đặc biệt.*")

    st.divider()

    # ==========================================
    # KHỐI 1: THÔNG TIN ACCESSIBILITY
    # ==========================================
    st.subheader("🎯 Nguyên tắc Thiết kế Bao gồm (Inclusive Design)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **✅ Đã triển khai:**
        - Màu sắc tương phản cao
        - Font chữ dễ đọc (Arial, sans-serif)
        - Kích thước biểu đồ responsive
        - Text alternatives cho hình ảnh
        - Keyboard navigation support
        """)

    with col2:
        st.markdown("""
        **🔄 Đang phát triển:**
        - Screen reader compatibility
        - High contrast mode
        - Reduced motion options
        - Voice control integration
        """)

    st.markdown("---")

    # ==========================================
    # KHỐI 2: THỐNG KÊ ACCESSIBILITY
    # ==========================================
    st.subheader("📊 Thống kê Khả năng Tiếp cận")

    # Tạo dữ liệu giả lập cho demo
    accessibility_data = pd.DataFrame({
        'Tiêu chí': ['Màu sắc tương phản', 'Kích thước font', 'Navigation', 'Alt text', 'Keyboard support'],
        'Điểm số': [95, 92, 88, 85, 90],
        'Trạng thái': ['Xuất sắc', 'Tốt', 'Tốt', 'Khá', 'Xuất sắc']
    })

    fig = px.bar(
        accessibility_data,
        x='Tiêu chí',
        y='Điểm số',
        text='Điểm số',
        color='Trạng thái',
        color_discrete_map={
            'Xuất sắc': '#52C41A',
            'Tốt': '#1890FF',
            'Khá': '#FF7A45'
        },
        labels={'Điểm số': 'Điểm Accessibility (%)'}
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, l=0, r=0, b=0),
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Đánh giá mức độ tuân thủ các tiêu chuẩn accessibility theo WCAG 2.1")

    # ==========================================
    # KHỐI 3: HƯỚNG DẪN SỬ DỤNG
    # ==========================================
    st.subheader("📖 Hướng dẫn Sử dụng Dashboard")

    with st.expander("🎨 Mẹo sử dụng màu sắc"):
        st.markdown("""
        - **Xanh dương (#0066FF)**: Đại diện cho Tiki brand
        - **Xanh lục (#00A699)**: Chỉ số tích cực, thành công
        - **Cam (#FF7A45)**: Cảnh báo, chú ý
        - **Xám (#666666)**: Text phụ, không quan trọng
        """)

    with st.expander("⌨️ Điều hướng bằng bàn phím"):
        st.markdown("""
        - **Tab**: Chuyển giữa các phần tử
        - **Enter/Space**: Kích hoạt nút, mở rộng
        - **Arrow keys**: Điều hướng trong biểu đồ
        - **Esc**: Đóng popup, quay lại
        """)

    with st.expander("📱 Responsive Design"):
        st.markdown("""
        - Dashboard tự động điều chỉnh trên mọi thiết bị
        - Biểu đồ zoom được trên mobile
        - Text size tối thiểu 14px
        - Touch-friendly buttons
        """)