# Interactive Routes Editor (pl)
## Description
A simple Django server that allows users to define, visualize, and edit routes on a background image of their choice. A logged-in user can edit and create routes through the editor by clicking on the map or entering coordinates in the form. Points can also be deleted and reordered (potentially moving points in the future).
## Admin panel
From the admin panel, one can manage the available background images (maps), user routes, as well as individual points.
## Dependencies
`django`,
`pillow`,
`djangorestframework` (Django REST framework),
`drf-yasg` (Swagger UI)
## Setup
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Creating superuser
```
python3 manage.py createsuperuser
```
Run with
```
python3 manage.py runserver
```
*Project for uni*