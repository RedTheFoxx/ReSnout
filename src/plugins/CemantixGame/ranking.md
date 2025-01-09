# Cemantix Game Ranking System

## Overview
The Cemantix Game uses a sophisticated ranking system combining ELO ratings with performance-based scoring. Players progress through ranks based on their cumulative points, with special bonuses for exceptional performances.

## Ranks & Tiers
Each rank has three tiers (III, II, I), with ascending point requirements:

| Rank     | Tier | Points |
|----------|------|--------|
| Bronze   | III  | 0      |
|          | II   | 100    |
|          | I    | 200    |
| Silver   | III  | 350    |
|          | II   | 525    |
|          | I    | 750    |
| Gold     | III  | 1000   |
|          | II   | 1300   |
|          | I    | 1600   |
| Platinum | III  | 2000   |
|          | II   | 2500   |
|          | I    | 3000   |
| Master   | III  | 3600   |
|          | II   | 4300   |
|          | I    | 5100   |

## Performance Scoring
Performance score $(S)$ calculation weights:
- Attempts: $2.0$ (primary factor)
- Time taken: $0.5$ (secondary factor)
- Accuracy & difficulty: $0.0$ (currently unused)

### Score Normalization
- **Attempts Score**:
  - $\leq 5$ attempts: $1.0$ (exceptional performance)
  - $> 5$ attempts: $$\max(0.1, \min(0.8, \frac{20.0}{\text{attempts}}))$$
- **Time Score**: $$\min(1.0, \frac{3600}{\max(\text{time\_taken}, 1)})$$

## Bonus & Penalty System
- **Penalty**: Score $< 0.2$
  - $1.5\times$ multiplier (50% more points lost)
- **Bonus**: Score $> 0.8$
  - $2.0\times$ multiplier (double points gained)
- **Exceptional Performance**: $\leq 5$ attempts
  - $2.5\times$ additional multiplier

## ELO System
- K-factor: $50$ (high volatility)
- Expected performance: $0.3$
- Shadow MMR: Moving average
  - $95\%$ previous MMR
  - $5\%$ new performance
- Points = $$K \times (\text{Performance} - \text{Shadow\_MMR}) \times \text{Bonus/Penalty\_Multiplier}$$

## Database Storage
The system maintains:
- Player ranks and points
- Global rankings
- Performance history
- Shadow MMR tracking
