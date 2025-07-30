"""
Implementación principal del compilador de proyectos
"""

import logging
import os
from pathlib import Path
from typing import Optional

from .compiler_service import CompilerService
from .file_manager import FileManager

logger = logging.getLogger(__name__)


class PythonCompiler:
    """Implementación principal para compilación de proyectos Python"""

    def __init__(
        self,
        compiler_service: Optional[CompilerService] = None,
        file_manager: Optional[FileManager] = None,
    ):
        self.compiler_service = compiler_service or CompilerService()
        self.file_manager = file_manager or FileManager()

    def compile_project(
        self,
        source_dir: str,
        output_dir: str,
        template: str = "basic",
        exclude_file: Optional[str] = None,
        remove_py: bool = False,
    ) -> bool:
        """
        Compila un proyecto Python completo

        Args:
            source_dir: Directorio fuente
            output_dir: Directorio de salida
            template: Template de exclusión
            exclude_file: Archivo custom de exclusiones
            remove_py: Si eliminar archivos .py originales

        Returns:
            True si la compilación fue exitosa
        """
        try:
            source_path = Path(source_dir).resolve()
            output_path = Path(output_dir).resolve()

            if not source_path.exists():
                logger.error(f"Directorio fuente no existe: {source_path}")
                return False

            # Crear directorio de salida
            if not self.file_manager.create_directory(output_path):
                return False

            # Obtener patrones de exclusión
            exclude_patterns = self.compiler_service.get_exclude_patterns(
                template, exclude_file
            )
            logger.info(f"Usando template: {template}")
            logger.info(f"Patrones de exclusión: {len(exclude_patterns)}")

            compiled_count = 0
            copied_count = 0
            excluded_count = 0

            # Recorrer todos los archivos
            for root, dirs, files in os.walk(source_path):
                # Filtrar directorios excluidos
                dirs[:] = [
                    d
                    for d in dirs
                    if not self.compiler_service.should_exclude(
                        Path(root) / d, exclude_patterns
                    )
                ]

                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(source_path)

                    # Verificar si debe excluirse
                    if self.compiler_service.should_exclude(file_path, exclude_patterns):
                        excluded_count += 1
                        continue

                    output_file_path = output_path / relative_path

                    if file.endswith(".py"):
                        # Compilar archivo Python
                        pyc_path = output_file_path.with_suffix(".pyc")
                        if self.compiler_service.compile_python_file(file_path, pyc_path):
                            compiled_count += 1

                            # Eliminar .py original si se solicita
                            if remove_py and output_file_path != file_path:
                                try:
                                    file_path.unlink()
                                except Exception as e:
                                    logger.warning(f"No se pudo eliminar {file_path}: {e}")
                        else:
                            # Si falla la compilación, copiar el archivo original
                            if self.file_manager.copy_file(file_path, output_file_path):
                                copied_count += 1
                    else:
                        # Copiar archivo tal como está
                        if self.file_manager.copy_file(file_path, output_file_path):
                            copied_count += 1

            logger.info(f"✅ Compilación completada:")
            logger.info(f"   📦 Archivos compilados: {compiled_count}")
            logger.info(f"   📋 Archivos copiados: {copied_count}")
            logger.info(f"   🚫 Archivos excluidos: {excluded_count}")
            logger.info(f"   📁 Salida: {output_path}")

            return True

        except Exception as e:
            logger.error(f"Error durante la compilación: {e}")
            return False

    def list_templates(self) -> None:
        """Lista los templates disponibles"""
        templates = self.compiler_service.list_available_templates()
        print("Templates disponibles:")
        for template in templates:
            patterns = self.compiler_service.get_exclude_patterns(template)
            print(f"  {template}:")
            for pattern in patterns[:5]:  # Mostrar solo los primeros 5
                print(f"    - {pattern}")
            if len(patterns) > 5:
                print(f"    ... y {len(patterns) - 5} más")
            print()
