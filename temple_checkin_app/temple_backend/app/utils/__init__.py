# 工具模組初始化檔案
from .auth import admin_required, active_user_required, get_current_user, token_required
from .helpers import (
    generate_uuid, success_response, error_response, paginate_response,
    safe_get_json, calculate_points, generate_amulet_uid
)
from .validators import (
    validate_username, validate_email_format, validate_password,
    validate_temple_data, validate_amulet_data, validate_checkin_data,
    validate_pagination_params
)

__all__ = [
    # Auth utilities
    'admin_required',
    'active_user_required', 
    'get_current_user',
    'token_required',
    
    # Helper functions
    'generate_uuid',
    'success_response',
    'error_response',
    'paginate_response',
    'safe_get_json',
    'calculate_points',
    'generate_amulet_uid',
    
    # Validators
    'validate_username',
    'validate_email_format',
    'validate_password',
    'validate_temple_data',
    'validate_amulet_data',
    'validate_checkin_data',
    'validate_pagination_params',
]