import time
from typing import Any, Dict, List, Optional

import requests

from marble.environments.base_env import BaseEnvironment
from marble.environments.research_utils.paper_collector import (
    get_paper_by_arxiv_id,
    get_paper_by_keyword,
    get_paper_by_title,
    get_recent_papers,
    get_related_papers,
)
from marble.environments.research_utils.profile_collector import (
    collect_publications_and_coauthors,
)


class TrainingEnvironment(BaseEnvironment):
    def __init__(self, config: Dict[str, Any], name: str = "TrainingEnv"):
        """
        Initialize the TrainingEnvironment.

        Args:
            name (str): The name of the environment.
        """
        super().__init__(name, config)