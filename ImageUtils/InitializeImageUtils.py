import sys
import logging
import logging.config

from pathlib import Path
from datetime import datetime

# Date
date = datetime.now().date()

# Adjust path for functions
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Initialize logging software
log_path = Path(project_root, 'Logging').as_posix()
logging.config.fileConfig(
    fname=Path(log_path, 'logging.conf'),
    defaults={'logdir': log_path, 'logdate': date.isoformat()}
)
logger = logging.getLogger(name=Path(__file__).stem)

# Check logger working
logging.info('Image Utils logging initialized successfully')
