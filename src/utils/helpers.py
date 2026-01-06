"""
General helper functions used across generators
"""

import uuid
import random
from typing import List, Tuple, Any, Optional
from datetime import datetime, timedelta


def generate_uuid() -> str:
    """Generate UUID string"""
    return str(uuid.uuid4())


def weighted_choice(choices: List[Tuple[Any, float]]) -> Any:
    """
    Make weighted random choice from (value, weight) tuples
    
    Args:
        choices: List of (value, weight) tuples
        
    Returns:
        Selected value
    """
    if not choices:
        return None
    
    values, weights = zip(*choices)
    return random.choices(values, weights=weights, k=1)[0]


def weighted_boolean(probability_true: float = 0.5) -> bool:
    """
    Generate weighted boolean
    
    Args:
        probability_true: Probability of returning True (0.0-1.0)
        
    Returns:
        Boolean based on probability
    """
    return random.random() < probability_true


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value to range
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def normalize_weights(weights: List[float]) -> List[float]:
    """
    Normalize weights to sum to 1.0
    
    Args:
        weights: List of weights
        
    Returns:
        Normalized weights
    """
    total = sum(weights)
    if total == 0:
        return [1.0 / len(weights)] * len(weights)
    return [w / total for w in weights]


def sample_from_distribution(
    distribution: dict,
    count: int = 1
) -> List[Any]:
    """
    Sample from a distribution dictionary
    
    Args:
        distribution: Dict mapping values to probabilities
        count: Number of samples
        
    Returns:
        List of sampled values
    """
    values = list(distribution.keys())
    weights = list(distribution.values())
    
    return random.choices(values, weights=weights, k=count)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate percentile of values
    
    Args:
        values: List of numeric values
        percentile: Percentile (0-100)
        
    Returns:
        Value at percentile
    """
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    index = int(len(sorted_values) * (percentile / 100))
    index = max(0, min(index, len(sorted_values) - 1))
    
    return sorted_values[index]


def exponential_growth_curve(
    position: float,
    total_duration: float,
    growth_rate: float = 2.0
) -> float:
    """
    Calculate value on exponential growth curve
    
    Args:
        position: Current position (0.0-1.0)
        total_duration: Total duration in same units
        growth_rate: Growth rate (>1.0 for growth, <1.0 for decay)
        
    Returns:
        Value at position
    """
    import math
    
    if position <= 0:
        return 0.0
    if position >= 1:
        return total_duration
    
    # Exponential formula
    value = (math.exp(position * math.log(growth_rate)) - 1) / (growth_rate - 1)
    return value * total_duration


def sigmoid_curve(x: float, midpoint: float = 0.5, steepness: float = 10.0) -> float:
    """
    Calculate value on sigmoid curve (S-curve)
    
    Args:
        x: Input value (0.0-1.0)
        midpoint: Midpoint of curve (0.0-1.0)
        steepness: Steepness of curve
        
    Returns:
        Value on sigmoid curve (0.0-1.0)
    """
    import math
    
    # Sigmoid function
    return 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))


def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split list into batches
    
    Args:
        items: List to batch
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def chunks(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Yield successive n-sized chunks from list
    
    Args:
        lst: List to chunk
        n: Chunk size
        
    Yields:
        Chunks of size n
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def random_subset(items: List[Any], min_size: int, max_size: int) -> List[Any]:
    """
    Get random subset of items
    
    Args:
        items: List to sample from
        min_size: Minimum subset size
        max_size: Maximum subset size
        
    Returns:
        Random subset
    """
    if not items:
        return []
    
    size = random.randint(min_size, min(max_size, len(items)))
    return random.sample(items, size)


def add_jitter(value: float, jitter_pct: float = 0.1) -> float:
    """
    Add random jitter to a value
    
    Args:
        value: Base value
        jitter_pct: Jitter as percentage of value (e.g., 0.1 = ±10%)
        
    Returns:
        Value with jitter applied
    """
    jitter = value * jitter_pct * random.uniform(-1, 1)
    return value + jitter


def round_to_nearest(value: float, nearest: float) -> float:
    """
    Round value to nearest multiple
    
    Args:
        value: Value to round
        nearest: Round to nearest multiple of this
        
    Returns:
        Rounded value
    """
    return round(value / nearest) * nearest


def color_from_string(text: str) -> str:
    """
    Generate consistent color hex code from string
    Used for project colors, tag colors, etc.
    
    Args:
        text: Input text
        
    Returns:
        Hex color code (e.g., '#FF5733')
    """
    # Asana's color palette
    colors = [
        '#4573D2',  # Blue
        '#E362E3',  # Purple
        '#E8384F',  # Red
        '#FDA82F',  # Orange
        '#FCAB10',  # Yellow
        '#8DA954',  # Green
        '#14C2D8',  # Teal
        '#AA62E3',  # Violet
    ]
    
    # Use hash of string to pick color consistently
    hash_val = hash(text)
    index = hash_val % len(colors)
    
    return colors[index]


def emoji_for_type(entity_type: str) -> str:
    """
    Get emoji for entity type (modern Asana style)
    
    Args:
        entity_type: Type of entity
        
    Returns:
        Emoji string
    """
    emoji_map = {
        'bug': '🐛',
        'feature': '✨',
        'task': '📋',
        'milestone': '🎯',
        'urgent': '🚨',
        'blocked': '🚫',
        'in_progress': '🔄',
        'done': '✅',
        'review': '👀',
        'design': '🎨',
        'backend': '⚙️',
        'frontend': '💻',
        'mobile': '📱',
        'data': '📊',
        'meeting': '📅',
        'documentation': '📝',
    }
    
    return emoji_map.get(entity_type.lower(), '📌')


def should_add_emoji(probability: float = 0.15) -> bool:
    """
    Decide if emoji should be added (modern workspace culture)
    
    Args:
        probability: Probability of adding emoji
        
    Returns:
        True if emoji should be added
    """
    return random.random() < probability


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format currency value
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    elif currency == 'GBP':
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def slug_from_text(text: str, max_length: int = 50) -> str:
    """
    Create URL-safe slug from text
    
    Args:
        text: Input text
        max_length: Maximum slug length
        
    Returns:
        URL-safe slug
    """
    import re
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug


def parse_tags_from_text(text: str) -> List[str]:
    """
    Extract hashtag-style tags from text
    
    Args:
        text: Text containing #tags
        
    Returns:
        List of tag strings
    """
    import re
    
    # Find all hashtags
    tags = re.findall(r'#(\w+)', text)
    
    return tags


def generate_short_id(length: int = 8) -> str:
    """
    Generate short alphanumeric ID
    
    Args:
        length: Length of ID
        
    Returns:
        Short ID string
    """
    import string
    
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def log_progress(current: int, total: int, prefix: str = '', logger=None):
    """
    Log progress percentage
    
    Args:
        current: Current count
        total: Total count
        prefix: Optional prefix message
        logger: Logger instance
    """
    if total == 0:
        return
    
    pct = 100 * current / total
    message = f"{prefix} {current:,}/{total:,} ({pct:.1f}%)"
    
    if logger:
        logger.info(message)
    else:
        print(message)


def estimate_time_remaining(
    current: int,
    total: int,
    elapsed_seconds: float
) -> str:
    """
    Estimate remaining time for operation
    
    Args:
        current: Current count
        total: Total count
        elapsed_seconds: Elapsed time so far
        
    Returns:
        Human-readable time estimate
    """
    if current == 0:
        return "Calculating..."
    
    rate = current / elapsed_seconds
    remaining = total - current
    remaining_seconds = remaining / rate
    
    if remaining_seconds < 60:
        return f"{remaining_seconds:.0f}s"
    elif remaining_seconds < 3600:
        minutes = remaining_seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = remaining_seconds / 3600
        return f"{hours:.1f}h"
