# Build e Deploy Flatpak

Questo documento spiega come buildare un Flatpak localmente e come pubblicarlo su Flathub.

## Script Disponibili

### 1. `build-flatpak-local.sh` - Build Locale

Questo script builda il Flatpak usando i sorgenti locali per test e sviluppo.

**Caratteristiche:**
- Usa i sorgenti locali (non richiede commit/tag)
- Installa automaticamente le dipendenze Flatpak necessarie
- Crea un build di test per verificare che tutto funzioni
- Ideale per lo sviluppo e test rapidi

**Uso:**
```bash
cd build-scripts
./build-flatpak-local.sh
```

**Prerequisiti:**
- `flatpak-builder` installato
- Git configurato
- Connessione internet per scaricare le dipendenze

### 2. `push-flathub.sh` - Preparazione per Flathub

Questo script prepara i file per la pubblicazione su Flathub.

**Caratteristiche:**
- Aggiorna automaticamente i file manifest e metainfo
- Verifica che il repository sia pulito e taggato
- Esegue un test build prima del push
- Committa e pusha le modifiche su GitHub
- Fornisce istruzioni dettagliate per la submission su Flathub

**Uso:**
```bash
cd build-scripts
./push-flathub.sh [versione]
```

Se non specifichi una versione, verrà usata quella dal PKGBUILD.

**Prerequisiti:**
- Repository Git pulito (nessuna modifica non committata)
- Tag di versione esistente (es. `v1.0.3`)
- Git configurato con nome utente e email
- `flatpak-builder` installato (per il test build opzionale)

## Workflow Completo

### Per lo sviluppo quotidiano:
1. Modifica il codice
2. Testa con: `./build-flatpak-local.sh`
3. Ripeti fino a quando non sei soddisfatto

### Per rilasciare una nuova versione:
1. Aggiorna la versione nel `PKGBUILD`
2. Committa tutte le modifiche
3. Crea un tag: `git tag v1.0.4`
4. Pusha il tag: `git push origin v1.0.4`
5. Esegui: `./push-flathub.sh`
6. Segui le istruzioni per creare la Pull Request su Flathub

## Struttura File Flatpak

I file Flatpak si trovano in `flathub-repo/io.github.pierspad.TextMerger/`:

- `io.github.pierspad.TextMerger.yml` - Manifest principale
- `io.github.pierspad.TextMerger.metainfo.xml` - Metadati dell'app
- `io.github.pierspad.TextMerger.desktop` - File desktop

## Primo Setup su Flathub

Se è la prima volta che pubblichi su Flathub:

1. Vai su https://github.com/flathub/flathub
2. Leggi la documentazione: https://docs.flathub.org/docs/for-app-authors/submission
3. Crea un fork del repository flathub/flathub
4. Usa il script `push-flathub.sh` per preparare i file
5. Copia la cartella `flathub-repo/io.github.pierspad.TextMerger` nel tuo fork
6. Crea una Pull Request

## Aggiornamenti Successivi

Per aggiornamenti di versioni esistenti:

1. Usa il script `push-flathub.sh`
2. Aggiorna il tuo fork di Flathub con i nuovi file
3. Crea una Pull Request con le modifiche

## Troubleshooting

### Errore "flatpak-builder non trovato"
```bash
# Ubuntu/Debian
sudo apt install flatpak-builder

# Fedora
sudo dnf install flatpak-builder

# Arch
sudo pacman -S flatpak-builder
```

### Errore "Git non configurato"
```bash
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua-email@example.com"
```

### Errore "Tag non trovato"
```bash
git tag v1.0.3  # Sostituisci con la versione corretta
git push origin v1.0.3
```

### Build fallisce
1. Controlla che `pyproject.toml` sia valido
2. Verifica che tutte le dipendenze siano specificate correttamente
3. Testa il build locale prima del push

## Note Importanti

- **Sempre testare localmente** prima di pushare su Flathub
- **Versioni semantiche**: Usa il formato `x.y.z`
- **Tag Git**: Devono seguire il formato `vx.y.z`
- **Commit pulito**: Il repository deve essere pulito prima del push
- **Backup**: Gli script creano automaticamente backup dei file modificati (.bak)

## Link Utili

- [Documentazione Flathub](https://docs.flathub.org/)
- [Flatpak Builder Reference](https://docs.flatpak.org/en/latest/flatpak-builder.html)
- [App Submission Guidelines](https://github.com/flathub/flathub/wiki/App-Submission)
