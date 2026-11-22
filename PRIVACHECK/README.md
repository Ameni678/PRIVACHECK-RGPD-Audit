# PRIVACHECK AI — Professional Edition

Application locale d'aide à l'analyse documentaire RGPD : extraction PDF/DOCX/TXT, repérage indicatif de critères, rapport PDF, assistant documentaire RAG, base de connaissances, historique et module ML.

## Démarrage rapide — Windows 10/11

1. Installer Python 3 (cocher **Add Python to PATH** pendant l'installation).
2. Extraire entièrement l'archive ZIP dans un dossier accessible en écriture.
3. Ouvrir le dossier `PRIVACHECK`.
4. Double-cliquer sur `OUVRIR_PRIVACHECK.bat`.
5. Au premier démarrage, le script crée `.venv` et installe les dépendances. Cela nécessite Internet.
6. Le navigateur s'ouvre sur **http://localhost:8501**. Si ce n'est pas le cas, saisir cette adresse dans le navigateur.
7. Pour arrêter l'application, revenir à la fenêtre noire et appuyer sur `Ctrl+C`.

## Langues

Le sélecteur propose 🇫🇷 Français, 🇬🇧 English, 🇩🇪 Deutsch et 🇸🇦 العربية. Les libellés courants de navigation et d'action sont traduits. Les passages spécialisés non encore traduits restent en anglais plutôt que d'être traduits automatiquement de façon incertaine. Les règles de détection repèrent surtout des formulations françaises et anglaises ; les documents allemands et arabes peuvent donc nécessiter une vérification humaine plus attentive.

## Logo et thème

Le logo fourni par l'utilisatrice est intégré dans `assets/privacheck_logo.png`. L'interface utilise un thème clair, bleu nuit et violet, avec une typographie agrandie et des cartes de synthèse.

## Assistant IA / RAG

La recherche documentaire locale fonctionne sans clé LLM. Pour activer la génération de réponses, renseigner `LLM_API_KEY` dans `.env` (et ajuster `LLM_BASE_URL` / `LLM_MODEL` si nécessaire). Ne jamais partager ce fichier ni publier la clé.

## Données et confidentialité

L'application est configurée pour fonctionner localement sur `127.0.0.1`. Les documents importés et les audits sont stockés dans la base SQLite locale. Si un fournisseur LLM est configuré, le contexte envoyé au fournisseur dépend de la configuration et de la fonction utilisée : ne pas y soumettre de documents confidentiels sans autorisation.

## Limites importantes

PRIVACHECK AI réalise un repérage documentaire indicatif. Ce n'est ni une certification, ni un avis juridique, ni un audit complet de conformité. Le jeu de données ML fourni est pédagogique. Les critères textuels peuvent manquer des formulations équivalentes et les résultats doivent être validés par une personne compétente.

## Vérification technique

Tests automatisés : `pytest -q` depuis ce dossier.
