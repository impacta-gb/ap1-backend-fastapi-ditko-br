from typing import List, Optional
from datetime import datetime
from local.src.domain.entities.local import Local
from local.src.domain.repositories.local_repository import LocalRepository


class CreateLocalUseClass:
    """Caso de uso para criar um local"""

    def __init__(self, repository: LocalRepository):
        