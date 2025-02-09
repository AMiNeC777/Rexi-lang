# Rexi Programming Language

Rexi est un langage de programmation expérimental qui combine simplicité syntaxique et typage fort. Il est conçu pour être facile à apprendre tout en maintenant une structure claire et des types expressifs.

## Caractéristiques

- Typage fort et statique
- Syntaxe claire et intuitive
- Types de données expressifs (IN, IR, STR, BINARY, TAB)
- Support natif des structures de contrôle
- Interpréteur complet écrit en Python

## Types de Données

- `IN` : Nombres entiers
- `IR` : Nombres réels
- `STR` : Chaînes de caractères
- `BINARY` : Valeurs booléennes (YES/NO ou 1/0)
- `TAB<type>` : Tableaux typés

## Syntaxe de Base

### Déclaration de Variables
```
IN age = 25;
STR nom = "Alice";
BINARY estMajeur = YES;
TAB<IN> nombres = [1, 2, 3];
```

### Structures de Contrôle
```
if age >= 18 then
    output "Majeur";
else
    output "Mineur";
end
```

### Sortie
```
output expression;
```

## Installation

1. Cloner le repository
```bash
git clone https://github.com/votre-username/rexi.git
cd rexi
```

2. S'assurer que Python 3.6+ est installé
```bash
python --version
```

3. Exécuter un programme Rexi
```bash
python rexi_interpreter.py votre_programme.rexi
```

## Exemple de Programme

```
# Calcul de moyenne
IN taille = 3;
IR somme = 0.0;
TAB<IR> notes = [15.5, 17.0, 12.5];

if taille > 0 then
    IR moyenne = somme / taille;
    output moyenne;
else
    output "Aucune note";
end
```

## Structure du Projet

```
rexi/
├── src/
│   ├── lexer.py       # Analyse lexicale
│   ├── parser.py      # Analyse syntaxique
│   ├── interpreter.py # Interpréteur
│   └── ast.py        # Définitions AST
├── examples/          # Exemples de programmes
├── tests/            # Tests unitaires
├── docs/             # Documentation
└── README.md         # Ce fichier
```

## Grammaire BNF

La grammaire complète du langage est disponible dans le fichier [grammar.bnf](docs/grammar.bnf).

## Tests

Pour exécuter les tests :
```bash
python -m pytest tests/
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

Amine Hamouchi
- GitHub: [@AMiNeC777](https://github.com/AMiNeC777)
- Email: aminehamouchi69@gamil.com

## Remerciements

- Inspiré par les langages Pascal et Python
- Développé dans le cadre d'un projet éducatif encadrer par Naoual MOUHNI
