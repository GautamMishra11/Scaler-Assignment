"""
Project generator
Creates projects with statuses, priorities, timelines, and progress tracking
"""

import uuid
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

logger = logging.getLogger(__name__)


class ProjectGenerator:
    """Generates synthetic projects"""

    # Project status distribution
    PROJECT_STATUSES = [
        ('planned', 0.20),
        ('active', 0.45),
        ('on_hold', 0.10),
        ('completed', 0.20),
        ('archived', 0.05),
    ]

    # Priority distribution
    PRIORITIES = [
        ('low', 0.20),
        ('medium', 0.45),
        ('high', 0.25),
        ('critical', 0.10),
    ]

    def __init__(
        self,
        db_manager,
        org_data: Dict,
        users: List[Dict],
        target_count: int,
    ):
        self.db = db_manager
        self.org_data = org_data
        self.users = users
        self.target_count = target_count
        self.faker = Faker()

        # Reproducibility
        Faker.seed(42)
        random.seed(42)

    def generate(self) -> List[Dict]:
        """Generate projects"""
        logger.info(f"Generating {self.target_count:,} projects...")

        projects = []

        for i in range(self.target_count):
            project = self._generate_project()
            projects.append(project)

            if (i + 1) % 500 == 0:
                logger.info(f"  Generated {i + 1:,}/{self.target_count:,} projects")

        logger.info("Inserting projects into database...")
        self.db.insert_many('projects', projects)

        logger.info(f"✓ Generated {len(projects):,} projects")
        self._log_statistics(projects)

        return projects

    def _generate_project(self) -> Dict:
        """Generate a single project"""

        now = datetime.now()

        # Creation date: last 18 months
        created_at = now - timedelta(days=random.randint(0, 540))

        status = self._weighted_choice(self.PROJECT_STATUSES)
        priority = self._weighted_choice(self.PRIORITIES)

        owner = random.choice(self.users)

        # Timeline logic
        start_date = created_at + timedelta(days=random.randint(0, 14))
        duration_days = random.randint(14, 180)
        due_date = start_date + timedelta(days=duration_days)

        completed_at = None
        progress = self._initial_progress(status)

        if status == 'completed':
            completed_at = start_date + timedelta(
                days=random.randint(int(duration_days * 0.6), duration_days)
            )
            progress = 100
        elif status == 'archived':
            completed_at = start_date + timedelta(days=duration_days)
            progress = 100
        elif status == 'on_hold':
            progress = random.randint(10, 60)
        elif status == 'active':
            progress = random.randint(5, 90)

        return {
            'project_id': str(uuid.uuid4()),
            'org_id': self.org_data['org_id'],
            'name': self._generate_project_name(),
            'description': self.faker.paragraph(nb_sentences=3),
            'status': status,
            'priority': priority,
            'progress': progress,
            'owner_id': owner['user_id'],
            'created_at': created_at.isoformat(),
            'start_date': start_date.isoformat(),
            'due_date': due_date.isoformat(),
            'completed_at': completed_at.isoformat() if completed_at else None,
        }

    def _generate_project_name(self) -> str:
        """Generate realistic project names"""
        patterns = [
            "{} Initiative",
            "{} Revamp",
            "{} Migration",
            "{} Optimization",
            "{} Platform",
            "{} Rollout",
        ]
        keyword = self.faker.catch_phrase().split()[0]
        pattern = random.choice(patterns)
        return pattern.format(keyword)

    def _initial_progress(self, status: str) -> int:
        """Initial progress based on status"""
        if status == 'planned':
            return 0
        if status == 'active':
            return random.randint(5, 40)
        if status == 'on_hold':
            return random.randint(10, 50)
        return 100

    def _weighted_choice(self, choices: List[tuple]) -> str:
        """Weighted random choice"""
        values, weights = zip(*choices)
        return random.choices(values, weights=weights, k=1)[0]

    def _log_statistics(self, projects: List[Dict]):
        """Log generation statistics"""
        logger.info("\nProject Statistics:")

        status_counts = {}
        for p in projects:
            status_counts[p['status']] = status_counts.get(p['status'], 0) + 1

        logger.info("  Status Distribution:")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / len(projects)
            logger.info(f"    {status:12s}: {count:6,} ({pct:5.1f}%)")

        avg_progress = sum(p['progress'] for p in projects) / len(projects)
        logger.info(f"  Avg progress: {avg_progress:.1f}%")
