# handlers.py
from sqlalchemy import event, func
from sqlalchemy.orm import Session

from intellity_back_final.models.course_editor_lms_models import Chapter, Module, Stage
from intellity_back_final.models.course_study_lms_models import ChapterProgress, CourseEnrollment, ModuleProgress, StageProgress

# подсчет  пройденных уроков и автоматическая их запись 
@event.listens_for(StageProgress, 'after_insert')
def receive_after_update(mapper, connection, target):
    print("вход в хэндлер")
    if target.is_completed:
        with Session(bind=connection) as session:
            stage = session.query(Stage).get(target.stage_id)
            if stage is not None:
                # Ваша логика обработки после вставки
                module_id = stage.module_id
                student_id = target.student_id
                total_stages = session.query(Stage).filter_by(module_id=module_id).count()
                completed_stages = session.query(StageProgress).join(Stage).filter(
                    Stage.module_id == module_id,
                    StageProgress.student_id == student_id,
                    StageProgress.is_completed == True
                ).count()
                if total_stages == completed_stages:
                    module_progress = session.query(ModuleProgress).filter_by(module_id=module_id, student_id=student_id).first()
                    if module_progress:
                        module_progress.is_completed = True
                        module_progress.end_time = func.now()
                    else:
                        session.add(ModuleProgress(
                            student_id=student_id,
                            module_id=module_id,
                            is_completed=True,
                            end_time=func.now()
                        ))
                    session.commit()

                    chapter_id = stage.module.chapter_id
                    total_modules = session.query(Module).filter_by(chapter_id=chapter_id).count()
                    completed_modules = session.query(ModuleProgress).join(Module).filter(
                        Module.chapter_id == chapter_id,
                        ModuleProgress.student_id == student_id,
                        ModuleProgress.is_completed == True
                    ).count()
                    print(total_modules)
                    print(completed_modules)
                    
                    if total_modules == completed_modules:
                        chapter_progress = session.query(ChapterProgress).filter_by(chapter_id=chapter_id, student_id=student_id).first()
                        if chapter_progress:
                            chapter_progress.is_completed = True
                            chapter_progress.end_time = func.now()
                        else:
                            session.add(ChapterProgress(
                                student_id=student_id,
                                chapter_id=chapter_id,
                                is_completed=True,
                                end_time=func.now()
                            ))
                        session.commit()

                        course_id = stage.module.chapter.course_id
                        total_chapters = session.query(Chapter).filter_by(course_id=course_id).count()
                        completed_chapters = session.query(ChapterProgress).join(Chapter).filter(
                            Chapter.course_id == course_id,
                            ChapterProgress.student_id == student_id,
                            ChapterProgress.is_completed == True
                        ).count()

                        if total_chapters == completed_chapters:
                            course_enrollment = session.query(CourseEnrollment).filter_by(course_id=course_id, student_id=student_id).first()
                            if course_enrollment:
                                course_enrollment.is_completed = True
                                course_enrollment.progress = 100.0
                                course_enrollment.end_time = func.now()
                            else:
                                session.add(CourseEnrollment(
                                    student_id=student_id,
                                    course_id=course_id,
                                    is_completed=True,
                                    progress=100.0,
                                    end_time=func.now()
                                ))
                            session.commit()