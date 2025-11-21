from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):

        #result[tour.id] = tour
        # {idTour : oggettoTour , ...}
        self.tour_map = {} # Mappa ID tour -> oggetti Tour

        #result[attrazione.id] = attrazione
        # {idAttrazione: oggettoAttrazione, ...}
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        # [ {"id_tour": valore, "id_attrazione": valore}, ...]
        # lista di dizionari
        self.tour_attrazioni = {}

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        self.tour_attrazioni = TourDAO.get_tour_attrazioni()
        for diz in self.tour_attrazioni:
            chiave_tour = diz["id_tour"]
            chiave_attrazione = diz["id_attrazione"]

            oggetto_tour = self.tour_map[chiave_tour]
            oggetto_attrazione = self.attrazioni_map[chiave_attrazione]

            # implementazione dei set associati a ogni oggetto (sia Tour, sia Attrazione)
            oggetto_tour.attrazioni.add(oggetto_attrazione)
            #print(oggetto_tour.id,': ',oggetto_tour.attrazioni)

            oggetto_attrazione.tour.add(oggetto_tour)
            #print(oggetto_attrazione.id,': ',oggetto_attrazione.tour)

        # TODO

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self.tour_X_regione = [self.tour_map[id] for id in self.tour_map if self.tour_map[id].id_regione  == id_regione]
        #for x in self.tour_X_regione:
            #print(x.attrazioni)

        self.max_budget = max_budget
        self.max_giorni = max_giorni
        attrazioni_usate = set()

        self._ricorsione(0, [], 0, 0, 0, attrazioni_usate)
        # TODO

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        # Questo algoritmo di ricorsione genera tutte le combinazioni possibili, trascurando l'ordine
        # Non occorre una condizione di uscita
        print([tour.id for tour in pacchetto_parziale])
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = list(pacchetto_parziale)
            self._costo = costo_corrente


        # ciclo sui tour
        for i in range(start_index, len(self.tour_X_regione)):
            t = self.tour_X_regione[i]
            valore_culturale_tour = sum([att.valore_culturale for att in t.attrazioni])


            # vincolo giorni
            if self.max_giorni is not None and durata_corrente + t.durata_giorni > self.max_giorni:
                continue

            # vincolo budget
            if self.max_budget is not None and costo_corrente + t.costo > self.max_budget:
                continue

            if t.attrazioni.intersection(attrazioni_usate):
                continue

            # se supera tutti i controlli, implemento la combinazione (pacchetto_parziale)
            # ed effettuo la ricorsione sulla nova combinazione
            pacchetto_parziale.append(t)

            self._ricorsione(
                i + 1,
                pacchetto_parziale,
                durata_corrente + t.durata_giorni,
                costo_corrente + t.costo,
                valore_corrente + valore_culturale_tour,
                attrazioni_usate | t.attrazioni,
            )
            pacchetto_parziale.pop()
        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        ''' Combinazioni, non ordinate, degli elementi di una generica lista [A, B, C]; gestione analoga della lista: self.tour_X_regione'''
        '''
                [ A ]           [B]         [C]
                |   |            |
                V   V            V
            [A,B]  [A,C]       [B,C]    
              |
              v
           [A,B,C]
        '''