"""
Asana Simulation Data Generator
Main entry point for generating realistic seed data
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.organizations import OrganizationGenerator
from generators.teams import TeamGenerator
from generators.users import UserGenerator
from generators.projects import ProjectGenerator
from generators.tasks import TaskGenerator
from generators.comments import CommentGenerator
from generators.custom_fields import CustomFieldGenerator
from generators.stories import StoryGenerator
from utils.database import DatabaseManager
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Configuration
class Config:
    """Centralized configuration"""
    # Database
    DB_PATH = Path("output/asana_simulation.sqlite")
    SCHEMA_PATH = Path("schema.sql")
    
    # Organization size (5K-10K employees)
    MIN_EMPLOYEES = 5000
    MAX_EMPLOYEES = 10000
    
    # Time range (6 months of historical data)
    MONTHS_OF_HISTORY = 6
    
    # Scaling factors
    PROJECTS_PER_TEAM = 6  # Average
    TASKS_PER_USER = 12    # Average active + completed
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # LLM Settings
    LLM_MODEL = "claude-sonnet-4-20250514"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 150
    
    # Random seed for reproducibility (optional)
    RANDOM_SEED = 42


def main():
    """Main execution flow"""
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("Starting Asana Simulation Data Generation")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Validate configuration
        validate_config(logger)
        
        # Initialize database
        logger.info("Initializing database...")
        db_manager = DatabaseManager(Config.DB_PATH, Config.SCHEMA_PATH)
        db_manager.initialize()
        
        # Generate data in dependency order
        logger.info("\n" + "=" * 80)
        logger.info("Phase 1: Core Entities (Organization, Teams, Users)")
        logger.info("=" * 80)
        
        # 1. Generate organization
        logger.info("\n[1/8] Generating organization...")
        org_gen = OrganizationGenerator(db_manager, Config.MIN_EMPLOYEES, Config.MAX_EMPLOYEES)
        org_data = org_gen.generate()
        employee_count = org_data['employee_count']
        logger.info(f"✓ Created organization: {org_data['name']} ({employee_count:,} employees)")
        
        # 2. Generate teams
        logger.info("\n[2/8] Generating teams...")
        team_gen = TeamGenerator(db_manager, org_data)
        teams = team_gen.generate()
        logger.info(f"✓ Created {len(teams)} teams")
        
        # 3. Generate users
        logger.info("\n[3/8] Generating users...")
        user_gen = UserGenerator(db_manager, org_data, employee_count)
        users = user_gen.generate()
        logger.info(f"✓ Created {len(users):,} users")
        
        # 4. Generate team memberships
        logger.info("\n[4/8] Assigning users to teams...")
        team_gen.assign_members(users)
        logger.info(f"✓ Created team memberships")
        
        logger.info("\n" + "=" * 80)
        logger.info("Phase 2: Project Structure")
        logger.info("=" * 80)
        
        # 5. Generate projects
        logger.info("\n[5/8] Generating projects...")
        project_gen = ProjectGenerator(
            db_manager, 
            org_data, 
            teams, 
            users,
            projects_per_team=Config.PROJECTS_PER_TEAM,
            months_of_history=Config.MONTHS_OF_HISTORY
        )
        projects = project_gen.generate()
        logger.info(f"✓ Created {len(projects)} projects")
        
        logger.info("\n" + "=" * 80)
        logger.info("Phase 3: Tasks & Activity")
        logger.info("=" * 80)
        
        # 6. Generate tasks
        logger.info("\n[6/8] Generating tasks (this may take several minutes)...")
        task_gen = TaskGenerator(
            db_manager, 
            projects, 
            users,
            tasks_per_user=Config.TASKS_PER_USER,
            api_key=Config.ANTHROPIC_API_KEY
        )
        tasks = task_gen.generate()
        logger.info(f"✓ Created {len(tasks):,} tasks")
        
        # 7. Generate custom fields
        logger.info("\n[7/8] Generating custom fields...")
        cf_gen = CustomFieldGenerator(db_manager, projects, tasks)
        cf_gen.generate()
        logger.info(f"✓ Created custom fields")
        
        # 8. Generate comments and stories
        logger.info("\n[8/8] Generating comments and activity stories...")
        comment_gen = CommentGenerator(
            db_manager, 
            tasks, 
            users,
            api_key=Config.ANTHROPIC_API_KEY
        )
        comments = comment_gen.generate()
        logger.info(f"✓ Created {len(comments):,} comments")
        
        story_gen = StoryGenerator(db_manager, tasks, projects, users)
        stories = story_gen.generate()
        logger.info(f"✓ Created {len(stories):,} activity stories")
        
        # Generate summary statistics
        logger.info("\n" + "=" * 80)
        logger.info("Generation Complete - Summary Statistics")
        logger.info("=" * 80)
        
        stats = db_manager.get_statistics()
        logger.info(f"\nDatabase: {Config.DB_PATH}")
        logger.info(f"Size: {stats['size_mb']:.2f} MB")
        logger.info(f"\nEntity Counts:")
        for table, count in stats['counts'].items():
            logger.info(f"  {table:25s}: {count:,}")
        
        # Validation checks
        logger.info("\n" + "=" * 80)
        logger.info("Running Validation Checks")
        logger.info("=" * 80)
        
        validation_results = run_validation_checks(db_manager, logger)
        
        if validation_results['passed']:
            logger.info("\n✓ All validation checks passed!")
        else:
            logger.warning(f"\n⚠ {validation_results['failed_count']} validation check(s) failed")
            logger.warning("See logs above for details")
        
        # Calculate elapsed time
        elapsed = datetime.now() - start_time
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Total execution time: {elapsed.total_seconds():.1f} seconds")
        logger.info(f"{'=' * 80}")
        
        logger.info("\n✅ Data generation complete!")
        logger.info(f"📁 Database location: {Config.DB_PATH.absolute()}")
        
    except Exception as e:
        logger.error(f"\n❌ Error during generation: {str(e)}", exc_info=True)
        sys.exit(1)


def validate_config(logger):
    """Validate configuration and dependencies"""
    issues = []
    
    # Check API key
    if not Config.ANTHROPIC_API_KEY:
        issues.append("ANTHROPIC_API_KEY not found in environment variables")
        logger.warning("⚠ No Anthropic API key found - LLM generation will use fallback mode")
    
    # Check schema file exists
    if not Config.SCHEMA_PATH.exists():
        issues.append(f"Schema file not found: {Config.SCHEMA_PATH}")
    
    # Create output directory
    Config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if issues:
        for issue in issues:
            if "Schema file" in issue:
                logger.error(f"Configuration issue: {issue}")
                sys.exit(1)
            else:
                logger.warning(f"Configuration issue: {issue}")


def run_validation_checks(db_manager, logger):
    """Run data validation checks"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    checks = []
    passed = True
    
    # Check 1: No orphaned tasks
    logger.info("\n[Check 1/5] Orphaned tasks...")
    cursor.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE project_id NOT IN (SELECT project_id FROM projects)
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned == 0:
        logger.info("  ✓ No orphaned tasks")
    else:
        logger.error(f"  ✗ Found {orphaned} orphaned tasks")
        passed = False
    checks.append(orphaned == 0)
    
    # Check 2: Temporal violations
    logger.info("\n[Check 2/5] Temporal consistency...")
    cursor.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE completed = 1 AND completed_at < created_at
    """)
    temporal_violations = cursor.fetchone()[0]
    if temporal_violations == 0:
        logger.info("  ✓ No temporal violations")
    else:
        logger.error(f"  ✗ Found {temporal_violations} temporal violations")
        passed = False
    checks.append(temporal_violations == 0)
    
    # Check 3: Referential integrity
    logger.info("\n[Check 3/5] Referential integrity...")
    cursor.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE assignee_id IS NOT NULL 
        AND assignee_id NOT IN (SELECT user_id FROM users)
    """)
    ref_violations = cursor.fetchone()[0]
    if ref_violations == 0:
        logger.info("  ✓ All foreign keys valid")
    else:
        logger.error(f"  ✗ Found {ref_violations} referential integrity violations")
        passed = False
    checks.append(ref_violations == 0)
    
    # Check 4: Completion rate realism
    logger.info("\n[Check 4/5] Task completion rates...")
    cursor.execute("""
        SELECT 
            p.project_type,
            COUNT(*) as total,
            SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed,
            ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        GROUP BY p.project_type
    """)
    for row in cursor.fetchall():
        project_type, total, completed, pct = row
        logger.info(f"  {project_type:20s}: {pct:5.1f}% ({completed:,}/{total:,})")
    checks.append(True)  # Informational only
    
    # Check 5: Workload sanity
    logger.info("\n[Check 5/5] User workload distribution...")
    cursor.execute("""
        SELECT MAX(task_count), AVG(task_count), MIN(task_count)
        FROM (
            SELECT assignee_id, COUNT(*) as task_count 
            FROM tasks 
            WHERE completed = 0 AND assignee_id IS NOT NULL
            GROUP BY assignee_id
        )
    """)
    result = cursor.fetchone()
    if result and result[0]:
        max_tasks, avg_tasks, min_tasks = result
        logger.info(f"  Active tasks per user: min={min_tasks or 0}, avg={avg_tasks:.1f}, max={max_tasks or 0}")
        if max_tasks and max_tasks > 30:
            logger.warning(f"  ⚠ Some users have >30 active tasks (max: {max_tasks})")
        else:
            logger.info(f"  ✓ Workload distribution reasonable")
    else:
        logger.info("  ✓ No active tasks assigned yet")
    checks.append(True)
    
    failed_count = len([c for c in checks if not c])
    
    return {
        'passed': passed,
        'failed_count': failed_count,
        'checks': checks
    }


if __name__ == "__main__":
    main()
