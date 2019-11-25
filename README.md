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
 * react -- https://reactjs.org/docs/getting-started.html
 * virtualenv -- https://virtualenv.pypa.io/en/latest/
 * tutte le librerie elencate nel file requirements.txt che si possono installare direttamente con il comando `pip install -r requirements.txt`
 
# Componenti

## authentication: ausili per la crittografia
Il modulo espone quattro funzioni:
 * `get_salt()` genera una stringa casuale da utilizzare successivamente per la crittografia
 * `get_serial(string)` genera una stringa esadecimale di 16 caratteri a partire da una stringa data, per identificare nodi, domande e contenuti
 * `hash_password(salt, password)` genera l'hash della password fornita dall'utente utilizzando un salt, che deve essere diverso per ciascun utente ma costante per lo stesso utente dal momento della sua registrazione in poi; questa funzione è utilizzata ogni volta che l'utente cambia password
 * `verify_password(salt, stored_password, provided_password)` verifica che la password (plain) fornita sia corretta, confrontandola con la password in database (hased) e utilizza il salt dell'utente che è salvato nel database
 
## fastapi
Il lato server di questa applicazione è gestito da [FastApi](https://fastapi.tiangolo.com/) attraverso il file main.py. Questo raccoglie le richieste ai vari endpoints disponibili e restituisce le adeguate risposte in formato Json per l'api e in formato html (la singola pagina di React) per l'indirizzo principale. Inoltre, si preoccupa di servire i file collocati nella cartella static/.

## ponydb: database e orm
Quando si deve accedere al database è sufficiente importare i tre oggetti fondamentali`db`, `db_session` e `select` con il comando `from ponydb import *`.

Con `db` si possono creare nuove entità tra quelle definite `User`, `Node`, `MultipleChoiceQuestion`, `Group` e `Content` con un comando come, ad esempio, `db.Node(serial='0123456789ABCDEF', short='Argomento esempio')`. Con `select` si possono recuperare i dati registrati nel database. Tutte le funzioni che utilizzano il database devono essere decorate con `@db_session`.

Per maggiori dettagli, fare riferimento alla [documentazione di ponyorm](https://docs.ponyorm.org/) e alla definizione stessa dei modelli nel file ponydb/models.py 

## reactfrontend
Il browser dell'utente riceve una singola pagina di html in cui tutte le funzionalità sono gestite dal frontend [ReactJs](https://reactjs.org/docs/getting-started.html). Questa applicazione comunica con il server attraverso delle richieste ajax alla api e modifica struttura e contenuti della pagina in conseguenza delle risposte che riceve.

L'estetica e l'impaginazione è sostenuta dal framework [bootstrap](https://getbootstrap.com/docs/4.3/getting-started/introduction/).

## static: files
In questa cartella, tutti i file che dovranno essere serviti attraverso il browser dell'utente.

In particolare, i contenuti dell'applicazione sono nella cartella _contents_, ordinati con numero seriale. Per questo motivo, cancellare i contenuti deve essere fatto con cautela per non disallineare filesystem e database.

## tests
Usando il modulo unittest, si conducono controlli automatizzati affinché modifiche al codice non interrompano il funzionamento di parti precedentemente costruite. Sostanzialmente, le funzionalità certe dell'applicazione sono solo quelle presenti in questo modulo.

Per eseguire i controlli `python -m unittset tests`.