Questo è un sito per la prenotazione di campi da calcio. In questa app di Django, i proprietari possono inserire i propri campi e gli utenti possono prenotare il campo.

**Primo**, installare python 3.7.0:
    
    https://www.python.org/downloads/release/python-374/
    
    
**Secondo**, aggiornare pip:

    pip install --updgrade pip


**Terzo**, installare le dipendenze:

    pip install --user -r requirements.txt


**Quarto**, installare sqlite3

    sudo apt install sqlite3


**Quinto**, avviare il server:

    python manage.py runserver


**Il sito sarà visitabile all’indirizzo** 127.0.0.1:8000

——————————————————————————————————————————————————————————————————————————————————————————


**Contenuto del db**:

è possibile caricare il contenuto del dump sul db attraverso il seguente comando:

    cat db_sqlite3.sql | sqlite3 db.sqlite3



**Utenti**:

	usn: utente
	psw: LDinamici

**Proprietari**:
	
	usn: proprietario
	psw: LDinamici

	usn: proprietario1
	psw: LDinamici


**Admin**:

	usn: admin
	psw: admin