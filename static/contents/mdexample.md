scaling-spoon
=============
_Applicazione a sostegno della didattica della matematica_ 

## Idea
L'idea è avere a disposizione un'applicazione che permette di distinguere gli utenti che si registrano in diversi gruppi (più o meno corrisopondenti al corso che frequentano) e servire loro materiale di studio e domande a scelta multipla per allenarsi; materiale di studio e domande sono suddivise per argomenti; gli argomenti sono organizzati secondo una struttura che rappresenta le relazioni di propedeuticità.
 
# Componenti

## fastapi
_FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints._

Nel file main.py è definita un'applicazione del framework [FastAPI](https://fastapi.tiangolo.com/) che si può servire con il comando `uvicorn main:app`. Questa raccoglie le richieste ai vari endpoints disponibili(definiti in `routers`) e restituisce le adeguate risposte in formato json o in formato html (generato dinamicamente con [jinja2](https://jinja.palletsprojects.com/en/2.10.x/) a partire dai componenti in `templates`). I contenuti sono conservati e recuperati con il database `popy`. L'applicazione rende accessibili all'url `/static` i file collocati nella omonima cartella.

## popy
Popy è un modulo per collegare il database [ponyorm](https://ponyorm.org/) a FastAPI. Espone principalmente i seguenti oggetti:
 * ModelContainer. In un modulo a parte si definiscono le basi per i dati da utilizzare e si genera con `ModelConteiner(bases_module, provider="sqlite", filename="database.sqlite", create_db=True)` un oggetto che contiene: un modello ponyorm per ciascuna base definita nel modulo; ciascun modello è collegato al database indicato; ciascun modello è dotati di un insieme di operazioni che facilitano l'interazione con il database; ciascun modello è arricchito con schemi di pydantic per validare i dati di ciascuna operazione.
 * Required, Optional, Set, Json. Nel definire le classi si possono usare questi campi, così come si definirebbero i modelli per ponydb.
 * db_session. Qualsiasi operazioni che coinvolga il database deve essere circondata da questo context manager:
     ```python
    with db_session:
        # Do something with database
    ```

Per maggiori dettagli, fare riferimento alla [documentazione di ponyorm](https://docs.ponyorm.org/) e alla definizione stessa dei modelli nel file bases.py 

## routers
Ogni richiesta http al server viene indirizzata ad un endpoint, una funzione che interpreta le informazioni presenti nella richiesta e produce una risposta. Nel pacchetto routers sono definiti vari moduli ognuno dei quali espone una sola funzione `make_router(mc: ModelContainer, app: FastAPI, templates: Jinja2Templates)` che restituisce un router il quale va aggiunto all'applicazione principale con `app.include_router(module.make_router(mc, app, templates))`. Maggiori informazioni sui [router di fastapi](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

## helpers
Nel modulo helpers sono raccolte alcune funzioni che aiutano in diverse parti dell'applicazione. Sono funzioni che non dipendono da altri moduli definiti nel progetto, ma sono librerie esterne.

## static
In questa cartella, tutti i file che dovranno essere serviti attraverso il browser dell'utente, come .js e .css.

~~In particolare, i contenuti dell'applicazione sono nella cartella _contents_, ordinati con numero seriale. Per questo motivo, cancellare i contenuti deve essere fatto con cautela per non disallineare filesystem e database.~~

## tests e selenium_testing
Per testare l'applicazione si usa [pytest](https://docs.pytest.org/en/latest/) e [selenium](https://selenium.dev/documentation/en/). I test si trovano nella cartella _tests_ e nella cartella _selenium_testing_, ogni file che si chiami _test*_ contiene dei test che saranno eseguiti automaticamente da pytest. Per eseguire i test di selenium è previsto che l'applicazione sia già attiva all'indirizzo http://127.0.0.1:8000.


## Applicazioni utilizzate
Sono stati utilizzati (e pertanto si ringraziano) i seguenti software liberi:
 * bootstrap -- https://getbootstrap.com/docs/4.3/getting-started/introduction/
 * git -- https://git-scm.com/
 * python 3.7.5 -- https://www.python.org/
 * pycharm -- https://www.jetbrains.com/pycharm/
 * atom -- https://atom.io/
 * virtualenv -- https://virtualenv.pypa.io/en/latest/
 * tutte le librerie elencate nel file requirements.txt che si possono installare direttamente con il comando `pip install -r requirements.txt`