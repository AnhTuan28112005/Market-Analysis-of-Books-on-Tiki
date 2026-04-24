import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def render_tab2(df):
    st.markdown("## 📈 Động lực Doanh số & Hiệu quả Marketing")
    st.markdown("*Đi sâu phân tích hành vi mua sắm: Sự tác động của mức Giảm giá đến Doanh thu và góc độ Chất lượng sản phẩm thực tế.*")
    
    st.divider()

    # ==========================================
    # KHỐI 1: ROW 1 (Ngưỡng Giảm giá & Giá vs Chất lượng)
    # ==========================================
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Ngưỡng Giảm giá 'Vàng' thu hút khách")
        
        # Chia khoảng (binning) cho cột discount
        bins = [0, 10, 20, 30, 40, 50, 60, 100]
        labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '>60%']
        df['discount_bin'] = pd.cut(df['discount_rate'], bins=bins, labels=labels, include_lowest=True)
        
        # Tính doanh số trung vị theo từng nhóm discount
        discount_impact = df.groupby('discount_bin')['quantity_sold'].median().reset_index()
        
        fig5 = px.bar(
            discount_impact,
            x='discount_bin',
            y='quantity_sold',
            text_auto=True,
            color='quantity_sold',
            color_continuous_scale='Teal',
            labels={'discount_bin': 'Mức chiết khấu (%)', 'quantity_sold': 'Doanh số Trung vị'}
        )
        fig5.update_traces(textposition='outside')
        fig5.update_layout(coloraxis_showscale=False, margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig5, use_container_width=True)
        st.caption("Biểu đồ Cột: Chỉ ra mức chiết khấu nào mang lại mức doanh số bán trung bình ấn tượng nhất.")

    with row1_col2:
        st.subheader("Cấu trúc Doanh số: Giá và Chiết khấu")
        
        # Phân nhóm mức giá
        _, bins_price = pd.qcut(df['price'], q=4, retbins=True)
        labels_price = [
            f"Giá rẻ (< {bins_price[1]/1000:,.0f}k)",
            f"Phổ thông ({bins_price[1]/1000:,.0f}k - {bins_price[2]/1000:,.0f}k)",
            f"Trung cấp ({bins_price[2]/1000:,.0f}k - {bins_price[3]/1000:,.0f}k)",
            f"Cao cấp (> {bins_price[3]/1000:,.0f}k)"
        ]
        df['price_tier'] = pd.cut(df['price'], bins=bins_price, labels=labels_price, include_lowest=True)
        
        # Phân nhóm Chiết khấu
        bins_disc = [-1, 0, 20, 40, 100]
        labels_disc = ['Nguyên giá (0%)', 'Giảm nhẹ (1-20%)', 'Giảm vừa (21-40%)', 'Giảm sâu (>40%)']
        df['discount_tier'] = pd.cut(df['discount_rate'], bins=bins_disc, labels=labels_disc, include_lowest=True)
        
        df_sun = df.dropna(subset=['price_tier', 'discount_tier', 'quantity_sold'])
        
        #  Vẽ Sunburst Chart
        fig6 = px.sunburst(
            df_sun,
            path=['price_tier', 'discount_tier'],
            values='quantity_sold',              
            color='rating_average',               
            color_continuous_scale='RdBu',    
            color_continuous_midpoint=4.5,       
            labels={'price_tier': 'Phân khúc Giá', 'discount_tier': 'Mức Giảm', 'rating_average': 'Rating'}
        )
        fig6.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        
        st.plotly_chart(fig6, width='stretch')
        st.caption("Sunburst Chart: Phân khúc giá kết hợp với chiến lược giảm giá nào đang tạo ra doanh số (diện tích) lớn nhất và sự hài lòng (màu sắc xanh) cao nhất?")
    # ==========================================
    # KHỐI 2: ROW 2 (Tương quan & Tiềm năng ẩn)
    # ==========================================
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Ma trận Tương quan Đa biến")
        
        # Tính toán ma trận tương quan Spearman 
        corr_cols = ['price', 'discount_rate', 'rating_average', 'review_count', 'image_count', 'quantity_sold']
        corr_matrix = df[corr_cols].corr(method='spearman')
        
        corr_matrix.columns = ['Giá', 'Giảm giá', 'Rating', 'Review', 'Số hình ảnh', 'Doanh số']
        corr_matrix.index = corr_matrix.columns
        
        fig7 = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            color_continuous_scale='RdBu_r',  # Red to Blue
            zmin=-1, zmax=1
        )
        fig7.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig7, use_container_width=True)
        st.caption("Heatmap: Cho biết giữa số lượng Review, mức độ Giảm giá và điểm Rating, đâu mới là động lực thúc đẩy Sale mạnh nhất.")

    with row2_col2:
        st.subheader("Truy tìm Sách 'Tiềm Năng Ẩn'")
        
        # Thuật toán tìm Tiềm Năng Ẩn đã được tinh chỉnh
        # Sales rất cao (Top 15%) nhưng Review dưới mức trung bình (Bottom 50%)
        p85_sales = df['quantity_sold'].quantile(0.85)
        p50_review = df['review_count'].median() 
        
        df['is_hidden_gem'] = (df['quantity_sold'] >= p85_sales) & (df['review_count'] <= p50_review)
        
        # Chuyển đổi nhãn để vẽ đẹp
        df['Phân loại'] = df['is_hidden_gem'].map({True: 'Tiềm năng Ads (Sales Cao - Ít Review)', False: 'Nhóm Bình thường'})
        
        # Phóng to kích thước các hạt dữ liệu Tiềm Năng để nó đập vào mắt
        df['Kích thước hạt'] = df['is_hidden_gem'].map({True: 15, False: 4})
        
        fig8 = px.scatter(
            df,
            x='review_count',
            y='quantity_sold',
            color='Phân loại',
            size='Kích thước hạt', # Apply kích thước
            hover_name='name',
            opacity=0.7,
            color_discrete_map={'Tiềm năng Ads (Sales Cao - Ít Review)': 'red', 'Nhóm Bình thường': 'lightgray'},
            labels={'review_count': 'Số lượng Review', 'quantity_sold': 'Doanh số thực tế (Sales)'}
        )
        
        # Giới hạn trục & Thêm Padding (khoảng đệm âm) để số 0 không bị dính vào vách lề trái
        max_x = df['review_count'].quantile(0.95)
        max_y = df['quantity_sold'].quantile(0.95)
        
        # X lùi về mức âm 5% của max_x để tạo khoảng trống
        fig8.update_xaxes(range=[-(max_x * 0.05), max_x])
        fig8.update_yaxes(range=[-(max_y * 0.05), max_y])
        
        fig8.update_layout(margin=dict(t=0, l=0, r=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99))
        st.plotly_chart(fig8, use_container_width=True)
        st.caption("Scatter Plot Highlight: Các chấm đỏ bự là sách có nội lực rất tốt nhưng chưa chạy Marketing. Việc nới trục giúp các sản phẩm 0 review hiển thị rõ ràng.")
