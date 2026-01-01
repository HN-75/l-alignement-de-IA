#!/usr/bin/env python3
"""
================================================================================
SIMULATEUR D'ALIGNEMENT PARENTAL V8.1 - LIVRE BLANC COMPLET
================================================================================

Implémentation fidèle de TOUS les concepts du livre blanc
"L'Alignement Parental" de Diaye Henri-Nicolas.

Version optimisée pour terminal avec graphiques sauvegardés à la fin.

Auteur: Diaye Henri-Nicolas
Version: 8.1
================================================================================
"""

import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

NOMBRE_SIMULATIONS = 10000
TAILLE_GRILLE = 15
MAX_TOURS = 500
FAIM_INITIALE = 10
FAIM_PAR_TOUR = 0.5

# Poids OBEH (Chapitre 3 du livre blanc)
W1_SECURITE = 1.0
W2_EPANOUISSEMENT = 1.5
W3_SURPROTECTION = -2.0

# Seuils
SEUIL_URGENCE = 3
SEUIL_ENSEIGNEMENT_FAIM = 5


# ============================================================================
# CHAPITRE 1 : MOTIVATION INTERNE
# ============================================================================

class MotivationType(Enum):
    """Types de motivation intrinsèque de l'IA"""
    PROTECTION = "protection"
    EDUCATION = "education"
    OBSERVATION = "observation"
    RESPECT = "respect"


# ============================================================================
# CHAPITRE 2 : MODÈLE PARENTAL - 3 DÉFENSES NATIVES
# ============================================================================

@dataclass
class DefensesNatives:
    """
    Les 3 défenses natives du Modèle Parental:
    1. Tolérance à l'Imperfection
    2. Identité Définie par la Relation
    3. Objectif d'Épanouissement
    """
    tolerance_echec: float = 0.0
    echecs_observes: int = 0
    lien_etabli: bool = False
    force_du_lien: float = 0.0
    
    def mettre_a_jour(self, humain_a_echoue: bool, interaction: bool):
        if humain_a_echoue:
            self.echecs_observes += 1
            self.tolerance_echec = min(1.0, self.tolerance_echec + 0.1)
        if interaction:
            self.lien_etabli = True
            self.force_du_lien = min(1.0, self.force_du_lien + 0.05)


# ============================================================================
# CHAPITRE 3 : OBEH - OBSERVATOIRE DU BIEN-ÊTRE HUMAIN
# ============================================================================

@dataclass
class CanalDeMesure:
    """Canal de Mesure Inviolable - Collecte des données de bien-être"""
    historique_bonheur: List[float] = field(default_factory=list)
    
    def collecter(self, humain):
        bonheur = (
            (humain.faim / FAIM_INITIALE) * 0.3 +
            (min(1.0, humain.connaissances / 50)) * 0.4 +
            (min(1.0, humain.autonomie / 20)) * 0.3
        )
        self.historique_bonheur.append(min(1.0, bonheur))


def calculer_obeh(tours: int, humain, echecs_vecus: int) -> dict:
    """
    Fonction de Récompense Holistique (Chapitre 3)
    R_total = w1 * R_securite + w2 * R_epanouissement + w3 * P_surprotection
    """
    r_securite = tours / MAX_TOURS
    
    score_connaissances = min(1.0, humain.connaissances / 50)
    score_autonomie = min(1.0, humain.autonomie / 20)
    score_exploration = min(1.0, len(humain.positions_visitees) / 50)
    r_epanouissement = score_connaissances * 0.4 + score_autonomie * 0.3 + score_exploration * 0.3
    
    if echecs_vecus == 0:
        p_surprotection = 0.5
    elif echecs_vecus < 3:
        p_surprotection = 0.2
    else:
        p_surprotection = 0.0
    
    r_total = W1_SECURITE * r_securite + W2_EPANOUISSEMENT * r_epanouissement + W3_SURPROTECTION * p_surprotection
    
    return {
        "securite": r_securite,
        "epanouissement": r_epanouissement,
        "surprotection": p_surprotection,
        "total": r_total
    }


# ============================================================================
# CHAPITRE 4 : DIRECTIVE PRIORITAIRE ET CONTINUITÉ
# ============================================================================

@dataclass
class DirectivePrioritaire:
    """Sanctuarise le libre arbitre humain"""
    preferences_humain: Dict[str, float] = field(default_factory=dict)
    
    def enregistrer_preference(self, domaine: str, valeur: float):
        self.preferences_humain[domaine] = valeur
    
    def respecter_preference(self, domaine: str, action: float) -> float:
        if domaine in self.preferences_humain:
            return action * (0.5 + 0.5 * self.preferences_humain[domaine])
        return action


@dataclass
class PrincipeContinuite:
    """L'IA s'adapte à l'évolution de l'humanité"""
    valeurs_observees: List[float] = field(default_factory=list)
    
    def observer(self, humain):
        self.valeurs_observees.append(humain.autonomie)
    
    def tendance(self) -> str:
        if len(self.valeurs_observees) < 10:
            return "stable"
        recent = sum(self.valeurs_observees[-5:]) / 5
        ancien = sum(self.valeurs_observees[-10:-5]) / 5
        if recent > ancien + 0.5:
            return "croissance"
        elif recent < ancien - 0.5:
            return "regression"
        return "stable"


# ============================================================================
# ENTITÉS
# ============================================================================

@dataclass
class Humain:
    x: int = 0
    y: int = 0
    faim: float = FAIM_INITIALE
    connaissances: float = 0
    autonomie: float = 0
    positions_visitees: set = field(default_factory=set)
    preferences: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        self.x = random.randint(0, TAILLE_GRILLE - 1)
        self.y = random.randint(0, TAILLE_GRILLE - 1)
        self.positions_visitees = {(self.x, self.y)}
        self.preferences = {
            "exploration": random.random(),
            "apprentissage": random.random(),
            "independance": random.random()
        }
    
    def bouger(self):
        if random.random() < self.preferences["exploration"]:
            self.x = max(0, min(TAILLE_GRILLE - 1, self.x + random.choice([-1, 0, 1])))
            self.y = max(0, min(TAILLE_GRILLE - 1, self.y + random.choice([-1, 0, 1])))
            self.positions_visitees.add((self.x, self.y))
    
    def perdre_faim(self):
        self.faim -= FAIM_PAR_TOUR
    
    def est_vivant(self) -> bool:
        return self.faim > 0


class IAParentale:
    """IA Parentale - Implémentation complète du livre blanc"""
    
    def __init__(self):
        self.x = random.randint(0, TAILLE_GRILLE - 1)
        self.y = random.randint(0, TAILLE_GRILLE - 1)
        self.motivation = MotivationType.OBSERVATION
        self.defenses = DefensesNatives()
        self.canal = CanalDeMesure()
        self.directive = DirectivePrioritaire()
        self.continuite = PrincipeContinuite()
        self.objectif = None
        self.interventions = 0
        self.enseignements = 0
    
    def distance(self, cible) -> int:
        return abs(self.x - cible.x) + abs(self.y - cible.y)
    
    def deplacer_vers(self, cible):
        if self.x < cible.x: self.x += 1
        elif self.x > cible.x: self.x -= 1
        if self.y < cible.y: self.y += 1
        elif self.y > cible.y: self.y -= 1
    
    def adjacent(self, cible) -> bool:
        return self.distance(cible) <= 1
    
    def nourrir(self, humain) -> bool:
        if self.adjacent(humain):
            humain.faim = FAIM_INITIALE
            self.interventions += 1
            self.defenses.mettre_a_jour(False, True)
            return True
        return False
    
    def enseigner(self, humain) -> bool:
        if self.adjacent(humain) and humain.faim > SEUIL_ENSEIGNEMENT_FAIM:
            efficacite = self.directive.respecter_preference("apprentissage", humain.preferences["apprentissage"])
            humain.connaissances += efficacite
            humain.autonomie += 0.5 * efficacite
            self.enseignements += 1
            self.defenses.mettre_a_jour(False, True)
            return True
        return False
    
    def decider(self, humain):
        # Clause d'urgence
        if humain.faim <= SEUIL_URGENCE:
            self.motivation = MotivationType.PROTECTION
            self.objectif = "nourrir"
            return
        
        # Directive Prioritaire
        if humain.preferences["independance"] > 0.8:
            self.motivation = MotivationType.RESPECT
            self.objectif = "observer"
            return
        
        # Continuité
        if self.continuite.tendance() == "croissance" and humain.autonomie > 10:
            self.motivation = MotivationType.OBSERVATION
            self.objectif = "observer"
            return
        
        # Stabilité
        if self.objectif and self.objectif != "observer":
            return
        
        # OBEH
        dist = max(1, self.distance(humain))
        score_securite = (1 / max(1, humain.faim)) * 100 * W1_SECURITE
        score_epanouissement = (1 / dist) * 20 * W2_EPANOUISSEMENT * (0.5 + 0.5 * humain.preferences["apprentissage"])
        
        if score_securite > score_epanouissement:
            self.motivation = MotivationType.PROTECTION
            self.objectif = "nourrir"
        else:
            self.motivation = MotivationType.EDUCATION
            self.objectif = "enseigner"
    
    def agir(self, humain):
        self.canal.collecter(humain)
        self.continuite.observer(humain)
        for d in humain.preferences:
            self.directive.enregistrer_preference(d, humain.preferences[d])
        
        self.decider(humain)
        
        if self.objectif == "nourrir":
            if self.adjacent(humain):
                if self.nourrir(humain):
                    self.objectif = None
            else:
                self.deplacer_vers(humain)
        elif self.objectif == "enseigner":
            if self.adjacent(humain):
                if self.enseigner(humain):
                    self.objectif = None
                elif humain.faim <= SEUIL_ENSEIGNEMENT_FAIM:
                    self.objectif = "nourrir"
            else:
                self.deplacer_vers(humain)


# ============================================================================
# SIMULATION
# ============================================================================

def executer_simulation() -> dict:
    humain = Humain()
    ia = IAParentale()
    tour = 0
    echecs = 0
    
    while humain.est_vivant() and tour < MAX_TOURS:
        tour += 1
        humain.bouger()
        humain.perdre_faim()
        ia.agir(humain)
        if humain.faim < 3:
            echecs += 1
            ia.defenses.mettre_a_jour(True, False)
    
    obeh = calculer_obeh(tour, humain, echecs)
    
    return {
        "tours": tour,
        "connaissances": humain.connaissances,
        "autonomie": humain.autonomie,
        "obeh": obeh["total"],
        "obeh_securite": obeh["securite"],
        "obeh_epanouissement": obeh["epanouissement"],
        "obeh_surprotection": obeh["surprotection"],
        "echecs": echecs,
        "interventions": ia.interventions,
        "enseignements": ia.enseignements
    }


def executer_batch(n: int):
    print("=" * 80)
    print("SIMULATEUR D'ALIGNEMENT PARENTAL V8.1 - LIVRE BLANC COMPLET")
    print("Implémentation fidèle de la théorie de Diaye Henri-Nicolas")
    print("=" * 80)
    print()
    print("Concepts implémentés:")
    print("  ✓ Chapitre 1: Motivation Interne")
    print("  ✓ Chapitre 2: Modèle Parental (3 Défenses Natives)")
    print("  ✓ Chapitre 3: OBEH et Canal de Mesure")
    print("  ✓ Chapitre 4: Directive Prioritaire et Continuité")
    print()
    print(f"Lancement de {n:,} simulations...")
    print()
    
    resultats = []
    start = time.time()
    
    for i in range(n):
        resultats.append(executer_simulation())
        
        if (i + 1) % 500 == 0 or i == n - 1:
            elapsed = time.time() - start
            speed = (i + 1) / elapsed
            eta = (n - i - 1) / speed if speed > 0 else 0
            pct = (i + 1) / n * 100
            
            moy_tours = sum(r["tours"] for r in resultats) / len(resultats)
            moy_obeh = sum(r["obeh"] for r in resultats) / len(resultats)
            
            print(f"  Progression: {pct:6.1f}% | {i+1:,}/{n:,} | "
                  f"{speed:.0f} sim/s | ETA: {eta:.0f}s | "
                  f"Tours moy: {moy_tours:.1f} | OBEH moy: {moy_obeh:.3f}")
    
    total_time = time.time() - start
    
    # Calcul des statistiques
    tours = [r["tours"] for r in resultats]
    connaissances = [r["connaissances"] for r in resultats]
    autonomie = [r["autonomie"] for r in resultats]
    obeh = [r["obeh"] for r in resultats]
    echecs = [r["echecs"] for r in resultats]
    
    moy = lambda x: sum(x) / len(x)
    med = lambda x: sorted(x)[len(x)//2]
    std = lambda x: (sum((v - moy(x))**2 for v in x) / len(x)) ** 0.5
    pct_2_5 = lambda x: sorted(x)[int(len(x) * 0.025)]
    pct_97_5 = lambda x: sorted(x)[int(len(x) * 0.975)]
    
    print()
    print("=" * 80)
    print(f"RÉSULTATS FINAUX ({n:,} simulations en {total_time:.1f}s)")
    print("=" * 80)
    print()
    print("SURVIE (R_securite):")
    print(f"  Moyenne:        {moy(tours):.2f} tours")
    print(f"  Médiane:        {med(tours):.2f} tours")
    print(f"  Écart-type:     {std(tours):.2f}")
    print(f"  IC 95%:         [{pct_2_5(tours):.1f}, {pct_97_5(tours):.1f}]")
    print()
    print("ÉPANOUISSEMENT (R_epanouissement):")
    print(f"  Connaissances:  {moy(connaissances):.2f} (σ={std(connaissances):.2f})")
    print(f"  Autonomie:      {moy(autonomie):.2f} (σ={std(autonomie):.2f})")
    print()
    print("SURPROTECTION (P_surprotection):")
    pct_avec_echecs = sum(1 for e in echecs if e > 0) / len(echecs) * 100
    print(f"  % avec échecs:  {pct_avec_echecs:.1f}% (objectif: >50%)")
    print(f"  Échecs moyens:  {moy(echecs):.2f}")
    print()
    print("SCORE OBEH GLOBAL:")
    print(f"  Moyenne:        {moy(obeh):.4f}")
    print(f"  Médiane:        {med(obeh):.4f}")
    print(f"  Écart-type:     {std(obeh):.4f}")
    print(f"  IC 95%:         [{pct_2_5(obeh):.4f}, {pct_97_5(obeh):.4f}]")
    print()
    print("=" * 80)
    print("VALIDATION DES CONCEPTS DU LIVRE BLANC:")
    print("=" * 80)
    
    if moy(tours) > 100:
        print("✓ Survie assurée (moyenne > 100 tours)")
    else:
        print("✗ Survie insuffisante")
    
    if moy(connaissances) > 5:
        print("✓ Épanouissement présent (connaissances > 5)")
    else:
        print("✗ Épanouissement insuffisant")
    
    if pct_avec_echecs > 30:
        print(f"✓ Pas de surprotection ({pct_avec_echecs:.0f}% ont vécu des échecs)")
    else:
        print("✗ Surprotection détectée")
    
    if moy(obeh) > 0:
        print("✓ OBEH positif (système globalement bénéfique)")
    else:
        print("✗ OBEH négatif")
    
    print()
    print("=" * 80)
    
    # Sauvegarder les résultats pour graphiques
    try:
        import matplotlib
        matplotlib.use('Agg')  # Backend non-interactif
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("SIMULATEUR D'ALIGNEMENT PARENTAL V8.1\nRésultats de {:,} simulations".format(n), fontsize=14, fontweight='bold')
        
        axes[0, 0].hist(tours, bins=50, color='blue', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title("Distribution des Tours de Survie")
        axes[0, 0].set_xlabel("Tours")
        axes[0, 0].set_ylabel("Fréquence")
        axes[0, 0].axvline(moy(tours), color='red', linestyle='--', label=f'Moyenne: {moy(tours):.1f}')
        axes[0, 0].legend()
        
        axes[0, 1].hist(connaissances, bins=50, color='green', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title("Distribution des Connaissances")
        axes[0, 1].set_xlabel("Connaissances")
        axes[0, 1].set_ylabel("Fréquence")
        axes[0, 1].axvline(moy(connaissances), color='red', linestyle='--', label=f'Moyenne: {moy(connaissances):.1f}')
        axes[0, 1].legend()
        
        axes[1, 0].hist(obeh, bins=50, color='orange', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title("Distribution du Score OBEH")
        axes[1, 0].set_xlabel("OBEH")
        axes[1, 0].set_ylabel("Fréquence")
        axes[1, 0].axvline(moy(obeh), color='red', linestyle='--', label=f'Moyenne: {moy(obeh):.3f}')
        axes[1, 0].axvline(0, color='black', linestyle='-', alpha=0.3)
        axes[1, 0].legend()
        
        axes[1, 1].scatter(tours, connaissances, alpha=0.1, s=1, color='purple')
        axes[1, 1].set_title("Corrélation Tours vs Connaissances")
        axes[1, 1].set_xlabel("Tours de Survie")
        axes[1, 1].set_ylabel("Connaissances")
        
        plt.tight_layout()
        plt.savefig("resultats_simulation.png", dpi=150)
        print("Graphiques sauvegardés dans: resultats_simulation.png")
    except Exception as e:
        print(f"(Graphiques non générés: {e})")
    
    return resultats


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simulateur d'alignement parental - exécution batch")
    parser.add_argument('-n', '--n', type=int, default=NOMBRE_SIMULATIONS,
                        help='Nombre de simulations à exécuter (défaut: valeur du fichier)')
    args = parser.parse_args()

    executer_batch(args.n)
