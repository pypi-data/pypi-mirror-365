# sarenza-automation-core

**sarenza-automation-core** est une bibliothèque Python réutilisable pour l'automatisation de tests web et mobile (Selenium / Appium), conçue pour les équipes QA de Sarenza.  
Elle fournit une base commune pour standardiser les drivers, les helpers, les interactions DOM, le support multi-navigateurs, et bien plus.

---

## Fonctionnalités principales

### Core modules

- `DriverFactory` : instancie les drivers locaux ou distants (Chrome, Firefox, Appium).
- `Logger` : wrapper autour de [Loguru](https://github.com/Delgan/loguru) pour des logs lisibles et uniformes.
- `ConfigReaderHelper` : lecture de fichiers de configuration INI ou JSON.
- `TranslationHelper` : lecture de clés de traduction depuis un fichier `languages.json`.
- `Exceptions` : gestion des exceptions spécifiques (`ClickInterceptedException`, etc).

---

### Helpers intégrés

#### `BasePage` — la boîte à outils des pages web

```python
from sarenza_automation_core.base.base_page import BasePage
```
| Méthode                                      | Description                                               |
| -------------------------------------------- | --------------------------------------------------------- |
| `get_element_by((By.ID, "my-id"))`           | Retourne un élément avec un `By` donné                    |
| `get_element("_xpath", "//button")`          | Retourne un élément via une chaîne `_xpath`, `_css`, etc. |
| `click_element((By.ID, "submit"))`           | Click + Retry avec gestion des erreurs                    |
| `type_into_element_by(by, text)`             | Envoie du texte dans un champ                             |
| `select_from_dropdown_by_value/visible_text` | Sélectionne une valeur dans un `select`                   |
| `click_using_javascript(css_selector)`       | Force le clic JS si nécessaire                            |
| `scroll_down_until_element_by(locator)`      | Scrolling fluide jusqu'à un élément                       |
| `verify_page_title(expected_title)`          | Vérifie que le titre contient un texte                    |
| `is_element_not_displayed(locator)`          | Vérifie si un élément est caché ou absent                 |
| `extract_pcid_from_url()`                    | Extrait un PCID de l’URL                                  |
| `go_to_page("/mon/url")`                     | Va vers une URL relative à `SUT_URL`                      |
| `sleep(5)`                                   | Pause utile pour les tests manuels                        |


### Module `BrowserConsoleInteractor`

| Méthode                    | Description                                                                                      |
|---------------------------|--------------------------------------------------------------------------------------------------|
| `get_variable(variable_name: str)` | Exécute un script JavaScript pour récupérer une variable globale du navigateur. Renvoie la valeur ou `None`. |
| `list_global_variables()` | Retourne la liste des variables globales disponibles dans `window` du navigateur.               |
| `execute_custom_script(script: str)` | Exécute un script JavaScript personnalisé dans le contexte du navigateur. Renvoie le résultat ou `None`.  |
### Exemple d'utilisation de `BrowserConsoleInteractor`

```python
from selenium import webdriver
from sarenza_automation_core.helpers.browser_console_interactor import BrowserConsoleInteractor

# Initialiser le navigateur (ex. Chrome)
driver = webdriver.Chrome()

# Accéder à une page contenant des variables globales
driver.get("https://sarenza.com")

# Initialiser l'interacteur console
console = BrowserConsoleInteractor(driver)

# 1. Récupérer la valeur d'une variable globale
tc_events = console.get_variable("tc_full_events")
print("tc_full_events:", tc_events)

# 2. Lister toutes les variables globales
globals_list = console.list_global_variables()
print("Variables globales:", globals_list)

# 3. Exécuter un script personnalisé
result = console.execute_custom_script("return document.title;")
print("Titre de la page :", result)

# Fermer le navigateur
driver.quit()
```

 **Note** : Le navigateur doit être lancé avec les bons profils et autorisations pour permettre l’accès aux objets JavaScript globaux.
### Module : `LocalStorageHelper`

| Méthode                  | Description                                                                                         |
|--------------------------|-----------------------------------------------------------------------------------------------------|
| `set_item(key: str, value)`   | Stocke une paire clé/valeur dans le `localStorage` du navigateur (la valeur est sérialisée en JSON).     |
| `get_item(key: str)`          | Récupère une valeur du `localStorage` par sa clé. Désérialise automatiquement en objet Python.            |
| `remove_item(key: str)`       | Supprime une entrée du `localStorage` correspondant à la clé donnée.                                     |

### Exemple d'utilisation de `LocalStorageHelper`
```python
from selenium import webdriver
from sarenza_automation_core.helpers.local_storage_helper import LocalStorageHelper

# Initialiser le navigateur
driver = webdriver.Chrome()

# Accéder à une page qui utilise le localStorage
driver.get("https://sarenza.com")

# Initialiser le helper
storage = LocalStorageHelper(driver)

# 1. Stocker une valeur
storage.set_item("test_key", {"user": "Alice", "role": "admin"})

# 2. Lire la valeur
value = storage.get_item("test_key")
print("Valeur récupérée :", value)

# 3. Supprimer la clé
storage.remove_item("test_key")

# Fermer le navigateur
driver.quit()
```
###  Module : `translation_helper.py`


| Fonction                   | Description                                                                                       |
|----------------------------|---------------------------------------------------------------------------------------------------|
| `_load_translations()`     | Charge les traductions depuis un fichier JSON (défini par `FILE_PATH` ou par défaut `languages/languages.json`). |
| `get_translation(lang, key)` | Retourne la traduction d’un mot-clé (`key`) dans une langue donnée (`lang`). Renvoie un message d'erreur si introuvable. |
| `get_translated_value(key)` | Retourne la traduction d’un mot-clé (`key`) dans la langue par défaut définie via la variable d’environnement `LANGUAGE`. |

### Exemple d'utilisation
```python 
import os
from sarenza_automation_core.helpers.translation_helper import get_translation, get_translated_value

# Facultatif : définir manuellement la langue et le chemin du fichier
os.environ["LANGUAGE"] = "fr"
os.environ["FILE_PATH"] = "languages/languages.json"

# Traduction directe
print(get_translation("fr", "Mr"))  # Ex: "Monsieur"

# Traduction avec langue par défaut
print(get_translated_value("Mr"))   # Ex: "Monsieur"
```
### Module : `user_information_helper.py`

| Fonction                   | Description                                                                                       |
|----------------------------|---------------------------------------------------------------------------------------------------|
| `__init__(target_folder)`  | Initialise l’instance avec un dossier cible (par défaut `user_info`) et crée un verrou pour les accès concurrents. |
| `save_user_info(user_info)`| Sauvegarde un dictionnaire d’informations utilisateur dans un fichier JSON (par date + thread). Supprime les fichiers anciens. |
| `fetch_user_info()`        | Récupère les informations utilisateur sauvegardées pour la date et le thread en cours. Renvoie `None` si aucun fichier trouvé. |
###  Exemple d'utilisation
```python 
from sarenza_automation_core.helpers.user_information_helper import UserInformationHelper

user_info_helper = UserInformationHelper()

# Sauvegarde d'information
user_info_helper.save_user_info({"username": "john_doe", "session_id": "abc123"})

# Récupération
info = user_info_helper.fetch_user_info()
print(info)

```

## Installation

### Pré-requis

-   Python 3.11 
    
-   Poetry installé
    

### Étapes d’installation

# 1. Cloner le repo si ce n’est pas déjà fait 
```bash 
git clone https://github.com/sarenza/sarenza-automation-core.git cd sarenza-automation-core  
```

# 2. Créer l’environnement virtuel avec Poetry 
```bash
poetry install
```

# 3. Activer l’environnement 
```bash
poetry shell
```

##  Lancer les tests



# Tous les tests unitaires
```bash 
 poetry run pytest -v
 ```

* * *

## Variables d’environnement supportées

Variable

Description

Par défaut 5 secondes

`TIMEOUT`

Timeout global pour les éléments


`SUT_URL`

URL de base de l’application testée


`FILE_PATH`

Fichier JSON de traduction

`languages.json`



## 📄 Licence

MIT – © Sarenza QA Team

