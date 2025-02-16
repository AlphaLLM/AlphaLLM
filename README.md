# AlphaLLM - Documentation GitHub 🚀

**AlphaLLM** est un bot Discord écrit en Python, qui regroupe plusieurs APIs : 

- Cerebras AI, un modèle de Llama 3.3 70B ultra-rapide et performant
- Pollinations AI, qui fournit des modèles populaires tels que GPT 4o, Deepseek, ou encore Qwen 72B
- Perplexity AI, qui fournit des réponses précises et d'actualité
- Pollinations AI, qui fournit également plusieurs modèles d'image tels que Flux, Turbo ou encore Flux3D

---

## **Fonctionnalités principales** 🌟

- 🧠 **Choix simple du modèle** : Reconnait le modèle sélectionné par l'utilisateur, grâce à un rôle Discord créé pour chaque modèle disponible lors de l'ajout du bot au serveur.
- 🛡️ **utilisation en MP** : Fonctionne également en MP, sauf que le modèle utilisé en MP est le modèle par défaut.
- 🔗 **Traitement des liens** : Remplace automatiquement les liens par leur contenu au format Markdown.
- 📕 **Traitement des fichiers** : Traite les fichiers (PDF, Docx, Images, etc) grâce à la librairie `Markitdown`.
- 📄 **Support Markdown** : Formate ses réponses suivant la syntaxe Markdown de Discord.
- 🖼️ **Génération d'images de qualité** : Génère des images jusqu'à 2048x2048.
- 🔁 **Bouton de régénération** : Régénère la réponse ou l'image.
- ⚠️ **Gestion des erreurs** : Gère les erreurs des différentes API et informe l'utilisateur en conséquence.

---

## **Installation** 🛠️

### Prérequis
1. 🖥️ Python 3.11
2. 🤖 Un bot Discord configuré avec tous les Intents et permissions.
3. 🔑 Une clé API pour OpenRouter, une autre pour Cerebras Cloud SDK.

### Étapes d'installation
1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/AlphaLLM/AlphaLLM.git
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez vos paramètres dans le fichier `.env` :
   ```venv
    DISCORD_TOKEN=""
    CEREBRAS_API_KEY=""
    OPENROUTER_API_KEY=""
    LOG_LEVEL='INFO'
   ```

4. Lancez le bot :
   ```bash
   python bot.py
   ```

---

## **Configuration** ⚙️

### Modèles utilisés 🧩

Modèles textuels disponibles :

- `OpenAI GPT 4o mini`
- `OpenAI GPT 4o`
- `Qwen 2.5 72B`
- `Qwen 2.5 Coder 32B`
- `Llama 3.3 70B`
- `Mistral Nemo`
- `Unity Mistral Large`
- `Midijourney`
- `Rtist`
- `SearchGPT`
- `Evil`
- `Claude Hybridspace`
- `DeepSeek R1`
- `Llama 3.1 8B Instruct`
- `Llamaguard 7B AWQ`
- `Gemini 2.0 Flash`
- `Gemini 2.0 Flash Thinking`
- `Hormoz 8B`
- `Perplexity`
- `Llama 3.3 70B (fast)`

Modèles d'images disponibles :

- `Flux`
- `Flux-Realism`
- `Flux-Cablyai`
- `Flux-Anime`
- `Flux-3d`
- `Any-Dark`
- `Flux-Pro`
- `Turbo`

---

## **Utilisation** 📚

### Commandes principales

1. **Mentionner le bot**
   Mentionnez le bot dans un message ou une réponse avec une question :
   ```text
   @AlphaLLM Peux-tu m'aider avec une commande Linux ?
   ```
   ```text
   @OpenAI GPT 4o Peux-tu m'écrire un long texte descriptif ?
   ```
   ```text
   @Deepseek R1 Peux-tu m'aider à résoudre ce problème mathématique complexe ?
   ```
   ```text
   @Perplexity Peux-tu me résumer l'actualité d'aujourd'hui ?
   ```

2. **Générer une image**
   Exemple avec tous les paramètres disponibles :
   ```text
   /image prompt:'A minecraft landscape, plains biome, voxel, blocky style, smooth shaders, blocky trees' model:[] width:2048 height:1024 nologo:True private:True enhance:False safe:True
   ```
   ![image](https://github.com/user-attachments/assets/a8c79981-5485-433a-ae63-dc48ee5a8888)
   ![image](https://github.com/user-attachments/assets/cbd8dfd7-b1c6-4212-b465-28fa59c03a4d)
   ![image](https://github.com/user-attachments/assets/a461acf8-b8be-4c86-bc45-e50235330270)
   ![image](https://github.com/user-attachments/assets/4eedc3e1-8958-43cb-ac61-4a87651f37a7)
   ![image](https://github.com/user-attachments/assets/1bee6530-b1f3-495b-927a-64e2bf2cecf3)

  Tous les paramètres à l'exception du prompt sont optionnels. Voici la valeur par défaut et la description de chaque paramètre :
  
  - `prompt` : le prompt décrivant l'image
  - `model` : le nom du modèle parmi ceux disponible (défault = Flux)
  - `width` : la largeur de l'image (défault = 1024)
  - `height` : la hauteur de l'image (défault = 1024)
  - `nologo` : le watermark du modèle (activer le watermark => False) (défault = True)
  - `private` : si l'image est publique ou non (rendre l'image privée => True) (défault = False)
  - `enhance` : si le prompt doit être amélioré par un modèle particulier (défault = False)
  - `safe` : si l'image peut être NSFW ou pas (activer le NSFW => False) (défault = True)

  Exceptions :
  - le paramètre safe sera forcé à True si le salon n'est pas en NSFW
  - si l'image est rendue publique, elle apparaitra dans le [feed public de Pollinations AI](https://image.pollinations.ai/feed) et dans le salon `#🎨-galerie` du serveur de support du bot.

---

## **Contributions** 🤝

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :
1. Forkez le dépôt.
2. Créez une branche pour votre fonctionnalité ou correction de bug :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```
3. Soumettez une Pull Request avec une description claire.

---

## **Support** 📧

Pour toute question ou problème, contactez-nous via [le serveur Discord de support](https://discord.gg/QGvyrUgwdK).

---

Merci d'utiliser AlphaLLM ! 🎮✨
