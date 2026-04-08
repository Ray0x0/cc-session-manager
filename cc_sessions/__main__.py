import sys

from .actions import clean_sessions
from .ui import main

if len(sys.argv) > 1 and sys.argv[1] == "clean":
    clean_sessions()
else:
    main()
