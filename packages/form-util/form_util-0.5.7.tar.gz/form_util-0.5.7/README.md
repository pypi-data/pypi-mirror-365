
````markdown
# form_util

**form_util** est une application Django réutilisable qui permet de générer et afficher facilement des formulaires dans vos projets Django.

---

##  Fonctionnalités

- Intégration facile dans n’importe quel projet Django
- Génération de formulaire personnalisable
- Rendu HTML prêt à l’emploi avec templates inclus

---

## Installation

```bash
pip install form_util
````


## Configuration

Ajoutez `form_util` dans `INSTALLED_APPS` de `settings.py` :

```python
INSTALLED_APPS = [
    ...
    'form_util',
]
```

---

## 🧠 Utilisation

Dans votre `urls.py` global :

```python
from django.urls import include, path

urlpatterns = [
    path('form/', include('form_util.urls')),
]
```


## Demarer le serveur django  

python manage.py migrate

python manage.py runserver 

Accédez ensuite à `http://localhost:8000/form/` pour voir le formulaire par défaut.

---
