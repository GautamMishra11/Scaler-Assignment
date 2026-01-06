"""
Name generation utilities with realistic distributions
"""

import random
from typing import List, Tuple, Optional
from faker import Faker


class NameGenerator:
    """
    Generates realistic names with demographic distributions
    Uses Faker with US Census data built-in
    """
    
    def __init__(self, locale: str = 'en_US', seed: Optional[int] = None):
        """
        Initialize name generator
        
        Args:
            locale: Faker locale (e.g., 'en_US', 'en_GB')
            seed: Random seed for reproducibility
        """
        self.faker = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
        
        # Cache generated names to avoid duplicates
        self.used_names = set()
        self.used_emails = set()
    
    def generate_name(self, gender: Optional[str] = None) -> str:
        """
        Generate realistic full name
        
        Args:
            gender: Optional gender ('male', 'female', or None for random)
            
        Returns:
            Full name string
        """
        max_attempts = 100
        
        for _ in range(max_attempts):
            if gender == 'male':
                name = self.faker.name_male()
            elif gender == 'female':
                name = self.faker.name_female()
            else:
                name = self.faker.name()
            
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        
        # Fallback: add suffix to avoid duplicates
        base_name = self.faker.name()
        counter = 1
        while f"{base_name} {counter}" in self.used_names:
            counter += 1
        
        name = f"{base_name} {counter}"
        self.used_names.add(name)
        return name
    
    def generate_email(
        self,
        name: str,
        domain: str,
        format_style: str = 'first.last'
    ) -> str:
        """
        Generate email from name
        
        Args:
            name: Full name
            domain: Email domain (e.g., 'company.com')
            format_style: Email format ('first.last', 'firstlast', 'flast', 'first')
            
        Returns:
            Email address
        """
        # Parse name
        parts = name.lower().split()
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]
        else:
            first = parts[0]
            last = 'user'
        
        # Clean special characters
        first = ''.join(c for c in first if c.isalnum())
        last = ''.join(c for c in last if c.isalnum())
        
        # Generate email based on format
        if format_style == 'first.last':
            email_local = f"{first}.{last}"
        elif format_style == 'firstlast':
            email_local = f"{first}{last}"
        elif format_style == 'flast':
            email_local = f"{first[0]}{last}"
        elif format_style == 'first':
            email_local = first
        else:
            email_local = f"{first}.{last}"
        
        email = f"{email_local}@{domain}"
        
        # Handle duplicates
        if email in self.used_emails:
            counter = 1
            while f"{email_local}{counter}@{domain}" in self.used_emails:
                counter += 1
            email = f"{email_local}{counter}@{domain}"
        
        self.used_emails.add(email)
        return email
    
    def generate_batch(
        self,
        count: int,
        gender_distribution: Optional[dict] = None
    ) -> List[str]:
        """
        Generate batch of names
        
        Args:
            count: Number of names to generate
            gender_distribution: Optional dict like {'male': 0.48, 'female': 0.51, None: 0.01}
            
        Returns:
            List of names
        """
        if gender_distribution is None:
            # Default distribution reflecting tech industry demographics
            gender_distribution = {
                'male': 0.51,
                'female': 0.48,
                None: 0.01  # Non-binary / not specified
            }
        
        names = []
        
        for _ in range(count):
            # Choose gender based on distribution
            gender = self._weighted_choice([
                (g, w) for g, w in gender_distribution.items()
            ])
            
            name = self.generate_name(gender=gender)
            names.append(name)
        
        return names
    
    def generate_username(
        self,
        name: Optional[str] = None,
        style: str = 'first_last'
    ) -> str:
        """
        Generate username (for internal systems)
        
        Args:
            name: Optional full name (generates if not provided)
            style: Username style ('first_last', 'flast', 'firstlast')
            
        Returns:
            Username string
        """
        if name is None:
            name = self.generate_name()
        
        parts = name.lower().split()
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]
        else:
            first = parts[0]
            last = ''
        
        # Clean
        first = ''.join(c for c in first if c.isalnum())
        last = ''.join(c for c in last if c.isalnum())
        
        if style == 'first_last':
            username = f"{first}_{last}" if last else first
        elif style == 'flast':
            username = f"{first[0]}{last}" if last else first
        elif style == 'firstlast':
            username = f"{first}{last}" if last else first
        else:
            username = f"{first}_{last}" if last else first
        
        return username
    
    def generate_display_name(
        self,
        name: str,
        include_title: bool = False,
        title: Optional[str] = None
    ) -> str:
        """
        Generate display name (as shown in UI)
        
        Args:
            name: Full name
            include_title: Whether to include professional title
            title: Optional specific title
            
        Returns:
            Display name
        """
        if include_title:
            if title is None:
                title = random.choice(['Mr.', 'Ms.', 'Dr.', ''])
            
            if title:
                return f"{title} {name}"
        
        return name
    
    def parse_name_components(self, name: str) -> dict:
        """
        Parse name into components
        
        Args:
            name: Full name string
            
        Returns:
            Dict with keys: first_name, middle_name, last_name, suffix
        """
        parts = name.split()
        
        components = {
            'first_name': '',
            'middle_name': '',
            'last_name': '',
            'suffix': ''
        }
        
        if len(parts) == 1:
            components['first_name'] = parts[0]
        elif len(parts) == 2:
            components['first_name'] = parts[0]
            components['last_name'] = parts[1]
        elif len(parts) == 3:
            components['first_name'] = parts[0]
            components['middle_name'] = parts[1]
            components['last_name'] = parts[2]
        else:
            # Handle longer names
            components['first_name'] = parts[0]
            components['middle_name'] = ' '.join(parts[1:-1])
            components['last_name'] = parts[-1]
        
        # Check for suffixes
        suffixes = ['Jr.', 'Sr.', 'II', 'III', 'IV', 'V']
        if components['last_name'] in suffixes:
            components['suffix'] = components['last_name']
            components['last_name'] = components['middle_name']
            components['middle_name'] = ''
        
        return components
    
    def _weighted_choice(self, choices: List[Tuple]) -> any:
        """Make weighted random choice"""
        if not choices:
            return None
        
        values, weights = zip(*choices)
        return random.choices(values, weights=weights, k=1)[0]


def generate_company_name(industry: Optional[str] = None) -> str:
    """
    Generate realistic company name
    
    Args:
        industry: Optional industry for themed name
        
    Returns:
        Company name
    """
    faker = Faker()
    
    # Prefixes common in tech
    prefixes = [
        'Data', 'Cloud', 'Smart', 'Fast', 'Secure', 'Easy', 'Quick',
        'Auto', 'Meta', 'Hyper', 'Ultra', 'Next', 'Future', 'Instant',
        'Rapid', 'Dynamic', 'Agile', 'Flow', 'Stream', 'Sync'
    ]
    
    # Suffixes by industry
    if industry == 'developer_tools':
        suffixes = ['Dev', 'Code', 'Build', 'Deploy', 'Stack', 'Kit', 'Tools', 'Lab']
    elif industry == 'security':
        suffixes = ['Guard', 'Shield', 'Secure', 'Safe', 'Lock', 'Vault', 'Defense']
    elif industry == 'analytics':
        suffixes = ['Metrics', 'Analytics', 'Insights', 'Data', 'Intelligence', 'Viz']
    elif industry == 'collaboration':
        suffixes = ['Team', 'Collab', 'Space', 'Hub', 'Connect', 'Together', 'Meet']
    elif industry == 'infrastructure':
        suffixes = ['Cloud', 'Infra', 'Deploy', 'Scale', 'Mesh', 'Grid', 'Network']
    else:
        suffixes = [
            'Tech', 'Labs', 'Systems', 'Solutions', 'Platform', 'Hub',
            'Studio', 'Works', 'Forge', 'Factory', 'Engine'
        ]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f"{prefix}{suffix}"


def generate_team_name(
    team_type: str,
    use_descriptor: bool = True
) -> str:
    """
    Generate realistic team name based on type
    
    Args:
        team_type: Type of team (engineering, product, marketing, etc.)
        use_descriptor: Whether to add descriptive prefix
        
    Returns:
        Team name
    """
    descriptors = {
        'engineering': [
            'Backend', 'Frontend', 'Mobile', 'Platform', 'Infrastructure',
            'Data', 'ML', 'Security', 'DevOps', 'API', 'Core', 'Growth'
        ],
        'product': [
            'Core Product', 'Growth', 'Enterprise', 'Consumer', 'Platform',
            'Monetization', 'Search', 'Discovery', 'Engagement'
        ],
        'design': [
            'Product Design', 'UX Research', 'Brand', 'Visual Design',
            'Design Systems', 'Creative', 'User Experience'
        ],
        'marketing': [
            'Demand Gen', 'Product Marketing', 'Content', 'Growth',
            'Brand', 'Digital', 'Performance', 'Communications'
        ],
        'sales': [
            'Enterprise Sales', 'SMB Sales', 'Inside Sales', 'Sales Ops',
            'Customer Success', 'Account Management', 'Solutions'
        ],
        'data': [
            'Data Science', 'Data Engineering', 'Analytics', 'BI',
            'ML Infrastructure', 'Data Platform'
        ],
    }
    
    if team_type.lower() in descriptors:
        descriptor = random.choice(descriptors[team_type.lower()])
        
        if use_descriptor:
            # Add team suffix sometimes
            if random.random() < 0.3:
                return f"{descriptor} Team"
            return descriptor
        else:
            return team_type.title()
    
    return f"{team_type.title()} Team"


def generate_project_name(
    project_type: str,
    team_type: Optional[str] = None,
    quarter: Optional[str] = None
) -> str:
    """
    Generate realistic project name
    
    Args:
        project_type: Type of project (sprint, campaign, bug_tracking, etc.)
        team_type: Optional team type for context
        quarter: Optional quarter (e.g., 'Q4 2024')
        
    Returns:
        Project name
    """
    if project_type == 'sprint':
        templates = [
            f"{quarter or 'Q4 2024'} Sprint",
            f"{team_type or 'Product'} Sprint {random.randint(1, 20)}",
            f"Sprint {random.randint(1, 52)} - {random.choice(['Platform', 'Growth', 'Performance'])}",
        ]
    elif project_type == 'campaign':
        templates = [
            f"{quarter or 'Q4 2024'} {random.choice(['Launch', 'Campaign', 'Initiative'])}",
            f"{random.choice(['Product', 'Feature', 'Service'])} Launch",
            f"{random.choice(['Email', 'Content', 'Social'])} Campaign",
        ]
    elif project_type == 'bug_tracking':
        templates = [
            f"{team_type or 'Engineering'} Bug Backlog",
            f"P{random.randint(0, 2)} Production Issues",
            "Critical Bugs",
            "Technical Debt"
        ]
    elif project_type == 'ongoing':
        templates = [
            "Customer Onboarding",
            "Weekly Releases",
            "Content Pipeline",
            "Support Queue",
            "Maintenance Tasks"
        ]
    else:
        templates = [
            f"{team_type or 'Product'} {random.choice(['Planning', 'Roadmap', 'Backlog'])}",
        ]
    
    return random.choice(templates)
