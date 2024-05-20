# Система обучения Intellity LMS
![alt text](image.png)
![image](https://github.com/twoballs-ai/intellity-back-final/assets/83840596/0a2b2463-7dc2-4cdd-bbfb-396edddcabd7)

# Learning Management System (LMS) - Models and Functionality

## Overview

This project implements a Learning Management System (LMS) using SQLAlchemy for the ORM and FastAPI for the API endpoints. The system supports users (students and teachers), courses, chapters, modules, stages (lessons), and tracks student progress through the courses.

## Models

### User Models

#### User
- `id`: Integer, primary key
- `email`: String, unique
- `password_hash`: String
- `type`: String (polymorphic identity)

#### Teacher (inherits from User)
- `id`: Integer, ForeignKey('user_model.id'), primary key
- `name`: String
- `lastName`: String
- `qualification`: String
- `skills`: Text

#### Student (inherits from User)
- `id`: Integer, ForeignKey('user_model.id'), primary key
- `interested_categories`: Text

### Course Models

#### CourseCategory
- `id`: Integer, primary key
- `title`: String, unique
- `description`: Text

#### Course
- `id`: Integer, primary key
- `category`: Integer, ForeignKey('course_category_model.id')
- `teacher_id`: Integer, ForeignKey('teacher_model.id', ondelete='CASCADE')
- `title`: String, unique
- `description`: Text
- `course_views`: BigInteger, default 0
- `chapter_model`: Relationship with `Chapter`

### Chapter Models

#### Chapter
- `id`: Integer, primary key
- `course_id`: Integer, ForeignKey('course_model.id', ondelete='CASCADE')
- `title`: String
- `description`: Text
- `sort_index`: Integer, default 1
- `is_exam`: Boolean, default False
- `exam_duration_minutes`: Integer
- `previous_chapter_id`: Integer, ForeignKey('chapter_model.id')
- `previous_chapter`: Relationship with self
- `course_model`: Relationship with `Course`
- `module_rel_model`: Relationship with `Module`

### Module Models

#### Module
- `id`: Integer, primary key
- `chapter_id`: Integer, ForeignKey('chapter_model.id', ondelete='CASCADE')
- `title`: String
- `description`: Text
- `chapter_rel_model`: Relationship with `Chapter`
- `stage_rel_model`: Relationship with `Stage`

### Stage Models

#### Stage
- `id`: Integer, primary key
- `type`: String (polymorphic identity)
- `module_id`: Integer, ForeignKey('module_model.id', ondelete='CASCADE')
- `title`: String
- `questions`: Relationship with `Question`
- `module_rel_model`: Relationship with `Module`

#### ClassicLesson (inherits from Stage)
- `html_code_text`: String

#### VideoLesson (inherits from Stage)
- `video_link`: String

#### ProgrammingLesson (inherits from Stage)
- `code_string`: String

#### QuizLesson (inherits from Stage)
- `questions`: Relationship with `Question`

### Question Models

#### Question
- `id`: Integer, primary key
- `question_text`: String
- `order`: Integer
- `quiz_id`: Integer, ForeignKey('stage_model.id')
- `is_true_answer`: Boolean
- `quiz`: Relationship with `QuizLesson`

### Enrollment Models

#### CourseEnrollment
- `id`: Integer, primary key
- `course_id`: Integer, ForeignKey('course_model.id')
- `student_id`: Integer, ForeignKey('student_model.id')
- `enrolled_time`: DateTime, default `datetime.utcnow`
- `progress`: Float, default 0.0
- `is_completed`: Boolean, default False

#### ChapterProgress
- `id`: Integer, primary key
- `chapter_id`: Integer, ForeignKey('chapter_model.id')
- `student_id`: Integer, ForeignKey('student_model.id')
- `is_completed`: Boolean, default False
- `start_time`: DateTime, default `datetime.utcnow`
- `end_time`: DateTime, nullable=True

#### ModuleProgress
- `id`: Integer, primary key
- `module_id`: Integer, ForeignKey('module_model.id')
- `student_id`: Integer, ForeignKey('student_model.id')
- `is_completed`: Boolean, default False
- `start_time`: DateTime, default `datetime.utcnow`
- `end_time`: DateTime, nullable=True

#### StageProgress
- `id`: Integer, primary key
- `stage_id`: Integer, ForeignKey('stage_model.id')
- `student_id`: Integer, ForeignKey('student_model.id')
- `is_completed`: Boolean, default False
- `start_time`: DateTime, default `datetime.utcnow`
- `end_time`: DateTime, nullable=True

## API Endpoints

### Enrollment Endpoints

#### Enroll Student in a Course

**POST** `/enroll/{student_id}/{course_id}`

Enrolls a student in a course.

**Parameters:**
- `student_id`: ID of the student
- `course_id`: ID of the course

**Response:**
- Returns the enrollment record.

#### Update Chapter Progress

**POST** `/update_chapter/{student_id}/{chapter_id}`

Updates the progress of a student in a chapter.

**Parameters:**
- `student_id`: ID of the student
- `chapter_id`: ID of the chapter
- `is_completed`: Boolean indicating if the chapter is completed

**Response:**
- Returns the updated chapter progress record.

#### Update Module Progress

**POST** `/update_module/{student_id}/{module_id}`

Updates the progress of a student in a module.

**Parameters:**
- `student_id`: ID of the student
- `module_id`: ID of the module
- `is_completed`: Boolean indicating if the module is completed

**Response:**
- Returns the updated module progress record.

#### Update Stage Progress

**POST** `/update_stage/{student_id}/{stage_id}`

Updates the progress of a student in a stage.

**Parameters:**
- `student_id`: ID of the student
- `stage_id`: ID of the stage
- `is_completed`: Boolean indicating if the stage is completed

**Response:**
- Returns the updated stage progress record.



## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This README provides an overview of the models, functionality, and usage of the Learning Management System (LMS) project. Adjust the paths, URLs, and other specific details according to your project's structure and configuration.
