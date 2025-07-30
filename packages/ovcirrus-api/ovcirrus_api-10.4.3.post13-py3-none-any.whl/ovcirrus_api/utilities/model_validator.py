from typing import Type, TypeVar, Optional
from pydantic import ValidationError, BaseModel
import logging

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)

from pydantic import ValidationError
import json
from typing import Type, Optional

def safe_model_validate(model_class: Type[T], data: dict) -> Optional[T]:
    try:
        # Attempt to validate the model data
        return model_class.model_validate(data)
    except ValidationError as ve:
        # Log validation-specific issues, e.g., missing or invalid fields
        logger.warning(f"Validation failed for {model_class.__name__}: {ve}")
        return None
    except json.decoder.JSONDecodeError as e:
        # Handle JSON parsing errors (invalid JSON format)
        logger.error(f"Malformed JSON encountered while validating {model_class.__name__}: {e}")
        return None
    except Exception as e:
        # Handle any other unexpected errors during the validation process
        logger.error(f"Unexpected error during model validation for {model_class.__name__}: {e}")
        return None
