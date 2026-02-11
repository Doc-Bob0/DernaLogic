"""
Module de layouts adaptatifs pour DermaLogic.

Fournit des layouts spécialisés selon la plateforme détectée.
"""

from gui.layouts.desktop import LayoutDesktop
from gui.layouts.mobile import LayoutMobile

__all__ = ['LayoutDesktop', 'LayoutMobile']
