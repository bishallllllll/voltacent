# Voltacent Quantitative Technologies

**Institutional Quantitative Alpha & Execution API**

Official public landing page and developer documentation portal for **Voltacent Quantitative Technologies** — providing high-throughput, point-in-time directional alpha signals, 32-dimensional causal deep learning market regime embeddings, and sub-second ECN order routing for proprietary trading desks and quantitative funds.

🌐 **Live Portal:** [https://bishalsarkar.me/voltacent/](https://bishalsarkar.me/voltacent/)

---

## ⚡ System Architecture

- **Predictive Engine:** Marcos López de Prado expanding-window walk-forward validation (11 annual folds, 2016–2026) with zero lookahead bias and strict point-in-time embargoes.
- **Deep Feature Discovery:** 32-dimensional causal Dilated Temporal Convolutional Network (TCN) autoencoder extracting multi-scale market regime latents (`dl_enc_0` .. `dl_enc_31`).
- **Consensus Ensemble:** Duck-typed gradient-boosted decision trees (XGBoost & LightGBM) calibrated to high-conviction threshold dead-zones ($\tau \ge 0.58$).
- **Cloud Infrastructure:** High-memory Amazon EC2 Spot clusters (`r6a.4xlarge`, 128 GB RAM), Amazon S3 columnar Parquet tick data lake, and dedicated 24/7 low-latency execution daemons in `us-east-1` monitored via Amazon CloudWatch.

---

## 📁 Repository Contents

- `index.html`: Standalone, high-performance dark-mode developer portal & landing page with interactive cURL, Python, and TypeScript SDK playground.
- `telemetry.json`: Real-time asynchronous feed providing verified execution metrics, forward win rate, and uptime verification from the AWS live canary node.
- `assets/`: High-resolution dashboard visualizations and telemetry benchmarks.
- `.nojekyll`: Bypasses Jekyll processing for pure static serving via GitHub Pages.

---

## 📄 License & Disclaimer

Copyright &copy; 2026 Voltacent Quantitative Technologies. All rights reserved.

*Regulatory & Risk Disclaimer:* Quantitative trading involves substantial risk of capital loss. Historical backtested walk-forward results and live forward testing are research evaluations and not guarantees of future performance. Voltacent provides quantitative technology and software APIs, not financial advisory services.
