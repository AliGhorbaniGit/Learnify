# Learnify  

Learnify is a dynamic educational platform that facilitates the sharing of knowledge through video tutorials and textual articles. It empowers students to contribute by curating tutorials or scholarly articles, fostering a collaborative and peer-driven learning environment. Built with modern tools, it offers robust authentication, content management, and user interaction features.  

---  

## Features  

- **User Authentication & Account Management**  
  - Email login and registration  
  - Password change and recovery  
  - Social accounts login (via google)  
  - Custom user model  
- **Content Sharing & Management**  
  - Users can submit articles and request adding new courses  
  - View and manage user profiles, including updates and edits  
  - Overview of other users' profiles  
- **Community & Collaboration**  
  - Users can request new courses  
  - Articles and tutorials curated by students
- **Interaction & Feedback**  
  - Commenting on articles and tutorials  
  - Rating and review system for content  
- **Admin & Moderation**  
  - Error handling and custom error pages  
  - Admin panel with customized fields  
  - Ticketing system for support  
- **Advanced Features**  
  - Search and filter views for content discovery  
  - Signals for event-driven actions  
  - Article submission and review workflows  
  - Multi-platform storage support via Django Storages and AWS  
- **Performance & Optimization**  
  - Query optimization with up to 20% improvement  
- **Testing**  
  - Comprehensive test suite to ensure stability and quality  
- **Additional**  
  - Error handlers for better user experience  

---  

## Technologies & Packages  

- Django (with custom user model)  
- Django Allauth (social authentication)  
- Django Storages & AWS S3 (media storage)  
- Jazmin (admin panel)  
- MySQL (database)  
- Signal dispatching for event handling  
- Custom error handlers  
- Ticketing system for user support  
- Query optimization techniques  
- Testing framework (unit test)
- Docker

---  

## Prerequisites  

- Python 3.10+  
- Pipenv or virtual environment  
- MySQL server  
- AWS credentials (for storage)
- Docker

---  


## environment setup

```bash
cp .example.env .env
```

Edit `.env` and set the required values.

---


## setup & run

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bat
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run development server:

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---



