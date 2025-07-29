import dask.dataframe as dd
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Literal, Optional, Union, Tuple

from .constants import HUMANIZED_METRICS, HUMANIZED_VIEW_TYPES


class Score(Enum):
    NONE = 'none'
    TRIVIAL = 'trivial'
    VERY_LOW = 'very low'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    VERY_HIGH = 'very high'
    CRITICAL = 'critical'


AnalysisAccuracy = Literal['accurate', 'optimistic', 'pessimistic']
Metric = Literal[
    'att_perf',
    'bw',
    'intensity',
    'iops',
    'time',
]
ViewType = Literal['file_name', 'proc_name', 'time_range']
ViewKey = Union[Tuple[ViewType], Tuple[ViewType, ViewType], Tuple[ViewType, ViewType, ViewType]]


@dataclass
class AnalysisRuntimeConfig:
    accuracy: AnalysisAccuracy
    checkpoint: bool
    cluster_type: str
    debug: bool
    memory: int
    num_threads_per_worker: int
    num_workers: int
    processes: bool
    threshold: float
    verbose: bool
    working_dir: str


@dataclass
class ScoringResult:
    critical_view: dd.DataFrame
    records_index: dd.Index
    scored_view: dd.DataFrame


@dataclass
class RawStats:
    job_time: dd.core.Scalar
    time_granularity: int
    total_count: dd.core.Scalar


@dataclass
class RuleReason:
    condition: str
    message: str


@dataclass
class Rule:
    name: str
    condition: str
    reasons: Optional[List[RuleReason]]
    # source: Optional[str]


@dataclass
class RuleResultReason:
    description: str
    # value: Optional[float]


@dataclass
class RuleResult:
    compact_desc: Optional[str]
    description: str
    detail_list: Optional[List[str]]
    extra_data: Optional[dict]
    object_hash: Optional[int]
    reasons: Optional[List[RuleResultReason]]
    value: Optional[Union[float, int, tuple]]
    value_fmt: Optional[str]
    _dataframe: Optional[pd.DataFrame] = None


@dataclass
class BottleneckOutput:
    description: str
    id: int
    metric: str
    num_files: int
    num_processes: int
    num_time_periods: int
    object_hash: int
    reasons: List[RuleResultReason]
    rule: str
    score: str
    view_name: str


@dataclass
class BottleneckResult:
    results: List[RuleResult]
    severities: Dict[str, int]


@dataclass
class ViewResult:
    critical_view: dd.DataFrame
    metric: str
    records: dd.DataFrame
    view: dd.DataFrame
    view_type: ViewType


MainView = dd.DataFrame

Characteristics = Dict[str, RuleResult]

ScoringPerView = Dict[ViewKey, ScoringResult]
ScoringPerViewPerMetric = Dict[Metric, ScoringPerView]

ViewResultsPerView = Dict[ViewKey, ViewResult]
ViewResultsPerViewPerMetric = Dict[Metric, ViewResultsPerView]


@dataclass
class OutputCharacteristicsType:
    complexity: float
    io_time: float
    job_time: float
    num_apps: int
    num_files: int
    num_nodes: int
    num_ops: int
    num_procs: int
    num_time_periods: int
    per_io_time: float


@dataclass
class OutputCountsType:
    raw_count: int
    hlm_count: int
    main_view_count: int
    avg_perspective_count: Dict[str, int]
    avg_perspective_count_std: Dict[str, float]
    avg_perspective_critical_count: Dict[str, int]
    avg_perspective_critical_count_std: Dict[str, float]
    perspective_skewness: Dict[str, float]
    root_perspective_skewness: Dict[str, float]
    per_records_discarded: Dict[str, float]
    per_records_retained: Dict[str, float]
    num_bottlenecks: Dict[str, int]
    num_metrics: int
    num_perspectives: int
    num_rules: int
    evaluated_records: Dict[str, int]
    perspective_count_tree: Dict[str, Dict[str, int]]
    perspective_critical_count_tree: Dict[str, Dict[str, int]]
    perspective_record_count_tree: Dict[str, Dict[str, int]]
    reasoned_records: Dict[str, int]
    slope_filtered_records: Dict[str, int]


@dataclass
class OutputSeveritiesType:
    critical_count: Dict[str, int]
    critical_tree: Dict[str, Dict[str, int]]
    very_high_count: Dict[str, int]
    very_high_tree: Dict[str, Dict[str, int]]
    high_count: Dict[str, int]
    high_tree: Dict[str, Dict[str, int]]
    medium_count: Dict[str, int]
    medium_tree: Dict[str, Dict[str, int]]
    low_count: Dict[str, int]
    very_low_count: Dict[str, int]
    trivial_count: Dict[str, int]
    none_count: Dict[str, int]
    root_critical_count: Dict[str, int]
    root_very_high_count: Dict[str, int]
    root_high_count: Dict[str, int]
    root_medium_count: Dict[str, int]
    root_low_count: Dict[str, int]
    root_very_low_count: Dict[str, int]
    root_trivial_count: Dict[str, int]
    root_none_count: Dict[str, int]


@dataclass
class OutputThroughputsType:
    bottlenecks: Dict[str, float]
    evaluated_records: Dict[str, float]
    perspectives: Dict[str, float]
    reasoned_records: Dict[str, float]
    rules: Dict[str, float]
    slope_filtered_records: Dict[str, float]


@dataclass
class OutputTimingsType:
    read_traces: Dict[str, float]
    compute_hlm: Dict[str, float]
    compute_main_view: Dict[str, float]
    compute_perspectives: Dict[str, float]
    detect_bottlenecks: Dict[str, float]
    attach_reasons: Dict[str, float]
    save_bottlenecks: Dict[str, float]


@dataclass
class OutputType:
    _bottlenecks: List[List[BottleneckOutput]]
    _characteristics: Characteristics
    _raw_stats: RawStats
    characteristics: OutputCharacteristicsType
    counts: OutputCountsType
    severities: OutputSeveritiesType
    throughputs: OutputThroughputsType
    timings: OutputTimingsType


@dataclass
class AnalyzerResultType:
    bottleneck_dir: str
    bottleneck_rules: dict
    characteristics: Characteristics
    evaluated_views: ScoringPerViewPerMetric
    main_view: MainView
    metric_boundaries: Dict[Metric, Union[int, float]]
    raw_stats: RawStats
    view_results: ViewResultsPerViewPerMetric
    _bottlenecks: Optional[dd.DataFrame] = None


def humanized_metric_name(metric: Metric):
    return HUMANIZED_METRICS[metric]


def humanized_view_name(view_key_type: Union[ViewKey, ViewType], separator='_'):
    if isinstance(view_key_type, tuple):
        return separator.join([HUMANIZED_VIEW_TYPES[view_type] for view_type in view_key_type])
    return HUMANIZED_VIEW_TYPES[view_key_type]


def view_name(view_key_type: Union[ViewKey, ViewType], separator='_'):
    return separator.join(view_key_type) if isinstance(view_key_type, tuple) else view_key_type
