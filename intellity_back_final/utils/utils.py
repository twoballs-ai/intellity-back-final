from intellity_back_final.models.site_utils_models import ActionLog, LogType
from sqlalchemy.orm import Session

def log_action(db: Session, user_id: int, action: str, log_type_id: int, object_id: str, model_name: str):
    action_log = ActionLog(
        user_id=user_id, 
        action=action, 
        log_type_id=log_type_id,
        object_id=object_id,
        model_name=model_name  # Save the model or table name
    )
    db.add(action_log)
    db.commit()
    db.refresh(action_log)
    return action_log