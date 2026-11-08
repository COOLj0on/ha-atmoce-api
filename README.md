# Atmoce Cloud API - Home Assistant

Integration Home Assistant pour récupérer les données d'une installation
ATMOCE via l'API Cloud officielle. Cette intégration est **100 % API** :
elle ne se connecte pas au réseau local et n'utilise pas Modbus TCP.

[![Lint](https://github.com/user/atmoce-api/workflows/Lint/badge.svg)](https://github.com/user/atmoce-api/actions/workflows/lint.yml)
[![Type Check](https://github.com/user/atmoce-api/workflows/Type%20Check/badge.svg)](https://github.com/user/atmoce-api/actions/workflows/type-check.yml)
[![Tests](https://github.com/user/atmoce-api/workflows/Tests/badge.svg)](https://github.com/user/atmoce-api/actions/workflows/test.yml)

## Installation

Copier `custom_components/atmoce` dans le répertoire
`config/custom_components/`, puis redémarrer Home Assistant. L'intégration peut
ensuite être ajoutée depuis **Settings > Devices & Services > Add Integration**.

## Configuration

Le flux demande :

- l'adresse e-mail ATMOCE (`username`) ;
- le mot de passe ATMOCE (`password`) ;
- l'identifiant du site ATMOCE (`site_id`).

L'authentification utilise :

```text
POST https://www.atmocecloud.com/permission-auth/api/login
```

avec `encrypted: true`, `appType: "web"` et le mot de passe encodé en Base64
dans le corps JSON. Le champ mot de passe est saisi comme champ sensible dans
le flux Home Assistant et n'est jamais écrit dans les journaux. Le Base64 est
un encodage demandé par l'API, pas un chiffrement.

La réponse fournit `prefix` et `token`. Ils sont utilisés pour authentifier les
appels suivants. Les identifiants sont vérifiés pendant la configuration avant
la création de l'entrée.

## Données récupérées

L'intégration envoie un `POST` vers :

```text
https://www.atmocecloud.com/energy-manage/webDeviceMonitor/getWebSingleDeviceDetailData
```

avec le corps suivant :

```json
{
  "typeCode": "gateway",
  "deviceId": 111285,
  "refreshRealtime": false
}
```

`deviceId` est le numéro numérique du gateway ATMOCE renseigné dans
`site_id`. L'intégration expose les données disponibles pour :

- puissance et énergie solaire ;
- puissance et énergie réseau importée ;
- énergie exportée ;
- tension et puissance réseau ;
- puissance de production ;
- consommations, production, demande et fourniture journalières et cumulées ;
- source de données et compteur d'erreurs de connexion.

L'API ATMOCE pouvant retourner des données avec plusieurs minutes de retard,
la fréquence de mise à jour est volontairement fixée à 15 minutes.

## Development

### Setup

Install development dependencies:

```bash
pip install -r dev-requirements.txt
```

### Code Quality

This project uses:

- **ruff** for linting and formatting
- **mypy** for static type checking
- **pytest** for testing

Run checks locally:

```bash
# Format and lint
python -m ruff format custom_components/atmoce/
python -m ruff check custom_components/atmoce/

# Type checking
python -m mypy custom_components/atmoce/ --show-error-codes

# Tests
python -m pytest custom_components/atmoce/tests/
```

### CI/CD Pipeline

Three GitHub Actions workflows automate code quality and testing:

- **Lint** (`.github/workflows/lint.yml`): Runs ruff format check and lint
- **Type Check** (`.github/workflows/type-check.yml`): Runs mypy on Python 3.10, 3.11, 3.12
- **Tests** (`.github/workflows/test.yml`): Runs pytest with coverage reporting

These workflows run on every push and pull request. All must pass before merging.
