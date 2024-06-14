# handlers.py
from sqlalchemy import event, func
from sqlalchemy.orm import Session

from intellity_back_final.models.course_editor_lms_models import Chapter, Module, Stage
from intellity_back_final.models.course_study_lms_models import ChapterProgress, CourseEnrollment, ModuleProgress, StageProgress
from datetime import datetime
# подсчет  пройденных уроков и автоматическая их запись 
@event.listens_for(StageProgress, 'after_update')
def receive_after_update(mapper, connection, target):
    if target.is_completed:
        student_id = target.student_id

        with Session(bind=connection) as session:
            stage = session.query(Stage).get(target.stage_id)

            if stage is not None:
                module_id = stage.module_id

                # Find all stages within the same module
                total_stages = session.query(Stage).filter_by(module_id=module_id).count()

                # Find all completed StageProgress within this module
                completed_stages = session.query(StageProgress).filter_by(
                    student_id=student_id,
                    is_completed=True
                ).join(Stage).filter(Stage.module_id == module_id).count()

                print(total_stages)
                print(completed_stages)
                if total_stages == completed_stages:
                    # Update Module Progress
                    module_progress = session.query(ModuleProgress).filter_by(
                        student_id=student_id,
                        module_id=module_id
                    ).first()

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

                    # Update Chapter Progress
                    chapter_id = stage.module.chapter_id
                    total_modules = session.query(Module).filter_by(chapter_id=chapter_id).count()
                    completed_modules = session.query(ModuleProgress).filter_by(
                        student_id=student_id,
                        is_completed=True
                    ).join(Module).filter(Module.chapter_id == chapter_id).count()

                    if total_modules == completed_modules:
                        chapter_progress = session.query(ChapterProgress).filter_by(
                            student_id=student_id,
                            chapter_id=chapter_id
                        ).first()

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

                        # Update Course Enrollment
                        course_id = stage.module.chapter.course_id
                        total_chapters = session.query(Chapter).filter_by(course_id=course_id).count()
                        completed_chapters = session.query(ChapterProgress).filter_by(
                            student_id=student_id,
                            is_completed=True
                        ).join(Chapter).filter(Chapter.course_id == course_id).count()

                        if total_chapters == completed_chapters:
                            course_enrollment = session.query(CourseEnrollment).filter_by(
                                student_id=student_id,
                                course_id=course_id
                            ).first()

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


@event.listens_for(CourseEnrollment, 'after_insert')
def create_students_tables(mapper, connection, target):
    db = Session(bind=connection)
    # Получить студента и курс
    student_id = target.student_id
    course_id = target.course_id

    # Найти все главы, модули и уроки, относящиеся к курсу
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    for chapter in chapters:
        # Создать запись прогресса для главы
        chapter_progress = ChapterProgress(
            student_id=student_id,
            chapter_id=chapter.id,
            is_completed=False,
            start_time=datetime.utcnow()
        )
        db.add(chapter_progress)
        db.flush()  # Сохранить изменения, чтобы получить ID

        modules = db.query(Module).filter(Module.chapter_id == chapter.id).all()
        for module in modules:
            # Создать запись прогресса для модуля
            module_progress = ModuleProgress(
                student_id=student_id,
                module_id=module.id,
                is_completed=False,
                start_time=datetime.utcnow()
            )
            db.add(module_progress)
            db.flush()  # Сохранить изменения, чтобы получить ID

            stages = db.query(Stage).filter(Stage.module_id == module.id).all()
            for stage in stages:
                # Создать запись прогресса для урока
                stage_progress = StageProgress(
                    student_id=student_id,
                    stage_id=stage.id,
                    is_completed=False,
                    start_time=datetime.utcnow()
                )
                db.add(stage_progress)
                db.flush()

    db.commit()
