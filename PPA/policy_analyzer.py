"""
Password Policy Analyzer - Core Analysis Engine

Dit module bevat de core logica voor het analyseren van password policies
tegen industry standards zoals NIST 800-63B en OWASP richtlijnen.

Classes:
    Severity: Enum voor severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    PolicyRequirement: Dataclass voor password policy vereisten
    Finding: Dataclass voor policy findings/issues
    BreachStatistics: Klasse met real-world breach statistics
    PolicyAnalyzer: Hoofdklasse voor policy analyse

Functions:
    calculate_security_score: Berekent overall security score op basis van findings
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PolicyRequirement:
    """Represents a password policy requirement"""
    min_length: int = 8
    max_length: Optional[int] = None
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    max_age_days: Optional[int] = None
    min_age_days: int = 0
    password_history: int = 0
    lockout_attempts: Optional[int] = None
    lockout_duration_minutes: Optional[int] = None
    prevent_common_passwords: bool = False
    prevent_user_info: bool = False
    prevent_repeating_chars: bool = False
    prevent_sequential_chars: bool = False


@dataclass
class Finding:
    """Represents a policy finding/issue"""
    severity: Severity
    title: str
    description: str
    recommendation: str
    standard: str  # NIST, OWASP, etc.
    breach_statistics: Optional[str] = None
    impact_score: int = 0  # 0-100


class BreachStatistics:
    """Real-world breach statistics and references"""
    
    STATS = {
        'nl': {
            "weak_passwords": {
                "percentage": 81,
                "description": "81% van alle datalekken zijn het gevolg van zwakke of gestolen wachtwoorden (Verizon DBIR 2023)",
                "source": "Verizon Data Breach Investigations Report 2023"
            },
            "password_reuse": {
                "percentage": 65,
                "description": "65% van gebruikers hergebruikt wachtwoorden tussen accounts (Google Security Study)",
                "source": "Google Security Study 2019"
            },
            "common_passwords": {
                "percentage": 91,
                "description": "91% van alle wachtwoorden kunnen binnen 6 uur worden gekraakt (Hive Systems 2023)",
                "source": "Hive Systems Password Table 2023"
            },
            "no_mfa": {
                "percentage": 99.9,
                "description": "99.9% van accounts zonder MFA kunnen worden gecompromitteerd met alleen een wachtwoord (Microsoft Security Intelligence)",
                "source": "Microsoft Security Intelligence Report"
            },
            "password_expiration": {
                "description": "NIST raadt af aan geforceerde wachtwoordverlopen omdat gebruikers dan zwakkere wachtwoorden kiezen",
                "source": "NIST 800-63B Section 5.1.1.2"
            },
            "complexity_requirements": {
                "description": "Complexity vereisten zonder lengte leiden vaak tot voorspelbare patronen (Password1!, Welcome123!)",
                "source": "NIST 800-63B, Microsoft Security Research"
            }
        },
        'en': {
            "weak_passwords": {
                "percentage": 81,
                "description": "81% of all data breaches are the result of weak or stolen passwords (Verizon DBIR 2023)",
                "source": "Verizon Data Breach Investigations Report 2023"
            },
            "password_reuse": {
                "percentage": 65,
                "description": "65% of users reuse passwords across accounts (Google Security Study)",
                "source": "Google Security Study 2019"
            },
            "common_passwords": {
                "percentage": 91,
                "description": "91% of all passwords can be cracked within 6 hours (Hive Systems 2023)",
                "source": "Hive Systems Password Table 2023"
            },
            "no_mfa": {
                "percentage": 99.9,
                "description": "99.9% of accounts without MFA can be compromised with just a password (Microsoft Security Intelligence)",
                "source": "Microsoft Security Intelligence Report"
            },
            "password_expiration": {
                "description": "NIST discourages forced password expiration because users then choose weaker passwords",
                "source": "NIST 800-63B Section 5.1.1.2"
            },
            "complexity_requirements": {
                "description": "Complexity requirements without length often lead to predictable patterns (Password1!, Welcome123!)",
                "source": "NIST 800-63B, Microsoft Security Research"
            }
        }
    }
    
    @classmethod
    def get_statistic(cls, key: str, lang: str = 'nl') -> Dict:
        stats = cls.STATS.get(lang, cls.STATS['nl'])
        return stats.get(key, {})


class PolicyAnalyzer:
    """Analyzes password policies against industry standards"""
    
    TRANSLATIONS = {
        'nl': {
            'min_length_critical_title': "Te korte minimale wachtwoordlengte",
            'min_length_critical_desc': "Je policy vereist minimaal {min_length} karakters. NIST 800-63B vereist minimaal 8 karakters.",
            'min_length_critical_rec': "Verhoog de minimale lengte naar minimaal 8 karakters, bij voorkeur 12-16 voor gevoelige accounts.",
            'min_length_high_title': "Suboptimale minimale wachtwoordlengte",
            'min_length_high_desc': "Je policy vereist {min_length} karakters. Hoewel dit voldoet aan NIST minimums, raadt NIST 12+ karakters aan voor betere beveiliging.",
            'min_length_high_rec': "Overweeg de minimale lengte te verhogen naar 12-16 karakters voor gevoelige accounts.",
            'min_length_high_stats': "Wachtwoorden met {min_length} karakters kunnen vaak binnen uren worden gekraakt. 12+ karakters verhogen de tijd exponentieel.",
            'max_length_title': "Te restrictieve maximale wachtwoordlengte",
            'max_length_desc': "Je policy beperkt wachtwoorden tot {max_length} karakters. Dit voorkomt het gebruik van lange passphrases.",
            'max_length_rec': "Verhoog de maximale lengte naar minimaal 64 karakters om passphrases mogelijk te maken.",
            'max_length_stats': "Passphrases zijn vaak veiliger dan complexe wachtwoorden omdat ze langer en makkelijker te onthouden zijn.",
            'complexity_high_title': "Complexity vereisten zonder voldoende lengte",
            'complexity_high_desc': "Je policy vereist hoofdletters, kleine letters, cijfers en speciale tekens, maar de minimale lengte is laag. Dit leidt tot voorspelbare patronen zoals 'Password1!' of 'Welcome123!'.",
            'complexity_high_rec': "Verwijder complexity vereisten OF verhoog de minimale lengte naar 12+ karakters. NIST raadt aan om lengte boven complexity te prioriteren.",
            'complexity_info_title': "Complexity vereisten aanwezig",
            'complexity_info_desc': "Je policy heeft complexity vereisten. NIST raadt aan om lengte boven complexity te prioriteren, maar met voldoende lengte is dit acceptabel.",
            'complexity_info_rec': "Overweeg om complexity vereisten te versoepelen en in plaats daarvan te focussen op lengte en het voorkomen van veelvoorkomende wachtwoorden.",
            'complexity_info_stats': "Complexity vereisten kunnen gebruikers frustreren en leiden tot zwakkere wachtwoorden als ze niet gecombineerd worden met voldoende lengte.",
            'expiration_high_title': "Geforceerde wachtwoordverlopen",
            'expiration_high_desc': "Je policy forceert wachtwoordverlopen elke {max_age_days} dagen. NIST raadt dit af omdat gebruikers dan zwakkere wachtwoorden kiezen of incrementele wijzigingen maken (Password1 → Password2).",
            'expiration_high_rec': "Verwijder geforceerde wachtwoordverlopen. In plaats daarvan: controleer op gecompromitteerde wachtwoorden en forceer alleen wijziging bij vermoeden van compromittering.",
            'expiration_medium_title': "Wachtwoordverlopen aanwezig",
            'expiration_medium_desc': "Je policy forceert wachtwoordverlopen elke {max_age_days} dagen. Hoewel dit minder agressief is, raadt NIST dit nog steeds af.",
            'expiration_medium_rec': "Overweeg om geforceerde verlopen te verwijderen en in plaats daarvan te focussen op detectie van gecompromitteerde wachtwoorden.",
            'history_high_title': "Geen wachtwoordgeschiedenis",
            'history_high_desc': "Je policy voorkomt niet dat gebruikers oude wachtwoorden hergebruiken. Dit maakt het makkelijker om terug te vallen op zwakke wachtwoorden.",
            'history_high_rec': "Implementeer wachtwoordgeschiedenis om de laatste 5-10 wachtwoorden te voorkomen.",
            'history_medium_title': "Beperkte wachtwoordgeschiedenis",
            'history_medium_desc': "Je policy voorkomt hergebruik van de laatste {password_history} wachtwoorden. Dit is beter dan niets, maar meer is aanbevolen.",
            'history_medium_rec': "Overweeg om de geschiedenis uit te breiden naar minimaal 5-10 wachtwoorden.",
            'lockout_critical_title': "Geen account lockout mechanisme",
            'lockout_critical_desc': "Je policy heeft geen account lockout mechanisme. Dit maakt brute force aanvallen mogelijk.",
            'lockout_critical_rec': "Implementeer account lockout na 5-10 mislukte pogingen met een lockout duur van 15-30 minuten.",
            'lockout_critical_stats': "Brute force aanvallen zijn verantwoordelijk voor een aanzienlijk deel van succesvolle account compromitteringen.",
            'lockout_medium_title': "Te permissieve account lockout",
            'lockout_medium_desc': "Je policy blokkeert accounts pas na {lockout_attempts} mislukte pogingen. Dit geeft aanvallers te veel kansen.",
            'lockout_medium_rec': "Verlaag het aantal toegestane pogingen naar 5-10 voordat lockout optreedt.",
            'lockout_medium_stats': "Moderne brute force tools kunnen duizenden pogingen per minuut uitvoeren.",
            'common_critical_title': "Geen controle op veelvoorkomende wachtwoorden",
            'common_critical_desc': "Je policy controleert niet op veelvoorkomende of gecompromitteerde wachtwoorden. Dit is een van de belangrijkste beveiligingsmaatregelen.",
            'common_critical_rec': "Implementeer controle tegen lijsten van veelvoorkomende wachtwoorden (zoals Have I Been Pwned) en gecompromitteerde wachtwoorden.",
            'user_info_title': "Geen controle op gebruikersinformatie in wachtwoorden",
            'user_info_desc': "Je policy voorkomt niet dat gebruikers hun gebruikersnaam, email of andere persoonlijke informatie in wachtwoorden gebruiken.",
            'user_info_rec': "Implementeer controle om te voorkomen dat wachtwoorden gebruikersnamen, email adressen of andere gebruikersinformatie bevatten.",
            'user_info_stats': "Wachtwoorden die gebruikersinformatie bevatten zijn makkelijker te raden bij targeted attacks.",
            'repeating_title': "Geen controle op herhalende karakters",
            'repeating_desc': "Je policy voorkomt niet dat gebruikers wachtwoorden met veel herhalende karakters gebruiken (bijv. 'aaaaaa' of '111111').",
            'repeating_rec': "Overweeg om wachtwoorden met meer dan 3-4 opeenvolgende identieke karakters te voorkomen.",
            'repeating_stats': "Herhalende karakters verminderen de entropie van wachtwoorden aanzienlijk.",
            'sequential_title': "Geen controle op sequentiële karakters",
            'sequential_desc': "Je policy voorkomt niet dat gebruikers sequentiële karakters gebruiken (bijv. '12345' of 'abcde').",
            'sequential_rec': "Overweeg om wachtwoorden met meer dan 3-4 opeenvolgende sequentiële karakters te voorkomen.",
            'sequential_stats': "Sequentiële patronen zijn makkelijker te raden en verminderen wachtwoordsterkte.",
            'score_excellent': "Uitstekend! Je password policy voldoet aan alle industry standards.",
            'score_good': "Goed! Je policy is sterk, maar er zijn nog enkele verbeteringen mogelijk.",
            'score_reasonable': "Redelijk. Je policy voldoet aan basisvereisten maar mist belangrijke beveiligingsmaatregelen.",
            'score_weak': "Zwak. Je policy heeft significante beveiligingsproblemen die direct moeten worden aangepakt.",
            'score_very_weak': "Zeer zwak. Je policy heeft kritieke beveiligingsproblemen.",
            'score_critical': "Kritiek. Je policy voldoet niet aan basisbeveiligingsstandaarden."
        },
        'en': {
            'min_length_critical_title': "Minimum password length too short",
            'min_length_critical_desc': "Your policy requires a minimum of {min_length} characters. NIST 800-63B requires at least 8 characters.",
            'min_length_critical_rec': "Increase the minimum length to at least 8 characters, preferably 12-16 for sensitive accounts.",
            'min_length_high_title': "Suboptimal minimum password length",
            'min_length_high_desc': "Your policy requires {min_length} characters. While this meets NIST minimums, NIST recommends 12+ characters for better security.",
            'min_length_high_rec': "Consider increasing the minimum length to 12-16 characters for sensitive accounts.",
            'min_length_high_stats': "Passwords with {min_length} characters can often be cracked within hours. 12+ characters increase the time exponentially.",
            'max_length_title': "Too restrictive maximum password length",
            'max_length_desc': "Your policy limits passwords to {max_length} characters. This prevents the use of long passphrases.",
            'max_length_rec': "Increase the maximum length to at least 64 characters to enable passphrases.",
            'max_length_stats': "Passphrases are often more secure than complex passwords because they are longer and easier to remember.",
            'complexity_high_title': "Complexity requirements without sufficient length",
            'complexity_high_desc': "Your policy requires uppercase, lowercase, numbers and special characters, but the minimum length is low. This leads to predictable patterns like 'Password1!' or 'Welcome123!'.",
            'complexity_high_rec': "Remove complexity requirements OR increase the minimum length to 12+ characters. NIST recommends prioritizing length over complexity.",
            'complexity_info_title': "Complexity requirements present",
            'complexity_info_desc': "Your policy has complexity requirements. NIST recommends prioritizing length over complexity, but with sufficient length this is acceptable.",
            'complexity_info_rec': "Consider relaxing complexity requirements and instead focus on length and preventing common passwords.",
            'complexity_info_stats': "Complexity requirements can frustrate users and lead to weaker passwords if not combined with sufficient length.",
            'expiration_high_title': "Forced password expiration",
            'expiration_high_desc': "Your policy forces password expiration every {max_age_days} days. NIST discourages this because users then choose weaker passwords or make incremental changes (Password1 → Password2).",
            'expiration_high_rec': "Remove forced password expiration. Instead: check for compromised passwords and only force changes when compromise is suspected.",
            'expiration_medium_title': "Password expiration present",
            'expiration_medium_desc': "Your policy forces password expiration every {max_age_days} days. While this is less aggressive, NIST still discourages this.",
            'expiration_medium_rec': "Consider removing forced expiration and instead focus on detecting compromised passwords.",
            'history_high_title': "No password history",
            'history_high_desc': "Your policy does not prevent users from reusing old passwords. This makes it easier to fall back to weak passwords.",
            'history_high_rec': "Implement password history to prevent the last 5-10 passwords.",
            'history_medium_title': "Limited password history",
            'history_medium_desc': "Your policy prevents reuse of the last {password_history} passwords. This is better than nothing, but more is recommended.",
            'history_medium_rec': "Consider expanding the history to at least 5-10 passwords.",
            'lockout_critical_title': "No account lockout mechanism",
            'lockout_critical_desc': "Your policy has no account lockout mechanism. This enables brute force attacks.",
            'lockout_critical_rec': "Implement account lockout after 5-10 failed attempts with a lockout duration of 15-30 minutes.",
            'lockout_critical_stats': "Brute force attacks are responsible for a significant portion of successful account compromises.",
            'lockout_medium_title': "Too permissive account lockout",
            'lockout_medium_desc': "Your policy only blocks accounts after {lockout_attempts} failed attempts. This gives attackers too many chances.",
            'lockout_medium_rec': "Reduce the number of allowed attempts to 5-10 before lockout occurs.",
            'lockout_medium_stats': "Modern brute force tools can perform thousands of attempts per minute.",
            'common_critical_title': "No common password check",
            'common_critical_desc': "Your policy does not check for common or compromised passwords. This is one of the most important security measures.",
            'common_critical_rec': "Implement checks against lists of common passwords (such as Have I Been Pwned) and compromised passwords.",
            'user_info_title': "No check for user information in passwords",
            'user_info_desc': "Your policy does not prevent users from using their username, email or other personal information in passwords.",
            'user_info_rec': "Implement checks to prevent passwords from containing usernames, email addresses or other user information.",
            'user_info_stats': "Passwords containing user information are easier to guess in targeted attacks.",
            'repeating_title': "No check for repeating characters",
            'repeating_desc': "Your policy does not prevent users from using passwords with many repeating characters (e.g. 'aaaaaa' or '111111').",
            'repeating_rec': "Consider preventing passwords with more than 3-4 consecutive identical characters.",
            'repeating_stats': "Repeating characters significantly reduce password entropy.",
            'sequential_title': "No check for sequential characters",
            'sequential_desc': "Your policy does not prevent users from using sequential characters (e.g. '12345' or 'abcde').",
            'sequential_rec': "Consider preventing passwords with more than 3-4 consecutive sequential characters.",
            'sequential_stats': "Sequential patterns are easier to guess and reduce password strength.",
            'score_excellent': "Excellent! Your password policy meets all industry standards.",
            'score_good': "Good! Your policy is strong, but there are still some improvements possible.",
            'score_reasonable': "Reasonable. Your policy meets basic requirements but lacks important security measures.",
            'score_weak': "Weak. Your policy has significant security issues that need to be addressed immediately.",
            'score_very_weak': "Very weak. Your policy has critical security issues.",
            'score_critical': "Critical. Your policy does not meet basic security standards."
        }
    }
    
    def __init__(self, lang: str = 'nl'):
        self.findings: List[Finding] = []
        self.lang = lang
        self.t = self.TRANSLATIONS.get(lang, self.TRANSLATIONS['nl'])
    
    def analyze(self, policy: PolicyRequirement) -> List[Finding]:
        """Analyze a password policy and return findings"""
        self.findings = []
        
        # NIST 800-63B Checks
        self._check_min_length(policy)
        self._check_max_length(policy)
        self._check_complexity_requirements(policy)
        self._check_password_expiration(policy)
        self._check_password_history(policy)
        self._check_account_lockout(policy)
        self._check_common_password_prevention(policy)
        self._check_user_info_prevention(policy)
        self._check_repeating_chars(policy)
        self._check_sequential_chars(policy)
        
        return sorted(self.findings, key=lambda x: (x.severity.value, -x.impact_score))
    
    def _check_min_length(self, policy: PolicyRequirement):
        """NIST 800-63B: Minimum 8 characters, but recommends allowing up to 64+"""
        if policy.min_length < 8:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                title=self.t['min_length_critical_title'],
                description=self.t['min_length_critical_desc'].format(min_length=policy.min_length),
                recommendation=self.t['min_length_critical_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=BreachStatistics.get_statistic("weak_passwords", self.lang)["description"],
                impact_score=95
            ))
        elif policy.min_length < 12:
            self.findings.append(Finding(
                severity=Severity.HIGH,
                title=self.t['min_length_high_title'],
                description=self.t['min_length_high_desc'].format(min_length=policy.min_length),
                recommendation=self.t['min_length_high_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=self.t['min_length_high_stats'].format(min_length=policy.min_length),
                impact_score=75
            ))
    
    def _check_max_length(self, policy: PolicyRequirement):
        """NIST 800-63B: Should allow up to at least 64 characters"""
        if policy.max_length and policy.max_length < 64:
            self.findings.append(Finding(
                severity=Severity.MEDIUM,
                title=self.t['max_length_title'],
                description=self.t['max_length_desc'].format(max_length=policy.max_length),
                recommendation=self.t['max_length_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=self.t['max_length_stats'],
                impact_score=50
            ))
    
    def _check_complexity_requirements(self, policy: PolicyRequirement):
        """NIST 800-63B: Complexity requirements are NOT recommended"""
        has_complexity = (policy.require_uppercase and policy.require_lowercase and 
                         policy.require_numbers and policy.require_special_chars)
        
        if has_complexity and policy.min_length < 12:
            self.findings.append(Finding(
                severity=Severity.HIGH,
                title=self.t['complexity_high_title'],
                description=self.t['complexity_high_desc'],
                recommendation=self.t['complexity_high_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=BreachStatistics.get_statistic("complexity_requirements", self.lang)["description"],
                impact_score=80
            ))
        elif has_complexity:
            self.findings.append(Finding(
                severity=Severity.LOW,
                title=self.t['complexity_info_title'],
                description=self.t['complexity_info_desc'],
                recommendation=self.t['complexity_info_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=self.t['complexity_info_stats'],
                impact_score=30
            ))
    
    def _check_password_expiration(self, policy: PolicyRequirement):
        """NIST 800-63B: Password expiration is NOT recommended"""
        if policy.max_age_days:
            if policy.max_age_days <= 90:
                self.findings.append(Finding(
                    severity=Severity.HIGH,
                    title=self.t['expiration_high_title'],
                    description=self.t['expiration_high_desc'].format(max_age_days=policy.max_age_days),
                    recommendation=self.t['expiration_high_rec'],
                    standard="NIST 800-63B Section 5.1.1.2",
                    breach_statistics=BreachStatistics.get_statistic("password_expiration", self.lang)["description"],
                    impact_score=70
                ))
            else:
                self.findings.append(Finding(
                    severity=Severity.MEDIUM,
                    title=self.t['expiration_medium_title'],
                    description=self.t['expiration_medium_desc'].format(max_age_days=policy.max_age_days),
                    recommendation=self.t['expiration_medium_rec'],
                    standard="NIST 800-63B Section 5.1.1.2",
                    breach_statistics=BreachStatistics.get_statistic("password_expiration", self.lang)["description"],
                    impact_score=50
                ))
    
    def _check_password_history(self, policy: PolicyRequirement):
        """NIST 800-63B: Should prevent reuse of recent passwords"""
        if policy.password_history == 0:
            self.findings.append(Finding(
                severity=Severity.HIGH,
                title=self.t['history_high_title'],
                description=self.t['history_high_desc'],
                recommendation=self.t['history_high_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=BreachStatistics.get_statistic("password_reuse", self.lang)["description"],
                impact_score=75
            ))
        elif policy.password_history < 5:
            self.findings.append(Finding(
                severity=Severity.MEDIUM,
                title=self.t['history_medium_title'],
                description=self.t['history_medium_desc'].format(password_history=policy.password_history),
                recommendation=self.t['history_medium_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=BreachStatistics.get_statistic("password_reuse", self.lang)["description"],
                impact_score=55
            ))
    
    def _check_account_lockout(self, policy: PolicyRequirement):
        """OWASP/NIST: Should have account lockout to prevent brute force"""
        if not policy.lockout_attempts:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                title=self.t['lockout_critical_title'],
                description=self.t['lockout_critical_desc'],
                recommendation=self.t['lockout_critical_rec'],
                standard="OWASP Authentication Cheat Sheet, NIST 800-63B",
                breach_statistics=self.t['lockout_critical_stats'],
                impact_score=90
            ))
        elif policy.lockout_attempts > 10:
            self.findings.append(Finding(
                severity=Severity.MEDIUM,
                title=self.t['lockout_medium_title'],
                description=self.t['lockout_medium_desc'].format(lockout_attempts=policy.lockout_attempts),
                recommendation=self.t['lockout_medium_rec'],
                standard="OWASP Authentication Cheat Sheet",
                breach_statistics=self.t['lockout_medium_stats'],
                impact_score=60
            ))
    
    def _check_common_password_prevention(self, policy: PolicyRequirement):
        """NIST 800-63B: Should check against common/breached passwords"""
        if not policy.prevent_common_passwords:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                title=self.t['common_critical_title'],
                description=self.t['common_critical_desc'],
                recommendation=self.t['common_critical_rec'],
                standard="NIST 800-63B Section 5.1.1.2",
                breach_statistics=BreachStatistics.get_statistic("common_passwords", self.lang)["description"],
                impact_score=95
            ))
    
    def _check_user_info_prevention(self, policy: PolicyRequirement):
        """OWASP: Should prevent passwords containing user information"""
        if not policy.prevent_user_info:
            self.findings.append(Finding(
                severity=Severity.MEDIUM,
                title=self.t['user_info_title'],
                description=self.t['user_info_desc'],
                recommendation=self.t['user_info_rec'],
                standard="OWASP Authentication Cheat Sheet",
                breach_statistics=self.t['user_info_stats'],
                impact_score=50
            ))
    
    def _check_repeating_chars(self, policy: PolicyRequirement):
        """OWASP: Should prevent excessive repeating characters"""
        if not policy.prevent_repeating_chars:
            self.findings.append(Finding(
                severity=Severity.LOW,
                title=self.t['repeating_title'],
                description=self.t['repeating_desc'],
                recommendation=self.t['repeating_rec'],
                standard="OWASP Authentication Cheat Sheet",
                breach_statistics=self.t['repeating_stats'],
                impact_score=30
            ))
    
    def _check_sequential_chars(self, policy: PolicyRequirement):
        """OWASP: Should prevent sequential characters"""
        if not policy.prevent_sequential_chars:
            self.findings.append(Finding(
                severity=Severity.LOW,
                title=self.t['sequential_title'],
                description=self.t['sequential_desc'],
                recommendation=self.t['sequential_rec'],
                standard="OWASP Authentication Cheat Sheet",
                breach_statistics=self.t['sequential_stats'],
                impact_score=25
            ))


def calculate_security_score(findings: List[Finding], lang: str = 'nl') -> Dict:
    """Calculate overall security score based on findings"""
    translations = PolicyAnalyzer.TRANSLATIONS.get(lang, PolicyAnalyzer.TRANSLATIONS['nl'])
    
    if not findings:
        return {
            "score": 100,
            "grade": "A+",
            "message": translations['score_excellent']
        }
    
    # Calculate base score
    base_score = 100
    severity_penalties = {
        Severity.CRITICAL: 20,
        Severity.HIGH: 15,
        Severity.MEDIUM: 10,
        Severity.LOW: 5,
        Severity.INFO: 2
    }
    
    for finding in findings:
        penalty = severity_penalties.get(finding.severity, 0)
        base_score -= penalty
    
    # Ensure score doesn't go below 0
    score = max(0, base_score)
    
    # Determine grade
    if score >= 90:
        grade = "A"
        message = translations['score_good']
    elif score >= 75:
        grade = "B"
        message = translations['score_reasonable']
    elif score >= 60:
        grade = "C"
        message = translations['score_weak']
    elif score >= 40:
        grade = "D"
        message = translations['score_very_weak']
    else:
        grade = "F"
        message = translations['score_critical']
    
    return {
        "score": score,
        "grade": grade,
        "message": message,
        "total_findings": len(findings),
        "critical_count": len([f for f in findings if f.severity == Severity.CRITICAL]),
        "high_count": len([f for f in findings if f.severity == Severity.HIGH]),
        "medium_count": len([f for f in findings if f.severity == Severity.MEDIUM]),
        "low_count": len([f for f in findings if f.severity == Severity.LOW])
    }
