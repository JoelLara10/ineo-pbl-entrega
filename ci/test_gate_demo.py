"""Intentional, opt-in failed assertion for a teaching demonstration."""
import os


def test_controlled_failure_blocks_promotion():
    assert os.getenv('INEO_FORCE_FAILURE', 'false').lower() != 'true', (
        'FALLO CONTROLADO solicitado: Jenkins debe fallar y omitir promocion. '
        'No es un defecto del sistema ni un resultado UAT.'
    )
