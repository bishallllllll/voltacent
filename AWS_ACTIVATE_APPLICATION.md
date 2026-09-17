# AWS Activate Founders Application Dossier
**Company:** Voltacent Quantitative Technologies  
**Portal:** https://bishalsarkar.me/voltacent/ (or https://voltacent.tech)  
**Primary Contact:** contact@bishalsarkar.me  

---

## 1. Company Information

| Field | Value to Enter |
| :--- | :--- |
| **Company Name** | Voltacent Quantitative Technologies |
| **Trading / Brand Name** | Voltacent Quant / Voltacent API |
| **Company Website** | `https://bishalsarkar.me/voltacent/` (or `https://voltacent.tech`) |
| **Primary Contact Email** | `contact@bishalsarkar.me` |
| **Country of Operation** | India (or your country of incorporation) |
| **Industry / Sector** | Financial Services & Technology (FinTech) |
| **Sub-Industry** | Capital Markets / Artificial Intelligence & Machine Learning |
| **Current Team Size** | 1–5 employees (Early-Stage Founder / Lab) |
| **Year Founded** | 2026 |
| **Funding Status** | Bootstrapped / Self-Funded |

---

## 2. Startup Overview & Elevator Pitch

### Question: What does your company do? (Elevator Pitch)
> *"Voltacent Quantitative Technologies is a financial machine learning and execution infrastructure company. We develop sub-second REST and WebSocket APIs providing point-in-time directional alpha forecasts, 32-dimensional causal deep learning market regime embeddings, and automated order execution for proprietary trading firms, algorithmic desks, and quantitative developers."*

### Question: What customer problem are you solving?
> *"Proprietary trading desks and quantitative traders face severe data snooping leakage and execution lookahead bias when deploying machine learning models to live financial markets. Furthermore, developing multi-timeframe feature pipelines and continuous model validation requires complex, high-memory distributed infrastructure. Voltacent provides pre-validated, point-in-time compliant regime embeddings and execution gateways that eliminate leakage, reduce backtest turnaround by 85%, and ensure institutional drawdown compliance."*

### Question: Describe your product or service.
> *"Our core platform consists of two integrated components:*
> 1. *Voltacent Signal & Regime API: A low-latency REST and WebSocket gateway streaming real-time directional probabilities ($\tau \ge 0.58$) and 32-D causal Dilated Temporal Convolutional Network (TCN) latent embeddings derived from 24 years of point-in-time tick data.*
> 2. *Automated Execution Engine: Headless Linux execution daemons operating in AWS us-east-1 that interface directly with institutional broker ECN bridges, enforcing real-time currency exposure guardrails (VAR_090) and dynamic trailing risk limits (VAR_059)."*

---

## 3. AWS Cloud Workload & Technical Architecture

### Question: How does your product use AWS services? (Credit Justification)
> *"Voltacent's data discovery, model training, and low-latency order routing rely extensively on the AWS cloud ecosystem:*
>
> 1. *Amazon EC2 Spot Instances (r6a.4xlarge, 16 vCPU / 128 GB RAM): We run memory-intensive, expanding-window walk-forward validation across 11 annual out-of-sample folds covering 123 currency pairs and 7 timeframes (M15 through Monthly). EC2 Spot instances allow us to parallelize heavy tree-boosting (XGBoost/LightGBM) and deep causal autoencoder training cost-effectively.*
> 2. *Amazon S3 Columnar Tick Lake: We store and query over 24 years of raw and feature-engineered historical tick data staged in columnar Apache Parquet format, partitioned by instrument, timeframe, and point-in-time timestamps.*
> 3. *Amazon EC2 Dedicated Execution Nodes (us-east-1): We run 24/7 low-latency headless execution gateways that connect to broker ECN servers via low-latency RPyC IPC bridges, ensuring sub-38ms execution velocity under live market conditions.*
> 4. *Amazon CloudWatch & Amazon SNS: Automated real-time telemetry monitors execution latency, slip distributions, and portfolio drawdown guardrails, triggering instant circuit-breakers if risk parameters deviate from backtested boundaries."*

### Question: How will AWS Activate credits be used over the next 12 months?
> *"The requested AWS Activate credits will directly fund our compute and storage expansion during our canary deployment:*
> * 65% allocated to Amazon EC2 Spot clusters for expanding our continuous walk-forward retraining pipeline and scaling deep causal sequence models.
> * 20% allocated to 24/7 dedicated low-latency EC2 execution nodes and VPC peering in us-east-1.
> * 15% allocated to Amazon S3 data lake storage, data transfer, and CloudWatch operational monitoring."*

---

## 4. Submission Checklist

- [x] Website is live and returning HTTP `200 OK` (`https://bishalsarkar.me/voltacent/`).
- [x] Dedicated AWS Infrastructure section visible on the landing page (`#aws-infrastructure`).
- [x] Contact email uses official domain mailbox (`contact@bishalsarkar.me`).
- [x] No mentions of retail forex copy-trading or bot-passing services.
- [x] OpenGraph social preview images and favicon load cleanly.
