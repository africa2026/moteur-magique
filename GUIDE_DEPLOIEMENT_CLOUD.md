# Guide de Déploiement Cloud Gratuit (Moteur de Rédaction Magique v5.0)

Ce guide vous explique comment déployer votre application sur des serveurs cloud gratuits pour y accéder depuis n'importe où, sans consommer vos crédits Manus.

## Architecture
- **Backend (Python/Flask)** : Sera hébergé sur **Render.com**
- **Frontend (React)** : Sera hébergé sur **Vercel.com**

---

## Étape 1 : Préparation du code sur GitHub
Pour déployer sur ces plateformes, le plus simple est de mettre votre code sur GitHub.
1. Créez un compte gratuit sur [GitHub](https://github.com/).
2. Créez un nouveau dépôt (repository) privé nommé `moteur-magique`.
3. Sur votre Mac, ouvrez le terminal dans le dossier `moteur-v4-final` et tapez :
   ```bash
   git init
   git add .
   git commit -m "Version 5.0 Initiale"
   git branch -M main
   git remote add origin https://github.com/VOTRE_NOM/moteur-magique.git
   git push -u origin main
   ```

---

## Étape 2 : Déploiement du Backend sur Render.com (Gratuit)
1. Allez sur [Render.com](https://render.com/) et créez un compte (vous pouvez vous connecter avec GitHub).
2. Cliquez sur **"New +"** en haut à droite, puis choisissez **"Web Service"**.
3. Connectez votre compte GitHub et sélectionnez le dépôt `moteur-magique`.
4. Remplissez les informations suivantes :
   - **Name** : `moteur-magique-api`
   - **Region** : Francfort (ou la plus proche de vous)
   - **Branch** : `main`
   - **Root Directory** : Laissez vide
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn -w 4 -b 0.0.0.0:$PORT backend.src.main:app`
5. Choisissez le plan **"Free"** (Gratuit).
6. Cliquez sur **"Create Web Service"**.
7. *Important :* Une fois déployé, Render vous donnera une URL (ex: `https://moteur-magique-api.onrender.com`). **Copiez cette URL**, vous en aurez besoin pour l'étape suivante.

---

## Étape 3 : Déploiement du Frontend sur Vercel.com (Gratuit)
1. Allez sur [Vercel.com](https://vercel.com/) et créez un compte (avec GitHub).
2. Cliquez sur **"Add New..."** puis **"Project"**.
3. Importez votre dépôt GitHub `moteur-magique`.
4. Dans la section **"Framework Preset"**, choisissez **"Vite"**.
5. Dans la section **"Root Directory"**, cliquez sur "Edit" et choisissez le dossier `frontend` (ou `moteur-frontend-v4` selon comment vous l'avez nommé dans votre repo).
6. Dans la section **"Environment Variables"**, ajoutez une nouvelle variable :
   - **Name** : `VITE_API_URL`
   - **Value** : Collez l'URL de Render obtenue à l'étape 2 (ex: `https://moteur-magique-api.onrender.com`)
7. Cliquez sur **"Deploy"**.

---

## C'est terminé !
Vercel vous donnera une URL finale (ex: `https://moteur-magique.vercel.app`). 
C'est votre application en ligne ! Vous pouvez l'ouvrir sur votre téléphone, votre tablette, ou la partager avec vos collaborateurs.

*Note sur les limites gratuites :*
- Le backend sur Render "s'endort" après 15 minutes d'inactivité. La première requête après une pause prendra environ 30 secondes pour le réveiller.
- Les fonctionnalités nécessitant Ollama (IA locale) utiliseront des modèles de secours si elles sont configurées, car Render gratuit n'a pas de GPU pour faire tourner Ollama.
