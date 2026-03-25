from enum import Enum
from dataclasses import dataclass

class AgentType(Enum):
    RISK_AVERSE = 'risk_averse'
    RISK_SEEKING = 'risk_seeking'
    MOMENTUM = 'momentum'
    CONTRARIAN = 'contrarian'
    NOISE = 'noise'

class Action(Enum):
    BUY = 'buy'
    SELL = 'sell'
    HOLD = 'hold'

@dataclass
class AgentState:
    cash: float
    stocks: int
    current_price: float

class TradingAgent:
    def __init__(self, agent_type: AgentType, initial_cash: float):
        self.agent_type = agent_type
        self.state = AgentState(cash=initial_cash, stocks=0, current_price=0.0)

    def act(self, market_conditions):
        pass  # logic for decision making based on personality type
