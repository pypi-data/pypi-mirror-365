try:
    from typing import Literal, NotRequired, TypeAlias, Optional, Dict, List, TypedDict  # Python 3.11+
except ImportError:
    try:
        from typing import Literal  # Python 3.8 - 3.10
    except ImportError:
        from typing_extensions import Literal  # Python 3.7 fallback

    from typing_extensions import NotRequired
    from typing_extensions import TypeAlias
    from typing_extensions import Optional
    from typing_extensions import Dict
    from typing_extensions import List 
    from typing_extensions import TypedDict
