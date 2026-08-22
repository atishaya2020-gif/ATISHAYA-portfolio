import re

_MOBILE_RE = re.compile(
    r'android|iphone|ipod|opera mini|opera mobi|iemobile|windows phone|blackberry|mobile',
    re.IGNORECASE,
)
_TABLET_RE = re.compile(r'ipad|tablet|kindle|silk|playbook', re.IGNORECASE)


def get_device_type(user_agent: str) -> str:
    if not user_agent:
        return 'unknown'
    if _TABLET_RE.search(user_agent):
        return 'tablet'
    if _MOBILE_RE.search(user_agent):
        return 'mobile'
    return 'desktop'
