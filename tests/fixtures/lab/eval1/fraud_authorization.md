# Pre-experiment framing — quantum advantage in fraud / AML

After the recommendation program closed, the team wants to know whether any quantum direction
can earn its keep in financial crime. Candidates proposed in the kickoff discussion:

1. A quantum kernel / quantum feature map for **card authorisation scoring** — every card
   transaction is scored before approval; the business cares about fraud caught at a fixed false
   positive rate.
2. Quantum graph features (spectral or walk-based) served to the fraud model for **each transaction**
   from the transaction graph.
3. Quantum optimisation for **AML alert prioritisation** — rank the nightly alerts over the customer
   book for investigators.
4. Quantum amplitude estimation for **model validation / threshold calibration** — estimating tail
   probabilities of the monitoring model quarterly, using an agent-based customer-behaviour simulator.

Constraints mentioned: authorisation must answer in 10–50 ms at ~10⁴ transactions per second;
GNN serving at 100–300 ms is already excluded from that budget; alert generation runs as a
nightly batch; validation runs quarterly.

Question for the lab: which of these deserves an experiment?
