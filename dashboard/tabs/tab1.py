import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def render_tab1(df):
    st.markdown("## 🏠 Tổng quan Thị trường & Cấu trúc Ngành hàng")
    st.markdown("*Cái nhìn vĩ mô về quy mô thị trường, sự phân bổ các thể loại và uy tín của các 'ông lớn' (Nhà xuất bản).*")
    
    st.divider()

    # ==========================================
    # KHỐI 1: KPI CARDS (Thẻ thông tin nổi bật)
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="📚 Tổng số Sách", value=f"{len(df):,}")
    with col2:
        st.metric(label="📈 Tổng Doanh số", value=f"{df['quantity_sold'].sum():,}")
    with col3:
        st.metric(label="💰 Giá trung bình", value=f"{int(df['price'].mean()):,} ₫")
    with col4:
        st.metric(label="⭐ Đánh giá trung bình", value=f"{df['rating_average'].mean():.1f}/5")

    st.markdown("---")

    # ==========================================
    # KHỐI 2: ROW 1 (Biểu đồ 1 & Biểu đồ 2)
    # ==========================================
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        # Biểu đồ 1: Treemap Thị phần doanh số
        st.subheader("Thị phần Doanh số theo Thể loại")
        df_treemap = df.groupby('crawl_category')['quantity_sold'].sum().reset_index()
        fig1 = px.treemap(
            df_treemap, 
            path=['crawl_category'], 
            values='quantity_sold',
            color='quantity_sold',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("Treemap thể hiện mức độ đóng góp doanh số. Diện tích ô càng lớn, doanh thu của thể loại càng cao.")

    with row1_col2:
        # Biểu đồ 2: Boxplot Phân phối giá
        st.subheader("Phân phối Giá theo Danh mục")
        # Lọc bớt sách vượt quá 1 triệu để boxplot dễ nhìn hơn (có thể điều chỉnh)
        df_box = df[df['price'] <= 1_000_000].copy()

        # Gom các danh mục English nhỏ vào nhóm chung để biểu đồ rõ ràng hơn
        df_box['category_display'] = df_box['crawl_category'].replace({
            "English - Children's Books": 'Sách Tiếng Anh',
            'English - Fiction': 'Sách Tiếng Anh'
        })

        # Chỉ hiển thị các danh mục có đủ dữ liệu để tránh bảng quá dày
        top_categories = df_box['category_display'].value_counts().nlargest(6).index
        df_box = df_box[df_box['category_display'].isin(top_categories)]

        # Sắp xếp danh mục theo giá trung vị để dễ so sánh
        category_order = df_box.groupby('category_display')['price'].median().sort_values().index

        fig2 = px.box(
            df_box,
            x='price',
            y='category_display',
            color='category_display',
            category_orders={'category_display': category_order},
            labels={'price': 'Giá bán (VNĐ)', 'category_display': 'Thể loại'}
        )
        fig2.update_layout(showlegend=False, xaxis_title="Giá bán (VNĐ)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Boxplot thể hiện phân phối giá theo nhóm danh mục chính. Các nhóm English nhỏ được gom chung để biểu đồ dễ đọc hơn.")

    st.markdown("---")

    # ==========================================
    # KHỐI 3: ROW 2 (Biểu đồ 3 & Biểu đồ 4)
    # ==========================================
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        # Biểu đồ 3: Top 10 NXB theo chỉ số tổng hợp
        st.subheader("Top 10 NXB Uy tín nhất")
        # Xử lý tính toán Publisher Score
        df_nxb = df.dropna(subset=['publisher_name'])
        pub_stats = df_nxb.groupby('publisher_name').agg({
            'product_id': 'count',
            'rating_average': 'median',
            'review_count': 'sum',
            'quantity_sold': 'sum'
        }).reset_index()
        
        # Chỉ xét NXB có trên 10 sản phẩm
        pub_stats = pub_stats[pub_stats['product_id'] >= 10]
        
        # Tính công thức SMART (Mục tiêu 3.2): Score = median(rating) * log1p(review_sum) * log1p(sales_sum)
        pub_stats['publisher_score'] = (
            pub_stats['rating_average'] * 
            np.log1p(pub_stats['review_count']) * 
            np.log1p(pub_stats['quantity_sold'])
        )
        
        top10_nxb = pub_stats.nlargest(10, 'publisher_score').sort_values('publisher_score', ascending=True)
        
        fig3 = px.bar(
            top10_nxb, 
            x='publisher_score', 
            y='publisher_name', 
            orientation='h',
            text=[f"{x:.1f}" for x in top10_nxb['publisher_score']],
            labels={'publisher_score': 'Điểm uy tín tổng hợp', 'publisher_name': 'Nhà xuất bản'},
            color='publisher_score',
            color_continuous_scale='Viridis' # Chuẩn Accessibility Tab 4 sau này
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(yaxis_title="", margin=dict(l=0, r=0, t=0, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Điểm uy tín kết hợp: Điểm đánh giá (Rating) + Số lượng chia sẻ (Review) + Doanh số đạt được.")

    with row2_col2:
        # Biểu đồ 4: Donut Chart Ngôn ngữ
        st.subheader("Sách Tiếng Anh vs Tiếng Việt")
        # Điền missing = Vietnamese nếu cột bị null
        df['book_language'] = df['book_language'].fillna('Vietnamese')
        df_lang = df.groupby('book_language')['product_id'].count().reset_index()
        df_lang.columns = ['Ngôn ngữ', 'Số lượng']
        
        fig4 = px.pie(
            df_lang, 
            values='Số lượng', 
            names='Ngôn ngữ', 
            hole=0.4,
            color='Ngôn ngữ',
            color_discrete_map={'Vietnamese': '#1f77b4', 'English': '#ff7f0e'}
        )
        # Thiết kế cho chuẩn Donut chart đẹp mắt
        fig4.update_traces(textposition='inside', textinfo='percent+label')
        fig4.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("Donut Chart trực quan sự chênh lệch thị phần lượng số sách ngoại văn so với sách nội.")

