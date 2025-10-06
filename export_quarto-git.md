# Versiebeheer met Quarto en YAML: Aanbevelingen

Voor versiebeheer met Quarto en YAML is het aan te raden om Git als versiebeheersysteem te gebruiken, waarbij je het YAML-configuratiebestand (`_quarto.yml`) meeneemt in de repository.

## Aanbevelingen

- **Gebruik Git voor versiebeheer**  
  Git is de meest gebruikte tool om wijzigingen in YAML-bestanden en Quarto-projecten bij te houden. Hiermee kan je effectief samenwerkingen managen, wijzigingen volgen, en eerdere versies herstellen.

- **YAML in Quarto projecten**  
  Het Quarto YAML-bestand (`_quarto.yml`) bevat projectbreed gedeelde instellingen, zoals metadata, outputformaten, en styling. Dit bestand hoort in je Git-repo te staan zodat alle projectleden dezelfde configuratie gebruiken.

- **Branching en Pull Requests**  
  Gebruik branches in Git om nieuwe functies of wijzigingen in YAML veilig te ontwikkelen, en gebruik pull requests voor code reviews zodat configuraties consistent en foutloos blijven.

- **Automatische validatie**  
  Combineer met YAML-linters of geautomatiseerde tests om YAML-syntaxis en regels te checken bij elke commit, wat fouten minimaliseert.

## Waarom YAML en Git samen

- YAML is leesbaar en geschikt om configuraties te beheren, maar zonder versiebeheer zijn samenwerkingen lastig.  
- Git houdt een complete geschiedenis van wijzigingen en combineert makkelijk met Quarto-projecten voor reproduceerbaarheid.

## Praktische stappen

1. Initialiseer een Git-repo in je Quarto-projectfolder (indien nog niet gedaan).  
2. Voeg `_quarto.yml` en je Quarto-documenten toe aan Git.  
3. Commit regelmatig met duidelijke berichten.  
4. Werk met branches voor grote wijzigingen.  
5. Zorg dat teammates code/reviews doen via pull requests.

## Samenvattend

- Quarto-gebruikers werken het beste met een Git-repo voor versiebeheer.  
- YAML-configuraties (bijvoorbeeld `_quarto.yml`) horen in Git thuis.  
- Gebruik best practices van Git (branches, commits, pull requests) ook voor deze configuraties.  
- Automatiseer waar mogelijk validatie van YAML-bestanden.

Deze aanpak geeft maximale transparantie, terugrolbaarheid en samenwerkingsefficiëntie voor Quarto-projecten met YAML-configuratie.

---

### Bronnen

- [Project Basics - Quarto](https://quarto.org/docs/projects/quarto-projects.html)  
- [Best Practices for Version Controlling YAML Files](https://moldstud.com/articles/p-best-practices-for-version-controlling-yaml-files)  
- [Git and GitHub - Richard Ressler](https://rressler.quarto.pub/data-413-613/02_git_github_main.html)  
- [Quarto Integration – RStudio User Guide](https://docs.posit.co/ide/user/ide/guide/documents/quarto-project.html)  
- [Is there a clever way of handling / organising a yaml? #3052](https://github.com/gethomepage/homepage/discussions/3052)  
- [Version Control with Git and GitHub](https://biostats-r.github.io/biostats/github/)
