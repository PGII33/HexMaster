import competences
import jimmys_ext
import unites
from competences import peut_cibler_allie

jimmys = True
try:
    from jimmys_ext import *
except ImportError:
    jimmys = False

if jimmys:
    # 1. On importe d’abord le module original
    # import unites
    OrigMourir = unites.Unite.mourir
    Origdebut_tour = unites.Unite.debut_tour
    Origutiliser_competence_active = competences.utiliser_competence_active
    Origest_competence_active = competences.est_competence_active
    Origutiliser_competence = unites.Unite.utiliser_competence
    Origpeut_cibler_allie = competences.peut_cibler_allie
    Origget_cooldown_competence = unites.Unite.get_cooldown_competence

    # 2. On définit les nouveautés
    # dans jimmys_ext

    # 3. On étend la liste et on remplace les méthodes par des méthodes étendus
    CLASSES_UNITE_ETENDU = jimmys_ext.JIMMYS_UNITE + unites.CLASSES_UNITES
    competences.COMPETENCES.update(JIMMYS_COMPETENCE)

    def mourir_etendu(self, toutes_unites=None):
        # appel de l’original
        etat_change = OrigMourir(self, toutes_unites)
        if etat_change:
            # on est passé de vivant→mort : on déclenche vos skills
            if self.comp == "boneful TADOS":
                liche_tados(self)
            elif self.comp == "angry TADOS":
                mechant_tados(self)
            elif self.comp == "Jimmy's TADOS":
                jimmy_tados(self)
        return etat_change

    def debut_tour_etendu(self, toutes_unites, plateau, q_range=None, r_range=None):
        # appels de l'original
        Origdebut_tour(self, toutes_unites, plateau, q_range, r_range)
        if self.comp == "Jimmy's tas d'os":
            jimmys_everywhere(self, toutes_unites)

    def utiliser_competence_active_etendu(unite, nom_competence, cible, toutes_unites=None):
        etat = Origutiliser_competence_active(unite, nom_competence, cible, toutes_unites)
        if nom_competence == "Jimmiest":
            return superjimmy(cible)
        return etat

    def est_competence_active_etendu(nom_competence):
        return Origest_competence_active(nom_competence) or nom_competence in ["Jimmiest"]

    def utiliser_competence_etendu(self, cible=None, toutes_unites=None):
        etat = Origutiliser_competence(cible, toutes_unites)
        if not self.competence_utilisee_ce_tour:
            success = co.utiliser_competence_active(self, self.comp, cible, toutes_unites)
            if success:
                # Activer le cooldown et marquer comme utilisée ce tour
                self.competence_utilisee_ce_tour = True
            return success
        return etat

    def peut_cibler_allie_etendu(nom_competence):
        return peut_cibler_allie(nom_competence) or nom_competence in ["Jimmiest"]

    def get_cooldown_competence_etendu(self):
        if self.comp == "Jimmiest":
            return 0
        return Origget_cooldown_competence(self)


    # 4 .on reinjecte
    unites.CLASSES_UNITES = CLASSES_UNITE_ETENDU
    unites.Unite.mourir = mourir_etendu
    unites.Unite.debut_tour = debut_tour_etendu
    competences.est_competence_active = est_competence_active_etendu
    competences.utiliser_competence_active = utiliser_competence_active_etendu
    competences.utiliser_competence = utiliser_competence_etendu
    competences.peut_cibler_allie = peut_cibler_allie_etendu
    unites.Unite.get_cooldown_competence = get_cooldown_competence_etendu

# 5. On lance le vrai point d’entrée
from main import *
if __name__ == "__main__":
    HexaMaster().run()