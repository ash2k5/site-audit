from dataclasses import dataclass, field


@dataclass
class SEOData:
    title: str = ""
    meta_description: str = ""
    h1_tags: list[str] = field(default_factory=list)
    h2_tags: list[str] = field(default_factory=list)
    canonical_url: str = ""
    og_title: str = ""
    og_description: str = ""
    has_schema_markup: bool = False
    images_missing_alt: int = 0
    total_images: int = 0
    internal_links: int = 0
    external_links: int = 0
    word_count: int = 0
    has_cta: bool = False
    has_contact_info: bool = False


@dataclass
class CoreWebVitals:
    lcp: float | None = None
    cls: float | None = None
    fid: float | None = None
    fcp: float | None = None
    ttfb: float | None = None
    speed_index: float | None = None


@dataclass
class PerformanceData:
    mobile_score: int | None = None
    desktop_score: int | None = None
    mobile_vitals: CoreWebVitals = field(default_factory=CoreWebVitals)
    opportunities: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)


@dataclass
class TechnicalData:
    status_code: int = 200
    is_https: bool = False
    final_url: str = ""
    redirect_count: int = 0
    response_time_ms: float = 0
    has_robots_txt: bool = False
    has_sitemap: bool = False


@dataclass
class AuditInput:
    url: str
    seo: SEOData
    performance: PerformanceData
    technical: TechnicalData


@dataclass
class CategoryScore:
    score: int
    grade: str
    summary: str
    findings: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    title: str
    impact: str
    effort: str
    detail: str


@dataclass
class AuditReport:
    url: str
    company_name: str
    overall_score: int
    executive_summary: str
    seo: CategoryScore
    performance: CategoryScore
    technical: CategoryScore
    content: CategoryScore
    quick_wins: list[str]
    recommendations: list[Recommendation]
    raw_data: AuditInput | None = None
