"""Independent exact-rational reference, deterministic seed 94317."""
from fractions import Fraction as F
import json, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from radar_trade_study import review_scenario
p=json.loads((ROOT/'examples/scenario-long.json').read_text())
r=random.Random(94317)
sample=['0.000000000000000001','0.000000000000000009','0.000000001','0.01','0.25','1','3','10','99999','999999999999999999.999999999999999999']
checked=0
for i in range(1000):
 side=r.choice(['long','short'])
 prices=sorted({r.choice(sample) for _ in range(5)},key=F)
 if len(prices)<3:continue
 lo,e,hi=prices[0],prices[len(prices)//2],prices[-1]
 z={**p,'side':side,'entry':e,'stop':lo if side=='long' else hi,'target':hi if side=='long' else lo,'equity':sample[-1],'risk_budget':r.choice(sample),'max_notional':r.choice(sample),'lot_step':r.choice(sample),'multiplier':r.choice(sample),'fee_bps_per_side':r.choice(['0','0.000000000000000001','0.01','1','10000']),'slippage_bps_per_side':r.choice(['0','0.000000000000000001','1','10000'])}
 v={k:F(z[k]) for k in ['entry','stop','target','equity','risk_budget','max_notional','lot_step','multiplier','fee_bps_per_side','slippage_bps_per_side']}
 E,S,T,M,step=(v[k] for k in ['entry','stop','target','multiplier','lot_step'])
 b=v['fee_bps_per_side']+v['slippage_bps_per_side']
 cost=(E+max(E,S,T))*M*b/10000
 loss=abs(E-S)*M+cost
 gain=abs(T-E)*M-cost
 bounds=[v['risk_budget']/(loss*step),v['max_notional']/(E*M*step)]
 entry_cost=E*M*b/10000
 if side=='long':bounds.append(v['equity']/((E*M+entry_cost)*step))
 q=min(x.numerator//x.denominator for x in bounds)*step
 out=review_scenario(z)
 expected='no_valid_scenario' if q<=0 or gain<=0 else 'ok'
 assert out['status']==expected,(z,out,expected)
 if expected=='ok':
  c=out['calculation']
  assert F(c['quantity'])==q,(z,c,q)
  assert F(c['modeled_loss'])==q*loss,(z,c,q*loss)
  assert F(c['net_gain'])==q*gain,(z,c,q*gain)
  assert F(c['modeled_loss'])<=v['risk_budget']
  assert F(c['notional'])<=v['max_notional']
  if side=='long':assert F(c['entry_outlay'])<=v['equity'] and F(c['cash_remaining'])>=0
 checked+=1
print('Exact Fraction arithmetic probes passed:',checked)
for text in ('2026-10-22T10:00:00-03:00','2026-10-22T13:00:00Z','2026-10-22T14:00:00+01:00'):
 out=review_scenario({**p,'observed_at':text})
 assert out['status']=='ok' and out['observed_at']=='2026-10-22T13:00:00+00:00'
print('Equivalent timezone observations normalized: 3')
