"""
Story/Activity generator for audit logs and activity feeds
"""

import uuid
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

logger = logging.getLogger(__name__)


class StoryGenerator:
    """Generates activity stories (audit log entries)"""
    
    # Story types and their distribution
    STORY_TYPES = [
        ('task_created', 0.20),
        ('task_updated', 0.25),
        ('task_completed', 0.15),
        ('task_assigned', 0.15),
        ('comment_added', 0.10),
        ('attachment_added', 0.05),
        ('task_moved', 0.05),
        ('task_deleted', 0.02),
        ('project_updated', 0.03),
    ]
    
    # Story text templates
    STORY_TEMPLATES = {
        'task_created': [
            'created task',
            'added new task',
            'created this task',
        ],
        'task_updated': [
            'updated task',
            'changed task details',
            'modified task',
            'updated description',
            'changed priority to {}',
            'updated due date',
        ],
        'task_completed': [
            'completed this task',
            'marked task as complete',
            'finished this task',
        ],
        'task_assigned': [
            'assigned to {}',
            'reassigned to {}',
            'assigned this to {}',
        ],
        'comment_added': [
            'added a comment',
            'commented on this task',
            'left a comment',
        ],
        'attachment_added': [
            'attached {}',
            'added attachment {}',
            'uploaded {}',
        ],
        'task_moved': [
            'moved task to {}',
            'changed project to {}',
            'moved to {}',
        ],
        'task_deleted': [
            'deleted this task',
            'removed this task',
        ],
        'project_updated': [
            'updated project',
            'changed project details',
            'modified project',
        ],
    }
    
    def __init__(self, db_manager, org_data: Dict, tasks: List[Dict], 
                 users: List[Dict], target_count: int):
        self.db = db_manager
        self.org_data = org_data
        self.tasks = tasks
        self.users = users
        self.target_count = target_count
        self.faker = Faker()
        
        # Set seed for reproducibility
        Faker.seed(42)
        random.seed(42)
    
    def generate(self) -> List[Dict]:
        """Generate all stories"""
        logger.info(f"Generating {self.target_count:,} activity stories...")
        
        stories = []
        
        # Generate stories for tasks
        # Each task gets 2-8 stories (activity entries)
        tasks_to_process = min(len(self.tasks), self.target_count // 3)  # Estimate ~3 stories per task
        
        for i, task in enumerate(random.sample(self.tasks, tasks_to_process)):
            if len(stories) >= self.target_count:
                break
            
            num_stories = random.randint(2, 8)
            num_stories = min(num_stories, self.target_count - len(stories))
            
            task_stories = self._generate_task_stories(task, num_stories)
            stories.extend(task_stories)
            
            # Progress logging
            if len(stories) % 1000 == 0:
                logger.info(f"  Generated {len(stories):,}/{self.target_count:,} stories...")
        
        # Batch insert
        logger.info("Inserting stories into database...")
        self.db.insert_many('stories', stories)
        
        logger.info(f"✓ Generated {len(stories):,} stories")
        
        # Log statistics
        self._log_statistics(stories)
        
        return stories
    
    def _generate_task_stories(self, task: Dict, num_stories: int) -> List[Dict]:
        """Generate activity stories for a task"""
        stories = []
        
        task_created = datetime.fromisoformat(task['created_at'])
        now = datetime.now()
        
        # Determine end time for stories
        if task['completed_at']:
            end_time = datetime.fromisoformat(task['completed_at'])
        else:
            end_time = now
        
        # First story: task creation
        creation_story = {
            'story_id': str(uuid.uuid4()),
            'task_id': task['task_id'],
            'actor_id': task['creator_id'],
            'story_type': 'task_created',
            'story_text': 'created task',
            'created_at': task_created.isoformat(),
        }
        stories.append(creation_story)
        
        # Generate remaining stories
        remaining = num_stories - 1
        if remaining <= 0:
            return stories
        
        # Distribute story times across task lifetime
        total_duration = (end_time - task_created).total_seconds()
        if total_duration <= 0:
            total_duration = 3600  # 1 hour minimum
        
        for i in range(remaining):
            # Generate timestamp (spread across task lifetime)
            progress = (i + 1) / remaining
            time_offset = total_duration * (progress ** 0.6)  # Slight curve
            story_time = task_created + timedelta(seconds=time_offset)
            
            # Ensure not in future
            if story_time > now:
                story_time = now - timedelta(seconds=random.randint(1, 3600))
            
            # Determine story type
            story_type = self._weighted_choice(self.STORY_TYPES)
            
            # Generate story text
            story_text = self._generate_story_text(story_type, task)
            
            # Actor (usually assignee or creator)
            if task['assignee_id'] and random.random() < 0.70:
                actor_id = task['assignee_id']
            else:
                actor_id = random.choice(self.users)['user_id']
            
            story = {
                'story_id': str(uuid.uuid4()),
                'task_id': task['task_id'],
                'actor_id': actor_id,
                'story_type': story_type,
                'story_text': story_text,
                'created_at': story_time.isoformat(),
            }
            stories.append(story)
        
        # If task is completed, ensure last story is completion
        if task['completed_at'] and stories[-1]['story_type'] != 'task_completed':
            stories[-1] = {
                'story_id': str(uuid.uuid4()),
                'task_id': task['task_id'],
                'actor_id': task['assignee_id'] if task['assignee_id'] else task['creator_id'],
                'story_type': 'task_completed',
                'story_text': 'completed this task',
                'created_at': task['completed_at'],
            }
        
        return stories
    
    def _generate_story_text(self, story_type: str, task: Dict) -> str:
        """Generate story text based on type"""
        templates = self.STORY_TEMPLATES.get(story_type, ['performed action'])
        template = random.choice(templates)
        
        # Fill in placeholders
        if '{}' in template:
            if story_type == 'task_assigned':
                # Get random user name
                user = random.choice(self.users)
                filler = user['name']
            elif story_type == 'attachment_added':
                filler = self.faker.file_name()
            elif story_type == 'task_moved':
                filler = self.faker.catch_phrase()
            elif story_type == 'task_updated':
                if 'priority' in template:
                    filler = random.choice(['high', 'medium', 'low'])
                else:
                    filler = ''
            else:
                filler = self.faker.word()
            
            story_text = template.format(filler)
        else:
            story_text = template
        
        return story_text
    
    def _weighted_choice(self, choices: List[tuple]) -> str:
        """Make weighted random choice"""
        values, weights = zip(*choices)
        return random.choices(values, weights=weights, k=1)[0]
    
    def _log_statistics(self, stories: List[Dict]):
        """Log generation statistics"""
        logger.info("\nStory Statistics:")
        
        # Type distribution
        type_counts = {}
        for story in stories:
            story_type = story['story_type']
            type_counts[story_type] = type_counts.get(story_type, 0) + 1
        
        logger.info("  Story Types:")
        for story_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / len(stories)
            logger.info(f"    {story_type:20s}: {count:6,} ({pct:5.1f}%)")
        
        # Stories per task
        task_story_counts = {}
        for story in stories:
            task_id = story['task_id']
            task_story_counts[task_id] = task_story_counts.get(task_id, 0) + 1
        
        if task_story_counts:
            avg_per_task = sum(task_story_counts.values()) / len(task_story_counts)
            logger.info(f"  Avg stories per task: {avg_per_task:.1f}")
