# 📊 Kế hoạch Đồ án Lab 01
## Phân tích Thị trường Sách trực tuyến trên Tiki
**Môn học:** Trực quan hóa Dữ liệu | **Nhóm:** 5 thành viên

---

## 1. Tổng quan Dự án

### Đề tài
> **"Phân tích thị trường Sách trực tuyến trên sàn Tiki — Yếu tố ảnh hưởng đến Doanh số và Trải nghiệm Khách hàng"**

### Dataset thực tế
| Thông tin | Giá trị |
|---|---|
| Nguồn | Tiki Public API (crawl thực tế — không dùng Kaggle) |
| Số sản phẩm | ~8.300 sản phẩm sách |
| Số đặc trưng | 25 cột |
| Thể loại | 6 thể loại tiếng Việt + 4 tiếng Anh |
| Thời điểm | Tháng 4/2026 |
| File | `data/raw/tiki_books_raw.csv` |

### Công nghệ sử dụng
| Giai đoạn | Thư viện |
|---|---|
| Thu thập | `requests`, `tqdm`, `json` |
| Xử lý | `pandas`, `numpy` |
| Trực quan hóa | `plotly`, `seaborn`, `matplotlib` |
| Machine Learning | `scikit-learn` |
| Dashboard | `streamlit` |

---

## 2. Cấu trúc thư mục

```
lab1/
├── data/
│   ├── raw/
│   │   ├── tiki_books_raw.csv          ✅ DONE (8.300+ dòng)
│   │   └── product_ids_checkpoint.json ✅ DONE
│   └── processed/
│       └── tiki_books_clean.csv        ← Cần làm (Notebook 02)
│
├── notebooks/
│   ├── 01_crawl_data.ipynb             ✅ DONE
│   ├── 02_preprocessing.ipynb          ← Cần làm
│   └── 03_eda.ipynb                    ← Cần làm
│
├── dashboard/
│   └── app.py                          ← Cần làm (sau EDA)
│
├── requirements.txt
├── README.md
└── implementation_plan.md              ← File này
```

---

## 3. Mô tả Dataset

### Các cột dữ liệu chính

| Cột | Ý nghĩa | Kiểu | Dùng cho |
|---|---|---|---|
| `product_id` | ID sản phẩm (khóa chính) | int | Dedup |
| `name` | Tên sách | str | Filter |
| `price` | Giá bán hiện tại (VNĐ) | int | Phân tích giá |
| `list_price` | Giá gốc trước giảm (VNĐ) | int | Tính tiết kiệm |
| `discount_rate` | % chiết khấu | float | MT 1.2 |
| `rating_average` | Điểm đánh giá trung bình (0–5) | float | MT 2.1 |
| `review_count` | Số lượt đánh giá | int | MT 2.1, 2.2 |
| `quantity_sold` | Số lượng bán trong kỳ | int | **Biến mục tiêu** |
| `all_time_sold` | Tổng doanh số lịch sử | int | MT 5.1 |
| `seller_name` | Tên người bán | str | MT 5.1 |
| `seller_type` | Loại người bán | str | MT 5.1 |
| `author_name` | Tác giả | str | MT 3.2 |
| `publisher_name` | Nhà xuất bản | str | MT 3.2 |
| `cover_type` | Loại bìa (mềm/cứng) | str | MT 4.1 |
| `num_pages` | Số trang | int | MT 4.1 |
| `pub_date` | Ngày xuất bản | str | Phân tích xu hướng |
| `image_count` | Số ảnh trong listing | int | EDA |
| `short_description` | Mô tả ngắn | str | Word Cloud |
| `category_name` | Thể loại cụ thể (cấp lá) | str | Phân tích |
| `crawl_category` | Thể loại cha (10 nhóm) | str | **Nhóm chính** |
| `book_language` | Ngôn ngữ (Vietnamese/English) | str | MT 4.2 |
| `inventory_status` | Tình trạng kho | str | Filter |
| `product_url` | URL sản phẩm | str | Tham khảo |
| `crawl_time` | Thời điểm crawl | str | Metadata |

---

## 4. Phân công & 10 Mục tiêu SMART

---

### 👤 Thành viên 1 — Phân tích Cấu trúc Giá & Chiết khấu

---

#### 🎯 Mục tiêu 1.1 — Phân bố giá theo thể loại

**Câu hỏi phân tích:**
- Giá trung vị của từng thể loại là bao nhiêu? Thể loại nào đắt nhất / rẻ nhất?
- Phân bố giá có lệch phải không? Có nhiều sách giá thấp hơn hay cao hơn?
- Mức chiết khấu phổ biến nhất là bao nhiêu? Có sự khác biệt giữa các thể loại không?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Lập bảng thống kê mô tả (mean, median, std, min, max, Q1, Q3) của `price` và `discount_rate` theo từng `crawl_category`. Xác định thể loại có IQR giá rộng nhất. |
| **Đo lường** | Bảng thống kê đầy đủ; Boxplot phân bố giá 10 thể loại; Histogram phân bố price. |
| **Khả thi** | Dữ liệu đầy đủ trong CSV. |
| **Liên quan** | Hiểu phân khúc thị trường sách theo giá để hỗ trợ quyết định nhập kho. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Boxplot | Phân bố `price` theo `crawl_category` (10 nhóm, sắp xếp theo median) | Plotly |
| 2 | Violin plot | So sánh `discount_rate` theo thể loại | Plotly |
| 3 | Histogram | Phân bố `price` (toàn bộ dataset, log scale) | Plotly |
| 4 | Bar chart | Top 5 thể loại có `discount_rate` trung vị cao nhất | Seaborn |
| 5 | Bảng | Thống kê mô tả (mean, median, std, Q1, Q3) theo thể loại | Pandas |

**Kết quả kỳ vọng:**
> Xác định được top 3 thể loại đắt nhất và rẻ nhất. Mô tả được khoảng giá phổ biến nhất của toàn thị trường.

---

#### 🎯 Mục tiêu 1.2 — Hiệu quả chiết khấu lên doanh số

**Câu hỏi phân tích:**
- Sách giảm giá > 30% có bán chạy hơn sách không giảm giá không?
- Ngưỡng discount nào (0–10%, 10–20%...) có doanh số trung bình cao nhất?
- Có mối tương quan thực sự giữa `discount_rate` và `quantity_sold` không?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Chia sách thành 8 nhóm discount (0–10%, 10–20%,..., 80–100%). Tính trung vị `quantity_sold` mỗi nhóm. Tính hệ số tương quan Spearman (discount, quantity_sold). |
| **Đo lường** | Hệ số Spearman r và p-value; Bar chart trung vị doanh số theo 8 nhóm; Scatter với trendline. |
| **Khả thi** | Hai cột `discount_rate` và `quantity_sold` có sẵn. |
| **Liên quan** | Gợi ý chiến lược định giá tối ưu cho nhà bán hàng trên Tiki. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Scatter plot | `discount_rate` vs `quantity_sold` (màu theo `crawl_category`, hover = tên sách) | Plotly |
| 2 | Bar chart | Doanh số trung vị theo 8 nhóm discount (0–10%, 10–20%...) | Plotly |
| 3 | Line chart | Trend doanh số trung bình theo nhóm discount | Seaborn |

**Kết quả kỳ vọng:**
> Xác định ngưỡng discount tối ưu (ví dụ: 20–30% có median sales cao nhất). Kết luận tương quan Spearman có ý nghĩa thống kê hay không (p < 0.05).

---

### 👤 Thành viên 2 — Phân tích Đánh giá & Uy tín Sản phẩm

---

#### 🎯 Mục tiêu 2.1 — Mối quan hệ Rating, Review và Doanh số

**Câu hỏi phân tích:**
- Rating cao (≥ 4.5) có đảm bảo doanh số cao không?
- `rating_average` hay `review_count` có tác động mạnh hơn tới doanh số?
- Sản phẩm cần có bao nhiêu review mới bắt đầu có doanh số tốt?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Phân sách thành 4 nhóm uy tín: [rating ≥ median & review ≥ median], [rating ≥ median & review < median], [rating < median & review ≥ median], [rating < median & review < median]. So sánh median `quantity_sold` của 4 nhóm. Tính tương quan Pearson: (rating, sales) và (log(review+1), sales). |
| **Đo lường** | Bảng 4 nhóm × 3 chỉ số; Heatmap tương quan Pearson; Scatter plot 3 chiều. |
| **Khả thi** | Ba cột `rating_average`, `review_count`, `quantity_sold` đều có sẵn. |
| **Liên quan** | Giúp người mua hiểu mức độ tin cậy của review; giúp người bán biết đầu tư vào review hay rating. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Scatter plot | `rating_average` vs `quantity_sold` (size = `review_count`, màu = `crawl_category`) | Plotly |
| 2 | Heatmap | Ma trận tương quan Pearson: price, discount, rating, review, quantity_sold | Seaborn |
| 3 | Bar chart | Doanh số trung vị theo 4 nhóm uy tín (Low-Low, Low-High, High-Low, High-High) | Plotly |
| 4 | KDE plot | Phân bố `rating_average` toàn bộ dataset | Seaborn |

**Kết quả kỳ vọng:**
> Kết luận yếu tố nào (rating hay review) có tương quan mạnh hơn với doanh số, dựa trên hệ số Pearson cụ thể.

---

#### 🎯 Mục tiêu 2.2 — Phát hiện sản phẩm "Tiềm năng ẩn"

**Câu hỏi phân tích:**
- Có bao nhiêu sản phẩm bán tốt nhưng chưa được đánh giá nhiều?
- Những sách này thuộc thể loại nào? Được bán bởi loại seller nào chủ yếu?
- Đây có phải sách mới ra mắt không?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Xác định sách có `review_count` ≤ percentile 25% **VÀ** `quantity_sold` ≥ percentile 75%. Lập danh sách Top 20 với đầy đủ thông tin. Phân tích phân bố thể loại và seller_type của nhóm này. |
| **Đo lường** | Số lượng sản phẩm thỏa điều kiện; Top 20 bảng; Pie chart phân bố thể loại nhóm này. |
| **Khả thi** | Filter 2 điều kiện đơn giản trên DataFrame. |
| **Liên quan** | Phát hiện cơ hội đầu tư — sách đang bán tốt nhưng chưa được tiếp thị mạnh. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Scatter plot | `review_count` vs `quantity_sold` — highlight "tiềm năng ẩn" màu đỏ (sao) | Plotly |
| 2 | Pie/Bar chart | Phân bố `crawl_category` của nhóm "tiềm năng ẩn" | Plotly |
| 3 | Table | Top 20 (name, category, price, quantity_sold, review_count, seller_type) | Pandas |

**Kết quả kỳ vọng:**
> Danh sách cụ thể sản phẩm tiềm năng với mô tả thể loại và seller chủ yếu.

---

### 👤 Thành viên 3 — Phân tích Thể loại & Nhà xuất bản

---

#### 🎯 Mục tiêu 3.1 — So sánh sức mạnh thị trường giữa các thể loại

**Câu hỏi phân tích:**
- Thể loại nào chiếm market share (tổng doanh số) cao nhất?
- Thể loại nào đang bị "Cung > Cầu" (nhiều sản phẩm nhưng doanh số thấp)?
- Sách tiếng Anh vs tiếng Việt: loại nào có doanh số trung bình cao hơn?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Tính `market_share (%) = tổng quantity_sold thể loại / tổng toàn bộ × 100`. Xếp hạng Top 3 theo: (a) tổng doanh số, (b) trung vị doanh số/sản phẩm, (c) số lượng sản phẩm. So sánh 3 bảng xếp hạng. |
| **Đo lường** | Market share %; Treemap; Bar chart kép (doanh số vs số sản phẩm); Boxplot doanh số. |
| **Khả thi** | `groupby` + `agg` cơ bản. |
| **Liên quan** | Hỗ trợ quyết định nhập kho và phân bổ ngân sách quảng cáo. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Boxplot | `quantity_sold` theo `crawl_category` (sắp xếp theo median giảm dần) | Plotly |
| 2 | Bar chart kép | Số sản phẩm vs Tổng doanh số theo thể loại (trục kép) | Plotly |
| 3 | Treemap | Market share (%) của từng thể loại | Plotly |
| 4 | Grouped bar | So sánh 3 chỉ số (price_median, discount_median, rating_mean) theo thể loại | Plotly |

**Kết quả kỳ vọng:**
> Xác định được top 3 thể loại theo doanh số và chỉ ra ít nhất 1 thể loại đang có Cung > Cầu.

---

#### 🎯 Mục tiêu 3.2 — Xếp hạng Nhà xuất bản theo chỉ số tổng hợp

**Câu hỏi phân tích:**
- NXB nào được tín nhiệm nhất trên thị trường? (Kết hợp rating, review, doanh số)
- NXB có nhiều sản phẩm (lớn) có đảm bảo chất lượng (rating) cao hơn không?
- NXB nào đang "chuyên" về thể loại nào?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Tính `publisher_score = median(rating) × log1p(sum(review_count)) × log1p(sum(quantity_sold))` cho mỗi NXB có ≥ 10 sản phẩm. Xếp hạng Top 10. |
| **Đo lường** | Bảng Top 10 NXB; Bar chart publisher_score; Heatmap profile (rating, review, sales) × Top 10 NXB. |
| **Khả thi** | `publisher_name` có sẵn sau crawl mới; tạo cột score bằng groupby. |
| **Liên quan** | Nhà phân phối, thư viện muốn hợp tác với NXB uy tín chọn đúng nhà. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Bar chart ngang | Top 10 NXB theo `publisher_score` (kèm số sản phẩm) | Plotly |
| 2 | Heatmap | 3 chỉ số thành phần (rating_mean, review_sum, sales_median) của Top 10 NXB | Seaborn |
| 3 | Scatter | Số sản phẩm vs Rating trung bình theo NXB (size = doanh số) | Plotly |
| 4 | Stacked bar | Phân bố thể loại trong Top 5 NXB | Plotly |

**Kết quả kỳ vọng:**
> Top 10 NXB có chỉ số uy tín tổng hợp cao, kèm profile chi tiết từng NXB.

---

### 👤 Thành viên 4 — Phân tích Đặc điểm Vật lý & Ngôn ngữ

---

#### 🎯 Mục tiêu 4.1 — Ảnh hưởng đặc điểm vật lý và hình ảnh đến doanh số

**Câu hỏi phân tích:**
- Sách bìa cứng có đắt hơn bìa mềm bao nhiêu lần? Có bán chạy hơn không?
- Thay vì số trang (do dữ liệu bị thiếu), việc người bán cập nhật nhiều hình ảnh (`image_count`) có giúp bán chạy hơn không?
- Sách có trên 5 ảnh mô tả có doanh thu trung vị cao hơn sách chỉ có 1 ảnh bìa không?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | So sánh giá và doanh số giữa nhóm `cover_type`. Phân sách thành 4 nhóm hình ảnh: 1 ảnh, 2-3 ảnh, 4-5 ảnh, >5 ảnh. Tính tương quan Pearson (`image_count`, `quantity_sold`). |
| **Đo lường** | Boxplot giá theo cover_type; Scatter image_count vs quantity_sold; Bar doanh số theo nhóm ảnh; Pearson r. |
| **Khả thi** | `image_count`, `cover_type` có sẵn dữ liệu chuẩn (image_count từ 1 đến 53). |
| **Liên quan** | Gợi ý người bán hàng chăm chút hình ảnh sản phẩm để tăng tỷ lệ chuyển đổi. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Boxplot | `price` theo `cover_type` (bìa cứng / bìa mềm / khác) | Plotly |
| 2 | Violin plot | `quantity_sold` theo `cover_type` | Plotly |
| 3 | Scatter | `image_count` vs `quantity_sold` (trendline hồi quy OLS) | Plotly |
| 4 | Bar chart | Doanh số trung vị theo 4 nhóm số lượng ảnh | Plotly |

**Kết quả kỳ vọng:**
> Kết luận chênh lệch giá giữa các loại bìa. Chứng minh được việc đăng nhiều ảnh minh họa có tác động dương đến doanh số hay không.

---

#### 🎯 Mục tiêu 4.2 — Phân tích thị trường sách ngoại ngữ

**Câu hỏi phân tích:**
- Tỷ lệ sách tiếng Anh / tiếng Việt trên Tiki là bao nhiêu?
- Sách tiếng Anh đắt hơn nhưng rating có cao hơn không?
- Thể loại nào có tỷ lệ sách tiếng Anh cao nhất?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Tính tỷ lệ phân bổ theo `book_language`. So sánh (price_median, rating_mean, quantity_sold_median) giữa English và Vietnamese. Vẽ heatmap % ngôn ngữ × thể loại. |
| **Đo lường** | Donut chart tỷ lệ; Grouped bar so sánh 3 chỉ số; Heatmap %; Bar top 5 thể loại tiếng Anh. |
| **Khả thi** | `book_language` đã được gán khi crawl. |
| **Liên quan** | Nhu cầu thị trường sách ngoại văn ở Việt Nam. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Donut chart | Phân bổ sách theo ngôn ngữ (Vietnamese / English) | Plotly |
| 2 | Grouped bar | So sánh price_median, rating_mean, sales_median theo ngôn ngữ | Plotly |
| 3 | Heatmap | Tỷ lệ ngôn ngữ (%) trong từng `crawl_category` | Seaborn |
| 4 | Bar chart | Top 5 thể loại có tỷ lệ sách tiếng Anh cao nhất (%) | Plotly |

**Kết quả kỳ vọng:**
> Biết tỷ lệ English/Vietnamese cụ thể. Kết luận sách tiếng Anh có giá cao hơn bao nhiêu % so với tiếng Việt.

---

### 👤 Thành viên 5 — Phân tích Người bán & Mô hình Dự đoán

---

#### 🎯 Mục tiêu 5.1 — Phân tích hệ sinh thái người bán (Seller Ecosystem)

**Câu hỏi phân tích:**
- Tiki Trading (chính hãng) vs Merchant (bên thứ ba): ai có giá thấp hơn? Doanh số cao hơn? Discount nhiều hơn?
- Top 10 Seller lớn nhất đang thống lĩnh thể loại nào?
- Merchant lớn có rating cao hơn hay thấp hơn Tiki Trading?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | So sánh (price, discount_rate, rating_average, quantity_sold) giữa "Tiki Trading" và "Merchant" bằng Mann-Whitney U test. Xác định Top 10 seller theo `all_time_sold`. Phân tích thể loại chủ lực của mỗi seller trong Top 10. |
| **Đo lường** | P-value Mann-Whitney; Boxplot chỉ số theo seller_type; Bar Top 10 Seller; Stacked bar thể loại theo seller. |
| **Khả thi** | `seller_name`, `seller_type`, `all_time_sold` có sẵn. |
| **Liên quan** | Hiểu cấu trúc cạnh tranh và chiến lược phân phối trên sàn TMĐT. |
| **Thời gian** | 2 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Boxplot | `price` theo `seller_type` (Tiki Trading vs Merchant) | Plotly |
| 2 | Boxplot | `discount_rate` theo `seller_type` | Plotly |
| 3 | Bar chart ngang | Top 10 Seller theo `all_time_sold` (màu theo seller_type) | Plotly |
| 4 | Scatter | `all_time_sold` vs `quantity_sold` (màu = seller_type) | Plotly |
| 5 | Stacked bar | Phân bố thể loại trong Top 10 Seller | Plotly |

**Kết quả kỳ vọng:**
> Kết luận có hay không sự khác biệt thống kê có ý nghĩa giữa Tiki Trading và Merchant về giá/doanh số. Top 10 seller và thể loại chủ lực.

---

#### 🎯 Mục tiêu 5.2 — Mô hình dự đoán Doanh số (RandomForest)

**Câu hỏi phân tích:**
- Yếu tố nào ảnh hưởng mạnh nhất đến `quantity_sold`? (giá, chiết khấu, rating, review, thể loại...)
- Mô hình có thể dự đoán doanh số với R² ≥ 0.40 không?
- Nếu tăng discount thêm 10%, doanh số kỳ vọng thay đổi thế nào?

**Mục tiêu SMART:**
| | Nội dung |
|---|---|
| **Cụ thể** | Train `RandomForestRegressor` với 7 features: `price`, `discount_rate`, `rating_average`, `review_count`, `image_count`, `cover_type` (encoded), `crawl_category` (encoded). Đánh giá trên test set 20%. Vẽ Feature Importance và Partial Dependence Plot cho `discount_rate`. |
| **Đo lường** | R², MAE, RMSE trên test set; Feature Importance bar chart; Predicted vs Actual scatter. |
| **Khả thi** | scikit-learn + dataset sau tiền xử lý đủ (~6.000+ dòng). |
| **Liên quan** | Cung cấp bằng chứng định lượng về yếu tố quyết định doanh số. |
| **Thời gian** | 3 ngày. |

**Danh sách biểu đồ cần thực hiện:**

| # | Loại biểu đồ | Nội dung | Thư viện |
|---|---|---|---|
| 1 | Bar chart ngang | Feature Importance (7 features, sắp xếp giảm dần) | Plotly |
| 2 | Scatter | Predicted vs Actual (đường y=x làm baseline) | Plotly |
| 3 | Line chart | Partial Dependence Plot: `discount_rate` → `quantity_sold` | sklearn + Plotly |
| 4 | Bảng | Metrics: R², MAE, RMSE trên train/test | Markdown |

**Kết quả kỳ vọng:**
> Feature Importance chart rõ ràng, chỉ ra yếu tố quan trọng nhất. R² ≥ 0.35 (có thể thấp do doanh số rất skewed).

---

## 5. Tổng hợp 10 Câu hỏi Phân tích

| # | Câu hỏi | TV | Phương pháp chính | Biểu đồ chính |
|---|---|---|---|---|
| Q1 | Thể loại nào có khoảng giá rộng nhất và đắt nhất? | TV1 | IQR, Bảng thống kê | Boxplot |
| Q2 | Ngưỡng discount nào tối ưu nhất cho doanh số? | TV1 | Spearman, Groupby | Bar chart nhóm discount |
| Q3 | Rating hay review có tương quan mạnh hơn với doanh số? | TV2 | Pearson, Heatmap | Scatter 3 chiều |
| Q4 | Sách "tiềm năng ẩn" thuộc thể loại và seller nào? | TV2 | Filter P25/P75 | Scatter highlight |
| Q5 | Thể loại nào đang bị Cung > Cầu? Market share ra sao? | TV3 | Market share, groupby | Treemap, Bar kép |
| Q6 | NXB nào có chỉ số tổng hợp (rating×review×sales) tốt nhất? | TV3 | Custom score | Bar + Heatmap |
| Q7 | Bìa cứng vs bìa mềm chênh lệch ra sao? Số hình ảnh ảnh hưởng doanh số không? | TV4 | Mann-Whitney, Boxplot | Boxplot kép |
| Q8 | Thể loại nào tiếp cận thị trường ngoại ngữ nhiều nhất? | TV4 | Crosstab, Heatmap | Heatmap |
| Q9 | Tiki Trading vs Merchant: ai có lợi thế về giá? Doanh số? | TV5 | Mann-Whitney U | Boxplot, Bar |
| Q10 | Yếu tố nào ảnh hưởng quan trọng nhất đến doanh số? | TV5 | RandomForest | Feature Importance |

---

## 6. Cấu trúc Dashboard — 4 Tab Chi tiết (Data Storytelling)

### Tab 1: 🏠 Tổng quan Thị trường & Cấu trúc Ngành hàng
> **Nội dung:** Cái nhìn vĩ mô về quy mô thị trường, phân bổ thể loại và uy tín của các "ông lớn" (Nhà xuất bản).
> **Phụ trách:** TV3 & TV4.

1. **Treemap (Thị phần doanh số theo thể loại):** Nhận diện ngay lập tức sự chênh lệch doanh số giữa các danh mục (diện tích ô = tổng sales).
2. **Boxplot (Phân phối giá theo danh mục):** Xác định khoảng giá an toàn và các điểm outlier "xa xỉ" ở từng phân khúc.
3. **Bar chart ngang (Top 10 NXB theo uy tín):** Xếp hạng NXB dựa trên `publisher_score`, thiết kế cột ngang giúp đọc tên dài dễ dàng.
4. **Donut Chart (Sách Tiếng Anh vs Tiếng Việt):** Cho góc nhìn nhanh về thị phần ngôn ngữ ngoại văn trên sàn.

### Tab 2: 📈 Động lực Doanh số & Hiệu quả Marketing
> **Nội dung:** Đi sâu hành vi mua sắm — Giá, Chiết khấu và Niềm tin (Review) ảnh hưởng thế nào đến túi tiền.
> **Phụ trách:** TV1 & TV2.

5. **Bubble Chart (Discount - Sales - Review):** Biểu đồ đa biến (X: Discount, Y: Sales, Kích thước: Review). *Lưu ý: Sẽ thêm bộ lọc danh mục để tránh overplotting.*
6. **Bar Chart (Doanh số trung vị theo 8 nhóm Discount):** Tiết lộ ngưỡng giảm giá "vàng" (binning) thu hút người mua nhất.
7. **Heatmap Tương quan (Correlation Matrix):** Chứng minh khoa học biến số nào (Review hay Rating) thực sự kéo doanh số đi lên.
8. **Scatter plot (Phát hiện "Tiềm năng ẩn"):** Highlight sách góc "Ít Review - Doanh số cao" để gợi ý đầu tư chạy ads.

### Tab 3: 📚 Đặc điểm Sản phẩm & Hệ sinh thái Người bán
> **Nội dung:** Phân tích đặc điểm vật lý (Bìa, Hình ảnh) và xem xét Tiki Trading vs Merchant.
> **Phụ trách:** TV4 & TV5.

9. **Double Boxplot (Tiki Trading vs Merchant):** So sánh trực diện hình thái ưu đãi và mức giá gốc giữa 2 nhóm người bán.
10. **Violin/Boxplot (Giá/Doanh số theo Cover Type):** Kiểm chứng xem việc xuất bản "bìa cứng" có thực sự đẩy được giá/doanh thu lên thay vì "bìa mềm".
11. **Scatter Plot + Trendline (Image Count vs Sales):** Trực quan hóa giá trị của việc người đăng sản phẩm đầu tư nhiều hình ảnh minh họa.
12. **Bar Chart (Feature Importance từ RandomForest):** Chốt định lượng yếu tố "vua" quyết định doanh số.

### Tab 4: 👁️ Accessibility Mode (Chế độ Hỗ trợ người mù màu)
> **Nội dung:** Tái hiện các biểu đồ quan trọng nhất của Tab 1 nhưng áp dụng Inclusive Design. Điểm cộng mạnh mẽ cho UX/UI.

*   **Giải pháp hình ảnh:** Chuyển toàn bộ palette màu sang hệ **Viridis** (tương phản sáng/tối tốt).
*   **Giải pháp cấu trúc:** Thêm text label đập trực tiếp vào biểu đồ; Dùng họa tiết (patterns) và nét đứt (dashed lines) thay vì phụ thuộc hoàn toàn vào màu sắc.

---

**Bộ lọc chung toàn trang (Sidebar):**
- Multiselect: Chọn Thể loại gốc (`crawl_category`)
- Slider: Khoảng giá (Price range)
- Slider: Khoảng giảm giá (Discount rate)
- Radio button: Ngôn ngữ (All / VN / EN)

## 7. Quy tắc viết Nhận xét Biểu đồ

> ❌ **KHÔNG VIẾT kiểu này:**
> "Biểu đồ cho thấy Manga bán chạy hơn sách giáo khoa."

> ✅ **VIẾT đúng chuẩn như sau:**
> "Theo Hình 3.2 (Boxplot doanh số theo thể loại), trung vị `quantity_sold` của nhóm **Manga - Truyện Tranh** đạt **1.240 bản**, cao hơn **3.1 lần** so với nhóm **Sách Giáo Khoa** (trung vị **400 bản**). Điều này cho thấy nhu cầu thị trường đối với thể loại giải trí hình ảnh đang vượt trội rõ rệt so với sách học thuật."

**Checklist mỗi biểu đồ trước khi nộp:**
- [ ] Tiêu đề mô tả rõ nội dung (tiếng Việt)
- [ ] Nhãn trục X, Y đầy đủ (kèm đơn vị nếu có: VNĐ, %, bản...)
- [ ] Legend/Chú thích rõ ràng
- [ ] Có nhận xét với số liệu cụ thể bên dưới
- [ ] Font chữ đủ lớn (≥ 11pt khi xuất PDF), không bị cắt xén
- [ ] Màu sắc phân biệt rõ giữa các nhóm

---

## 8. Lịch trình thực hiện (còn lại)

| Ngày | Nhiệm vụ | Người thực hiện | Output cụ thể |
|---|---|---|---|
| N (hôm nay) | Hoàn tất crawl lại dữ liệu (có author + publisher) | Chờ script chạy | `tiki_books_raw.csv` mới ≥ 8.000 dòng |
| N+1 | Tiền xử lý toàn bộ (`02_preprocessing.ipynb`) | Cả nhóm review | `tiki_books_clean.csv` |
| N+2 | EDA Mục tiêu 1.1, 1.2 | TV1 | ≥ 5 biểu đồ + nhận xét |
| N+2 | EDA Mục tiêu 2.1, 2.2 | TV2 | ≥ 5 biểu đồ + nhận xét |
| N+3 | EDA Mục tiêu 3.1, 3.2 | TV3 | ≥ 5 biểu đồ + nhận xét |
| N+3 | EDA Mục tiêu 4.1, 4.2 | TV4 | ≥ 5 biểu đồ + nhận xét |
| N+4 | EDA Mục tiêu 5.1 + train RF (5.2) | TV5 | ≥ 5 biểu đồ + model metrics |
| N+5–7 | Dashboard Streamlit (4 tab) | Cả nhóm | `app.py` chạy được |
| N+8–9 | Viết báo cáo PDF | Cả nhóm | Draft PDF |
| N+10 | Hoàn thiện, đóng gói ZIP, kiểm tra output | Cả nhóm | **File nộp hoàn chỉnh** |

---

## 9. Cấu trúc Báo cáo PDF (≤ 24 trang)

| Phần | Nội dung | Trang gợi ý |
|---|---|---|
| 1. Thông tin nhóm | Họ tên, MSSV, tỷ lệ đóng góp | 1 |
| 2. Tổng quan | Lý do chọn đề tài, 10 mục tiêu SMART | 2–3 |
| 3. Quy trình dữ liệu | Tiki API, cấu trúc dataset, pipeline tiền xử lý, thống kê dữ liệu sau làm sạch | 4–8 |
| 4. EDA & Phân tích | Biểu đồ + nhận xét định lượng cho 10 mục tiêu (≥ 20 hình) | 9–18 |
| 5. Dashboard | Screenshot 4 tab + mô tả tính năng tương tác | 19–22 |
| 6. Kết luận | Trả lời 10 câu hỏi dựa trên kết quả phân tích cụ thể | 23 |
| 7. Tài liệu tham khảo | Link Tiki API, thư viện sử dụng | 24 |

---

## 10. Checklist Nộp bài

- [x] `data/raw/tiki_books_raw.csv` — **dữ liệu thô ≥ 8.000 dòng ✅**
- [ ] `data/processed/tiki_books_clean.csv` — dữ liệu đã xử lý
- [x] `notebooks/01_crawl_data.ipynb` — **có output cells ✅**
- [ ] `notebooks/02_preprocessing.ipynb` — **phải có output cells**
- [ ] `notebooks/03_eda.ipynb` — **phải có output + ≥ 20 biểu đồ**
- [ ] `dashboard/app.py` — chạy được bằng `streamlit run app.py`
- [ ] `requirements.txt` — đầy đủ thư viện
- [ ] `README.md` — hướng dẫn chạy project
- [ ] Báo cáo PDF ≤ 24 trang

> [!IMPORTANT]
> **Tuyệt đối KHÔNG xóa output** trong Notebook trước khi nộp. Giảng viên chấm điểm dựa trên output — nếu cell trống sẽ bị trừ điểm nặng.

> [!WARNING]
> **Không sử dụng dữ liệu** từ Kaggle, GitHub hay bất kỳ dataset có sẵn nào. Giảng viên sẽ kiểm tra mã nguồn Crawler và so sánh timestamp dữ liệu. Nếu không có code crawl thực tế → 0 điểm phần thu thập dữ liệu.

> [!NOTE]
> File checkpoint `product_ids_checkpoint.json` nên được giữ lại trong `data/raw/` khi nộp để minh chứng quy trình crawl 2 bước.
