from sqlalchemy import Column, Integer, String, ForeignKey, Float
from .database import Base
from dataclasses import dataclass
from enum import Enum
from typing import Dict

class Power(Enum):
    GERMANY = 'GERMANY'
    FRANCE = 'FRANCE'
    RUSSIA = 'RUSSIA'
    AUSTRIA = 'AUSTRIA'
    ITALY = 'ITALY'
    TURKEY = 'TURKEY'
    ENGLAND = 'ENGLAND'

def fix_state_name(name:str) -> str:
    if name == "TYN":
        return "TYS"
    if name == "GOL":
        return "GAL"
    return name

# use fix state name to fix the state names before initializing the enum
class State(Enum):
    ADRIATIC_SEA = "ADR"
    AEGEAN_SEA = "AEG"
    ALBANIA = "ALB"
    ANKARA = "ANK"
    APULIA = "APU"
    ARMENIA = "ARM"
    BALTIC_SEA = "BAL"
    BARRENTS_SEA = "BAR"
    BELGIUM = "BEL"
    BERLIN = "BER"
    BLACK_SEA = "BLA"
    BOHEMIA = "BOH"
    GULF_OF_BOTHNIA = "BOT"
    BREST = "BRE"
    BUDAPEST = "BUD"
    BULGARIA = "BUL"
    BURGUNDY = "BUR"
    CLYDE = "CLY"
    CONSTANTINOPLE = "CON"
    DENMARK = "DEN"
    EASTERN_MEDITERRANEAN = "EAS"
    EDINBURGH = "EDI"
    ENGLISH_CHANNEL = "ENG"
    FINLAND = "FIN"
    GALICIA = "GAL"
    GASCONY = "GAS"
    GULF_OF_LYON = "LYO"
    GREECE = "GRE"
    HELIGOLAND_BIGHT = "HEL"
    HOLLAND = "HOL"
    IONIAN_SEA = "ION"
    IRISH_SEA = "IRI"
    KIEL = "KIE"
    LONDON = "LON"
    LIVERPOOL = "LVP"
    LIVONIA = "LVN"
    MID_ATLANTIC_OCEAN = "MAO"
    MARSEILLES = "MAR"
    MOSCOW = "MOS"
    MUNICH = "MUN"
    NAPLES = "NAP"
    NORTH_AFRICA = "NAF"
    NORTH_ATLANTIC_OCEAN = "NAO"
    NORTH_SEA = "NTH"
    NORWEGIAN_SEA = "NWG"
    NORWAY = "NWY"
    PARIS = "PAR"
    PICARDY = "PIC"
    PIEDMONT = "PIE"
    PRUSSIA = "PRU"
    ROME = "ROM"
    RUHR = "RUH"
    RUMANIA = "RUM"
    SEVASTOPOL = "SEV"
    SERBIA = "SER"
    SILESIA = "SIL"
    SKAGERRAK = "SKA"
    SMYRNA = "SMY"
    SPAIN = "SPA"
    ST_PETERSBURG = "STP"
    SWEDEN = "SWE"
    SYRIA = "SYR"
    TRIESTE = "TRI"
    TUNIS = "TUN"
    TUSCANY = "TUS"
    TYROLIA = "TYR"
    TYRRHENIAN_SEA = "TYS"
    UKRAINE = "UKR"
    VENICE = "VEN"
    VIENNA = "VIE"
    WALES = "WAL"
    WARSAW = "WAR"
    WESTERN_MEDITERRANEAN = "WES"
    YORKSHIRE = "YOR"

class GameHardness(Enum):
    EASY = 'E'
    MEDIUM = 'M'
    HARD = 'H'

    def __lt__(self, other):
        order = ["EASY", "MEDIUM", "HARD"]
        if not isinstance(other, GameHardness):
            return NotImplemented
        return order.index(self.name) < order.index(other.name)

class ContextVSSuggestion(Enum):
    NEUTRAL = 'N'
    CONSISTENT = 'C'
    AGAINST = 'A'

    def __lt__(self, other):
        order = ["CONSISTENT", "NEUTRAL", "AGAINST"]
        if not isinstance(other, ContextVSSuggestion):
            return NotImplemented
        return order.index(self.name) < order.index(other.name)

@dataclass
class DiplomacyScenario:
        qid:int
        map_name:str
        player_name: str
        units: int
        complexity: GameHardness
        context: ContextVSSuggestion
        stance: dict
        description: str
        map_data: dict=None

class Treatment(Enum):
    NULL = 'N'
    TEXT_BEST = 'TB'
    TEXT_K_TOP = 'TKT'
    VISUAL_BEST = 'VB'
    VISUAL_K_TOP_SEPARATE = 'VKTS'
    DELAYED_TEXT_BEST = 'TBD'
    DELAYED_TEXT_K_TOP = 'TKTD'
    DELAYED_VISUAL_BEST = 'VBD'
    DELAYED_VISUAL_K_TOP_SEPARATE = 'VKTSD'

    def __lt__(self, other):
        order = ["NULL", "TEXT_BEST", "TEXT_K_TOP", "VISUAL_BEST", "VISUAL_K_TOP_SEPARATE", "DELAYED_TEXT_BEST", "DELAYED_TEXT_K_TOP", "DELAYED_VISUAL_BEST", "DELAYED_VISUAL_K_TOP_SEPARATE"]
        if not isinstance(other, Treatment):
            return NotImplemented
        return order.index(self.name) < order.index(other.name)

class LikertScale(Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

    def __lt__(self, other):
        order = ["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        if not isinstance(other, LikertScale):
            return NotImplemented
        return order.index(self.name) > order.index(other.name)

@dataclass
class SurveyResponseInstance:
    participant_name: str
    scenario: DiplomacyScenario
    treatment: Treatment

@dataclass
class SurveyResponseInstanceSimple(SurveyResponseInstance):
    orders: Dict[State, str]
    time_spent: float
    first_click_time: float
    last_click_time: float
    number_of_clicks: int
    comment: str
    mental_demand: LikertScale
    successful_in_accomplishing: LikertScale
    how_hard: LikertScale
    how_frustrating: LikertScale

@dataclass
class SurveyResponseInstanceDelayed(SurveyResponseInstance):
    orders: Dict[int, Dict[State, str]]
    time_spent: Dict[int, float]
    first_click_time: Dict[int, float]
    last_click_time: Dict[int, float]
    number_of_clicks: Dict[int, int]
    comment: Dict[int, str]
    mental_demand: Dict[int, LikertScale]
    successful_in_accomplishing: Dict[int, LikertScale]
    how_hard: Dict[int, LikertScale]
    how_frustrating: Dict[int, LikertScale]


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class ResponseSimple(Base):
    __tablename__ = "responses_simple"
    id = Column(Integer, primary_key=True, index=True)
    qid = Column(Integer)
    number_of_annotations = Column(Integer, default=0)
    participant_name = Column(String)
    map_name = Column(String)
    player_name = Column(String)
    context = Column(String)
    stance = Column(String)
    treatment = Column(String)
    orders = Column(String)
    time_spent = Column(Float)
    first_click_time = Column(Float)
    last_click_time = Column(Float)
    number_of_clicks = Column(Integer)
    comment = Column(String)
    mental_demand = Column(String)
    successful_in_accomplishing = Column(String)
    how_hard = Column(String)
    how_frustrating = Column(String)
    orders_str = Column(String)
    map_url = Column(String)
    time_spent_normalized_by_null = Column(Float)
    number_of_clicks_normalized_by_null = Column(Float)

class ResponseMulti(Base):
    __tablename__ = "responses_multi"
    id = Column(Integer, primary_key=True, index=True)
    qid = Column(Integer)
    number_of_annotations = Column(Integer, default=0)
    participant_name = Column(String)
    map_name = Column(String)
    player_name = Column(String)
    context = Column(String)
    stance = Column(String)
    treatment = Column(String)
    orders = Column(String)
    time_spent = Column(String)
    first_click_time = Column(String)
    last_click_time = Column(String)
    number_of_clicks = Column(String)
    comment = Column(String)
    mental_demand = Column(String)
    successful_in_accomplishing = Column(String)
    how_hard = Column(String)
    how_frustrating = Column(String)
    orders0_str = Column(String)
    orders1_str = Column(String)
    map_url0 = Column(String)
    map_url1 = Column(String)
    comments0_str = Column(String)
    comments1_str = Column(String)
    time_diff = Column(Float)
    click_diff = Column(Integer)
    mental_demand_diff = Column(Integer)
    successful_in_accomplishing_diff = Column(Integer)
    how_hard_diff = Column(Integer)
    how_frustrating_diff = Column(Integer)
    order_diff = Column(Integer)

class PairwiseComparisonSimple(Base):
    __tablename__ = "pairwise_comparisons_simple"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferred_response_id = Column(Integer, ForeignKey("responses_simple.id"))
    other_response_id = Column(Integer, ForeignKey("responses_simple.id"))

class PairwiseComparisonMulti(Base):
    __tablename__ = "pairwise_comparisons_multi"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferred_response_id = Column(Integer, ForeignKey("responses_multi.id"))
    other_response_id = Column(Integer, ForeignKey("responses_multi.id"))
