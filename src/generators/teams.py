"""
Team generator with realistic organizational structures
"""

import uuid
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

logger = logging.getLogger(__name__)


class TeamGenerator:
    """Generates realistic team data"""
    
    # Team types and their distribution
    TEAM_TYPES = [
        ('department', 0.40),
        ('project', 0.30),
        ('cross_functional', 0.20),
        ('working_group', 0.10),
    ]
    
    # Department-based teams
    DEPARTMENT_TEAMS = {
        'Engineering': [
            'Backend Team',
            'Frontend Team',
            'Mobile Team',
            'Infrastructure Team',
            'DevOps Team',
            'Platform Team',
            'Security Team',
        ],
        'Product': [
            'Product Team',
            'Growth Team',
            'Analytics Team',
        ],
        'Design': [
            'Design Team',
            'UX Research Team',
        ],
        'Marketing': [
            'Marketing Team',
            'Content Team',
            'Growth Marketing Team',
            'Brand Team',
        ],
        'Sales': [
            'Sales Team',
            'Sales Engineering Team',
            'Account Management Team',
        ],
        'Operations': [
            'Operations Team',
            'Business Operations Team',
        ],
        'Data': [
            'Data Team',
            'Data Engineering Team',
            'Data Science Team',
        ],
        'HR': [
            'People Operations Team',
        ],
        'Finance': [
            'Finance Team',
        ],
        'Legal': [
            'Legal Team',
        ],
    }
    
    def __init__(self, db_manager, org_data: Dict, users: List[Dict], target_count: int):
        self.db = db_manager
        self.org_data = org_data
        self.users = users
        self.target_count = target_count
        self.faker = Faker()
        
        # Set seed for reproducibility
        Faker.seed(42)
        random.seed(42)
        
        # Group users by department
        self.users_by_dept = {}
        for user in users:
            dept = user['department']
            if dept not in self.users_by_dept:
                self.users_by_dept[dept] = []
            self.users_by_dept[dept].append(user)
    
    def generate(self) -> List[Dict]:
        """Generate all teams"""
        logger.info(f"Generating {self.target_count:,} teams...")
        
        teams = []
        
        # Generate department-based teams first
        dept_teams = self._generate_department_teams()
        teams.extend(dept_teams)
        
        # Generate additional project/cross-functional teams
        remaining = self.target_count - len(teams)
        if remaining > 0:
            additional_teams = self._generate_additional_teams(remaining)
            teams.extend(additional_teams)
        
        # Trim if we generated too many
        teams = teams[:self.target_count]
        
        # Batch insert
        logger.info("Inserting teams into database...")
        self.db.insert_many('teams', teams)
        
        logger.info(f"✓ Generated {len(teams):,} teams")
        
        # Log statistics
        self._log_statistics(teams)
        
        return teams
    
    def _generate_department_teams(self) -> List[Dict]:
        """Generate teams based on departments"""
        teams = []
        org_created = datetime.fromisoformat(self.org_data['created_at'])
        now = datetime.now()
        
        for department, team_names in self.DEPARTMENT_TEAMS.items():
            # Only create teams for departments that have users
            if department not in self.users_by_dept:
                continue
            
            dept_users = self.users_by_dept[department]
            
            # Determine how many teams this department needs
            num_teams = min(len(team_names), max(1, len(dept_users) // 8))
            
            for i in range(num_teams):
                team_name = team_names[i] if i < len(team_names) else f"{department} Team {i+1}"
                
                # Select team members (5-15 people per team)
                team_size = min(len(dept_users), random.randint(5, 15))
                team_members = random.sample(dept_users, team_size)
                
                # Pick team lead (someone senior)
                admins = [u for u in team_members if u['role'] == 'admin']
                team_lead = admins[0] if admins else team_members[0]
                
                # Team creation date (after org creation, before now)
                created_at = self._get_team_creation_date(org_created, now)
                
                team = {
                    'team_id': str(uuid.uuid4()),
                    'org_id': self.org_data['org_id'],
                    'name': team_name,
                    'description': f"{team_name} focused on {department.lower()} initiatives",
                    'team_type': 'department',
                    'owner_id': team_lead['user_id'],
                    'created_at': created_at.isoformat(),
                    'is_archived': False,
                    'member_count': len(team_members),
                }
                
                teams.append(team)
                
                # Store members for later use
                team['_members'] = team_members  # Temporary field
        
        return teams
    
    def _generate_additional_teams(self, count: int) -> List[Dict]:
        """Generate project and cross-functional teams"""
        teams = []
        org_created = datetime.fromisoformat(self.org_data['created_at'])
        now = datetime.now()
        
        for i in range(count):
            team_type = self._weighted_choice(self.TEAM_TYPES)
            
            # Generate team name based on type
            if team_type == 'project':
                team_name = f"{self.faker.catch_phrase()} Project"
            elif team_type == 'cross_functional':
                team_name = f"{self.faker.bs().title()} Initiative"
            else:  # working_group
                team_name = f"{self.faker.word().title()} Working Group"
            
            # Random team size
            team_size = random.randint(3, 12)
            team_members = random.sample(self.users, min(team_size, len(self.users)))
            
            # Pick owner
            owner = random.choice(team_members)
            
            # Creation date
            created_at = self._get_team_creation_date(org_created, now)
            
            # Some teams might be archived (5%)
            is_archived = random.random() < 0.05
            
            team = {
                'team_id': str(uuid.uuid4()),
                'org_id': self.org_data['org_id'],
                'name': team_name,
                'description': f"{team_name} - {self.faker.bs()}",
                'team_type': team_type,
                'owner_id': owner['user_id'],
                'created_at': created_at.isoformat(),
                'is_archived': is_archived,
                'member_count': len(team_members),
            }
            
            teams.append(team)
            team['_members'] = team_members
        
        return teams
    
    def _get_team_creation_date(self, org_created: datetime, now: datetime) -> datetime:
        """Generate realistic team creation date"""
        # Teams created between org creation and now
        total_days = (now - org_created).days
        
        # Most teams created in first 50% of company lifetime
        if random.random() < 0.7:
            days = random.uniform(0, total_days * 0.5)
        else:
            days = random.uniform(total_days * 0.5, total_days)
        
        return org_created + timedelta(days=days)
    
    def _weighted_choice(self, choices: List[tuple]) -> str:
        """Make weighted random choice"""
        values, weights = zip(*choices)
        return random.choices(values, weights=weights, k=1)[0]
    
    def _log_statistics(self, teams: List[Dict]):
        """Log generation statistics"""
        logger.info("\nTeam Statistics:")
        
        # Type distribution
        type_counts = {}
        for team in teams:
            team_type = team['team_type']
            type_counts[team_type] = type_counts.get(team_type, 0) + 1
        
        logger.info("  Team Types:")
        for team_type, count in sorted(type_counts.items()):
            pct = 100 * count / len(teams)
            logger.info(f"    {team_type:20s}: {count:6,} ({pct:5.1f}%)")
        
        # Archive status
        archived = sum(1 for t in teams if t['is_archived'])
        logger.info(f"  Archived: {archived:,} ({100*archived/len(teams):.1f}%)")
        
        # Member count stats
        member_counts = [t['member_count'] for t in teams]
        avg_members = sum(member_counts) / len(member_counts)
        logger.info(f"  Avg team size: {avg_members:.1f} members")
