"""
Organization generator
Creates the top-level organization entity
"""

import uuid
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)


class OrganizationGenerator:
    """Generates organization data"""
    
    # B2B SaaS companies from Y Combinator (examples - you'd scrape this)
    COMPANY_EXAMPLES = [
        {"name": "DataFlow Analytics", "industry": "Analytics", "domain": "dataflow.io"},
        {"name": "SecureStack", "industry": "Security", "domain": "securestack.com"},
        {"name": "DevTools Pro", "industry": "Developer Tools", "domain": "devtools.pro"},
        {"name": "CloudSync Platform", "industry": "Infrastructure", "domain": "cloudsync.io"},
        {"name": "CollabSpace", "industry": "Collaboration", "domain": "collabspace.com"},
        {"name": "APIverse", "industry": "Developer Tools", "domain": "apiverse.dev"},
        {"name": "MetricsHub", "industry": "Analytics", "domain": "metricshub.io"},
        {"name": "CodeGuard", "industry": "Security", "domain": "codeguard.io"},
        {"name": "TeamFlow", "industry": "Collaboration", "domain": "teamflow.app"},
        {"name": "InfraMesh", "industry": "Infrastructure", "domain": "inframesh.io"},
    ]
    
    def __init__(self, db_manager, min_employees=5000, max_employees=10000):
        self.db = db_manager
        self.min_employees = min_employees
        self.max_employees = max_employees
    
    def generate(self) -> Dict[str, Any]:
        """Generate organization data"""
        logger.info("Generating organization...")
        
        # Select a random company
        company = random.choice(self.COMPANY_EXAMPLES)
        
        # Generate employee count (normal distribution)
        mean_employees = (self.min_employees + self.max_employees) / 2
        std_dev = (self.max_employees - self.min_employees) / 6
        employee_count = int(random.gauss(mean_employees, std_dev))
        employee_count = max(self.min_employees, min(self.max_employees, employee_count))
        
        # Organization was created 24-36 months ago (mature company)
        months_ago = random.randint(24, 36)
        created_at = datetime.now() - timedelta(days=months_ago * 30)
        
        org_data = {
            'org_id': str(uuid.uuid4()),
            'name': company['name'],
            'domain': company['domain'],
            'created_at': created_at.isoformat(),
            'is_organization': True,
            'employee_count': employee_count,
            'industry': company['industry']
        }
        
        # Insert into database
        self.db.insert_one('organizations', org_data)
        
        logger.info(f"  Organization ID: {org_data['org_id']}")
        logger.info(f"  Name: {org_data['name']}")
        logger.info(f"  Domain: {org_data['domain']}")
        logger.info(f"  Industry: {org_data['industry']}")
        logger.info(f"  Employees: {employee_count:,}")
        logger.info(f"  Created: {created_at.strftime('%Y-%m-%d')}")
        
        return org_data
