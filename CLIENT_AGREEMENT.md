# Voltacent Technologies: Proprietary Software Licensing & Performance Royalty Agreement

**Document Ref:** `VLT-PaaS-2026-V1`  
**Licensor:** Voltacent Quantitative Technologies ("Voltacent")  
**Licensee:** The Client ("Licensee")  

---

## 1. Nature of the Relationship & Regulatory Status

1.1. **Software & Technology Provider Only:** Voltacent is purely a quantitative financial software, machine learning model, and algorithmic routing technology provider. Voltacent is **not** a Registered Investment Advisor (RIA), Commodity Trading Advisor (CTA), broker-dealer, or fund manager.  
1.2. **No Custody of Client Capital:** At no point does Voltacent accept, hold, custody, or manage client trading deposits or pooled funds.  
1.3. **Simulated Evaluation Environment:** The Licensee acknowledges that trading occurs exclusively on simulated demo evaluation accounts issued by independent, third-party proprietary trading firms ("Prop Firms", e.g., FTMO, The 5%ers, Pipster). Prop firm payouts are performance contractor compensation disbursed by the Prop Firm, not profits from a pooled capital fund.

---

## 2. Scope of Services & Software Deployment

2.1. **Algorithmic Automation:** Voltacent grants Licensee a non-exclusive, revocable license to deploy Voltacent's automated trading algorithms (the "Software") to execute trades on the Licensee's designated Prop Firm account(s).  
2.2. **Risk Parameters & Guardrails:** The Software executes according to strict quantitative rules, including:
* Maximum 1 active USD currency leg simultaneously (`VAR_090`).
* Dynamic trailing stop loss limits and automated daily drawdown ceilings (`VAR_059`).
* Decision bar timing calibrated to point-in-time H1 candle closes ($\tau \ge 0.58$).
2.3. **Mandatory Platform Requirement (MetaTrader 5 / MT5 Only):** The Software is engineered exclusively for automated execution via **MetaTrader 5 (MT5)**. The Licensee **must** select an MT5-supported account tier that permits algorithmic Expert Advisor (EA) execution when purchasing their Prop Firm challenge. Proprietary web terminals, TradeLocker, MatchTrader, DXtrade, and manual-only platforms are strictly unsupported. Voltacent assumes no obligation or liability to manage or trade unsupported platforms.

---

## 3. Performance Royalty & Fee Structure (60/40 Split)

3.1. **Zero Upfront Management Fee:** Voltacent charges **$0.00** in upfront software setup or recurring monthly subscription fees during active account management.  
3.2. **Performance Royalty Split:** When an account reaches funded status and the Prop Firm issues a payout:
* **Licensee Share:** **60.0%** of the net payout disbursed by the Prop Firm.
* **Voltacent Royalty:** **40.0%** of the net payout disbursed by the Prop Firm.
3.3. **Payment Terms:**
* The Licensee agrees to notify Voltacent within twenty-four (24) hours of receiving payout confirmation from the Prop Firm.
* Voltacent will issue an invoice for the 40% software performance royalty.
* The Licensee agrees to remit payment to Voltacent within forty-eight (48) hours of receiving funds from the Prop Firm.
3.4. **Payment Channels:** Performance royalties may be settled in:
* USD Coin (USDC) / Tether (USDT) on Arbitrum, Solana, or Ethereum.
* Direct corporate wire transfer to Voltacent's designated business bank account.

---

## 4. Evaluation Challenge Fee & Market Risk Policy (Non-Reimbursable)

4.1. **Client Fee Responsibility:** The Licensee is solely responsible for all evaluation purchase fees, challenge registration costs, platform charges, and account reset fees paid to third-party Prop Firms.  
4.2. **Strict Zero Reimbursement Policy:** Under no circumstances shall Voltacent refund, reimburse, guarantee, or be held liable for any challenge evaluation fees, account breaches, or disqualifications incurred on the Licensee's account.  
4.3. **Mutual No-Fault Termination:** In the event an evaluation account is disqualified or fails to achieve funded status, neither party owes the other any fees, penalties, or compensation. The Agreement terminates with zero continuing liability for either party.

---

## 5. Account Exclusivity & Interference

5.1. **No Manual Intervention:** The Licensee explicitly agrees **not** to place manual trades, modify open stop-loss or take-profit orders, or connect third-party Expert Advisors while the account is managed by Voltacent.  
5.2. **Breach of Exclusivity:** Any manual interference by the Licensee immediately terminates this Agreement and grants Voltacent the right to halt automation and revoke software licenses without notice.

---

## 6. Execution & Acceptance

By connecting and submitting supported **MetaTrader 5 (MT5)** Prop Firm login credentials (Account ID, Master Password, and Server Name) to Voltacent's execution gateway, the Licensee acknowledges, accepts, and agrees to be bound by all terms, conditions, and risk policies of this Agreement.

---

**Voltacent Quantitative Technologies**  
Authorized Signature: *Voltacent Operations Desk*  
Contact: `contact@bishalsarkar.me`  
Portal: `https://bishalsarkar.me/voltacent/`
