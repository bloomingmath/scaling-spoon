scaling-spoon
=============
_Applicazione a sostegno della didattica della matematica_

## Idea
L'idea è avere a disposizione un'applicazione che permette di distinguere gli utenti che si registrano in diversi gruppi (più o meno corrisopondenti al corso che frequentano) e servire loro materiale di studio e domande a scelta multipla per allenarsi; materiale di studio e domande sono suddivise e oranizzate per argomenti; gli argomenti sono strutturati secondo una struttura che rappresenta le relazioni di propedeuticità.

## Applicazioni necessarie e consigliate
Vengono utilizzati i seguenti software:
 * bootstrap -- https://getbootstrap.com/docs/4.3/getting-started/introduction/
 * fastapi -- https://fastapi.tiangolo.com/
 * git -- https://git-scm.com/
 * python 3.6.8 -- https://www.python.org/
 * pycharm -- https://www.jetbrains.com/pycharm/
 * ~~react -- https://reactjs.org/docs/getting-started.html~~
 * virtualenv -- https://virtualenv.pypa.io/en/latest/
 * tutte le librerie elencate nel file requirements.txt che si possono installare direttamente con il comando `pip install -r requirements.txt`
 
# Componenti

## authentication
Dal modulo si possono importare cinque funzioni che servono a gestire creazione e login degli utenti. Il modulo funziona dipendendo da ponydb. Le funzioni sono:
 * `create_db_user(db: Database, username: str, email: str, salt: str, hashed: str, fullname: str = "") -> db.User` crea un nuovo utente con i dati forniti e lo salva nel database. Non gestisce le eccezioni.
 * `generate_access_token(username: str, expires_delta: timedelta = None) -> str` genera un token con codifica jwt, digitalmente firmata per poterne verificare l'autenticità in seguito per permettere l'accesso all'utente username; questo token deve essere inviato ad ogni successiva richiesta come header "Authorization: bearer token" o come cookie "access-token".
 * `get_db_user_or_none(db: Database, **kwargs: Any) -> Optional[db.User]` recupera un utente dal database a partire da qualsiasi keyword (probabilmente username o email). Qualsiasi eccezione venga sollevata o per qualsiasi motivo non sia possibile recuperare tale utente, restituisce None.
 * `get_user_by_access_token_or_none(db: Database, token: str) -> Optional[db.User]` a partire da un token come quelli generati da `generate_access_token` recupera l'utente corrispondente o restituisce None se per qualsiasi motivo non è possibile recuperare l'utente.
 * `get_user_by_username_and_password_or_none(db: Database, username: str, password: str) -> Optional[db.User]` con username e password, recupera un utente dal database; se per qualsiasi motivo non è possibile recuperare l'utente (ad esempio se la password è sbagliata) restituisce None.
 

## fastapi
Il lato server di questa applicazione è gestito da [FastApi](https://fastapi.tiangolo.com/) attraverso il file main.py. Questo raccoglie le richieste ai vari endpoints disponibili e restituisce le adeguate risposte in formato Json per l'api e in formato html. Inoltre, si preoccupa di servire i file collocati nelle cartelle static/, templates/ e reactfrontend/public/.

## ponydb
Per utilizzare il database è sufficiente importare due oggetti fondamentali: `db` e `db_session`.

Con `db` di può interaggire con i cinque modelli definiti che sono :`User`, `Node`, `MultipleChoiceQuestion`, `Group` e `Content`. Per ciascuno di essi si possono svolgere le stesse operazioni, comunemente:
 * creare nuove entità `db.Node(serial='0123456789ABCDEF', short='Argomento esempio')`
 * recuperare un singolo oggetto `db.User.get(username="someuser")`
 * recuperare un insieme di oggetti `db.Content.select(filetype="png")`
 * modificare un oggetto `db.Node.get(serial="0123456789ABCDEF").short = "Nuovo titolo"`
 * cancellare un oggetto `db.User.get(username="someuser").delete()`
 
 Tutte le funzioni che utilizzano il database devono essere decorate con `@db_session` o utilizzarlo come context:
```
with db_session:
    ...something with db...
```

Per maggiori dettagli, fare riferimento alla [documentazione di ponyorm](https://docs.ponyorm.org/) e alla definizione stessa dei modelli nel file ponydb/models.py 

## static
In questa cartella, tutti i file che dovranno essere serviti attraverso il browser dell'utente.

In particolare, i contenuti dell'applicazione sono nella cartella _contents_, ordinati con numero seriale. Per questo motivo, cancellare i contenuti deve essere fatto con cautela per non disallineare filesystem e database.

## tests
Usando il modulo unittest, si conducono controlli automatizzati affinché modifiche al codice non interrompano il funzionamento di parti precedentemente costruite. Sostanzialmente, le funzionalità certe dell'applicazione sono solo quelle presenti in questo modulo.

Per eseguire i controlli `python -m unittset tests`.