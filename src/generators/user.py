"""
User generator with realistic distributions
Complete implementation example
"""

import uuid
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

logger = logging.getLogger(__name__)


class UserGenerator:
    """Generates realistic user data"""
    
    # Role distribution based on Asana's reported metrics
    ROLE_DISTRIBUTION = {
        'member': 0.85,
        'admin': 0.12,
        'guest': 0.02,
        'limited_access': 0.01
    }
    
    # Job titles by department (from LinkedIn taxonomy)
    JOB_TITLES = {
        'engineering': [
            ('Software Engineer', 0.35),
            ('Senior Software Engineer', 0.25),
            ('Staff Engineer', 0.10),
            ('Principal Engineer', 0.05),
            ('Engineering Manager', 0.15),
            ('Senior Engineering Manager', 0.07),
            ('Director of Engineering', 0.03),
        ],
        'product': [
            ('Product Manager', 0.40),
            ('Senior Product Manager', 0.30),
            ('Principal Product Manager', 0.10),
            ('Director of Product', 0.15),
            ('VP of Product', 0.05),
        ],
        'design': [
            ('Product Designer', 0.40),
            ('Senior Product Designer', 0.30),
            ('Lead Designer', 0.15),
            ('Design Manager', 0.10),
            ('Head of Design', 0.05),
        ],
        'marketing': [
            ('Marketing Manager', 0.30),
            ('Senior Marketing Manager', 0.25),
            ('Content Marketing Manager', 0.15),
            ('Growth Marketing Manager', 0.15),
            ('Director of Marketing', 0.10),
            ('VP of Marketing', 0.05),
        ],
        'sales': [
            ('Account Executive', 0.40),
            ('Senior Account Executive', 0.25),
            ('Sales Manager', 0.15),
            ('Director of Sales', 0.12),
            ('VP of Sales', 0.08),
        ],
        'data': [
            ('Data Analyst', 0.35),
            ('Data Scientist', 0.30),
            ('Senior Data Scientist', 0.20),
            ('Data Engineering Manager', 0.10),
            ('Head of Data', 0.05),
        ],
        'operations': [
            ('Operations Manager', 0.40),
            ('Senior Operations Manager', 0.25),
            ('Operations Analyst', 0.20),
            ('Director of Operations', 0.10),
            ('VP of Operations', 0.05),
        ],
        'hr': [
            ('HR Manager', 0.35),
            ('Senior HR Manager', 0.25),
            ('HR Business Partner', 0.20),
            ('Director of People', 0.15),
            ('Chief People Officer', 0.05),
        ],
        'finance': [
            ('Financial Analyst', 0.35),
            ('Senior Financial Analyst', 0.25),
            ('Finance Manager', 0.20),
            ('Director of Finance', 0.15),
            ('CFO', 0.05),
        ],
        'legal': [
            ('Legal Counsel', 0.40),
            ('Senior Legal Counsel', 0.30),
            ('General Counsel', 0.20),
            ('Legal Operations Manager', 0.10),
        ],
    }
    
    # Timezone distribution (remote-first SaaS company)
    TIMEZONE_DISTRIBUTION = [
        ('America/Los_Angeles', 0.30),
        ('America/New_York', 0.20),
        ('America/Chicago', 0.07),
        ('America/Denver', 0.03),
        ('Europe/London', 0.12),
        ('Europe/Berlin', 0.08),
        ('Europe/Paris', 0.05),
        ('Asia/Singapore', 0.06),
        ('Asia/Tokyo', 0.05),
        ('Australia/Sydney', 0.04),
    ]
    
    def __init__(self, db_manager, org_data: Dict, target_count: int):
        self.db = db_manager
        self.org_data = org_data
        self.target_count = target_count
        self.faker = Faker()
        
        # Set seed for reproducibility (optional)
        Faker.seed(42)
        random.seed(42)
    
    def generate(self) -> List[Dict]:
        """Generate all users"""
        logger.info(f"Generating {self.target_count:,} users...")
        
        users = []
        
        # Determine hiring timeline
        org_created = datetime.fromisoformat(self.org_data['created_at'])
        now = datetime.now()
        
        # Generate users
        for i in range(self.target_count):
            user = self._generate_user(i, org_created, now)
            users.append(user)
            
            # Progress logging
            if (i + 1) % 500 == 0:
                logger.info(f"  Generated {i + 1:,}/{self.target_count:,} users...")
        
        # Batch insert for performance
        logger.info("Inserting users into database...")
        self.db.insert_many('users', users)
        
        logger.info(f"✓ Generated {len(users):,} users")
        
        # Log statistics
        self._log_statistics(users)
        
        return users
    
    def _generate_user(self, index: int, org_created: datetime, now: datetime) -> Dict:
        """Generate a single user"""
        
        # Generate unique name
        name = self.faker.name()
        
        # Create email from name
        email = self._create_email(name)
        
        # Assign role based on distribution
        role = self._weighted_choice([
            (role, weight) for role, weight in self.ROLE_DISTRIBUTION.items()
        ])
        
        # Determine department (will match with team assignment later)
        department = self._weighted_choice([
            ('Engineering', 0.40),
            ('Product', 0.12),
            ('Sales', 0.15),
            ('Marketing', 0.10),
            ('Operations', 0.08),
            ('Design', 0.05),
            ('Data', 0.05),
            ('HR', 0.02),
            ('Finance', 0.02),
            ('Legal', 0.01),
        ])
        
        # Assign job title based on department
        job_title = self._get_job_title(department.lower())
        
        # Determine creation date (hiring date)
        created_at = self._get_hiring_date(index, org_created, now)
        
        # Last active date (most users active recently)
        last_active_at = self._get_last_active_date(created_at, now)
        
        # Active status (95% active, 5% inactive/on leave)
        is_active = random.random() < 0.95
        
        # Timezone
        timezone = self._weighted_choice(self.TIMEZONE_DISTRIBUTION)
        
        return {
            'user_id': str(uuid.uuid4()),
            'org_id': self.org_data['org_id'],
            'email': email,
            'name': name,
            'role': role,
            'job_title': job_title,
            'department': department,
            'created_at': created_at.isoformat(),
            'last_active_at': last_active_at.isoformat() if last_active_at else None,
            'is_active': is_active,
            'timezone': timezone,
        }
    
    def _create_email(self, name: str) -> str:
        """Create email from name"""
        # Split name and clean
        parts = name.lower().split()
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]
        else:
            first = parts[0]
            last = "user"
        
        # Remove special characters
        first = ''.join(c for c in first if c.isalnum())
        last = ''.join(c for c in last if c.isalnum())
        
        # Add number if needed for uniqueness (simple approach)
        email = f"{first}.{last}@{self.org_data['domain']}"
        
        return email
    
    def _get_job_title(self, department: str) -> str:
        """Get job title for department"""
        if department not in self.JOB_TITLES:
            department = 'operations'  # Default
        
        titles = self.JOB_TITLES[department]
        return self._weighted_choice(titles)
    
    def _get_hiring_date(self, index: int, org_created: datetime, now: datetime) -> datetime:
        """
        Generate realistic hiring date based on company growth curve
        
        Pattern:
        - Founding team (first 50): org creation date
        - Rapid growth (months 1-12): exponential hiring
        - Steady state (months 13-24): linear growth
        """
        total_months = (now - org_created).days / 30
        
        if index < 50:
            # Founding team - all hired at company start
            return org_created + timedelta(days=random.randint(0, 7))
        
        # Calculate position in growth curve
        position_pct = index / self.target_count
        
        if total_months <= 12:
            # Early stage - exponential growth
            # y = e^(x) scaled to total_months
            import math
            month = (math.log(1 + position_pct * (math.e - 1)) / math.log(math.e)) * total_months
        else:
            # Mature stage - mix of exponential (first 12 months) and linear
            if position_pct < 0.6:
                # First 60% hired in exponential phase (first 12 months)
                import math
                scaled_pct = position_pct / 0.6
                month = (math.log(1 + scaled_pct * (math.e - 1)) / math.log(math.e)) * 12
            else:
                # Last 40% hired linearly over remaining months
                scaled_pct = (position_pct - 0.6) / 0.4
                month = 12 + scaled_pct * (total_months - 12)
        
        # Add random jitter (±15 days)
        days = month * 30 + random.uniform(-15, 15)
        days = max(0, min(days, total_months * 30))  # Clamp to valid range
        
        return org_created + timedelta(days=days)
    
    def _get_last_active_date(self, created_at: datetime, now: datetime) -> datetime:
        """
        Generate last active date
        
        Distribution:
        - 90% active within last 7 days
        - 5% active 8-30 days ago
        - 5% inactive >30 days
        """
        rand = random.random()
        
        if rand < 0.90:
            # Active within last 7 days
            days_ago = random.uniform(0, 7)
        elif rand < 0.95:
            # Active 8-30 days ago
            days_ago = random.uniform(8, 30)
        else:
            # Inactive >30 days
            days_ago = random.uniform(31, 180)
        
        last_active = now - timedelta(days=days_ago)
        
        # Can't be before creation
        if last_active < created_at:
            last_active = created_at + timedelta(days=random.randint(1, 30))
        
        return last_active
    
    def _weighted_choice(self, choices: List[tuple]) -> str:
        """Make weighted random choice from (value, weight) tuples"""
        values, weights = zip(*choices)
        return random.choices(values, weights=weights, k=1)[0]
    
    def _log_statistics(self, users: List[Dict]):
        """Log generation statistics"""
        logger.info("\nUser Statistics:")
        
        # Role distribution
        role_counts = {}
        for user in users:
            role = user['role']
            role_counts[role] = role_counts.get(role, 0) + 1
        
        logger.info("  Roles:")
        for role, count in sorted(role_counts.items()):
            pct = 100 * count / len(users)
            logger.info(f"    {role:20s}: {count:6,} ({pct:5.1f}%)")
        
        # Department distribution
        dept_counts = {}
        for user in users:
            dept = user['department']
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        logger.info("  Departments:")
        for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / len(users)
            logger.info(f"    {dept:20s}: {count:6,} ({pct:5.1f}%)")
        
        # Activity
        active_count = sum(1 for u in users if u['is_active'])
        logger.info(f"  Active users: {active_count:,} ({100*active_count/len(users):.1f}%)")
