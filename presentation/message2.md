# 📊 สรุปเนื้อหาสำหรับ Business Analytics Project Presentation
**ชื่อโปรเจกต์:** Brazilian E-commerce Sales & Inventory Analysis  
**ชื่อทีม:** ฟุตบอลกำลังร้องไห้  
**ชุดข้อมูล:** Brazilian E-Commerce Public Dataset by Olist (Kaggle)  
**ขอบเขตเวลาข้อมูล:** มกราคม 2017 – สิงหาคม 2018 (2017-01 ถึง 2018-08)  

---

## 1. Executive Summary (บทสรุปผู้บริหาร)

* **Problem Summary (ปัญหาทางธุรกิจ):**  
  ความล่าช้าในการจัดส่งสินค้า (Delivery Delay) ส่งผลกระทบเชิงลบโดยตรงต่อคะแนนความพึงพอใจของลูกค้า (Review Score) และสร้างความเสี่ยงต่อการยกเลิกคำสั่งซื้อ (Order Cancellation) ในบางหมวดสินค้า ซึ่งส่งผลเสียต่อรายได้และภาพลักษณ์ของแพลตฟอร์มในระยะยาว

* **Core Objective (เป้าหมายหลัก):**  
  1. วิเคราะห์ความสัมพันธ์เชิงสถิติระหว่างความล่าช้าในการจัดส่งกับคะแนนรีวิวของลูกค้า  
  2. ระบุหมวดหมู่สินค้าที่มีความเสี่ยงสูงในการถูกยกเลิกคำสั่งซื้อ  
  3. เสนอกลยุทธ์เชิงรุกเพื่อลดอัตราการส่งช้า ปรับปรุงการดำเนินงาน และรักษาความพึงพอใจของลูกค้า

* **Key Findings & Achievements (ผลลัพธ์และการค้นพบสำคัญ):**  
  * **คะแนนรีวิวลดลงแบบขั้นบันได (Dose-Response Effect):** มีความสัมพันธ์เชิงลบอย่างมีนัยสำคัญทางสถิติ ($Spearman\ \rho = -0.176, p < 0.001$) โดยออเดอร์ที่ส่งตรงเวลาได้คะแนนเฉลี่ย **4.29 ดาว** แต่หากส่งช้าเกิน 8 วัน คะแนนจะดิ่งลงเหลือเพียง **1.73 ดาว** (ลดลงถึง 2.56 ดาว)
  * **Root Cause Identification:** ค้นพบว่าสาเหตุหลักของการส่งช้าเกิดจาก **Transit Time ในขั้นตอนการขนส่งจริงที่พุ่งสูงขึ้น (7.9 วัน $\rightarrow$ 25.7 วัน)** ไม่ได้เกิดจากความล่าช้าในขั้นตอนการอนุมัติคำสั่งซื้อ (Order Approval)

---

## 2. Business Problem & Context (บริบทและปัญหาทางธุรกิจ)

### 🔴 Problem Statement
ระบบขนส่งของแพลตฟอร์มมีจุดอ่อนด้านความสถียรของ Transit Time โดยเฉพาะอย่างยิ่งในช่วงเทศกาลสำคัญ ส่งผลให้อัตราการจัดส่งล่าช้าพุ่งสูงขึ้นกว่าปกติเกือบ **3 เท่า** ในบางช่วงเวลา

### ⚠️ Business Impact (ผลกระทบหากไม่ได้รับการแก้ไข)
1. **Customer Satisfaction Drop:** คะแนนรีวิวเฉลี่ยลดลงอย่างรุนแรงจาก $4.29 \rightarrow 1.73$ ดาว ในกลุ่มที่ส่งช้าที่สุด ($n = 3,252$ ออเดอร์)
2. **High Cancellation in Specific Categories:** สินค้าบางหมวดมีความเสี่ยงยกเลิกสูงกว่าปกติอย่างมีนัยสำคัญ เช่น `books_general_interest` และ `fixed_telephony` มีอัตราการยกเลิกสูงถึง **1.40%** (สูงกว่าค่าเฉลี่ยรวมของแพลตฟอร์มที่ 0.48% ถึง 3 เท่า)
3. **Long-term Customer Retention:** กระทบต่ออัตราการกลับมาซื้อซ้ำ (Repeat Purchase Rate) และมูลค่าตลอดช่วงชีวิตของลูกค้า (Customer Lifetime Value)

### 🎯 Scope of Study
* **ชุดข้อมูลหลัก:** ออเดอร์ที่จัดส่งสำเร็จ (`status = delivered`) จำนวน **96,470 รายการ**
* **ชุดข้อมูลสำหรับประเมินความพึงพอใจ:** ออเดอร์ที่มีคะแนนรีวิวระบุไว้ จำนวน **95,824 รายการ**

---

## 3. Data Overview & Architecture (ภาพรวมข้อมูล)

* **Data Source:** [Olist Brazilian E-Commerce Dataset (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
  * *เหตุผลที่เลือก:* เป็นโครงสร้างข้อมูลแบบ Relational Database เชื่อมโยงผ่าน Keys (`order_id`, `product_id`, `seller_id`, `customer_id`) ช่วยให้วิเคราะห์ข้อมูลได้ครบทุกมิติ
* **Metadata Structure:**  
  * **Fact Table:** `olist_orders_dataset`
  * **Dimension Tables:** `order_items`, `order_payments`, `order_reviews`, `products`, `sellers`, `customers`, `geolocation`
* **Target Variables (ตัวแปรเป้าหมาย):**
  1. **Task ความพึงพอใจลูกค้า:** `review_score` แปลงเป็น Binary Group  
     * $1$ = พอใจ ($4-5$ ดาว)  
     * $0$ = ไม่พอใจ ($< 4$ ดาว)
  2. **Task ความเสี่ยงการยกเลิก:** `order_status`  
     * `delivered` vs `canceled`

---

## 4. Data Preparation & Feature Engineering (การเตรียมและการวิศวกรรมข้อมูล)

### 🧹 Data Cleaning & Transformation
* **Missing Values:** แทนที่ค่าว่างใน `review_score` (จำนวน 978 รายการ) ด้วยค่ากลาง (Mean Imputation)
* **Outlier Handling:** พบ Outliers ในคอลัมน์ `price` จำนวน 8,427 รายการ ดำเนินการ Capping ขอบเขตบนตามหลัก Interquartile Range (IQR) 
* **Data Type Conversion:** แปลงข้อมูลวันที่และเวลาจากรูปแบบ String เป็น Datetime เพื่อคำนวณระยะเวลา (Time Delta)

### 🛠️ Feature Engineering (ตัวแปรสร้างใหม่)

| ชื่อ Feature | สูตรคำนวณ / คำอธิบาย | Rationale & Business Value |
| :--- | :--- | :--- |
| `transit_time` | $Date_{received} - Date_{delivered\_to\_carrier}$ | แยกปัญหาขนส่งจริง ออกจากขั้นตอนอนุมัติออเดอร์/การเตรียมของของ Seller |
| `delay_bucket` | จัดกลุ่มความล่าช้าเทียบวันประเมิน (4 ระดับ) | แปลงตัวเลขเป็นกลุ่มธุรกิจเข้าใจง่าย เผยรูปแบบ Dose-Response Effect |
| `is_late` | Flag (1/0) กรณีส่งถึงลูกค้าช้ากว่าวันประเมิน | ใช้ระบุสถานะส่งช้าในเชิงภาพรวม |
| `seller_late_ship_flag` | Flag (1/0) กรณี Seller ส่งให้ Carrier ช้ากว่า `shipping_limit_date` | ประเมิน Compliance และวินัยการทำงานของ Seller |
| `freight_ratio` | $\text{freight\_value} \div \text{price}$ | เปรียบเทียบภาระค่าส่งเทียบกับราคาสินค้าในแต่ละพื้นที่ |
| `review_satisfied` | Target Classification ($1: 4-5 \text{ ดาว}, 0: <4 \text{ ดาว}$) | ปรับข้อมูลให้เหมาะกับ Binary Logistic Regression |

* **Tools Used:** `Python` (`Pandas`, `Scikit-Learn`, `Matplotlib`, `Seaborn`)

---

## 5. Exploratory Data Analysis (EDA) & Key Insights

### 📈 Visual Insights
1. **Price Distribution:** สินค้าส่วนใหญ่กระจุกตัวอยู่ในช่วงราคา **20–50 BRL** (มากกว่า 10,000 ออเดอร์)
2. **Freight Costs:** ค่าจัดส่งส่วนใหญ่อยู่ในช่วง **13.08–21.15 BRL** (Median = 16.26 BRL) แต่พบ Outliers สูงสุดถึง **409.68 BRL**
3. **Correlation Analysis:**  
   * `price` กับ `freight_value` มีความสัมพันธ์เชิงบวกปานกลาง ($r = 0.41$)
   * `review_score` กับ ความล่าช้า มีความสัมพันธ์เชิงลบ ($r = -0.23$)
4. **Top Revenue Categories:** หมวด `health_beauty` และ `watches_gifts` สร้างรายได้สูงสุดเป็นอันดับ 1 และ 2 (รวมกันเกิน 1.2 ล้าน BRL) ตามด้วย `bed_bath_table` และ `sports_leisure`
5. **Geographic Freight Disparity:** รัฐห่างไกล เช่น Rondônia (RO) และ Roraima (RR) มีค่า `freight_ratio` สูงเกือบ **60%** ของราคาสินค้า ในขณะที่ São Paulo (SP) ต่ำสุดเพียง **~26%**
6. **Dose-Response Effect (Delay vs Score):**
   * On-time / Early: **4.29 ดาว**
   * Late 1–3 วัน: **3.76 ดาว**
   * Late 4–7 วัน: **2.32 ดาว**
   * Late 8+ วัน: **1.73 ดาว**
7. **Seasonality Patterns:** อัตราการจัดส่งล่าช้าเฉลี่ยอยู่ที่ **8.1%** แต่พุ่งสูงใน 2 ช่วงเวลาหลัก:
   * **พฤศจิกายน 2017 (~14%):** เทศกาล Black Friday
   * **กุมภาพันธ์–มีนาคม 2018 (~21–22%):** เทศกาล Carnival ของบราซิล

### ⚡ Immediate Actions (Quick Wins - ดำเนินการได้ทันที)
* **Increase Buffer Capacity:** สำรองกำลังการขนส่งล่วงหน้าอย่างน้อย 30 วัน ก่อนเข้าสู่ช่วงเทศกาล Black Friday (พ.ย.) และ Carnival (ก.พ.-มี.ค.)
* **Freight Subsidy / Negotiation:** เจรจาค่าจัดส่งใหม่ในรัฐห่างไกล (RO, RR) หรือวางแผนจัดตั้งจุดกระจายสินค้า (Hub) เพื่อลดภาระ `freight_ratio`
* **Focus High-Value Categories:** เพิ่มการสนับสนุนการตลาดและการจัดการสต็อกในหมวดทำรายได้หลัก (`health_beauty`, `watches_gifts`)

---

## 6. Machine Learning Modeling & Evaluation

### 🤖 Algorithm Selection
* **Logistic Regression:** เลือกใช้เนื่องจากตัวแปรเป้าหมายเป็น Binary Classification และต้องการความสามารถในการตีความผลลัพธ์ (Interpretability) เพื่ออธิบายปัจจัยขับเคลื่อนให้ผู้บริหารเข้าใจได้ชัดเจน
* **Validation Strategy:** Train-Test Split ในอัตราส่วน **70:30**

### 📊 Model Performance

#### Model 1: Review Satisfaction Prediction (ทำนายความพึงพอใจลูกค้า)
* **Accuracy:** `0.79`
* **Confusion Matrix:** `[[1900, 4147], [1912, 20943]]`

| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **0 (ไม่พอใจ: < 4 ดาว)** | 0.50 | 0.31 | 0.39 | 6,047 |
| **1 (พอใจ: 4-5 ดาว)** | 0.83 | 0.92 | 0.87 | 22,855 |

#### Model 2: Order Cancellation Risk Prediction (ทำนายความเสี่ยงการยกเลิก)
* **ROC-AUC:** `0.641`
* **Precision:** `0.008`
* **Recall:** `0.598`
* **F1-Score:** `0.015`
* **Confusion Matrix:** `TP = 55, FN = 37, FP = 7,056, TN = 12,240`

> ⚠️ **ข้อควรระวังในการใช้งาน (Technical Caution Note):**  
> โมเดล Cancellation Prediction มีค่า Precision ต่ำมาก ($0.008$) ซึ่งทำให้เกิด False Positive สูง (7,056 รายการ) **จึงไม่ควรใช้เป็นระบบตอบโต้อัตโนมัติ (Fully Automated System)** แต่ให้ใช้เป็นระบบคัดกรองความเสี่ยงเบื้องต้น (Early Screening Tool) เพื่อให้ทีมงานเข้าตรวจสอบร่วมกับดุลยพินิจ

---

## 7. Machine Learning Insights & Strategic Recommendations

### 💡 Core Model Insights
1. **Transit Time is the Key Bottleneck:** การส่งช้าไม่ได้เกิดจากความล่าช้าในการอนุมัติคำสั่งซื้อ แต่เกิดจากระยะเวลาขนส่งจริง (`transit_time`) ที่เพิ่มขึ้นจาก **7.9 วัน** (กลุ่มปกติ) เป็น **25.7 วัน** (กลุ่มส่งช้า)
2. **Seller Compliance Drop:** อัตราที่ Seller ส่งมอบสินค้าให้ Carrier ช้ากว่ากำหนด (`shipping_limit_date`) เพิ่มขึ้นจาก **7.4%** ในกลุ่มปกติ เป็น **27.2%** ในกลุ่มส่งช้า
3. **Proactive Intervention Potential:** โมเดล Cancellation ตรวจจับลูกค้าเสี่ยงได้ **~60%** (Recall = 0.598) ช่วยเปิดโอกาสให้แพลตฟอร์มเข้าแทรกแซงก่อนเกิดการยกเลิกจริง

---

### 🚀 4 Strategic Action Plans (กลยุทธ์ขับเคลื่อนด้วย ML)


```

[1. Transit Time Optimization] ──> ลด Transit Time จาก 25.7 วัน เหลือ ~10 วัน
[2. Seller Compliance]        ──> คุมอัตรา Seller ส่งช้าจาก 27.2% ลงเหลือ 7.4%
[3. Seasonality Management]   ──> วาง Flex-Capacity ล่วงหน้า 30 วันก่อนเทศกาล
[4. Customer Intervention]    ──> คัดกรองออเดอร์เสี่ยงสูงเพื่อส่งข้อความ/คูปองดูแลเชิงรุก

```

1. **Transit Time Optimization (ปรับปรุงเส้นทางขนส่ง):**  
   เจรจาปรับเปลี่ยน Service Level Agreement (SLA) ร่วมกับบริษัทขนส่งในเส้นทางวิกฤต ตั้งเป้าลด Transit Time ในกลุ่มส่งช้าลงจาก **25.7 วัน ให้เหลือใกล้เคียง 10 วัน** (ลดลง ~50%)
2. **Seller Compliance Enforcement (จัดระเบียบวินัยผู้ขาย):**  
   กำหนดมาตรการจูงใจและบทลงโทษสำหรับ Seller ที่ส่งสินค้าให้ Carrier ล่าช้า ตั้งเป้าลดอัตรา Seller ส่งช้าจาก **27.2% ให้กลับสู่ระดับ baseline ปกติที่ 7.4%**
3. **Proactive Seasonality Management (วางแผนรับช่วงเทศกาล):**  
   จัดทำแผนเพิ่มกำลังขนส่งสำรอง (Flex-Capacity) ล่วงหน้าอย่างน้อย 30 วัน ก่อนช่วง Black Friday (พ.ย.) และ Carnival (ก.พ.-มี.ค.) เพื่อป้องกันปัญหาขนส่งคอขวด
4. **Proactive Customer Intervention (ดูแลลูกค้าเชิงรุก):**  
   ใช้ออเดอร์ที่โมเดลระบุว่ามีความเสี่ยงสูง ส่งข้อความแจ้งเตือนสถานะ หรือมอบคูปองชดเชยเชิงรุกก่อนที่ลูกค้าจะยกเลิกคำสั่งซื้อหรือให้รีวิวคะแนนต่ำ

---

### 🎯 Expected Business Impact (ผลลัพธ์ที่คาดว่าจะได้รับ)
* **Stabilized Delivery Rates:** สามารถควบคุมอัตราการจัดส่งล่าช้าให้อยู่ในระดับ Baseline **3–8%** ได้ตลอดทั้งปี แม้ในช่วงเทศกาลที่มีปริมาณออเดอร์หนาแน่น
* **Review Score Recovery:** คะแนนรีวิวเฉลี่ยในกลุ่มที่เคยส่งช้ามีโอกาสฟื้นตัวกลับเข้าใกล้ระดับปกติ (**4.29 ดาว**) ช่วยรักษาอัตราการซื้อซ้ำ ภาพลักษณ์ และความน่าเชื่อถือของแพลตฟอร์มในระยะยาว

---

## 8. Conclusion & Takeaway Message

ความล่าช้าในการจัดส่งสินค้าส่งผลกระทบโดยตรงต่อความพึงพอใจของลูกค้าในลักษณะ Dose-Response อย่างชัดเจน โดยสาเหตุรากเหง้า (Root Cause) เกิดจาก **Transit Time ในขั้นตอนขนส่งจริง** และ **วินัยของ Seller** ทีมงานจึงเสนอ **4 กลยุทธ์หลัก** เพื่อเพิ่มประสิทธิภาพระบบขนส่ง ควบคุม Seller และยกระดับประสบการณ์ลูกค้าให้ยั่งยืน

---
*หมายเหตุ: ข้อมูล อัตราส่วน และตัวเลขทางสถิติทั้งหมดในเอกสารนี้ อ้างอิงจากผลการวิเคราะห์จริงของโปรเจกต์ (Week 2-3 และ Lab4)*

