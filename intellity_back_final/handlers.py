# handlers.py
from sqlalchemy import event, func
from sqlalchemy.orm import Session

from intellity_back_final.models.course_editor_lms_models import Chapter, ClassicLesson, Course, Module, ProgrammingLesson, QuizLesson, Stage, VideoLesson
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




def create_stage_progress(session, enrollment, stage):
    stage_progress = StageProgress(
        student_id=enrollment.student_id,
        stage_id=stage.id,
        is_completed=False  # Изначально урок не завершен
    )
    session.add(stage_progress)
    session.commit()



def handle_after_delete_stage(mapper, connection, target):
    with Session(bind=connection) as session:
        print(target)
        try:
            print(target)
            # Retrieve the associated module
            module = session.query(Module).filter(Module.id == target.module_id).first()
            if module:
                # Update total_stages_in_module
                module.total_stages_in_module -= 1
                session.add(module)
                session.flush()

                # Retrieve the associated chapter
                chapter = module.chapter
                if chapter:
                    # Update total_stages_in_chapter
                    chapter.total_stages_in_chapter -= 1
                    session.add(chapter)
                    session.flush()

                    # Retrieve the associated course
                    course = chapter.course
                    if course:
                        # Update total_stages
                        course.total_stages -= 1
                        session.add(course)
                        session.flush()

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Exception: {e}")
            raise

def handle_after_insert_lesson(connection,target):
    # print(session)
    with Session(bind=connection) as session:
        try:
            module = session.query(Module).filter(Module.id == target.module_id).first()
            # Обновление счетчика уроков у модуля, главы и курса
            module.total_stages_in_module += 1
            session.add(module)
            module.chapter.total_stages_in_chapter += 1
            session.add(module.chapter)
            module.chapter.course.total_stages += 1
            session.add(module.chapter.course)

            # Обновление прогресса у студентов
            enrollments = session.query(CourseEnrollment).filter_by(course_id=module.chapter.course_id).all()
            for enrollment in enrollments:
                create_stage_progress(session, enrollment, target)

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

@event.listens_for(ClassicLesson, 'after_insert')
def after_insert_classic_lesson(mapper, connection, target):
    handle_after_insert_lesson(connection,target)

@event.listens_for(ClassicLesson, 'after_delete')
def after_delete_lesson(mapper, connection, target):
    print(target)
    handle_after_delete_stage(mapper,connection,target)

@event.listens_for(ProgrammingLesson, 'after_insert')
def after_insert_programming_lesson(mapper, connection, target):
    handle_after_insert_lesson(connection,target)
@event.listens_for(ProgrammingLesson, 'after_delete')
def after_delete_lesson(mapper, connection, target):
    print(target)
    handle_after_delete_stage(mapper,connection,target)
@event.listens_for(QuizLesson, 'after_insert')
def after_insert_quiz_lesson(mapper, connection, target):
    handle_after_insert_lesson(connection,target)
@event.listens_for(QuizLesson, 'after_delete')
def after_delete_lesson(mapper, connection, target):
    print(target)
    handle_after_delete_stage(mapper,connection,target)

@event.listens_for(VideoLesson, 'after_insert')
def after_insert_video_lesson(mapper, connection, target):
    handle_after_insert_lesson(connection,target)
@event.listens_for(VideoLesson, 'after_delete')
def after_delete_lesson(mapper, connection, target):
    print(target)
    handle_after_delete_stage(mapper,connection,target)

@event.listens_for(Module, 'after_insert')
def after_insert_module(mapper, connection, target):
    with Session(bind=connection) as session:
        try:
            
            chapter = session.query(Chapter).filter(Chapter.id == target.chapter_id).first()
            chapter.total_modules_in_chapter += 1
            session.add(chapter)
            chapter.course.total_modules += 1
            session.add(chapter.course)

            # Обновление прогресса у студентов
            enrollments = session.query(CourseEnrollment).filter_by(course_id=chapter.course_id).all()
            for enrollment in enrollments:
                create_module_progress(session, enrollment, target)

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

def create_module_progress(session, enrollment, module):
    module_progress = ModuleProgress(
        student_id=enrollment.student_id,
        module_id=module.id,
        is_completed=False  # Изначально модуль не завершен
    )
    session.add(module_progress)


@event.listens_for(Module, 'after_delete')
def after_delete_module(mapper, connection, target):
    with Session(bind=connection) as session:
        try:
            chapter = session.query(Chapter).filter_by(id=target.chapter_id).first()

            if chapter:
                # Обновление счетчика модулей у главы
                chapter.total_modules_in_chapter -= 1
                session.add(chapter)

                # Обновление счетчика модулей у курса
                if chapter.course:
                    chapter.course.total_modules -= 1
                    session.add(chapter.course)
                else:
                    print(f"Warning: Chapter {chapter.id} does not have an associated course.")
            else:
                print(f"Warning: Module's chapter with id {target.chapter_id} not found.")
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Exception: {e}")
            raise

@event.listens_for(Chapter, 'after_insert')
def after_insert_chapter(mapper, connection, target):
    with Session(bind=connection) as session:
        
        try:

            course = session.query(Course).filter(Course.id == target.course_id).first()
            course.total_chapters += 1
            session.add(course)

            # Обновление прогресса у студентов
            enrollments = session.query(CourseEnrollment).filter_by(course_id=target.course_id).all()
            for enrollment in enrollments:
                create_chapter_progress(session, enrollment, target)

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

def create_chapter_progress(session, enrollment, chapter):
    chapter_progress = ChapterProgress(
        student_id=enrollment.student_id,
        chapter_id=chapter.id,
        is_completed=False  # Изначально глава не завершена
    )
    session.add(chapter_progress)


@event.listens_for(Chapter, 'after_delete')
def after_delete_chapter(mapper, connection, target):

    with Session(bind=connection) as session:
    
        try:
            course = session.query(Course).filter(Course.id == target.course_id).first()
            # Обновление счетчика глав у курса
            course.total_chapters -= 1
            session.add(course)

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()