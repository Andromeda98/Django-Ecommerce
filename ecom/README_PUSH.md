# Instrucciones seguras para subir este repo a GitHub

Estos pasos te ayudan a subir tu repositorio a GitHub evitando publicar datos sensibles (db.sqlite3, claves, /media, etc.)

1) Verifica el `.gitignore` (ya incluido en la raíz)

2) Si tienes archivos sensibles ya trackeados (por ejemplo `db.sqlite3` o `media/`), elimínalos del índice antes de subir:

```bat
# desde la raíz del proyecto
git rm --cached db.sqlite3
git rm -r --cached media
git commit -m "Remove local DB and media from repository and add .gitignore"
```

3) Asegúrate que `SECRET_KEY` no esté hardcodeada en `ecom/settings.py` — ya hemos cambiado el código para leer `DJANGO_SECRET_KEY` desde el entorno.

4) Añade tu SECRET_KEY localmente en un fichero `.env` (no lo subas al repo). Usa `.env.example` como guía.

5) Crea (o apunta) al repositorio remoto en GitHub y sube tus cambios. Ejemplo usando HTTPS:

```bat
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M master
git push -u origin master
```

6) Si ya publicaste secretos en GitHub y necesitas eliminarlos del historial, usa `git filter-repo` o BFG.

Recomendación final: rotar cualquier secreto (SECRET_KEY, API keys) que haya sido puesto en un repo público por seguridad.
