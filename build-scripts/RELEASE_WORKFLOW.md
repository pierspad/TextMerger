# Workflow di Rilascio per TextMerger

## Panoramica

Questo progetto ora ha un workflow automatizzato per il rilascio che sincronizza automaticamente le versioni tra tutti i file necessari.

## File Coinvolti

- **PKGBUILD** (build-scripts/): File principale che contiene le info del pacchetto
- **pyproject.toml** (root): File di configurazione Python per il progetto
- **packaging/pyproject.toml**: File per il packaging 
- **Flatpak manifest** (flathub-repo/): File YAML per Flatpak
- **Metainfo XML** (flathub-repo/): Metadati per i software center

## Workflow di Rilascio

### 1. Rilascio Automatico (Raccomandato)

```bash
# Rilascia una nuova versione (es. 1.0.2)
./build-scripts/release.sh 1.0.2

# Oppure usa la versione corrente dal PKGBUILD
./build-scripts/release.sh
```

Questo script:
- Aggiorna la versione nel PKGBUILD (se specificata)
- Sincronizza TUTTE le versioni nei vari file
- Verifica la coerenza
- Crea il tag git
- Ti guida sui prossimi passi

### 2. Build per le Piattaforme

Dopo il rilascio, puoi buildare per:

#### AUR (Arch Linux)
```bash
./build-scripts/build-aur.sh
./build-scripts/push-aur.sh
```

#### Flatpak/Flathub
```bash
./build-scripts/build-flatpak.sh
```

## Vantaggi del Nuovo Sistema

### Prima (Problematico)
- Versioni hardcoded in ogni file
- Bisognava ricordarsi di aggiornare 5+ file diversi
- Errori umani frequenti
- Hash commit manuali

### Ora (Automatizzato)
- **Una sola fonte di verità**: il PKGBUILD
- **Sincronizzazione automatica** di tutti i file
- **Hash commit automatici** per Flatpak
- **Verifica coerenza** prima del rilascio
- **Workflow unificato** per tutte le piattaforme

## Dettagli Tecnici

### Script di Rilascio (`release.sh`)
- Legge versione dal PKGBUILD
- Aggiorna tutti i file di configurazione
- Crea tag git con nome `v{VERSION}`
- Verifica coerenza tra tutti i file

### Script Flatpak (`build-flatpak.sh`)
- Estrae info automaticamente dal PKGBUILD
- Aggiorna manifest YAML con versione corrente
- Ottiene hash commit automaticamente (da tag o HEAD)
- Aggiorna metainfo XML con data corrente

### Script AUR (`build-aur.sh`)
- Già esisteva e funziona bene
- Sincronizza automaticamente con packaging/pyproject.toml

## Risoluzione Problemi

### Q: Il build Flatpak fallisce con "tag non trovato"
**A:** Assicurati di aver pushato il tag git:
```bash
git push origin v1.0.2
```

### Q: Le versioni non sono sincronizzate
**A:** Usa sempre lo script di rilascio invece di modificare manualmente:
```bash
./build-scripts/release.sh 1.0.2
```

### Q: Hash commit sbagliato nel manifest Flatpak
**A:** Lo script usa automaticamente:
1. Hash del tag `v{VERSION}` se esiste
2. Hash dell'HEAD corrente se il tag non esiste

### Q: Come aggiornare solo una parte?
**A:** Non farlo. Usa sempre il workflow completo per evitare inconsistenze.

## Processo per Flathub

1. Fai il rilascio: `./build-scripts/release.sh 1.0.2`
2. Pusha tutto: `git push && git push origin v1.0.2`
3. Testa il build: `./build-scripts/build-flatpak.sh`
4. Crea PR su Flathub con i file aggiornati

## Migliorie Future

- [ ] Integrazione con GitHub Actions
- [ ] Build automatici su tag push
- [ ] Validazione automatica dei file manifest
- [ ] Release notes automatiche
