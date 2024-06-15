import os
from datetime import datetime

# Список URL-адресов, которые нужно добавить в карту сайта
urls = [
    "/",
    "/detail/{course_id}",
    "/about",
    "/category",
    "/logout",
    "/student-profile",
    "/student-profile/my-courses",
    "/student-profile/profile-settings",
    "/student-profile/reset-password",
    "/teacher-profile",
    "/teacher-profile/my-courses",
    "/teacher-profile/add-course",
    "/teacher-profile/profile-settings",
    "/teacher-profile/reset-password",
    "/course-editor/{course_id}",
    "/course-settings/{course_id}",
    "/course-learning/{course_id}"
]

# Основной URL вашего сайта
base_url = "http://intellity.ru:8000"

# Текущая дата в формате ISO 8601
current_date = datetime.now().isoformat()

# Создание файла sitemap.xml
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

    for url in urls:
        url = url.replace("{course_id}", "{course_id}")  # Replace placeholders
        f.write("  <url>\n")
        f.write(f"    <loc>{base_url}{url}</loc>\n")
        f.write(f"    <lastmod>{current_date}</lastmod>\n")
        f.write("    <changefreq>weekly</changefreq>\n")
        f.write("    <priority>0.8</priority>\n")
        f.write("  </url>\n")

    f.write('</urlset>\n')

print("Sitemap generated successfully.")